"""Shared LLM client singletons with timeout configuration."""

from __future__ import annotations

from functools import lru_cache

from app.config import settings

LLM_TIMEOUT = 30  # seconds


@lru_cache(maxsize=1)
def get_llm(max_tokens: int = 300) -> object:
    """Get a shared ChatAnthropic client instance."""
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model="claude-haiku-4-5-20241022",
        api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=max_tokens,
        timeout=LLM_TIMEOUT,
    )
