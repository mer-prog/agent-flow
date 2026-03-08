# AgentFlow — Multi-Agent AI Customer Support Platform

> **What:** A full-stack AI customer support system integrating LangGraph multi-agent orchestration, FastMCP tool integration, and RAG-based knowledge retrieval
> **For:** Enterprises and development teams exploring AI-powered customer support
> **Tech:** React 19 · FastAPI · LangGraph · FastMCP · PostgreSQL 17 + pgvector · Claude Haiku 4.5

## Skills Demonstrated

| Skill | Implementation |
|-------|---------------|
| Full-Stack Development | End-to-end development with React 19 SPA (TypeScript) + async FastAPI backend (~1,500 lines frontend, ~2,600 lines backend) |
| AI/LLM Integration | LangGraph multi-agent graph (5 agents + formatter), Claude Haiku 4.5, RAG pipeline, FastMCP tool integration, dual-mode operation |
| API Design & Integration | RESTful API design (7 routers, 22 endpoints), SSE streaming, MCP Streamable HTTP transport |
| Database Design & Management | PostgreSQL 17 + pgvector with 8-table schema, async ORM (SQLAlchemy 2.0 + asyncpg), Alembic migrations |
| Authentication & Authorization | JWT authentication (access/refresh tokens), role-based access control (admin, agent, customer) |
| System Architecture | State machine-based multi-agent orchestration, MCP-based tool decoupling, Docker multi-stage builds |
| UI/UX Design | Tailwind CSS 4 dark theme, i18next multilingual support (EN/JP), real-time SSE streaming UI, Recharts data visualization |

## Tech Stack

### Backend

| Category | Technology | Purpose |
|----------|-----------|---------|
| Framework | FastAPI >=0.115 | Async REST API server |
| Agents | LangGraph >=0.2, LangChain Core >=0.3 | Multi-agent graph orchestration |
| LLM | langchain-anthropic >=0.3 (Claude Haiku 4.5) | Intent classification, response generation, sentiment analysis |
| Embeddings | langchain-openai >=0.3 (text-embedding-3-small) | Knowledge base vector embeddings |
| MCP | FastMCP >=2.0 | Standardized agent tool protocol |
| Database | PostgreSQL 17 + pgvector >=0.3 | Relational data + vector search |
| ORM | SQLAlchemy >=2.0 (async) + asyncpg >=0.30 | Async database access |
| Migrations | Alembic >=1.14 | Database schema management |
| Auth | python-jose >=3.3 + bcrypt >=4.2 | JWT token generation, password hashing |
| Logging | structlog >=24.4 | Structured log output |

### Frontend

| Category | Technology | Purpose |
|----------|-----------|---------|
| Framework | React ^19.0.0 | UI components |
| Routing | React Router ^7.1.0 | SPA routing |
| Styling | Tailwind CSS ^4.0.0 | Utility-first CSS |
| Build Tool | Vite ^6.0.0 | Fast builds with HMR |
| Language | TypeScript ^5.7.0 | Type-safe development |
| i18n | i18next ^24.2.0 + react-i18next ^15.4.0 | EN/JP multilingual support |
| Charts | Recharts ^2.15.0 | Dashboard statistics visualization |

### Infrastructure

| Category | Technology | Purpose |
|----------|-----------|---------|
| Container | Docker multi-stage build | Frontend build + backend runtime |
| Database Image | pgvector/pgvector:pg17 | PostgreSQL with vector extension |
| Deployment | Render (free tier compatible) | Web service + managed PostgreSQL |
| Package Manager | uv | Python dependency management |

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                      React 19 Frontend                              │
│             Vite + TypeScript + Tailwind CSS 4 + i18next           │
│                                                                     │
│  Chat │ Tickets │ Escalations │ Knowledge │ Dashboard │ AgentFlow  │
│  Settings │ Login                                                   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP / SSE
                            ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                               │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  API Routers (7)                                                │  │
│  │  auth │ chat │ conversations │ tickets │ escalations │          │  │
│  │  knowledge │ stats                                              │  │
│  └───────────────────────────┬─────────────────────────────────────┘  │
│                              │                                        │
│  ┌───────────────────────────▼─────────────────────────────────────┐  │
│  │            LangGraph Multi-Agent Graph                          │  │
│  │                                                                 │  │
│  │  router_agent ──┬──→ faq_agent ────────┐                       │  │
│  │  (intent        ├──→ ticket_agent ─────┤                       │  │
│  │   classifier)   ├──→ escalation_agent ──┤──→ formatter → END   │  │
│  │                 └──→ chitchat_agent ────┘   (response           │  │
│  │                                              formatting)        │  │
│  │  Live Mode: Claude Haiku 4.5 + OpenAI Embeddings               │  │
│  │  Demo Mode: Keyword classifiers + SHA-256 pseudo-embeddings    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  FastMCP Tool Server (5 Tools)                                  │  │
│  │  search_knowledge_base │ create_ticket │ update_ticket │        │  │
│  │  get_support_metrics │ escalate_to_human                        │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  Service Layer                                                  │  │
│  │  auth │ embedding │ knowledge │ security                        │  │
│  └───────────────────────────┬─────────────────────────────────────┘  │
└──────────────────────────────┼────────────────────────────────────────┘
                               │
              ┌────────────────┴─────────────────┐
              ▼                                  ▼
  ┌─────────────────────┐           ┌──────────────────────┐
  │  PostgreSQL 17      │           │  External APIs       │
  │  + pgvector         │           │  Anthropic (Claude)  │
  │                     │           │  OpenAI (Embeddings) │
  │  8 Tables:          │           └──────────────────────┘
  │  users              │
  │  conversations      │
  │  messages           │
  │  tickets            │
  │  escalations        │
  │  agent_runs         │
  │  kb_articles        │
  │  kb_chunks          │
  └─────────────────────┘
```

## Key Features

### Multi-Agent Chat System

- **Intent Classification Router** — Automatically classifies user messages into 4 categories: FAQ, Ticket, Escalation, and Chitchat
- **RAG-Based FAQ Responses** — Retrieves relevant information from the knowledge base via pgvector similarity search to generate answers
- **Automatic Ticket Creation** — Extracts title, priority, and category from conversation content to auto-generate support tickets
- **Sentiment-Based Escalation** — Detects negative sentiment and suggests escalation to human operators
- **SSE Real-Time Streaming** — Token-by-token real-time response display

### Dual-Mode Operation

- **Live Mode** — High-accuracy NLP via Claude Haiku 4.5 + semantic search via OpenAI text-embedding-3-small
- **Demo Mode** — No API keys required. Keyword-based classifiers + SHA-256 pseudo-embeddings enable full functionality

### Knowledge Base Management

- Article CRUD operations
- Automatic chunking and embedding generation
- Cosine similarity vector search
- Category filtering and publication status management

### Ticket Management

- 4-level priority (low, medium, high, urgent)
- Status tracking (open, in_progress, resolved, closed)
- Role-based display control (customers see own tickets; agents/admins see all)

### Escalation Management

- Pending escalations queue
- Sentiment score-based prioritization
- Approval/rejection workflow

### Dashboard & Analytics

- Conversation, ticket, and escalation statistics
- Agent performance metrics
- Resolution rate and response time visualization (Recharts)

### Authentication & Authorization

- JWT tokens (access + refresh)
- 3 user roles: admin, agent, customer
- Automatic token refresh on 401

### Multilingual Support

- EN/JP language switching via i18next
- Automatic browser language detection

## Project Structure

```text
agent-flow/
├── app/                          # FastAPI backend (~2,600 lines)
│   ├── main.py                  # Entry point, middleware config
│   ├── config.py                # Settings, dual-mode detection
│   ├── database.py              # SQLAlchemy async engine & session
│   ├── models/                  # SQLAlchemy ORM models (8 tables)
│   │   ├── user.py             # User, UserRole enum
│   │   ├── conversation.py     # Conversation, ConversationStatus
│   │   ├── message.py          # Message, MessageRole
│   │   ├── ticket.py           # Ticket, TicketStatus, TicketPriority
│   │   ├── escalation.py       # Escalation, EscalationStatus
│   │   ├── agent_run.py        # AgentRun, AgentType, AgentRunStatus
│   │   └── knowledge.py        # KBArticle, KBChunk + pgvector
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── api/                     # REST API routers (7)
│   │   ├── auth.py             # /api/auth — register, login, refresh
│   │   ├── chat.py             # /api/chat — SSE streaming
│   │   ├── conversations.py    # /api/conversations — conversation CRUD
│   │   ├── tickets.py          # /api/tickets — ticket management
│   │   ├── escalations.py      # /api/escalations — escalation management
│   │   ├── knowledge.py        # /api/knowledge — KB CRUD + search
│   │   ├── stats.py            # /api/stats — dashboard statistics
│   │   └── deps.py             # Dependency injection (auth, DB session)
│   ├── agents/                  # LangGraph agent system
│   │   ├── state.py            # AgentState TypedDict definition
│   │   ├── graph.py            # Agent graph build & compile
│   │   ├── router.py           # Router agent — intent classification
│   │   ├── faq.py              # FAQ agent — RAG search & response
│   │   ├── ticket.py           # Ticket agent — field extraction
│   │   ├── escalation.py       # Escalation agent — sentiment analysis
│   │   ├── chitchat.py         # Chitchat agent
│   │   └── formatter.py        # Response formatter
│   ├── mcp/                     # FastMCP tool server
│   │   └── server.py           # 5 MCP tool definitions
│   ├── services/                # Business logic
│   │   ├── auth.py             # Auth helpers
│   │   ├── embedding.py        # Embedding service — live/demo toggle
│   │   └── knowledge.py        # Knowledge base search & chunking
│   └── core/                    # Core utilities
│       ├── security.py         # JWT token generation/verification
│       └── logging.py          # structlog configuration
├── frontend/                     # React 19 SPA (~1,500 lines)
│   └── src/
│       ├── App.tsx             # Routing & auth wrapper
│       ├── api/client.ts       # HTTP client — auto token refresh
│       ├── hooks/              # useAuth, useSSE
│       ├── i18n/               # i18next config + EN/JP translations
│       ├── pages/              # 8 page components
│       ├── components/         # Shared layout
│       └── types/              # TypeScript type definitions
├── tests/                        # Test suite (54 tests)
├── alembic/                      # Database migrations
├── scripts/seed.py               # Seed data — demo users, KB articles
├── docker-compose.yml            # PostgreSQL 17 + pgvector
├── Dockerfile                    # Multi-stage build (Node.js + Python)
├── render.yaml                   # Render deployment config
└── pyproject.toml                # Python dependencies & config
```

## API Endpoints

### Authentication (/api/auth)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login (issue tokens) |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current user profile |

### Chat (/api/chat)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send message (SSE streaming response) |
| GET | `/api/chat/{conversation_id}/history` | Get conversation history |

### Conversations (/api/conversations)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/conversations` | List conversations (paginated) |
| GET | `/api/conversations/{id}` | Get conversation detail (with messages) |
| PATCH | `/api/conversations/{id}` | Update conversation (title/status) |
| DELETE | `/api/conversations/{id}` | Delete conversation |

### Tickets (/api/tickets)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tickets` | List tickets (role-aware display) |
| POST | `/api/tickets` | Create ticket |
| GET | `/api/tickets/{id}` | Get ticket details |
| PATCH | `/api/tickets/{id}` | Update ticket |

### Escalations (/api/escalations)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/escalations` | List escalations (admins/agents only) |
| GET | `/api/escalations/{id}` | Get escalation details |
| POST | `/api/escalations/{id}/review` | Review escalation (approve/reject) |

### Knowledge Base (/api/knowledge)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/knowledge` | List published articles |
| POST | `/api/knowledge` | Create article (admins/agents) |
| GET | `/api/knowledge/{id}` | Get article detail (with chunks) |
| PATCH | `/api/knowledge/{id}` | Update article (re-chunks on content change) |
| DELETE | `/api/knowledge/{id}` | Delete article |
| POST | `/api/knowledge/search` | Vector similarity search |

### Statistics (/api/stats)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/stats/agent-performance` | Agent performance metrics |

### Health Check & MCP

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (shows operation mode) |
| — | `/mcp` | FastMCP Streamable HTTP endpoint |

## Database Schema

| Table | Key Columns | Description |
|-------|-------------|-------------|
| **users** | id (UUID), email, hashed_password, role | User accounts |
| **conversations** | id (UUID), user_id (FK), title, status | Chat conversations |
| **messages** | id (UUID), conversation_id (FK), role, content | Messages within conversations |
| **tickets** | id (UUID), conversation_id (FK), user_id (FK), status, priority | Support tickets |
| **escalations** | id (UUID), conversation_id (FK), ticket_id (FK), sentiment_score | Escalation records |
| **agent_runs** | id (UUID), conversation_id (FK), agent_type, duration_ms | Agent execution logs |
| **kb_articles** | id (UUID), title, content, category, is_published | Knowledge base articles |
| **kb_chunks** | id (UUID), article_id (FK), embedding (Vector(1536)) | Embedding chunks |

## AI/ML Pipeline

### Agent Graph Processing Flow

```text
User Message
       │
       ▼
  router_agent
  (Intent Classification: FAQ / Ticket / Escalation / Chitchat)
       │
       ├─── intent: faq ──────→ faq_agent
       │                        ├─ KB vector search (pgvector cosine similarity)
       │                        └─ Generate answer from search results
       │
       ├─── intent: ticket ───→ ticket_agent
       │                        ├─ Extract title, priority, category
       │                        └─ Auto-create support ticket
       │
       ├─── intent: escalation → escalation_agent
       │                         ├─ Calculate sentiment score (0.0-1.0)
       │                         └─ Set human review flag
       │
       └─── intent: chitchat ──→ chitchat_agent
                                 └─ General conversational response
       │
       ▼
   formatter
   (Final response formatting with metadata)
       │
       ▼
   Return response via SSE streaming
```

### Dual-Mode Implementation

| Component | Live Mode | Demo Mode |
|-----------|-----------|-----------|
| Intent Classification | Claude Haiku 4.5 | Regex pattern matching |
| FAQ Responses | Claude Haiku 4.5 + KB search | Template responses |
| Ticket Extraction | Claude Haiku 4.5 | Regex field extraction |
| Sentiment Analysis | Claude Haiku 4.5 (0.0-1.0) | Keyword-based analysis |
| Embedding Generation | OpenAI text-embedding-3-small | SHA-256 pseudo-embeddings |

### MCP Tool Integration

Via FastMCP 2.0, agents invoke 5 tools (mounted at `/mcp` with Streamable HTTP transport):

- **search_knowledge_base_tool** — Knowledge base search using pgvector cosine similarity
- **create_ticket** — Create support tickets
- **update_ticket** — Update ticket status and priority
- **get_support_metrics** — Aggregate dashboard statistics
- **escalate_to_human** — Create escalation to human operators

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for PostgreSQL)
- uv (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/mer-prog/agent-flow.git
cd agent-flow

# 2. Start PostgreSQL + pgvector
docker compose up -d

# 3. Configure environment variables
cp .env.example .env

# 4. Install Python dependencies
uv sync

# 5. Run database migrations
alembic upgrade head

# 6. Start the backend
uv run fastapi dev app/main.py

# 7. Start the frontend (separate terminal)
cd frontend && npm install && npm run dev
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | — |
| `JWT_SECRET` | JWT signing secret key | Yes | — |
| `ANTHROPIC_API_KEY` | Anthropic API key (for live mode) | No | — |
| `OPENAI_API_KEY` | OpenAI API key (for live mode) | No | — |
| `APP_ENV` | Runtime environment | No | `development` |
| `LOG_LEVEL` | Log level | No | `INFO` |
| `CORS_ORIGINS` | CORS allowed origins (JSON array) | No | `["http://localhost:5173"]` |

### Docker Build (Production)

```bash
docker build -t agent-flow .
docker run -p 8000:8000 --env-file .env agent-flow
```

## Testing

```bash
uv run pytest        # Run all 54 tests
uv run pytest -x     # Stop on first failure
uv run pytest -v     # Verbose output
```

| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_agents.py | 20 | Agent intent classification, sentiment analysis, ticket extraction, demo mode behavior |
| test_schemas.py | 14 | Pydantic schema validation and serialization |
| test_config.py | 8 | Configuration loading, default values, dual-mode detection |
| test_embedding.py | 6 | Embedding generation, dimensionality, demo mode SHA-256 |
| test_security.py | 6 | JWT token generation/verification, password hashing |
| **Total** | **54** | |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| LangGraph Multi-Agent | 3-stage pipeline (intent classification → specialist agent → formatter) implemented as a state machine. Shared state (AgentState TypedDict) enables loose coupling, making it straightforward to add or modify agents |
| Dual-Mode (Live/Demo) | Automatically switches based on API key availability. Developers can trial all features at zero cost, then seamlessly transition to high-accuracy mode in production |
| FastMCP Tool Integration | Agent tools (knowledge search, ticket operations, etc.) standardized via the MCP protocol. Adding or modifying tools requires no changes to agent code |
| pgvector for Vector Search | Leverages PostgreSQL's pgvector extension instead of a dedicated vector database, minimizing infrastructure complexity while enabling cosine similarity-based semantic search |
| SSE Streaming | Server-Sent Events chosen over WebSocket. For unidirectional streaming (server → client), SSE provides simpler implementation and native HTTP/2 compatibility |
| Async-First | All database operations, API handlers, and agent nodes use async/await, optimizing concurrent processing of I/O-bound LLM API calls and database queries |
| Docker Multi-Stage Build | Separates frontend build (Node.js) from backend runtime (Python), minimizing production image size |

## Running Costs

### Free Tier Operation

| Service | Plan | Monthly Cost |
|---------|------|-------------|
| Render Web Service | Free | $0 |
| Render PostgreSQL | Free | $0 |
| **Total (Demo Mode)** | | **$0** |

### Additional Costs with Live Mode (API Keys)

| Service | Pricing | Estimated Cost |
|---------|---------|---------------|
| Anthropic Claude Haiku 4.5 | Input $0.80/1M tokens, Output $4.00/1M tokens | ~$1-5/month (light usage) |
| OpenAI Embeddings (text-embedding-3-small) | $0.02/1M tokens | ~$0.01-0.10/month |
| **Total (Live Mode)** | | **~$1-5/month** |

> Demo mode requires no API keys and operates completely free of charge.

## Documentation

- [Japanese Spec (日本語仕様書)](README_AgentFlow_マルチエージェントCS_JP.md)
- [English Spec](README_AgentFlow_マルチエージェントCS_EN.md)

## Author

**[@mer-prog](https://github.com/mer-prog)**
