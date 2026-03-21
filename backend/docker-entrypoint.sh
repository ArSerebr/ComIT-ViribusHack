#!/bin/sh
set -e
cd /app
alembic upgrade head
if [ "${SKIP_SEED:-}" != "1" ]; then
  python -m scripts.seed_db
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
