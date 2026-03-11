# LEGAL_RAG MERN Setup

This project now includes a MERN stack setup:

- Frontend (React + Vite): `frontend`
- Backend (Express + MongoDB): `backend-mern`

## 1) Start MongoDB

Make sure MongoDB is running locally on:

`mongodb://127.0.0.1:27017`

## 2) Run backend

```powershell
cd c:\Users\spkmv\OneDrive\Desktop\LEGAL_RAG\backend-mern
npm install
npm run dev
```

Backend URL: `http://localhost:5000`

## 3) Run frontend

```powershell
cd c:\Users\spkmv\OneDrive\Desktop\LEGAL_RAG\frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

## API endpoints added

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/health`

## Notes

- Update `backend-mern/.env` before production use.
- Existing Python backend remains untouched in `backend/` during this migration phase.
