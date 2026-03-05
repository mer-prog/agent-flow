"""Tests for configuration and settings."""

from app.config import Settings


def test_default_demo_mode():
    s = Settings(DATABASE_URL="postgresql://localhost/test")
    assert not s.is_live_mode


def test_live_mode_requires_both_keys():
    s = Settings(
        DATABASE_URL="postgresql://localhost/test",
        ANTHROPIC_API_KEY="sk-ant-test",
        OPENAI_API_KEY="sk-test",
    )
    assert s.is_live_mode


def test_live_mode_partial_keys():
    s = Settings(
        DATABASE_URL="postgresql://localhost/test",
        ANTHROPIC_API_KEY="sk-ant-test",
    )
    assert not s.is_live_mode


def test_async_url_conversion():
    s = Settings(DATABASE_URL="postgres://user:pass@host/db")
    assert s.async_database_url.startswith("postgresql+asyncpg://")


def test_async_url_strips_sslmode():
    s = Settings(DATABASE_URL="postgres://host/db?sslmode=require")
    assert "sslmode" not in s.async_database_url


def test_needs_ssl():
    s = Settings(DATABASE_URL="postgres://host/db?sslmode=require")
    assert s.needs_ssl


def test_no_ssl_local():
    s = Settings(DATABASE_URL="postgresql://localhost/db")
    assert not s.needs_ssl


def test_sync_url_conversion():
    s = Settings(DATABASE_URL="postgres://user:pass@host/db")
    assert s.sync_database_url.startswith("postgresql+psycopg2://")
