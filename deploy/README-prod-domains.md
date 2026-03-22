# Прод: домены, HTTPS, `.env` на сервере

Порты на **хосте** (как в `docker-compose`): `8000` API, `8080` главный фронт, `8010` admin-panel, `8081` analytics. Nginx на 80/443 проксирует на эти порты.

## 1. DNS

У регистратора для зоны `robofirst.ru` (или где лежит `comit.robofirst.ru`):

| Запись | Тип | Значение |
|--------|-----|----------|
| `comit` | A | IP сервера |
| `api.comit` | A | тот же IP |
| `admin.comit` | A | тот же IP |
| `analytics.comit` | A | тот же IP |

(Или CNAME, если так принято в вашей DNS.)

## 2. Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Docker-порты слушают на `127.0.0.1` или `0.0.0.0` — снаружи в интернет лучше открыть только **80/443**; порты 8000/8080/8010/8081 не обязательно торчать наружу, если весь трафик идёт через nginx на том же хосте.

## 3. Let's Encrypt (один сертификат на все поддомены)

Поставить nginx-конфиг сначала **только HTTP** (блок `listen 443` временно закомментировать) или использовать standalone — проще поставить заготовку из `deploy/nginx-comit.conf`, затем:

```bash
sudo mkdir -p /var/www/certbot
sudo certbot certonly --webroot -w /var/www/certbot \
  -d comit.robofirst.ru \
  -d api.comit.robofirst.ru \
  -d admin.comit.robofirst.ru \
  -d analytics.comit.robofirst.ru \
  --email YOUR@EMAIL --agree-tos --non-interactive
```

Если уже есть nginx с `location /.well-known` — можно:

```bash
sudo certbot --nginx \
  -d comit.robofirst.ru \
  -d api.comit.robofirst.ru \
  -d admin.comit.robofirst.ru \
  -d analytics.comit.robofirst.ru
```

Каталог сертификата обычно: `/etc/letsencrypt/live/comit.robofirst.ru/` (первое имя в `-d`).

Автообновление:

```bash
sudo certbot renew --dry-run
# cron/systemd timer у certbot обычно уже есть
```

## 4. Nginx

```bash
sudo cp /path/to/repo/deploy/nginx-comit.conf /etc/nginx/sites-available/comit
sudo ln -sf /etc/nginx/sites-available/comit /etc/nginx/sites-enabled/comit
sudo nginx -t && sudo systemctl reload nginx
```

Проверка: `curl -I https://api.comit.robofirst.ru/health`

## 5. `.env` на сервере (Drone: `drone-configs/.../env`)

Минимум для согласованности с доменами и портами:

```env
# Порты публикации на хост (как в compose)
BACKEND_PUBLISH_PORT=8000
FRONTEND_PORT=8080
ADMIN_PANEL_PORT=8010
FRONTEND_ANALYTICS_PORT=8081

# Фронт собирается с полным URL API (без слэша в конце)
VITE_API_BASE_URL=https://api.comit.robofirst.ru

# Django: разрешённые хосты для admin
DJANGO_ALLOWED_HOSTS=admin.comit.robofirst.ru,127.0.0.1,localhost

# Локальный DSN для скриптов на хосте (если используете); в контейнерах DSN задаёт compose
DATABASE_URL=postgresql+asyncpg://postgres:ВАШ_ПАРОЛЬ@localhost:5432/viribus
```

Важно:

- **`VITE_API_BASE_URL`** должен быть задан **до** `docker compose build frontend` — иначе SPA уйдёт на неверный API. После смены — пересборка образа `frontend` (новый деплой).
- **`POSTGRES_*` и пароль в `DATABASE_URL`** — как у вас в проде (`viribus` и т.д.), главное **совпадение** с томом Postgres.
- **JWT_SECRET**, пароли админки — свои сильные значения.

## 6. CORS / cookie

Backend в `main.py` сейчас `allow_origins=["*"]` — для прод можно сузить до `https://comit.robofirst.ru` и `https://analytics.comit.robofirst.ru`. Если позже включите cookie с `Secure` — нужен HTTPS на том же сайте (у вас уже будет).

## 7. Чеклист после деплоя

1. DNS резолвится на IP сервера.
2. `docker compose ps` — контейнеры up, порты 8000/8080/8010/8081 на хосте.
3. С хоста: `curl -s http://127.0.0.1:8000/health`.
4. Через nginx: `curl -s https://api.comit.robofirst.ru/health`.
5. Открыть в браузере `https://comit.robofirst.ru` и проверить запросы к API в DevTools → Network (должен быть `https://api.comit.robofirst.ru/...`).
