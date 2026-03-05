# AgentFlow — Multi-Agent Customer Support Platform

> **What:** A customer support platform that orchestrates five specialized AI agents via LangGraph to handle FAQ, ticket management, escalation, and general conversation automatically.
>
> **Who:** Engineers seeking production-ready patterns for AI agent orchestration, RAG pipelines, and human-in-the-loop workflows.
>
> **Tech:** LangGraph · FastMCP · FastAPI · React 19 · PostgreSQL 17 · pgvector · Tailwind CSS 4

Source Code: [https://github.com/mer-prog/agent-flow](https://github.com/mer-prog/agent-flow)

---

## Skills Demonstrated

| Skill | Implementation |
|-------|---------------|
| Multi-Agent Orchestration | Built a LangGraph StateGraph with Router → 4 specialist agents → Formatter using conditional edge routing and type-safe TypedDict state management |
| RAG Pipeline | Implemented pgvector cosine similarity search with sentence-aware chunking (~500 chars) and 1536-dimensional vector embeddings for knowledge base retrieval |
| Dual-Mode Architecture | Designed automatic switching between a zero-cost demo mode (keyword classifiers + SHA-256 pseudo-embeddings) and a full LLM-powered live mode |
| Real-Time Streaming | Implemented Server-Sent Events for streaming agent traces and token-by-token chat responses from backend to frontend |
| Async-First Architecture | Built fully asynchronous DB operations, API handlers, and agent nodes using FastAPI + SQLAlchemy 2.0 async + asyncpg |
| MCP Server | Exposed 5 tools via FastMCP with Streamable HTTP transport, enabling external AI clients to invoke knowledge search, ticket management, and escalation |
| Auth & Access Control | Implemented JWT HS256 (access/refresh tokens) + bcrypt password hashing + role-based access control (admin/agent/customer) |

---

## Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Backend | Python >=3.12, FastAPI >=0.115 | Async REST API server |
| Agent Framework | LangGraph >=0.2 | StateGraph-based multi-agent orchestration |
| LLM | langchain-anthropic >=0.3 (Claude Haiku 4.5) | Intent classification, response generation, sentiment analysis |
| Embeddings | langchain-openai >=0.3 (text-embedding-3-small) | 1536-dimensional vector embedding generation |
| MCP | FastMCP >=2.0 | Model Context Protocol server (5 tools) |
| Database | PostgreSQL 17 + pgvector >=0.3 | Relational DB + vector similarity search |
| ORM | SQLAlchemy[asyncio] >=2.0, asyncpg >=0.30 | Async database operations |
| Migrations | Alembic >=1.14 | Async DB schema migrations |
| Auth | python-jose[cryptography] >=3.3, bcrypt >=4.2 | JWT token issuance + password hashing |
| Logging | structlog >=24.4 | Structured logging (dev: console / prod: JSON) |
| Config | pydantic-settings >=2.7 | Type-safe environment variable management |
| Frontend | React ^19.0.0, React DOM ^19.0.0 | Single Page Application |
| Routing | React Router DOM ^7.1.0 | Client-side routing |
| i18n | i18next ^24.2.0, react-i18next ^15.4.0 | Japanese and English localization |
| Charts | recharts ^2.15.0 | Dashboard KPI visualizations |
| Icons | lucide-react ^0.468.0 | UI icons |
| Styling | Tailwind CSS ^4.0.0 | Utility-first CSS (dark theme) |
| Build | Vite ^6.0.0, TypeScript ^5.7.0 | Fast builds + strict type checking |
| Testing | pytest >=8.0, pytest-asyncio >=0.24 | Async-capable test framework |
| Containers | Docker Compose (pgvector/pgvector:pg17) | Local development PostgreSQL |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (React 19)                        │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│  │Login │ │Dash- │ │ Chat │ │Ticket│ │Escal-│ │Know- │       │
│  │      │ │board │ │(SSE) │ │      │ │ation │ │ledge │       │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘       │
│     └────────┴────────┴────────┴────────┴────────┘            │
│                         │ HTTP / SSE                           │
└─────────────────────────┼─────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│                    FastAPI Backend                              │
│  ┌──────────────────────┼──────────────────────────────────┐  │
│  │               REST API Routers (7 modules)               │  │
│  │  auth · chat · conversations · tickets                   │  │
│  │  escalations · knowledge · stats                         │  │
│  └──────────────────────┼──────────────────────────────────┘  │
│                         │                                      │
│  ┌──────────────────────┼──────────────────────────────────┐  │
│  │              LangGraph Agent Graph                       │  │
│  │                                                          │  │
│  │              ┌──────────┐                                │  │
│  │   START ───▶ │  Router  │                                │  │
│  │              └────┬─────┘                                │  │
│  │       ┌───────┬───┴───┬───────┐                         │  │
│  │       ▼       ▼       ▼       ▼                         │  │
│  │    ┌─────┐ ┌──────┐ ┌─────┐ ┌──────┐                   │  │
│  │    │ FAQ │ │Ticket│ │Esca.│ │Chat  │                    │  │
│  │    │(RAG)│ │      │ │(HITL)│ │      │                    │  │
│  │    └──┬──┘ └──┬───┘ └──┬──┘ └──┬───┘                   │  │
│  │       └───────┴────────┴───────┘                        │  │
│  │                    │                                     │  │
│  │           ┌────────▼────────┐                           │  │
│  │           │   Formatter     │                            │  │
│  │           └────────┬────────┘                           │  │
│  │                   END                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                      │
│  ┌──────────────┐  ┌────┴───────┐  ┌───────────────────────┐  │
│  │ FastMCP (5T) │  │  Services  │  │      Security         │  │
│  │ /mcp         │  │ auth/embed/│  │ JWT + bcrypt + RBAC   │  │
│  │              │  │ knowledge  │  │                       │  │
│  └──────────────┘  └────┬───────┘  └───────────────────────┘  │
└─────────────────────────┼─────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────┐
│              PostgreSQL 17 + pgvector                          │
│  ┌──────┐ ┌──────────┐ ┌────────┐ ┌──────┐ ┌──────────────┐  │
│  │users │ │conversa- │ │messages│ │ticket│ │kb_articles   │  │
│  │      │ │tions     │ │        │ │      │ │+ kb_chunks   │  │
│  │      │ │          │ │        │ │      │ │(VECTOR 1536) │  │
│  └──────┘ └──────────┘ └────────┘ └──────┘ └──────────────┘  │
│  ┌───────────┐ ┌─────────────┐                                │
│  │escalations│ │ agent_runs  │                                │
│  └───────────┘ └─────────────┘                                │
└───────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. Multi-Agent Orchestration
A LangGraph StateGraph with 6 nodes: the Router agent classifies user intent (faq / ticket / escalation / chitchat) and conditionally routes to the appropriate specialist agent. All results converge at the Formatter node. An `agent_trace` list captures execution time and metadata for each node, providing a full audit trail.

### 2. RAG Knowledge Base Search
Knowledge base articles are split into sentence-aware chunks (~500 characters each), with 1536-dimensional vector embeddings generated per chunk. User queries are vectorized and matched against chunks via pgvector cosine similarity. The FAQ agent injects retrieved context into the LLM prompt for grounded answers.

### 3. Dual-Mode Operation
- **Demo Mode** (no API keys): Keyword regex intent classification, SHA-256 deterministic pseudo-embeddings (1536-dim), and template responses. Fully functional at zero external API cost.
- **Live Mode** (`ANTHROPIC_API_KEY` + `OPENAI_API_KEY` configured): Claude Haiku 4.5 for intent classification, response generation, and sentiment analysis. OpenAI text-embedding-3-small for real vector embeddings.

### 4. Real-Time Chat Streaming
The `POST /api/chat` endpoint delivers Server-Sent Events with agent trace entries and response tokens in real time. The frontend `useSSE` custom hook parses the ReadableStream incrementally and renders streaming text with a blinking cursor.

### 5. Human-in-the-Loop Escalation
The Escalation agent computes a sentiment score (0.0 to 1.0) from the user message and sets `require_human_review = true`. Admins and agents can approve or reject escalations through the management interface.

### 6. MCP Tool Server
FastMCP exposes 5 tools via Streamable HTTP transport at `/mcp`. External AI clients (e.g., Claude Desktop) can invoke knowledge base search, ticket creation/update, metrics retrieval, and escalation creation.

### 7. JWT Authentication + Role-Based Access Control
bcrypt password hashing, HS256 JWT tokens (30-minute access / 7-day refresh), and three roles (admin / agent / customer) with endpoint-level access enforcement. Customers can only access their own resources; agents and admins have full access.

### 8. Dashboard Analytics
Six KPI cards (conversations, active conversations, open tickets, pending escalations, resolution rate, average response time) plus agent performance bar charts and pie charts rendered with recharts.

### 9. Internationalization (i18n)
i18next + react-i18next with Japanese and English support. Automatic browser language detection with manual toggle in the settings page.

---

## Project Structure

```
agent-flow/
├── app/                              # Backend (Python)
│   ├── main.py                       # FastAPI app bootstrap + router registration (68 lines)
│   ├── config.py                     # pydantic-settings configuration (82 lines)
│   ├── database.py                   # SQLAlchemy async engine (31 lines)
│   ├── agents/                       # LangGraph agent nodes
│   │   ├── state.py                  #   AgentState TypedDict (20 lines)
│   │   ├── graph.py                  #   StateGraph build + compile (68 lines)
│   │   ├── llm.py                    #   ChatAnthropic singleton (23 lines)
│   │   ├── router.py                 #   Intent classification agent (110 lines)
│   │   ├── faq.py                    #   RAG FAQ agent (90 lines)
│   │   ├── ticket.py                 #   Ticket creation agent (115 lines)
│   │   ├── escalation.py             #   Sentiment analysis + escalation (100 lines)
│   │   ├── chitchat.py               #   Conversational agent (74 lines)
│   │   ├── formatter.py              #   Response formatting (36 lines)
│   │   └── __init__.py               #   Shared utility (13 lines)
│   ├── mcp/
│   │   └── server.py                 # FastMCP server + 5 tools (197 lines)
│   ├── services/
│   │   ├── auth.py                   # User registration, auth, tokens (59 lines)
│   │   ├── embedding.py              # Dual-mode embeddings (41 lines)
│   │   └── knowledge.py              # KB search + chunking (90 lines)
│   ├── core/
│   │   ├── security.py               # bcrypt + JWT utilities (33 lines)
│   │   └── logging.py                # structlog setup (27 lines)
│   ├── models/                       # SQLAlchemy models (8 tables)
│   │   ├── user.py                   #   User (42 lines)
│   │   ├── conversation.py           #   Conversation (42 lines)
│   │   ├── message.py                #   Message (35 lines)
│   │   ├── ticket.py                 #   Ticket (66 lines)
│   │   ├── escalation.py             #   Escalation (52 lines)
│   │   ├── agent_run.py              #   Agent execution log (51 lines)
│   │   ├── knowledge.py              #   KB article + chunks (47 lines)
│   │   └── __init__.py               #   Model re-exports (27 lines)
│   ├── schemas/                      # Pydantic schemas
│   │   ├── auth.py                   #   Authentication (39 lines)
│   │   ├── chat.py                   #   Chat (16 lines)
│   │   ├── conversation.py           #   Conversation (45 lines)
│   │   ├── ticket.py                 #   Ticket (45 lines)
│   │   ├── escalation.py             #   Escalation (33 lines)
│   │   ├── knowledge.py              #   Knowledge base (61 lines)
│   │   └── stats.py                  #   Statistics (24 lines)
│   └── api/                          # REST API routers
│       ├── deps.py                   #   DI (get_db, get_current_user) (50 lines)
│       ├── auth.py                   #   Authentication (60 lines)
│       ├── chat.py                   #   Chat + SSE streaming (137 lines)
│       ├── conversations.py          #   Conversation CRUD (106 lines)
│       ├── tickets.py                #   Ticket CRUD (104 lines)
│       ├── escalations.py            #   Escalation management (91 lines)
│       ├── knowledge.py              #   KB CRUD + search (142 lines)
│       └── stats.py                  #   Dashboard statistics (102 lines)
├── frontend/                         # Frontend (React 19)
│   ├── src/
│   │   ├── main.tsx                  # Entry point (14 lines)
│   │   ├── App.tsx                   # Routing shell (42 lines)
│   │   ├── api/client.ts             # HTTP client + token management (70 lines)
│   │   ├── types/index.ts            # Type definitions (88 lines)
│   │   ├── hooks/
│   │   │   ├── useAuth.ts            # Auth hook (52 lines)
│   │   │   └── useSSE.ts             # SSE streaming hook (75 lines)
│   │   ├── i18n/
│   │   │   ├── config.ts             # i18next setup (16 lines)
│   │   │   ├── ja.ts                 # Japanese translations (70 lines)
│   │   │   └── en.ts                 # English translations (70 lines)
│   │   ├── constants/colors.ts       # Status color mappings (21 lines)
│   │   ├── components/Layout.tsx     # Sidebar + main layout (97 lines)
│   │   └── pages/
│   │       ├── LoginPage.tsx         # Login / registration form (110 lines)
│   │       ├── DashboardPage.tsx     # KPIs + charts (132 lines)
│   │       ├── ChatPage.tsx          # Real-time chat (174 lines)
│   │       ├── TicketsPage.tsx       # Ticket list + filters (101 lines)
│   │       ├── EscalationsPage.tsx   # Escalation management (124 lines)
│   │       ├── KnowledgePage.tsx     # Knowledge base + search (176 lines)
│   │       ├── AgentFlowPage.tsx     # Agent graph visualization (117 lines)
│   │       └── SettingsPage.tsx      # Settings (54 lines)
│   ├── index.html                    # HTML template (12 lines)
│   ├── package.json                  # Dependencies (30 lines)
│   ├── vite.config.ts                # Vite config (15 lines)
│   └── tsconfig.json                 # TypeScript config (20 lines)
├── tests/                            # Test suite (54 tests)
│   ├── test_config.py                # Config tests (51 lines, 8 tests)
│   ├── test_security.py              # Security tests (49 lines, 6 tests)
│   ├── test_schemas.py               # Schema tests (87 lines, 19 tests)
│   ├── test_agents.py                # Agent tests (131 lines, 19 tests)
│   └── test_embedding.py             # Embedding tests (38 lines, 6 tests)
├── alembic/                          # DB migrations
│   ├── env.py                        # Async migration config (73 lines)
│   └── versions/001_initial.py       # Initial schema (151 lines)
├── scripts/seed.py                   # Seed data loader (174 lines)
├── docker-compose.yml                # PostgreSQL 17 + pgvector (20 lines)
├── pyproject.toml                    # Python dependencies (42 lines)
├── .env.example                      # Environment variable template (15 lines)
└── docs/DESIGN_SPEC.md               # Design specification (471 lines)
```

---

## Database Design

### ER Diagram

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  users   │────<│conversations │────<│ messages │
│          │     │              │     │          │
│ id (PK)  │     │ id (PK)      │     │ id (PK)  │
│ email    │     │ user_id (FK) │     │ conv_id  │
│ password │     │ title        │     │ role     │
│ full_name│     │ status       │     │ content  │
│ role     │     │ metadata_    │     │ metadata_│
│ is_active│     └──────┬───────┘     └──────────┘
└────┬─────┘            │
     │            ┌─────┴──────┐
     │            │            │
┌────▼─────┐ ┌───▼────────┐ ┌─▼───────────┐
│ tickets  │ │escalations │ │ agent_runs  │
│          │ │            │ │             │
│ id (PK)  │ │ id (PK)    │ │ id (PK)     │
│ user_id  │ │ conv_id    │ │ conv_id     │
│ conv_id  │ │ ticket_id  │ │ agent_type  │
│ title    │ │ reason     │ │ input_data  │
│ desc     │ │ sentiment  │ │ output_data │
│ status   │ │ status     │ │ duration_ms │
│ priority │ │ reviewed_by│ │ status      │
│ category │ │ notes      │ │ error_msg   │
│ assigned │ └────────────┘ └─────────────┘
└──────────┘

┌──────────────┐     ┌──────────────┐
│ kb_articles  │────<│  kb_chunks   │
│              │     │              │
│ id (PK)      │     │ id (PK)      │
│ title        │     │ article_id   │
│ content      │     │ content      │
│ category     │     │ embedding    │
│ is_published │     │  (VEC 1536)  │
└──────────────┘     │ chunk_index  │
                     └──────────────┘
```

### Table Summary (8 tables + 8 enum types)

| Table | Key Columns | Description |
|-------|------------|-------------|
| users | id, email, hashed_password, full_name, role, is_active | User management with 3 roles: admin, agent, customer |
| conversations | id, user_id, title, status, metadata_ | Chat conversations. Status: active, closed, archived |
| messages | id, conversation_id, role, content, metadata_ | Messages within conversations. Role: user, assistant, system |
| tickets | id, user_id, title, description, status, priority, category, assigned_to | Support tickets with 4 priority levels and 4 status values |
| escalations | id, conversation_id, reason, sentiment_score, status, reviewed_by, notes | Escalation records with sentiment score and approve/reject workflow |
| agent_runs | id, conversation_id, agent_type, input_data, output_data, duration_ms, status | Agent execution logs tracking 6 agent types |
| kb_articles | id, title, content, category, is_published | Knowledge base articles |
| kb_chunks | id, article_id, content, embedding (VECTOR 1536), chunk_index | Article chunks with pgvector embeddings |

---

## API Endpoints

### Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/auth/register` | Register a new user | None |
| POST | `/api/auth/login` | Login and receive JWT tokens | None |
| POST | `/api/auth/refresh` | Refresh access token | Refresh token |
| GET | `/api/auth/me` | Get current user profile | Required |

### Chat

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/chat` | Send message and receive SSE stream response | Required |
| GET | `/api/chat/{id}/history` | Get conversation message history | Required |

### Conversations

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/conversations` | List conversations (pagination + status filter) | Required |
| GET | `/api/conversations/{id}` | Get conversation detail with messages | Required |
| PATCH | `/api/conversations/{id}` | Update conversation | Required |
| DELETE | `/api/conversations/{id}` | Delete conversation | Required |

### Tickets

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/tickets` | List tickets (customers see only their own) | Required |
| POST | `/api/tickets` | Create a new ticket | Required |
| GET | `/api/tickets/{id}` | Get ticket details | Required |
| PATCH | `/api/tickets/{id}` | Update ticket (customers limited to title/description) | Required |

### Escalations

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/escalations` | List escalations | Agent/Admin |
| GET | `/api/escalations/{id}` | Get escalation details | Agent/Admin |
| POST | `/api/escalations/{id}/review` | Approve or reject | Agent/Admin |

### Knowledge Base

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/knowledge` | List published articles | Required |
| POST | `/api/knowledge` | Create article (auto chunks + embeds) | Agent/Admin |
| GET | `/api/knowledge/{id}` | Get article with chunks | Required |
| PATCH | `/api/knowledge/{id}` | Update article (re-chunks on content change) | Agent/Admin |
| DELETE | `/api/knowledge/{id}` | Delete article (cascades to chunks) | Agent/Admin |
| POST | `/api/knowledge/search` | Semantic search | Required |

### Statistics

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/stats` | Dashboard KPIs | Required |
| GET | `/api/stats/agent-performance` | Per-agent execution statistics | Required |

### System

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/health` | Health check (shows operating mode) | None |

---

## MCP Tools

FastMCP server provides Streamable HTTP transport at the `/mcp` endpoint.

| Tool Name | Parameters | Description |
|-----------|-----------|-------------|
| `search_knowledge_base` | query, top_k=5 | Semantic search via pgvector cosine similarity |
| `create_ticket` | title, description, priority, category, user_id | Create a support ticket |
| `update_ticket` | ticket_id, status, priority, assigned_to | Update ticket status, priority, or assignment |
| `get_support_metrics` | days=30 | Dashboard KPIs (conversations, tickets, resolution rate) |
| `escalate_to_human` | conversation_id, reason | Create an escalation for human agent review |

---

## Screen Specifications

| Screen | Path | Functionality |
|--------|------|--------------|
| Login | `/login` | Email/password form with login/register toggle |
| Dashboard | `/` | 6 KPI cards, agent performance bar chart and pie chart |
| Chat | `/chat` | Conversation sidebar + real-time SSE streaming |
| Tickets | `/tickets` | Ticket list with status filter buttons |
| Escalations | `/escalations` | Escalation management with approve/reject actions |
| Knowledge Base | `/knowledge` | Article list + semantic search + article creation |
| Agent Flow | `/agent-flow` | SVG agent graph visualization |
| Settings | `/settings` | Language toggle (JP/EN), operating mode info |

---

## Security Design

| Measure | Implementation |
|---------|---------------|
| Password Protection | bcrypt hashing with automatic salt generation |
| Auth Tokens | JWT HS256 (access: 30 min / refresh: 7 days) |
| Token Validation | Authorization header Bearer token with token type verification |
| Access Control | Role-based (admin/agent/customer), enforced at endpoint level |
| Data Isolation | Customers can only access their own resources |
| Input Validation | Pydantic request validation (length constraints, type checks) |
| CORS | Configurable allowed origins |

---

## Test Suite

54 tests across 5 files using `pytest` + `pytest-asyncio` for async test support.

| File | Tests | Coverage |
|------|-------|---------|
| test_config.py | 8 | Demo/live mode detection, URL conversion, SSL detection |
| test_security.py | 6 | bcrypt hash roundtrip, JWT access/refresh tokens |
| test_schemas.py | 19 | Auth, ticket, and knowledge base schema validation |
| test_agents.py | 19 | Router classification, sentiment analysis, ticket extraction, template responses |
| test_embedding.py | 6 | Dimension check, determinism, value range, case insensitivity |

```bash
uv run pytest          # Run all tests
uv run pytest -x       # Stop on first failure
```

---

## Seed Data

`scripts/seed.py` provides idempotent test data seeding.

| Data | Contents |
|------|---------|
| Users (3) | admin@example.com (admin), agent@example.com (agent), demo@example.com (customer) |
| KB Articles (5) | Getting Started, Pricing Plans, Return Policy, Technical Requirements, Account Security |
| Tickets (3) | Password reset (high/open), Double billing (urgent/in progress), Dark mode request (low/resolved) |
| Conversations (1) | Pricing inquiry (active) |

Passwords are configurable via environment variables: `SEED_ADMIN_PASSWORD`, `SEED_AGENT_PASSWORD`, `SEED_CUSTOMER_PASSWORD`

---

## Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (for PostgreSQL)
- uv (Python package manager)

### Instructions

```bash
# 1. Clone the repository
git clone https://github.com/mer-prog/agent-flow.git
cd agent-flow

# 2. Start PostgreSQL
docker compose up -d

# 3. Configure environment variables
cp .env.example .env
# Edit .env (make sure to change JWT_SECRET)

# 4. Install Python dependencies
uv sync

# 5. Run database migrations
alembic upgrade head

# 6. Load seed data (optional)
uv run python scripts/seed.py

# 7. Start the backend
uv run fastapi dev app/main.py

# 8. Start the frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables

| Variable | Description | Required |
|----------|------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET` | JWT signing secret key (HS256) | Yes |
| `ANTHROPIC_API_KEY` | Claude API key (for live mode) | No |
| `OPENAI_API_KEY` | OpenAI API key (for live mode) | No |
| `APP_ENV` | Runtime environment (development / production) | No |
| `LOG_LEVEL` | Log level (default: INFO) | No |
| `CORS_ORIGINS` | Allowed origins (JSON array format) | No |

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| LangGraph StateGraph | Enables conditional edge routing, typed state management, and agent tracing out of the box. Future-ready for checkpointing and human interrupts |
| Dual-Mode (Demo/Live) | Allows full feature verification without API keys, supporting development, demos, and production from a single codebase |
| pgvector over dedicated vector DB | Native PostgreSQL vector search eliminates the need for a separate vector database while maintaining transactional consistency |
| FastMCP for MCP server | Model Context Protocol enables external AI clients (e.g., Claude Desktop) to invoke tools directly, extending agent capabilities beyond the application |
| SSE over WebSocket | Simpler implementation than WebSocket, HTTP/2 compatible, and well-suited for unidirectional streaming of agent traces and tokens |
| JWT access + refresh tokens | Short-lived access tokens (30 min) for security, long-lived refresh tokens (7 days) for user experience |
| SHA-256 pseudo-embeddings | Deterministic, reproducible vectors without external API calls for demo mode. Same query always returns the same vector |
| React 19 + Tailwind CSS 4 | Latest React hooks + utility-first CSS for efficient dark theme implementation |
| structlog | Console output in development, JSON structured logs in production. Automatic environment-based switching |

---

## Running Costs

| Service | Plan | Monthly Cost |
|---------|------|-------------|
| Render | Free (Web Service) | $0 |
| Neon | Free (PostgreSQL + pgvector) | $0 |
| Claude API (live mode) | Pay-per-use | ~$0.01-0.05 / message |
| OpenAI API (live mode) | Pay-per-use | ~$0.001 / embedding request |
| **Total (demo mode)** | | **$0** |

---

## Author

[@mer-prog](https://github.com/mer-prog)
