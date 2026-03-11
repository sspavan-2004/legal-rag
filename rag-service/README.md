# Legal RAG Service

A Retrieval-Augmented Generation (RAG) service for legal question answering using Groq (Llama 3.1 8B Instant) and Sentence Transformers.

## Features

- **Groq LLM**: Fast chat completions with `llama-3.1-8b-instant`
- **Semantic Search**: Sentence transformer embeddings for intelligent document retrieval
- **Legal Knowledge Base**: 10 curated legal documents covering various practice areas
- **REST API**: FastAPI server for easy integration
- **CORS Enabled**: Ready for frontend integration

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Variables

Set these before starting the server:

```bash
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

`GROQ_MODEL` is optional; defaults to `llama-3.1-8b-instant`.

You can also use a local env file at [rag-service/.env](rag-service/.env):

1. Copy [rag-service/.env.example](rag-service/.env.example) to [rag-service/.env](rag-service/.env)
2. Paste your real key into `GROQ_API_KEY`

## Usage

Start the server:
```bash
python server.py
```

The service will be available at `http://localhost:8000`

## API Endpoints

### `GET /`
Health check with service info

### `GET /health`
Service health status

### `POST /query`
Query the RAG pipeline

Request body:
```json
{
  "question": "What are the elements of a valid contract?",
  "top_k": 3
}
```

Response:
```json
{
  "question": "...",
  "answer": "...",
  "sources": [
    {
      "title": "Contract Law - Essential Elements",
      "relevance_score": 0.856,
      "snippet": "..."
    }
  ],
  "num_sources": 3
}
```

### `GET /documents`
List all available legal documents

## Testing

Test the pipeline directly:
```bash
python rag_pipeline.py
```

This will run test queries and show the RAG pipeline in action.

## Architecture

1. **Retrieval**: Uses `all-MiniLM-L6-v2` sentence transformer to embed documents and queries
2. **Ranking**: Calculates cosine similarity to find most relevant documents
3. **Generation**: Uses Groq (`llama-3.1-8b-instant`) to generate contextual answers from retrieved documents
4. **API**: FastAPI server exposes the pipeline as REST endpoints

## Legal Documents Included

- Contract Law (Elements, Formation)
- Copyright Law (Protection, Duration)
- Tort Law (Negligence Standards)
- Criminal Law (Burden of Proof)
- Property Law (Adverse Possession)
- Constitutional Law (First Amendment)
- Employment Law (At-Will Doctrine)
- Evidence Law (Hearsay Rule)
- Corporate Law (Fiduciary Duties)
- Family Law (Child Custody)

## Integration with Chat Backend

The Node.js chat backend can call this service:

```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: userMessage })
});
const data = await response.json();
```
