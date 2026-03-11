"""
RAG Pipeline backed by a persisted FAISS vector store.
"""

import json
import os
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")


class SimpleRAGPipeline:
    def __init__(self):
        print("Initializing RAG Pipeline...")

        self.store_dir = Path(__file__).resolve().parent / "data" / "vector_store"
        self.index_path = self.store_dir / "index.faiss"
        self.metadata_path = self.store_dir / "metadata.json"
        self.embeddings_path = self.store_dir / "embeddings.npy"

        print("Loading sentence transformer for query embeddings...")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is not set. Please configure it before starting rag-service.")
        self.client = Groq(api_key=groq_api_key)

        self._load_vector_store()
        print(f"RAG Pipeline initialized successfully with {len(self.metadata)} chunks")

    def _load_vector_store(self) -> None:
        if not self.index_path.exists() or not self.metadata_path.exists() or not self.embeddings_path.exists():
            raise FileNotFoundError(
                "Vector store not found. Run ingest_precomputed.py first to create index.faiss, metadata.json, and embeddings.npy"
            )

        self.index = faiss.read_index(str(self.index_path))

        with self.metadata_path.open("r", encoding="utf-8") as file:
            self.metadata = json.load(file)

        self.embeddings = np.load(self.embeddings_path).astype(np.float32)

        if not isinstance(self.metadata, list):
            raise ValueError("metadata.json must be a list of chunk objects")

        if self.embeddings.ndim != 2:
            raise ValueError("embeddings.npy must be a 2D array")

        if len(self.metadata) != self.embeddings.shape[0]:
            raise ValueError("metadata and embeddings row count mismatch")

        if self.index.ntotal != len(self.metadata):
            raise ValueError("FAISS index count and metadata count mismatch")

    def _persist_vector_store(self) -> None:
        self.store_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        np.save(self.embeddings_path, self.embeddings.astype(np.float32))
        with self.metadata_path.open("w", encoding="utf-8") as file:
            json.dump(self.metadata, file, ensure_ascii=False)

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        vectors = vectors.astype(np.float32)
        faiss.normalize_L2(vectors)
        return vectors

    def add_document(self, title: str, content: str, doc_id=None) -> dict:
        if doc_id is None:
            doc_id = len(self.metadata) + 1

        new_vector = self.embedder.encode([content], convert_to_tensor=False)
        new_vector = self._normalize(np.asarray(new_vector, dtype=np.float32))

        self.index.add(new_vector)
        self.embeddings = np.vstack([self.embeddings, new_vector])
        self.metadata.append(
            {
                "chunk_index": len(self.metadata),
                "filename": title,
                "text": content,
                "id": str(doc_id),
            }
        )

        self._persist_vector_store()

        return {
            "document_id": str(doc_id),
            "title": title,
            "total_documents": len(self.metadata),
        }

    def delete_document(self, title: str = None, doc_id=None) -> dict:
        if not title and doc_id is None:
            return {"success": False, "message": "Provide title or doc_id"}

        to_remove = []
        for idx, item in enumerate(self.metadata):
            item_id = str(item.get("id", ""))
            filename = str(item.get("filename", ""))
            if title and filename.lower() == title.lower():
                to_remove.append(idx)
            elif doc_id is not None and item_id == str(doc_id):
                to_remove.append(idx)

        if not to_remove:
            return {"success": False, "message": "Document not found"}

        mask = np.ones(len(self.metadata), dtype=bool)
        mask[to_remove] = False

        self.embeddings = self.embeddings[mask]
        self.metadata = [row for i, row in enumerate(self.metadata) if i not in set(to_remove)]

        dim = self.embeddings.shape[1] if self.embeddings.size else self.index.d
        self.index = faiss.IndexFlatIP(dim)
        if self.embeddings.size:
            self.index.add(self.embeddings.astype(np.float32))

        self._persist_vector_store()

        return {
            "success": True,
            "message": f"Deleted {len(to_remove)} chunk(s)",
            "title": title,
            "total_documents": len(self.metadata),
        }

    def retrieve_relevant_documents(self, query: str, top_k: int = 3, threshold: float = 0.3) -> List[Tuple[str, str, float]]:
        query_vector = self.embedder.encode([query], convert_to_tensor=False)
        query_vector = self._normalize(np.asarray(query_vector, dtype=np.float32))

        k = max(1, min(top_k, len(self.metadata)))
        scores, indices = self.index.search(query_vector, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            if float(score) < threshold:
                continue
            item = self.metadata[idx]
            title = item.get("filename") or item.get("title") or f"Chunk {idx}"
            text = item.get("text", "")
            results.append((title, text, float(score)))

        return results

    def retrieve_from_text(self, query: str, text: str, title: str = "User Document", top_k: int = 3, threshold: float = 0.3) -> List[Tuple[str, str, float]]:
        """Retrieve relevant chunks from a specific text document"""
        # Split text into chunks (simple sentence-based chunking)
        sentences = [s.strip() for s in text.split('.') if s.strip() and len(s.strip()) > 20]
        
        if not sentences:
            return []
        
        # Encode all sentences
        doc_vectors = self.embedder.encode(sentences, convert_to_tensor=False)
        doc_vectors = self._normalize(np.asarray(doc_vectors, dtype=np.float32))
        
        # Encode query
        query_vector = self.embedder.encode([query], convert_to_tensor=False)
        query_vector = self._normalize(np.asarray(query_vector, dtype=np.float32))
        
        # Compute similarities
        scores = np.dot(doc_vectors, query_vector.T).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score < threshold:
                continue
            results.append((title, sentences[idx] + '.', score))
        
        return results

    def generate_answer(self, query: str, context: str, user_doc_context: str = None) -> str:
        if user_doc_context:
            prompt = (
                "You are a legal assistant. Answer the user's question using the provided context. "
                "The user has uploaded a document - prioritize information from it when relevant.\n\n"
                f"Question: {query}\n\n"
                f"USER'S UPLOADED DOCUMENT:\n{user_doc_context}\n\n"
                f"KNOWLEDGE BASE (from our storage):\n{context}\n\n"
                "Answer the question based on the above context, giving priority to the user's document."
            )
        else:
            prompt = (
                "You are a legal assistant. Answer the user's question strictly using the provided legal context. "
                "If the context is insufficient, clearly say so and provide a cautious, general legal explanation.\n\n"
                f"Question: {query}\n\n"
                f"Legal Context:\n{context}"
            )

        response = self.client.chat.completions.create(
            model=self.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
        )

        return response.choices[0].message.content.strip()

    def query(self, question: str, top_k: int = 3, user_doc_text: str = None, user_doc_title: str = None, threshold: float = 0.3, high_score_threshold: float = 0.7) -> dict:
        # Retrieve from user's uploaded document first if provided
        user_docs = []
        skip_kb_search = False
        
        if user_doc_text:
            user_docs = self.retrieve_from_text(
                query=question,
                text=user_doc_text,
                title=user_doc_title or "User Document",
                top_k=3,
                threshold=threshold
            )
            
            # Check if any user document has high similarity score (0.7+)
            if user_docs:
                max_user_score = max(score for _, _, score in user_docs)
                if max_user_score >= high_score_threshold:
                    skip_kb_search = True
                    print(f"High similarity found in user document ({max_user_score:.3f}), skipping knowledge base search")
        
        # Retrieve from FAISS knowledge base only if no high-scoring user doc results
        kb_docs = []
        if not skip_kb_search:
            kb_docs = self.retrieve_relevant_documents(question, top_k=3, threshold=threshold)
        
        # Combine results
        all_sources = []
        
        # Add user document results first (prioritized)
        for title, content, score in user_docs:
            all_sources.append({
                "title": f"📄 {title}",
                "relevance_score": round(score, 3),
                "snippet": (content[:200] + "...") if len(content) > 200 else content,
                "source_type": "user_document"
            })
        
        # Add knowledge base results (if not skipped)
        for title, content, score in kb_docs:
            all_sources.append({
                "title": f"📚 {title}",
                "relevance_score": round(score, 3),
                "snippet": (content[:200] + "...") if len(content) > 200 else content,
                "source_type": "knowledge_base"
            })
        
        # Build context strings
        user_context = "\n\n".join([content for _, content, _ in user_docs]) if user_docs else None
        kb_context = "\n\n".join([content for _, content, _ in kb_docs]) if kb_docs else ""
        
        # Generate answer (don't pass kb_context if it was skipped due to high user doc score)
        if skip_kb_search and user_context:
            answer = self.generate_answer(question, "", user_context)
        else:
            answer = self.generate_answer(question, kb_context, user_context)

        return {
            "question": question,
            "answer": answer,
            "sources": all_sources,
            "num_sources": len(all_sources),
            "user_doc_sources": len(user_docs),
            "kb_sources": len(kb_docs),
            "kb_search_skipped": skip_kb_search,
        }


_rag_pipeline = None


def get_rag_pipeline():
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = SimpleRAGPipeline()
    return _rag_pipeline


if __name__ == "__main__":
    rag = SimpleRAGPipeline()
    result = rag.query("What are the essential elements of a contract?")
    print(result["answer"])
