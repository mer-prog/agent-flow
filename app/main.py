import pathlib
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, chat, conversations, escalations, knowledge, stats, tickets
from app.config import settings
from app.core.logging import setup_logging
from app.mcp.server import mcp

import structlog

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    mode = "live" if settings.is_live_mode else "demo"
    structlog.get_logger().info("AgentFlow starting", mode=mode, env=settings.APP_ENV)
    yield
    structlog.get_logger().info("AgentFlow shutting down")


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
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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


# Serve frontend static files in production
_static_dir = pathlib.Path(__file__).parent / "static"
if _static_dir.is_dir():
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
