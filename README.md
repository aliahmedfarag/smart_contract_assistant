# Smart Contract Assistant

AI-powered document analysis system using RAG for intelligent contract Q&A.

## Overview

Upload contracts (PDF/DOCX), ask questions, and receive accurate answers with source citations.

## Features

- PDF and DOCX document ingestion
- Semantic search using FAISS
- AI-powered Q&A with LLaMA 3.3
- Source citations
- Chat history tracking
- Document summarization
- Safety guardrails
- Gradio UI interface
- FastAPI with LangServe

## Technology Stack

- **LLM**: Groq API (LLaMA 3.3-70B)
- **Framework**: LangChain
- **Vector Store**: FAISS
- **Embeddings**: HuggingFace Sentence Transformers
- **UI**: Gradio
- **API**: FastAPI + LangServe
- **Document Processing**: PyPDF2, python-docx

## Installation

### Prerequisites
- Python 3.8+
- Groq API Key

### Setup

1. Clone repository
```bash
git clone <repository-url>
cd smart_contract_assistant
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment
Create `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

### Gradio UI
```bash
python app.py
```
Open: http://127.0.0.1:7860

### FastAPI Server
```bash
python server.py
```
Open: http://127.0.0.1:8000/docs

### Evaluation
```bash
python evaluate.py
```

## Project Structure
```
smart_contract_assistant/
├── src/
│   ├── ingestion.py    # Document processing
│   ├── retrieval.py    # Semantic search
│   ├── qa_chain.py     # Q&A system
│   └── utils.py        # Helper functions
├── app.py              # Gradio interface
├── server.py           # FastAPI server
├── evaluate.py         # Evaluation pipeline
└── requirements.txt    # Dependencies
```

## API Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload document
- `POST /ask` - Ask question
- `GET /history` - Get chat history
- `DELETE /history` - Clear history
- `/langserve/playground` - LangServe playground

## Evaluation Results

- Accuracy: 100%
- Success Rate: 80%
- Average Sources: 1.0

## Configuration

Adjust settings in source files:

**Chunk size** (src/ingestion.py):
```python
DocumentIngestion(chunk_size=800, chunk_overlap=150)
```

**Model** (src/qa_chain.py):
```python
ChatGroq(model_name="llama-3.3-70b-versatile")
```

## Limitations

- Maximum file size: 50MB
- English language optimized
- Requires internet connection
- Local deployment only

## License

Educational project for NVIDIA DLI Course.

## Acknowledgments

Built with LangChain, Groq, HuggingFace, and FastAPI.