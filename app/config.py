from pydantic_settings import BaseSettings, SettingsConfigDict


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


settings = Settings()
