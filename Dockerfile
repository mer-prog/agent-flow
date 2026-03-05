# Stage 1: Build React frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Python backend
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY alembic.ini ./
COPY alembic/ alembic/
COPY app/ app/
COPY scripts/ scripts/

# Copy built frontend into app/static for FastAPI to serve
COPY --from=frontend-build /app/frontend/dist app/static/

# Copy startup script
COPY start.sh ./
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
