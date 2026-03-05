#!/bin/bash

echo "Running database migrations..."
uv run alembic upgrade head || { echo "Migration failed!"; exit 1; }

echo "Seeding database..."
uv run python scripts/seed.py || echo "Seed skipped or failed (continuing anyway)"

echo "Starting AgentFlow..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
