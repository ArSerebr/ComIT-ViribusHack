#!/bin/sh
set -e
cd /app

echo "Waiting for database to be ready..."
until alembic upgrade head; do
  echo "Database not ready yet, retrying in 3s..."
  sleep 3
done
if [ "${SKIP_SEED:-}" != "1" ]; then
  python -m scripts.seed_db
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
