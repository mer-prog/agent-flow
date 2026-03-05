# AgentFlow — Design Specification

## Overview

AgentFlow is a multi-agent customer support platform built with **LangGraph + FastMCP + FastAPI**.
It demonstrates production-quality AI agent orchestration with human-in-the-loop escalation,
RAG-powered FAQ, ticket management, and real-time streaming — all deployable at $0/month.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI 0.135, Uvicorn |
| Agent Orchestration | LangGraph 1.0 (StateGraph) |
| LLM | Claude Haiku 4.5 (via langchain-anthropic) |
| Embeddings | OpenAI text-embedding-3-small (1536d) |
| MCP | FastMCP 3.1 (Streamable HTTP) |
| Database | PostgreSQL 17 (Neon), SQLAlchemy 2.0 async, asyncpg |
| Vector Search | pgvector (cosine similarity) |
| Migrations | Alembic (async) |
| Auth | JWT HS256 (python-jose), bcrypt |
| Frontend | React 19, Vite, Tailwind CSS 4, react-i18next |
| Logging | structlog |
| Deploy | Render Free + Neon Free |

## Dual-Mode Architecture

### Demo Mode (no API keys)
- Keyword-based intent classification (Router)
- SHA-256 pseudo-embeddings for vector search
- Template-based responses
- Fully functional without external API costs

### Live Mode (API keys set)
- Claude Haiku 4.5 for intent classification and responses
- OpenAI text-embedding-3-small for real embeddings
- Full LLM-powered agent responses

Mode is auto-detected: if `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are set → Live mode, otherwise → Demo mode.

---

## Project Structure

```
agent-flow/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, router mounting
│   ├── config.py             # pydantic-settings configuration
│   ├── database.py           # SQLAlchemy async engine + session
│   ├── models/
│   │   ├── __init__.py       # Re-exports all models + Base
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── ticket.py
│   │   ├── escalation.py
│   │   ├── knowledge.py      # kb_articles + kb_chunks
│   │   └── agent_run.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── conversation.py
│   │   ├── ticket.py
│   │   ├── escalation.py
│   │   ├── knowledge.py
│   │   └── stats.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py           # Dependency injection (get_db, get_current_user)
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── conversations.py
│   │   ├── tickets.py
│   │   ├── escalations.py
│   │   ├── knowledge.py
│   │   └── stats.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py          # AgentState TypedDict
│   │   ├── graph.py          # LangGraph StateGraph construction
│   │   ├── router.py         # Router Agent node
│   │   ├── faq.py            # FAQ Agent node (RAG)
│   │   ├── ticket.py         # Ticket Agent node
│   │   ├── escalation.py     # Escalation Agent node (HITL)
│   │   ├── chitchat.py       # Chitchat Agent node
│   │   └── formatter.py      # Response Formatter node
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── server.py         # FastMCP server + 5 tools
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py           # JWT + password hashing
│   │   ├── embedding.py      # Dual-mode embedding service
│   │   └── knowledge.py      # KB search service
│   └── core/
│       ├── __init__.py
│       ├── security.py       # Password hashing, JWT utils
│       └── logging.py        # structlog configuration
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── i18n/
│   │   └── types/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
├── alembic.ini
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── CLAUDE.md
└── docs/
    └── DESIGN_SPEC.md
```

---

## Database Schema

### Enums

```python
class UserRole(str, Enum):
    admin = "admin"
    agent = "agent"
    customer = "customer"

class ConversationStatus(str, Enum):
    active = "active"
    closed = "closed"
    archived = "archived"

class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class EscalationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"

class AgentType(str, Enum):
    router = "router"
    faq = "faq"
    ticket = "ticket"
    escalation = "escalation"
    chitchat = "chitchat"
    formatter = "formatter"

class AgentRunStatus(str, Enum):
    started = "started"
    completed = "completed"
    failed = "failed"

class IntentType(str, Enum):
    faq = "faq"
    ticket = "ticket"
    escalation = "escalation"
    chitchat = "chitchat"
```

### Tables

#### users
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| email | VARCHAR(255) | UNIQUE, NOT NULL, indexed |
| hashed_password | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| role | UserRole enum | NOT NULL, default "customer" |
| is_active | BOOLEAN | NOT NULL, default true |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |
| updated_at | TIMESTAMPTZ | onupdate now() |

#### conversations
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| user_id | UUID | FK → users.id, NOT NULL |
| title | VARCHAR(255) | nullable |
| status | ConversationStatus | NOT NULL, default "active" |
| metadata_ | JSONB | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |
| updated_at | TIMESTAMPTZ | onupdate now() |

#### messages
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| conversation_id | UUID | FK → conversations.id, NOT NULL |
| role | MessageRole | NOT NULL |
| content | TEXT | NOT NULL |
| metadata_ | JSONB | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |

#### tickets
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| conversation_id | UUID | FK → conversations.id, nullable |
| user_id | UUID | FK → users.id, NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | NOT NULL |
| status | TicketStatus | NOT NULL, default "open" |
| priority | TicketPriority | NOT NULL, default "medium" |
| category | VARCHAR(100) | nullable |
| assigned_to | UUID | FK → users.id, nullable |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |
| updated_at | TIMESTAMPTZ | onupdate now() |

#### escalations
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| conversation_id | UUID | FK → conversations.id, NOT NULL |
| ticket_id | UUID | FK → tickets.id, nullable |
| reason | TEXT | NOT NULL |
| sentiment_score | FLOAT | nullable |
| status | EscalationStatus | NOT NULL, default "pending" |
| reviewed_by | UUID | FK → users.id, nullable |
| reviewed_at | TIMESTAMPTZ | nullable |
| notes | TEXT | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |
| updated_at | TIMESTAMPTZ | onupdate now() |

#### kb_articles
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| title | VARCHAR(255) | NOT NULL |
| content | TEXT | NOT NULL |
| category | VARCHAR(100) | nullable |
| is_published | BOOLEAN | NOT NULL, default true |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |
| updated_at | TIMESTAMPTZ | onupdate now() |

#### kb_chunks
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| article_id | UUID | FK → kb_articles.id, NOT NULL, ondelete CASCADE |
| content | TEXT | NOT NULL |
| embedding | VECTOR(1536) | nullable |
| chunk_index | INTEGER | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |

#### agent_runs
| Column | Type | Constraints |
|--------|------|------------|
| id | UUID | PK, default uuid4 |
| conversation_id | UUID | FK → conversations.id, NOT NULL |
| agent_type | AgentType | NOT NULL |
| input_data | JSONB | NOT NULL |
| output_data | JSONB | nullable |
| duration_ms | INTEGER | nullable |
| status | AgentRunStatus | NOT NULL, default "started" |
| error_message | TEXT | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, server_default now() |

---

## LangGraph Agent Graph

```
                    ┌──────────┐
        START ────▶ │  Router  │
                    └────┬─────┘
                         │
            ┌────────────┼────────────┬────────────┐
            ▼            ▼            ▼            ▼
        ┌───────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  FAQ  │  │  Ticket  │  │Escalation│  │ Chitchat │
        └───┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
            │            │            │              │
            └────────────┴────────────┴──────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Response Formatter   │
                    └───────────┬───────────┘
                                │
                               END
```

### AgentState (TypedDict)
```python
class AgentState(TypedDict):
    messages: list[dict]
    intent: str | None
    confidence: float
    user_id: str
    conversation_id: str
    context: dict
    response: str | None
    agent_trace: list[dict]
    require_human_review: bool
    ticket_id: str | None
    kb_results: list[dict]
```

### Agent Nodes

1. **Router Agent**: Classifies user intent → faq | ticket | escalation | chitchat
2. **FAQ Agent**: RAG pipeline — embed query → pgvector search → generate answer
3. **Ticket Agent**: Creates/updates support tickets from conversation
4. **Escalation Agent**: Sentiment analysis → human-in-the-loop via `langgraph.interrupt()`
5. **Chitchat Agent**: General conversational responses
6. **Response Formatter**: Formats final response with metadata

---

## MCP Server

FastMCP 3.1 mounted at `/mcp` with Streamable HTTP transport.

### Tools

| Tool | Description | Parameters |
|------|------------|-----------|
| `search_knowledge_base` | Semantic search over KB chunks | `query: str, top_k: int = 5` |
| `create_ticket` | Create a new support ticket | `title: str, description: str, priority: str, category: str` |
| `update_ticket` | Update an existing ticket | `ticket_id: str, status: str, ...` |
| `get_support_metrics` | Dashboard statistics | `days: int = 30` |
| `escalate_to_human` | Trigger human escalation | `conversation_id: str, reason: str` |

---

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login → JWT tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Current user profile |

### Chat
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send message → SSE stream response |
| GET | `/api/chat/{conversation_id}/history` | Get conversation history |

### Conversations
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/conversations` | List conversations |
| GET | `/api/conversations/{id}` | Get conversation |
| PATCH | `/api/conversations/{id}` | Update conversation |
| DELETE | `/api/conversations/{id}` | Delete conversation |

### Tickets
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tickets` | List tickets |
| POST | `/api/tickets` | Create ticket |
| GET | `/api/tickets/{id}` | Get ticket |
| PATCH | `/api/tickets/{id}` | Update ticket |

### Escalations
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/escalations` | List escalations |
| GET | `/api/escalations/{id}` | Get escalation |
| POST | `/api/escalations/{id}/review` | Approve/reject escalation |

### Knowledge Base
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/knowledge` | List articles |
| POST | `/api/knowledge` | Create article |
| GET | `/api/knowledge/{id}` | Get article |
| PATCH | `/api/knowledge/{id}` | Update article |
| DELETE | `/api/knowledge/{id}` | Delete article |
| POST | `/api/knowledge/search` | Semantic search |

### Stats
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stats` | Dashboard KPIs |
| GET | `/api/stats/agent-performance` | Agent performance metrics |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

---

## Frontend Pages

1. **Login** (`/login`) — Email/password form, JWT storage
2. **Dashboard** (`/`) — KPI cards + charts
3. **Chat** (`/chat`) — Real-time chat with SSE streaming
4. **Tickets** (`/tickets`) — Ticket list with filters and detail view
5. **Escalations** (`/escalations`) — Approve/reject actions (HITL)
6. **Knowledge Base** (`/knowledge`) — Article CRUD + search
7. **Agent Flow** (`/agent-flow`) — Visual agent execution trace
8. **Settings** (`/settings`) — Profile, API keys, language toggle

### Design
- Dark theme (zinc/slate palette)
- Mobile-first responsive
- i18n: Japanese (ja) default, English (en)

---

## Authentication

- **Algorithm**: HS256
- **Access Token**: 30-minute expiry
- **Refresh Token**: 7-day expiry
- **Password Hashing**: bcrypt

---

## Deployment

- **Backend**: Render Free (Web Service)
- **Database**: Neon Free (PostgreSQL + pgvector)
- **Cost**: $0/month

---

## Implementation Phases

### Phase 1: Foundation
- Python project with uv, FastAPI scaffold, 8 SQLAlchemy models, Alembic + pgvector, Pydantic schemas, health endpoint, docker-compose, .env.example, CLAUDE.md

### Phase 2: Agent Core
- LangGraph StateGraph, 5 agent nodes + formatter, dual-mode (demo/live), embedding service, KB search service

### Phase 3: MCP Server
- FastMCP 3.1 server, 5 tools, mount on /mcp

### Phase 4: API Endpoints
- JWT auth, CRUD endpoints, SSE chat streaming, stats

### Phase 5: Frontend
- React 19 + Vite + Tailwind CSS 4, all 8 pages, i18n (ja/en), dark theme

### Phase 6: Polish & Deploy
- Render config, seed data, error handling, CORS, production build
