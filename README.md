# 🎓 AI History & Geography Teacher Assistant
### المساعد التعليمي الذكي لمدرسي التاريخ والجغرافيا

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_pgvector-4169E1.svg?logo=postgresql)](https://github.com/pgvector/pgvector)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg?logo=tailwindcss)](https://tailwindcss.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker)](https://www.docker.com)

A production-ready, enterprise-grade AI Educational Assistant for History and Geography educators. Features a grounded **Retrieval-Augmented Generation (RAG)** pipeline over teacher-approved curriculum references, a student-facing **Telegram Bot** (with decoupled architecture ready for WhatsApp), and a rich **React Teacher Dashboard** with Arabic RTL support.

---

## 📑 Table of Contents / فهرس المحتويات

1. [Key Features](#-key-features)
2. [System Architecture](#-system-architecture)
3. [Prerequisites](#-prerequisites)
4. [Quick Start with Docker Compose](#-quick-start-with-docker-compose)
5. [Telegram Bot & Webhook Setup](#-telegram-bot--webhook-setup)
6. [Local Development Setup](#-local-development-setup)
7. [Environment Variables Reference](#-environment-variables-reference)
8. [CLI Utilities](#-cli-utilities)
9. [Project Directory Structure](#-project-directory-structure)
10. [RAG Pipeline & Hallucination Protection](#-rag-pipeline--hallucination-protection)
11. [Testing Suite](#-testing-suite)
12. [License](#-license)

---

## ✨ Key Features

- **📚 Grounded Curriculum RAG**:
  - Hybrid search combining **pgvector cosine semantic similarity** + **PostgreSQL Full-Text Search (tsvector)** merged via **Reciprocal Rank Fusion (RRF)**.
  - Ingestion pipeline supporting **PDF, DOCX, TXT, MD, PPTX** with sentence-boundary token chunking and Arabic text normalization.
  - Strict anti-hallucination guardrails: no fabricated facts, page numbers, or unverified claims.
- **🤖 Multi-Channel Student Bot**:
  - Interactive student assistance via **Telegram Bot API** (`/start`, `/help`, `/subjects`, `/cancel`).
  - Contextual multi-turn memory and typing indicator.
  - Decoupled `MessageRouter` layer for future WhatsApp integration without backend changes.
- **🧠 Multi-Provider AI Failover**:
  - Primary provider: **Google Gemini** (`gemini-2.0-flash` + `text-embedding-004`).
  - Automatic fallback chain: **Groq** (`llama-3.3-70b-versatile`), **OpenRouter**, and **OpenAI**.
- **📊 Teacher Dashboard (Web)**:
  - Built with **React 18**, **TypeScript**, and **Tailwind CSS v4** with native Arabic RTL layout.
  - Live metric cards (Students, Conversations, References, Tokens, Latency).
  - Conversation viewer with RAG confidence scores and retrieved chunk inspector.
  - Subject hierarchy manager (Subjects, Units, Lessons).
  - Custom AI instruction editor and teacher answer correction overrides.
- **⚡ Background Processing**:
  - **ARQ (Async Redis Queue)** worker for non-blocking document indexing and conversation summarization.

---

## 🏛️ System Architecture

```
                                 ┌────────────────────────┐
                                 │    Students / Users    │
                                 └───────────┬────────────┘
                                             │
                                  (Telegram / WhatsApp)
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                          Nginx Reverse Proxy (:80)                             │
├──────────────────────────────────────┬─────────────────────────────────────────┤
│                  /                   │                  /api                   │
│                  ▼                   │                   ▼                     │
│      ┌──────────────────────┐        │       ┌──────────────────────┐          │
│      │   React Frontend     │        │       │   FastAPI Backend    │          │
│      │      Dashboard       │        │       │        (:8000)       │          │
│      └──────────────────────┘        │       └───────────┬──────────┘          │
│                                      │                   │                     │
└──────────────────────────────────────┼───────────────────┼─────────────────────┘
                                       │                   │
                                       │       ┌───────────┴───────────┐
                                       │       │  RAG Engine Pipeline  │
                                       │       └───────────┬───────────┘
                                       │                   │
                                       ▼                   ▼
                    ┌─────────────────────┐     ┌─────────────────────┐
                    │ PostgreSQL+pgvector │     │   Redis + Workers   │
                    │ (Vectors & Chunks)  │     │  (Async Ingestion)  │
                    └─────────────────────┘     └─────────────────────┘
```

---

## 📋 Prerequisites

- **Docker** & **Docker Compose** (recommended for production & staging)
- **Python 3.12+** (for local backend development)
- **Node.js 20+** & **npm** (for local frontend development)
- **PostgreSQL 16** with `pgvector` & `pg_trgm` extensions
- **Redis 7+**

---

## 🚀 Quick Start with Docker Compose

### 1. Configure Environment

Copy the example `.env` file and customize your configuration:

```bash
cp .env.example .env
```

Ensure the following variables are filled in `.env`:
```ini
# Security
JWT_SECRET=your_generated_64_char_secret_key

# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Google Gemini API Key (from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Start Full Stack

```bash
docker compose up --build -d
```

Services will be accessible at:
- **Teacher Dashboard**: [http://localhost](http://localhost)
- **API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

### 3. Create Admin Teacher Account

Create the first administrator user with the bootstrap script:

```bash
docker compose exec backend python /app/../scripts/create_admin.py admin@example.com StrongPassword123! "أستاذ أحمد"
```

Open [http://localhost](http://localhost) and log in!

---

## 📡 Telegram Bot & Webhook Setup

The bot supports both **Long Polling** (for development) and **Webhooks** (for production).

### Polling Mode (Default for Development)
In `.env`:
```ini
TELEGRAM_USE_POLLING=true
```

### Webhook Mode (Production)
1. Ensure your application is exposed behind a valid HTTPS domain (e.g. `https://your-domain.com` or an ngrok tunnel `https://xxxx.ngrok-free.app`).
2. Update `.env`:
   ```ini
   TELEGRAM_WEBHOOK_URL=https://your-domain.com
   TELEGRAM_WEBHOOK_SECRET=your_generated_webhook_secret
   TELEGRAM_USE_POLLING=false
   ```
3. Set the webhook with the CLI utility:
   ```bash
   python scripts/set_webhook.py --token <TELEGRAM_BOT_TOKEN> --url https://your-domain.com --secret <TELEGRAM_WEBHOOK_SECRET>
   ```

---

## 💻 Local Development Setup

### Backend

```bash
cd backend

# Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Background Worker

```bash
cd backend
arq app.workers.settings.WorkerSettings
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## ⚙️ Environment Variables Reference

| Variable | Default | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | `development` or `production` |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL async connection URI |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URI |
| `JWT_SECRET` | `change-me` | 256-bit secret key for JWT tokens |
| `JWT_ACCESS_EXPIRE_MINUTES` | `30` | Access token lifespan |
| `JWT_REFRESH_EXPIRE_DAYS` | `7` | Refresh token lifespan |
| `TELEGRAM_BOT_TOKEN` | - | Telegram Bot API token from @BotFather |
| `TELEGRAM_WEBHOOK_URL` | - | Public HTTPS URL for Webhook mode |
| `TELEGRAM_WEBHOOK_SECRET` | - | Secret token verified on webhook delivery |
| `TELEGRAM_USE_POLLING` | `true` | `true` for polling, `false` for webhooks |
| `AI_PRIMARY_PROVIDER` | `gemini` | Primary AI provider (`gemini`, `groq`, `openrouter`, `openai`) |
| `AI_FALLBACK_PROVIDERS` | `groq,openrouter` | Comma-separated fallback provider order |
| `GEMINI_API_KEY` | - | Google AI Studio API key |
| `GROQ_API_KEY` | - | Groq Cloud API key |
| `OPENROUTER_API_KEY` | - | OpenRouter API key |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `RAG_TOP_K` | `5` | Number of context chunks retrieved |
| `RAG_SIMILARITY_THRESHOLD` | `0.70` | Minimum cosine similarity threshold |
| `RAG_CHUNK_SIZE` | `600` | Tokens per reference chunk |
| `RAG_CHUNK_OVERLAP` | `75` | Overlapping tokens between chunks |

---

## 🛠️ CLI Utilities

### 1. Create Administrator Account
```bash
python scripts/create_admin.py <email> <password> <name>
```

### 2. Manage Telegram Webhook
```bash
# View webhook status
python scripts/set_webhook.py --token <BOT_TOKEN> --info

# Set webhook
python scripts/set_webhook.py --token <BOT_TOKEN> --url <HTTPS_URL> --secret <SECRET>

# Delete webhook (returns bot to polling mode)
python scripts/set_webhook.py --token <BOT_TOKEN> --delete
```

---

## 📂 Project Directory Structure

```
BotAssistant/
├── backend/
│   ├── app/
│   │   ├── ai/            # AI Provider abstraction & failover chain
│   │   │   ├── base.py
│   │   │   ├── failover.py
│   │   │   ├── gemini.py
│   │   │   ├── groq.py
│   │   │   ├── openai_provider.py
│   │   │   ├── openrouter.py
│   │   │   └── router.py
│   │   ├── api/           # REST API routes & Webhooks
│   │   ├── core/          # Security, Logging, Rate Limiter, Exceptions
│   │   ├── document/      # Text extraction (PDF, DOCX, PPTX), cleaning, language detection
│   │   ├── messaging/     # Telegram Bot integration & multi-platform router
│   │   ├── models/        # SQLAlchemy ORM models + pgvector vector types
│   │   ├── rag/           # Hybrid retriever, prompt builder, validator, citations
│   │   ├── schemas/       # Pydantic validation schemas
│   │   ├── services/      # Business logic services
│   │   ├── workers/       # ARQ background task queues
│   │   ├── config.py      # App settings
│   │   ├── database.py    # Database connection & session factory
│   │   └── main.py        # FastAPI entry point & lifespan
│   ├── alembic/           # Alembic database migrations
│   ├── tests/             # Pytest test suite
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/    # Layout, Sidebar, Cards, UI elements
│   │   ├── pages/         # Dashboard, Students, Conversations, References, Subjects...
│   │   ├── services/      # Axios API client
│   │   ├── App.tsx        # Route router
│   │   ├── index.css      # Dark theme design system with RTL
│   │   └── main.tsx       # React entry point
│   ├── Dockerfile
│   └── package.json
├── docker/
│   ├── nginx/             # Nginx reverse proxy configuration
│   └── postgres/          # PostgreSQL initialization script (pgvector)
├── scripts/
│   ├── create_admin.py    # Admin creation CLI
│   └── set_webhook.py     # Webhook management CLI
├── docker-compose.yml     # Production Docker Compose
├── docker-compose.dev.yml # Development Docker Compose
└── README.md
```

---

## 🛡️ RAG Pipeline & Hallucination Protection

1. **Ingestion**: Documents are extracted, cleaned from diacritics/artifacts, and chunked with sentence boundaries.
2. **Hybrid Search**: When a question arrives, query vectors search `reference_chunks` via cosine similarity, alongside PostgreSQL full-text search across content keywords.
3. **Fusion & Ranking**: Both score sets merge using **Reciprocal Rank Fusion (RRF)**.
4. **Correction Injection**: Semantic vector search checks if teacher corrections exist for the question (similarity > 0.8) and injects them as high-priority truth.
5. **Answer Validation**: If no reference chunks are found or confidence is below threshold, the system returns a polite refusal rather than fabricating answers.
6. **Citation Formatting**: Verified citations include reference title, unit, lesson, and page number without hallucinating.

---

## 🧪 Testing Suite

Run the full automated test suite with pytest:

```bash
cd backend
pytest -v
```

Tests cover:
- **`test_auth.py`**: Password hashing verification, JWT access & refresh token lifecycles.
- **`test_chunker.py`**: Arabic and multilingual sentence boundary token splitting, page preservation.
- **`test_retriever.py`**: Reciprocal Rank Fusion scoring algorithm.
- **`test_rag.py`**: Prompt builder assembly, anti-hallucination validator, and citation deduplication.

---

## 📄 License

Proprietary — Developed for Educational Institution. All rights reserved.
