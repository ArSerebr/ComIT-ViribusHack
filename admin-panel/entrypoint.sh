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

exec gunicorn admin_panel.wsgi:application --bind 0.0.0.0:8001
