# Legal RAG - AI-Powered Legal Document Analysis

A production-ready full-stack application combining **Retrieval-Augmented Generation (RAG)** with a modern web interface for intelligent legal document analysis and chat.

## 🎯 Features

- **RAG Pipeline**: Intelligent retrieval and generation using Hugging Face embeddings and Groq LLM
- **Real-time Chat**: Interactive Q&A interface for legal documents
- **Document Processing**: Automatic chunking and embedding of legal documents
- **MongoDB Integration**: Persistent storage of conversations and documents
- **Docker & Kubernetes Ready**: Complete containerization and orchestration setup
- **OAuth2 Authentication**: Google Sign-In support

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│                  Port: 5173 (Docker)                     │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│                  Backend (Node.js/Express)              │
│                  Port: 5001 (Docker)                    │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼────────┐  ┌────▼──────────────┐
│   MongoDB     │  │  RAG Service      │
│   Port: 27017 │  │  (Python/FastAPI) │
└───────────────┘  │  Port: 8000       │
                   └───────────────────┘
```

## 📦 Project Structure

```
legal-rag/
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── pages/           # Chat, Login, Home pages
│   │   ├── components/      # Reusable UI components
│   │   └── lib/            # API utilities
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── backend-mern/            # Node.js + Express backend
│   ├── src/
│   │   ├── controllers/     # Chat, Auth logic
│   │   ├── models/         # User, Document schemas
│   │   ├── routes/         # API endpoints
│   │   └── middleware/     # Auth, Error handling
│   ├── Dockerfile
│   ├── package.json
│   └── server.js
├── rag-service/             # Python RAG pipeline
│   ├── server.py            # FastAPI app
│   ├── rag_pipeline.py      # Core RAG logic
│   ├── legal_documents.py   # Document processing
│   ├── Dockerfile
│   ├── requirements.txt
│   └── data/               # Vector store & embeddings
└── docker-compose.yml       # Full stack orchestration
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (version 2.0+)
- Node.js 16+ (for local dev)
- Python 3.11+ (for local dev)

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/sspavan-2004/legal-rag.git
cd legal-rag
docker compose up -d --build
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5001
- RAG Service: http://localhost:8000/health
- MongoDB: mongodb://localhost:27017

### Option 2: Local Development

**1. Setup Backend**
```bash
cd backend-mern
npm install
cp .env.example .env
npm run dev  # Runs on port 5001
```

**2. Setup RAG Service**
```bash
cd rag-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python server.py  # Runs on port 8000
```

**3. Setup Frontend**
```bash
cd frontend
npm install
npm run dev  # Runs on port 5173
```

## ⚙️ Environment Variables

Create `.env` files in each service:

**backend-mern/.env**
```
PORT=5001
MONGODB_URI=mongodb://localhost:27017/legal_rag
JWT_SECRET=your_secure_secret_key
GOOGLE_CLIENT_ID=your_google_oauth_id
GOOGLE_CLIENT_SECRET=your_google_oauth_secret
GOOGLE_REDIRECT_URI=http://localhost:5001/api/auth/google/callback
RAG_SERVICE_URL=http://localhost:8000
CLIENT_URL=http://localhost:5173
```

**rag-service/.env**
```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
HF_HOME=/home/appuser/.cache/huggingface
TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/transformers
```

**frontend/.env** (optional, auto-configured in Docker)
```
VITE_API_BASE_URL=http://localhost:5001/api
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/google/callback` - Google OAuth callback

### Chat
- `POST /api/chat` - Send message (requires auth)
- `GET /api/chat/history` - Get conversation history
- `POST /api/documents/upload` - Upload legal documents

### RAG Service
- `POST /api/rag/query` - Query documents with RAG
- `GET /health` - Service health check

## 🐳 Docker Commands

**Build Images**
```bash
docker compose build
```

**Start Services**
```bash
docker compose up -d
```

**Stop Services**
```bash
docker compose down
```

**View Logs**
```bash
docker compose logs -f <service-name>  # mongodb, rag-service, backend, frontend
```

**Remove Everything** (use carefully)
```bash
docker compose down -v
```

## ☸️ Kubernetes Deployment

Ready for Kubernetes with manifests in `k8s/` folder (coming soon):
```bash
kubectl apply -f k8s/
```

## 🔌 Technologies Used

### Frontend
- React 18
- Vite
- Tailwind CSS
- Axios for API calls

### Backend
- Node.js + Express
- MongoDB + Mongoose
- JWT Authentication
- Google OAuth2

### RAG Service
- Python 3.11
- FastAPI
- Sentence Transformers (Hugging Face)
- LangChain
- Groq API (LLaMA 3.1)
- FAISS for vector storage

### DevOps
- Docker & Docker Compose
- Kubernetes (K8s)
- Jenkins (CI/CD pipeline)

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### MongoDB unhealthy
```bash
docker compose down -v
docker compose up -d
```

### RAG Service crashing
Check logs: `docker compose logs rag-service`
Ensure `.env` has valid `GROQ_API_KEY`

### Permission denied on HF cache
Already handled in docker-compose.yml with root user for rag-service

## 📄 License

MIT License - see LICENSE file

## 👨‍💻 Author

[sspavan-2004](https://github.com/sspavan-2004)

## 🎓 Learning Resources

- [Docker Docs](https://docs.docker.com/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/)
- [Hugging Face](https://huggingface.co/)

## 🤝 Support

For issues, suggestions, or collaborations:
- Open an issue on GitHub
- Check existing documentation
- Review Docker logs for debugging

---

**Happy coding! 🚀**
