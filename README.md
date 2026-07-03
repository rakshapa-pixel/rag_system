# RAG Chat

A full-stack Retrieval-Augmented Generation (RAG) application that lets users upload PDF documents and ask questions about them using Google's Gemini AI.

---

## Features

- **PDF ingestion** — upload any PDF and ask natural-language questions about it
- **Gemini 2.5 Flash** — fast, accurate answers grounded in your document
- **Per-user isolation** — each user's documents and vector store are kept separate
- **Google OAuth SSO** — sign in with Google or use username/password
- **Cloud-ready** — connects to TryChroma (vector DB) and Aiven PostgreSQL with automatic local fallback for development
- **Document management** — upload and delete documents; chat history resets cleanly on change
- **Source attribution** — every answer includes the source file and page numbers

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3, Flask-SQLAlchemy, Flask-CORS, Authlib |
| Database | Aiven PostgreSQL (production) / SQLite (dev fallback) |
| Vector store | TryChroma Cloud (production) / ChromaDB local (dev fallback) |
| Embeddings | `all-MiniLM-L6-v2` via HuggingFace |
| LLM | Google Gemini 2.5 Flash |
| Frontend | React 18 + Vite |
| Auth | Session cookies + Google OAuth 2.0 |
| Validation | Marshmallow schemas |

---

## Project Structure

```
rag_system/
├── app.py                  # App factory, CORS, OAuth registration
├── config.py               # Config class, DB URL resolution with fallback
├── extensions.py           # OAuth singleton
├── models.py               # SQLAlchemy models (User, Document, Query)
├── rag.py                  # Core RAG pipeline (chunking, embeddings, chain)
├── main.py                 # CLI interface for ingest + query
├── check_db.py             # Dev utility: inspect stored DB records
├── requirements.txt
│
├── routes/
│   ├── auth.py             # /api/auth/* (signup, login, logout, Google OAuth)
│   ├── documents.py        # /api/documents, /api/ingest
│   └── query.py            # /api/query
│
├── repositories/           # Data access layer (User, Document, Query)
├── services/               # Business logic (ingest_service, rag_service)
├── schemas/                # Marshmallow schemas for request/response validation
├── utils/                  # login_required decorator, request parser
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── api/            # fetch wrappers (auth, documents, query)
    │   └── components/     # AuthPage, ChatPage, Header, MessageList, InputBar
    └── vite.config.js
```

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone and install backend dependencies

```bash
git clone https://github.com/rakshapa-pixel/rag_system.git
cd rag_system

python3 -m venv rag-env
source rag-env/bin/activate        # Windows: rag-env\Scripts\activate
pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials — see [Environment Variables](#environment-variables) below.

Also copy the frontend env:

```bash
cp frontend/.env.example frontend/.env
```

### 4. Run the application

Open **two terminals**:

**Terminal 1 — Flask backend:**
```bash
source rag-env/bin/activate
python app.py
```

**Terminal 2 — Vite frontend:**
```bash
cd frontend
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173)

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```env
# Flask
SECRET_KEY=change-this-in-production

# Gemini (required)
# Get from: https://aistudio.google.com/app/apikey
GEMINI_KEY=your-gemini-api-key

# Aiven PostgreSQL (optional — falls back to SQLite if not set)
# Get from: https://console.aiven.io → your service → Connection info
DATABASE_URL="postgresql://avnadmin:password@yourhost.aivencloud.com:12345/defaultdb?sslmode=require"

# TryChroma Cloud (optional — falls back to local ChromaDB if not set)
# Get from: https://trychroma.com → Dashboard
CHROMA_API_KEY=chma-xxxxxxxxxxxxxxxx
CHROMA_TENANT=your-tenant-uuid
CHROMA_DATABASE=default

# Google OAuth (optional — disables SSO button if not set)
# Get from: https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET="GOCSPX-your-client-secret"
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/google/callback

# Where Flask redirects after OAuth (must match your frontend URL)
FRONTEND_URL=http://localhost:5173
```

> **Note:** `DATABASE_URL` and `GOOGLE_CLIENT_SECRET` values containing special characters must be wrapped in double quotes.

---

## API Reference

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Create account |
| `POST` | `/api/auth/login` | Log in |
| `POST` | `/api/auth/logout` | Log out |
| `GET` | `/api/auth/me` | Check session |
| `GET` | `/api/auth/providers` | Which SSO providers are active |
| `GET` | `/api/auth/google` | Start Google OAuth flow |
| `GET` | `/api/auth/google/callback` | Google OAuth callback |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/documents` | List uploaded documents |
| `POST` | `/api/ingest` | Upload and process a PDF |
| `DELETE` | `/api/documents/:id` | Remove a document |

### Query

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query` | Ask a question about the active document |

---

## CLI Usage

The app also ships a command-line interface for quick testing without the web UI:

```bash
# Ingest a PDF
python main.py --ingest path/to/document.pdf

# Ask questions interactively
python main.py --query
```

---

## Cloud Services

The app is designed to work both locally and with cloud services. On startup it prints which backend is active:

```
✓ Connected to Aiven PostgreSQL: pg-xxx.aivencloud.com:22202
✓ Connected to TryChroma Cloud
```

If credentials are missing or invalid, it falls back automatically:

```
⚠️  Cannot reach configured DATABASE_URL — falling back to local SQLite
⚠️  TryChroma Cloud connection failed — falling back to local ChromaDB
```

| Service | Free tier | Purpose |
|---------|-----------|---------|
| [TryChroma](https://trychroma.com) | Yes | Vector database |
| [Aiven PostgreSQL](https://aiven.io) | Yes (trial) | Managed Postgres |
| [Google AI Studio](https://aistudio.google.com) | Yes | Gemini API key |

---

## Development Notes

- **Inspect the database:** `python check_db.py`
- **Session cookies** use `SameSite=Lax` and `HttpOnly`
- **Google OAuth** requires the Google button to link directly to `http://localhost:5000/api/auth/google` (not through the Vite proxy) to preserve the OAuth state cookie — this is handled automatically via `VITE_BACKEND_URL` in `frontend/.env`
- The `OAUTHLIB_INSECURE_TRANSPORT` flag is set automatically in development — no need to add it to `.env`
- Vector data is stored per-user in a collection named `user_{id}`, compatible with both local and cloud ChromaDB
