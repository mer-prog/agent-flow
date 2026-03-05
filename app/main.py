from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, conversations, escalations, knowledge, stats, tickets
from app.config import settings
from app.core.logging import setup_logging
from app.mcp.server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    yield


app = FastAPI(
    title="AgentFlow",
    description="Multi-agent customer support platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(tickets.router)
app.include_router(escalations.router)
app.include_router(knowledge.router)
app.include_router(stats.router)

# Mount MCP server on /mcp with Streamable HTTP transport
app.mount("/mcp", mcp.http_app())


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": "live" if settings.is_live_mode else "demo",
    }
