from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Mount MCP server on /mcp with Streamable HTTP transport
app.mount("/mcp", mcp.http_app())


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": "live" if settings.is_live_mode else "demo",
    }
