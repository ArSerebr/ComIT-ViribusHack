# QmsgCore — Групповые чаты ComIT

Go-сервис для групповых чатов: REST + WebSocket, хранение в PostgreSQL, AI-ответы через PulseCore.

## Стек

Go 1.24 · chi v5 · gorilla/websocket · pgx v5 · JWT HS256

## API

```
GET  /healthz
POST /v1/auth/token              — выпуск access token по uid

# Под Authorization: Bearer <token>
GET|POST|PATCH|DELETE /v1/groups/...
GET|POST /v1/groups/{id}/messages
POST /v1/groups/{id}/messages/{id}/reactions
GET  /v1/ws?access_token=...     — WebSocket
```

## Запуск

```bash
cd QmsgCore/backend && go mod download
GC_DATABASE_DSN=postgres://... GC_JWT_SECRET=... go run ./cmd/server/main.go
```

```bash
docker build -t comit-qmsg-core ./QmsgCore/backend
docker run --rm -p 8090:8090 -e GC_DATABASE_DSN="..." -e GC_JWT_SECRET="..." comit-qmsg-core
```

При старте автоматически применяются миграции из `migrations/`.

## Ключевые переменные окружения

- `GC_DATABASE_DSN` — PostgreSQL DSN (обязательно)
- `GC_JWT_SECRET` — должен совпадать с `JWT_SECRET` основного backend
- `GC_PULSE_BASE_URL` — URL PulseCore для AI-ответов
- `GC_SERVER_PORT` — порт (по умолчанию `8090`)

Backend подключается через `QMSG_CORE_BASE_URL`. Детали протокола: `docs/QMSGCORE_MESSAGING_SYSTEM.md`.
