# Document Intelligence

A multi-tenant SaaS system that parses financial and legal PDF documents, enabling natural-language Q&A with exact page citations.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for PostgreSQL + Redis)
- [Node.js](https://nodejs.org/) >= 20 (for the frontend)
- [Python](https://www.python.org/) >= 3.12 (for the backend)

## Quick Start

### 1. Start infrastructure services

```bash
docker compose up -d
```

This starts:
- **PostgreSQL 16** with the pgvector extension (port 5432)
- **Redis 7** (port 6379)
- **MinIO** (S3-compatible storage, port 9000, console 9001)

### 2. Start the backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at [http://localhost:8000](http://localhost:8000).

Health check: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The app is available at [http://localhost:3000](http://localhost:3000).

## Running Tests

### Backend

```bash
cd backend
source .venv/bin/activate
pytest
```

## Project Structure

```
├── frontend/          # Next.js + TypeScript + Tailwind CSS
├── backend/           # FastAPI + Python + Pydantic
├── docker-compose.yml # PostgreSQL (pgvector) + Redis + MinIO
└── README.md
```

## Architecture

- **Frontend → Backend**: Browser calls FastAPI directly (not proxied through Next.js API routes)
- **Authentication**: Clerk (JWT validation)
- **Multi-tenancy**: PostgreSQL row-level security (RLS)
- **Storage**: S3 for PDFs, PostgreSQL for structured data, pgvector for embeddings
- **Background jobs**: ARQ (Redis-backed)

See [CONTEXT.md](CONTEXT.md) for domain terminology and `docs/adr/` for architectural decision records.
