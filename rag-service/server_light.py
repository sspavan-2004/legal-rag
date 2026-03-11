"""
FastAPI Server for Lightweight RAG Pipeline (T5-Small)
Use this for faster startup/testing, then switch to server.py for production T5-Large
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from rag_pipeline_light import get_lightweight_rag_pipeline

app = FastAPI(title="Legal RAG Service (Lightweight)", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5001", "http://localhost:5173", "http://127.0.0.1:5001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class Source(BaseModel):
    title: str
    relevance_score: float
    snippet: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    num_sources: int

class UploadRequest(BaseModel):
    title: str
    content: str
    user_id: Optional[str] = None

class UploadResponse(BaseModel):
    message: str
    document_id: int
    title: str
    total_documents: int

# Global RAG pipeline (lazy loaded)
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline on startup"""
    global rag_pipeline
    print("Starting Lightweight RAG service...")
    try:
        rag_pipeline = get_lightweight_rag_pipeline()
        print("Lightweight RAG service ready!")
    except Exception as e:
        print(f"Error initializing RAG pipeline: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Legal RAG Service (Lightweight)",
        "status": "running",
        "model": "T5-Small",
        "embedder": "all-MiniLM-L6-v2"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "pipeline_loaded": rag_pipeline is not None}

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG pipeline with a legal question
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = rag_pipeline.query(request.question, top_k=request.top_k)
        return QueryResponse(**result)
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all available legal documents"""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    return {
        "total": len(rag_pipeline.documents),
        "documents": [{"id": d["id"], "title": d["title"]} for d in rag_pipeline.documents]
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_document(request: UploadRequest):
    """
    Upload a new document to the RAG knowledge base
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if not request.title or not request.title.strip():
        raise HTTPException(status_code=400, detail="Document title is required")
    
    if not request.content or not request.content.strip():
        raise HTTPException(status_code=400, detail="Document content is required")
    
    try:
        # Add document to RAG pipeline
        result = rag_pipeline.add_document(request.title, request.content)
        
        return UploadResponse(
            message="Document uploaded and indexed successfully",
            document_id=result["document_id"],
            title=result["title"],
            total_documents=result["total_documents"]
        )
    except Exception as e:
        print(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

if __name__ == "__main__":
    print("Starting Lightweight Legal RAG Service on http://localhost:8000")
    print("Using T5-Small for faster initialization")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
