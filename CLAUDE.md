# AgentFlow — Project Guide

## Overview
Multi-agent customer support platform: LangGraph + FastMCP + FastAPI + React 19.

## Quick Start
```bash
docker compose up -d          # PostgreSQL + pgvector
cp .env.example .env          # Configure environment
uv sync                       # Install Python dependencies
alembic upgrade head          # Run migrations
uv run fastapi dev app/main.py  # Start dev server
cd frontend && npm install && npm run dev  # Start frontend
```

## Project Structure
- `app/` — FastAPI backend
  - `models/` — SQLAlchemy models (8 tables)
  - `schemas/` — Pydantic request/response schemas
  - `api/` — REST API routers
  - `agents/` — LangGraph agent graph (5 agents + formatter)
  - `mcp/` — FastMCP server (5 tools)
  - `services/` — Business logic (auth, embedding, KB search)
  - `core/` — Security, logging utilities
- `alembic/` — Database migrations
- `frontend/` — React 19 + Vite + Tailwind CSS 4 SPA
- `docs/` — Design specification

## Key Patterns
- **Async everywhere**: All DB ops, API handlers, and agent nodes use async/await
- **Dual-mode**: Demo mode (no API keys) uses keyword classifiers + SHA-256 embeddings. Live mode uses Claude Haiku 4.5 + OpenAI embeddings
- **Type-safe**: Strict typing with Pydantic models and TypedDict states
- **Enums**: Python `str, Enum` classes mirrored as PostgreSQL enum types

## Database
- PostgreSQL 17 with pgvector extension
- Async via asyncpg + SQLAlchemy 2.0
- Migrations via Alembic (async)

## Testing
```bash
uv run pytest                 # Run all tests
uv run pytest -x              # Stop on first failure
```

## Environment Variables
See `.env.example` for all required/optional variables.
