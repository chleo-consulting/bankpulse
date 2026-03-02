#!/bin/bash
set -e

echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Starting uvicorn on port ${PORT:-8000}..."
exec uv run uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
