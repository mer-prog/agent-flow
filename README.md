# AgentFlow

Multi-agent AI customer support platform built with LangGraph + FastMCP + FastAPI + React 19.

## Features

- **Multi-Agent Orchestration** — 5 specialized agents (router, FAQ, ticket, escalation, chitchat) + formatter via LangGraph state machine
- **Dual-Mode Operation** — Demo mode (no API keys) with keyword classifiers + SHA-256 embeddings, or live mode with Claude Haiku 4.5 + OpenAI embeddings
- **RAG Knowledge Base** — pgvector cosine similarity search with automatic chunking & embedding
- **MCP Tool Integration** — 5 tools via FastMCP 2.0 (Streamable HTTP transport)
- **SSE Streaming** — Real-time token-by-token agent responses
- **JWT Auth + RBAC** — Access/refresh tokens with admin, agent, customer roles
- **i18n** — Japanese/English via i18next with browser language detection

## Quick Start

```bash
# Start PostgreSQL + pgvector
docker compose up -d

# Configure environment
cp .env.example .env

# Install & run backend
uv sync
alembic upgrade head
uv run fastapi dev app/main.py

# Install & run frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 19, TypeScript, Tailwind CSS 4, Vite, i18next, Recharts |
| Backend | FastAPI, LangGraph, LangChain, FastMCP 2.0, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 17 + pgvector |
| AI | Claude Haiku 4.5, OpenAI text-embedding-3-small |
| Infra | Docker, Render |

## Documentation

- [Japanese Spec (日本語仕様書)](README_AgentFlow_マルチエージェントCS_JP.md)
- [English Spec](README_AgentFlow_マルチエージェントCS_EN.md)

## Testing

```bash
uv run pytest        # Run all 54 tests
uv run pytest -x     # Stop on first failure
```

## License

MIT

## Author

[@mer-prog](https://github.com/mer-prog)
