import re

from pydantic_settings import BaseSettings, SettingsConfigDict


def _strip_param(url: str, param: str) -> str:
    """Remove a query parameter from a URL."""
    url = re.sub(rf"([?&]){param}=[^&]*&?", r"\1", url)
    return url.rstrip("?&")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://agentflow:agentflow@localhost:5432/agentflow"

    # JWT
    JWT_SECRET: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM (optional — omit for demo mode)
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    @property
    def is_live_mode(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY and self.OPENAI_API_KEY)

    @property
    def async_database_url(self) -> str:
        """DATABASE_URL normalized for asyncpg.

        - Fixes scheme to postgresql+asyncpg://
        - REMOVES sslmode (asyncpg doesn't support it; SSL is passed via connect_args)
        - REMOVES channel_binding (unsupported by asyncpg)
        """
        url = self.DATABASE_URL
        # Fix scheme
        if url.startswith("postgres://"):
            url = "postgresql+asyncpg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]
        # Remove sslmode and channel_binding — asyncpg doesn't support either
        url = _strip_param(url, "sslmode")
        url = _strip_param(url, "channel_binding")
        return url

    @property
    def needs_ssl(self) -> bool:
        """Whether the original DATABASE_URL requested SSL (i.e. Neon / cloud PG)."""
        return "sslmode=" in self.DATABASE_URL

    @property
    def sync_database_url(self) -> str:
        """DATABASE_URL normalized for psycopg2 (sync).

        - Fixes scheme to postgresql+psycopg2://
        - Keeps sslmode=require as-is (psycopg2 supports it)
        - Removes channel_binding=require (not always supported)
        """
        url = self.DATABASE_URL
        # Fix scheme
        if url.startswith("postgres://"):
            url = "postgresql+psycopg2://" + url[len("postgres://"):]
        elif url.startswith("postgresql+asyncpg://"):
            url = "postgresql+psycopg2://" + url[len("postgresql+asyncpg://"):]
        elif url.startswith("postgresql://"):
            url = "postgresql+psycopg2://" + url[len("postgresql://"):]
        # Remove channel_binding
        url = _strip_param(url, "channel_binding")
        return url


settings = Settings()
