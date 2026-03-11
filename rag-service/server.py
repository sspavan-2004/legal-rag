"""
FastAPI Server for RAG Pipeline
Provides REST API for legal question answering
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from rag_pipeline import get_rag_pipeline

app = FastAPI(title="Legal RAG Service", version="1.0.0")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

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
    user_doc_text: Optional[str] = None
    user_doc_title: Optional[str] = None
    threshold: Optional[float] = 0.3
    high_score_threshold: Optional[float] = 0.7

class Source(BaseModel):
    title: str
    relevance_score: float
    snippet: str
    source_type: Optional[str] = None

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    num_sources: int
    user_doc_sources: Optional[int] = 0
    kb_sources: Optional[int] = 0
    kb_search_skipped: Optional[bool] = False

class UploadRequest(BaseModel):
    title: str
    content: str
    user_id: Optional[str] = None

class UploadResponse(BaseModel):
    document_id: str
    title: str
    message: str

# Global RAG pipeline (lazy loaded)
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline on startup"""
    global rag_pipeline
    print("Starting RAG service...")
    try:
        rag_pipeline = get_rag_pipeline()
        print("RAG service ready!")
    except Exception as e:
        print(f"Error initializing RAG pipeline: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Legal RAG Service",
        "status": "running",
        "model": GROQ_MODEL,
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
    Supports hybrid retrieval from user document + knowledge base
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = rag_pipeline.query(
            question=request.question,
            top_k=request.top_k,
            user_doc_text=request.user_doc_text,
            user_doc_title=request.user_doc_title,
            threshold=request.threshold,
            high_score_threshold=request.high_score_threshold
        )
        return QueryResponse(**result)
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all available legal documents"""
    from legal_documents import get_all_documents
    docs = get_all_documents()
    return {
        "total": len(docs),
        "documents": [{"id": d["id"], "title": d["title"]} for d in docs]
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_document(request: UploadRequest):
    """
    Upload and index a new legal document
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if not request.title or not request.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    if not request.content or not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    try:
        # Add document to pipeline (in-memory)
        doc_id = f"uploaded_{len(rag_pipeline.metadata) + 1}"
        rag_pipeline.add_document(title=request.title, content=request.content, doc_id=doc_id)
        
        return UploadResponse(
            document_id=doc_id,
            title=request.title,
            message=f"Document '{request.title}' uploaded and indexed successfully"
        )
    except Exception as e:
        print(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@app.delete("/documents/{doc_title}")
async def delete_document(doc_title: str):
    """
    Delete a document by title
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if not doc_title or not doc_title.strip():
        raise HTTPException(status_code=400, detail="Document title cannot be empty")
    
    try:
        result = rag_pipeline.delete_document(title=doc_title)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=f"Document '{doc_title}' not found")
        
        return {
            "success": True,
            "message": result["message"],
            "deleted_title": result["title"],
            "total_documents": result["total_documents"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

if __name__ == "__main__":
    print("Starting Legal RAG Service on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
