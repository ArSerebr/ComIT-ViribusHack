#!/bin/sh
set -e
cd /app

# Sync PostgreSQL → News/data/raw/news.csv (merge keeps static rows not in DB).
# Не блокируем старт API: при пустой БД (ещё не прогнали миграции backend) sync может упасть.
if [ -n "$DATABASE_URL" ]; then
  _url="$DATABASE_URL"
  case "$_url" in
    *+asyncpg*) _url=$(echo "$_url" | sed 's/+asyncpg//') ;;
    *+psycopg*) _url=$(echo "$_url" | sed 's/+psycopg2//;s/+psycopg//') ;;
  esac
  i=0
  while [ "$i" -lt 8 ]; do
    if python scripts/sync_from_db.py --database-url "$_url" --merge; then
      break
    fi
    i=$((i + 1))
    sleep 2
  done
fi

exec uvicorn api_server:app --host 0.0.0.0 --port 9000
