"""
Lightweight RAG Pipeline using T5-Small for faster initialization
Use this for testing/demo, then switch to rag_pipeline.py with T5-Large for production
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from typing import List, Tuple
from legal_documents import get_all_documents

class LightweightRAGPipeline:
    def __init__(self):
        """Initialize the RAG pipeline with T5-small and sentence embeddings"""
        print("Initializing Lightweight RAG Pipeline...")
        
        # Load sentence transformer for retrieval
        print("Loading sentence transformer for embeddings...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load T5-small for faster generation (smaller than T5-large)
        print("Loading T5-small model (lighter version)...")
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.model = T5ForConditionalGeneration.from_pretrained('t5-small')
        
        # Move to GPU if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        print(f"Using device: {self.device}")
        
        # Load and embed legal documents
        self.documents = get_all_documents()
        self.document_contents = [doc['content'] for doc in self.documents]
        self.document_titles = [doc['title'] for doc in self.documents]
        
        print("Creating document embeddings...")
        self.document_embeddings = self.embedder.encode(
            self.document_contents, 
            convert_to_tensor=False,
            show_progress_bar=True
        )
        
        print("Lightweight RAG Pipeline initialized successfully!")
    
    def add_document(self, title: str, content: str, doc_id: int = None) -> dict:
        """
        Add a new document to the knowledge base and update embeddings
        """
        if doc_id is None:
            doc_id = len(self.documents) + 1
        
        # Create new document
        new_doc = {
            "id": doc_id,
            "title": title,
            "content": content
        }
        
        # Add to documents list
        self.documents.append(new_doc)
        self.document_contents.append(content)
        self.document_titles.append(title)
        
        # Generate embedding for new document
        print(f"Generating embedding for: {title}")
        new_embedding = self.embedder.encode([content], convert_to_tensor=False)[0]
        
        # Add to embeddings array
        self.document_embeddings = np.vstack([self.document_embeddings, new_embedding])
        
        print(f"Document '{title}' added successfully! Total documents: {len(self.documents)}")
        
        return {
            "document_id": doc_id,
            "title": title,
            "total_documents": len(self.documents)
        }
    
    def retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        """
        Retrieve top-k most relevant documents for a query
        Returns: List of (title, content, similarity_score) tuples
        """
        # Embed the query
        query_embedding = self.embedder.encode([query], convert_to_tensor=False)[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self.document_embeddings, query_embedding) / (
            np.linalg.norm(self.document_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return documents with scores
        results = []
        for idx in top_indices:
            results.append((
                self.document_titles[idx],
                self.document_contents[idx],
                float(similarities[idx])
            ))
        
        return results
    
    def generate_answer(self, query: str, context: str, max_length: int = 200) -> str:
        """
        Generate an answer using T5-small given query and context
        """
        # Format input for T5
        input_text = f"answer question: {query} context: {context}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
                temperature=0.7,
                do_sample=True,
                top_p=0.9
            )
        
        # Decode
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer
    
    def query(self, question: str, top_k: int = 3) -> dict:
        """
        Main RAG query function
        1. Retrieve relevant documents
        2. Generate answer using T5-small
        3. Return answer with sources
        """
        print(f"\n{'='*60}")
        print(f"Query: {question}")
        print(f"{'='*60}")
        
        # Retrieve relevant documents
        print(f"Retrieving top {top_k} relevant documents...")
        retrieved_docs = self.retrieve_relevant_documents(question, top_k=top_k)
        
        # Show retrieved documents
        print("\nRetrieved Documents:")
        for i, (title, content, score) in enumerate(retrieved_docs, 1):
            print(f"{i}. {title} (Score: {score:.3f})")
        
        # Combine context from retrieved documents
        context = "\n\n".join([content for _, content, _ in retrieved_docs])
        
        # Generate answer
        print("\nGenerating answer with T5-small...")
        answer = self.generate_answer(question, context)
        
        # Prepare response
        response = {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "title": title,
                    "relevance_score": round(score, 3),
                    "snippet": content[:200] + "..."
                }
                for title, content, score in retrieved_docs
            ],
            "num_sources": len(retrieved_docs)
        }
        
        print(f"\nAnswer: {answer}")
        print(f"{'='*60}\n")
        
        return response

# Global instance (lazy loaded)
_lightweight_rag_pipeline = None

def get_lightweight_rag_pipeline():
    """Get or create the lightweight RAG pipeline singleton"""
    global _lightweight_rag_pipeline
    if _lightweight_rag_pipeline is None:
        _lightweight_rag_pipeline = LightweightRAGPipeline()
    return _lightweight_rag_pipeline
