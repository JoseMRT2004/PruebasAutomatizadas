#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export APP_DB_PATH="${APP_DB_PATH:-gestion.db}"
exec uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
