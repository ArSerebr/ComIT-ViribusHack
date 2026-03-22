#!/bin/sh
set -e

cd /app

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if not User.objects.filter(username=email).exists():
    User.objects.create_superuser(
        username=email,
        email=email,
        password=password,
    )
PY
fi

# --timeout: иначе при «пустых» TCP-пробах / медленном клиенте sync-воркер ловит WORKER TIMEOUT (по умолчанию 30s).
# --workers: второй воркер подхватывает запросы, пока первый ждёт сокет.
exec gunicorn admin_panel.wsgi:application \
  --bind 0.0.0.0:8001 \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile -
