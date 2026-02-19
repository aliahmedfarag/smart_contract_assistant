from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langserve import add_routes
import os
import shutil

from src.ingestion import DocumentIngestion
from src.qa_chain import QASystem

load_dotenv()

app = FastAPI(
    title="Smart Contract Assistant API",
    description="AI-powered document analysis system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ingestion = None
qa_system = None


class QuestionRequest(BaseModel):
    question: str
    k: int = 4


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict]
    guardrail_triggered: bool = False


llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.1
)

prompt = PromptTemplate(
    template="Answer this question clearly: {question}",
    input_variables=["question"]
)

add_routes(app, prompt | llm, path="/langserve")


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "document_loaded": qa_system is not None,
        "langserve": "http://127.0.0.1:8000/langserve"
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global ingestion, qa_system

    if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX supported")

    try:
        os.makedirs("data", exist_ok=True)
        temp_path = f"data/{file.filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ingestion = DocumentIngestion()
        save_name = os.path.splitext(file.filename)[0]
        vectorstore = ingestion.ingest_document(temp_path, save_name)
        qa_system = QASystem(vectorstore)

        return {
            "message": "Document processed successfully",
            "filename": file.filename,
            "status": "ready"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=QuestionResponse)
async def ask(request: QuestionRequest):
    global qa_system

    if qa_system is None:
        raise HTTPException(status_code=400, detail="Please upload a document first")

    try:
        result = qa_system.ask(request.question)
        return QuestionResponse(
            question=request.question,
            answer=result['answer'],
            sources=result['sources'],
            guardrail_triggered=result.get('guardrail_triggered', False)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def history():
    if qa_system is None:
        return {"history": [], "total": 0}
    h = qa_system.get_history()
    return {"history": h, "total": len(h)}


@app.delete("/history")
async def clear():
    if qa_system:
        qa_system.clear_history()
    return {"message": "History cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)