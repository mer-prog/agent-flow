#!/bin/bash
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Seeding database..."
uv run python scripts/seed.py || echo "Seed skipped (may already exist)"

echo "Starting AgentFlow..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
