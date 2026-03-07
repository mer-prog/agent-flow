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


# Spec Management Rules

## Spec Files

- JP版: `README_{project}_{system-type}_JP.md` — 日本語仕様書
- EN版: `README_{project}_{system-type}_EN.md` — 英語仕様書
- 両ファイルは常にペアで管理し、内容を同期させる

## Format Standards

- セクション番号は付けない（`## Skills Demonstrated` であり `## 1. Skills Demonstrated` ではない）
- 見出しレベル: タイトル `#`、セクション `##`、サブセクション `###`
- コードブロックには言語指定を付ける
- Architecture Overview には ASCII 図を必ず含める
- Skills Demonstrated の項目名は標準リストから選択する:
  - Full-Stack Development / Frontend Development / Backend Development
  - API Design & Integration / Database Design & Management
  - Authentication & Authorization / AI/LLM Integration
  - Real-Time Communication / Cloud Architecture & Deployment
  - DevOps & CI/CD / Security Implementation / Payment Integration
  - Performance Optimization / Testing & Quality Assurance
  - UI/UX Design / Mobile Development / Data Visualization
  - System Architecture / Microservices Architecture / Event-Driven Architecture

## Required Sections (in order)

- Skills Demonstrated
- Tech Stack
- Architecture Overview (ASCII diagram required)
- Key Features
- Project Structure
- Setup
- Design Decisions
- Running Costs
- Author (@mer-prog)

## Optional Sections (add when applicable)

- API Endpoints / Database Schema / Payment Flow
- AI/ML Pipeline / Security / WebSocket Events
- Environment Variables / Deployment / Testing

## Language Rules

- JP版: 日本語で統一（技術用語のみ英語可）
- EN版: 英語で統一（日本語の混入禁止）

## Git Rules

- 新規作成: `docs: add {project-name} JP/EN spec`
- 更新: `docs: update {project-name} JP/EN spec`
- JP版とEN版は1コミットにまとめる
- 仕様書の変更は必ずコードベースの現状を反映させる（フルリジェネレート方式）
- Author セクションには必ず `@mer-prog` を記載する
