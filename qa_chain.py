import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from src.retrieval import DocumentRetriever

load_dotenv()

FORBIDDEN_TOPICS = [
    "password", "hack", "weapon", "illegal",
    "drug", "violence", "exploit"
]


class QASystem:

    def __init__(self, vectorstore):
        self.retriever = DocumentRetriever(vectorstore, k=4)
        self.chat_history = []

        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.1
        )

        self.prompt_template = PromptTemplate(
            template="""You are a helpful assistant analyzing documents.
Answer ONLY based on the context provided.
If the answer is not in the context, say exactly: "I cannot find this information in the document."
Do not make up information.

Context:
{context}

Question: {question}

Answer:""",
            input_variables=["context", "question"]
        )

    def check_guardrails(self, question: str) -> Dict:
        question_lower = question.lower()

        for topic in FORBIDDEN_TOPICS:
            if topic in question_lower:
                return {
                    "passed": False,
                    "reason": f"Question contains forbidden topic: {topic}"
                }

        if len(question.strip()) < 3:
            return {"passed": False, "reason": "Question too short"}

        if len(question) > 500:
            return {"passed": False, "reason": "Question too long"}

        return {"passed": True, "reason": ""}

    def ask(self, question: str, k: int = 4) -> Dict[str, Any]:
        guard_result = self.check_guardrails(question)
        if not guard_result["passed"]:
            return {
                "question": question,
                "answer": f"Warning: {guard_result['reason']}",
                "sources": [],
                "guardrail_triggered": True
            }

        result = self.retriever.get_context(question, k=k)
        context = result["context"]
        sources = result["sources"]

        if not context:
            return {
                "question": question,
                "answer": "I cannot find relevant information in the document",
                "sources": [],
                "guardrail_triggered": False
            }

        prompt = self.prompt_template.format(
            context=context[:3000],
            question=question
        )

        response = self.llm.invoke(prompt)
        answer = response.content.strip()

        self.chat_history.append({
            "question": question,
            "answer": answer
        })

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources),
            "guardrail_triggered": False
        }

    def summarize(self) -> str:
        docs = self.retriever.search("main topics summary overview", k=5)
        combined = "\n".join([doc.page_content for doc in docs])

        prompt = f"""Summarize the following document in simple clear points:

{combined[:3000]}

Summary:"""

        response = self.llm.invoke(prompt)
        return response.content.strip()

    def get_history(self) -> List[Dict]:
        return self.chat_history

    def clear_history(self):
        self.chat_history = []