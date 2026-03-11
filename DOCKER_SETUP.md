# Docker Setup for LEGAL_RAG

## Prerequisites

- Docker Desktop installed and running
- `backend-mern/.env` present (copy from `backend-mern/.env.example`)
- `rag-service/.env` present (copy from `rag-service/.env.example` and set `GROQ_API_KEY`)

## Important Security Note

- Do not commit real secrets to `.env.example` or source control.
- Keep real keys only in local `.env` files.
- If a secret was exposed previously, rotate it before pushing images or code.
- Root `.gitignore` now ignores service `.env` files while keeping `.env.example` tracked.

## Services

- `frontend` -> http://localhost:5173
- `backend` -> http://localhost:5001
- `rag-service` -> http://localhost:8000
- `mongodb` -> mongodb://localhost:27017

## Start Everything

```powershell
cd C:\Users\spkmv\OneDrive\Desktop\LEGAL_RAG
docker compose up -d --build
```

## Check Status

```powershell
docker compose ps
docker compose config
docker compose logs -f rag-service
docker compose logs -f backend
```

`docker compose config` is useful to validate final merged config before running.

## Stop Everything

```powershell
docker compose down
```

## Stop and Remove Volumes (Fresh DB + model cache reset)

```powershell
docker compose down -v
```

## Notes

- Backend uses container DNS names, not localhost, for internal calls:
  - MongoDB: `mongodb://mongodb:27017/legal_rag`
  - RAG service: `http://rag-service:8000`
- Frontend is built as static assets and served by Nginx in Docker.
- In Docker, the frontend proxies `/api` requests to the backend container.
- In local non-Docker development, the frontend still defaults to `http://localhost:5001/api`.
