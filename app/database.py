import ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


def _make_connect_args() -> dict:
    """Build connect_args for asyncpg. Adds SSL context for Neon/cloud PG."""
    if not settings.needs_ssl:
        return {}
    ctx = ssl.create_default_context()
    return {"ssl": ctx}


engine = create_async_engine(
    settings.async_database_url,
    echo=settings.APP_ENV == "development",
    connect_args=_make_connect_args(),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
