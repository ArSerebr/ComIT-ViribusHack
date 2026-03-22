# QmsgCore

QmsgCore — Go-сервис групповых чатов ComIT (REST + WebSocket) с хранением в PostgreSQL и интеграцией с PulseCore для AI-ответов внутри групп.

## Назначение

Сервис реализует:

- выпуск JWT-токенов для chat-клиента,
- CRUD групп,
- управление участниками и ролями,
- отправку/чтение сообщений,
- реакции и репорты сообщений,
- real-time доставку через WebSocket,
- AI-ответы в группу через PulseCore.

## Технологии

- Go 1.24
- chi v5 (HTTP router)
- gorilla/websocket
- pgx v5 (PostgreSQL)
- JWT HS256

## Структура

- `backend/cmd/server/main.go` — запуск сервера
- `backend/internal/config` — ENV-конфиг
- `backend/internal/httpapi` — роутер, middleware, handlers
- `backend/internal/services` — доменная логика (groups/messages/pulse)
- `backend/internal/realtime` — websocket hub
- `backend/internal/db` — пул и миграции
- `backend/migrations/001_init.sql` — инициализация схемы
- `docs/` — расширенная документация и интеграционный гайд

## Базовые endpoint'ы

Публичный:

- `GET /healthz`
- `POST /v1/auth/token` — выпуск access token по `uid`

Под `Authorization: Bearer <token>`:

- `GET|POST|PATCH|DELETE /v1/groups...`
- `GET|POST|DELETE /v1/groups/{groupID}/members...`
- `GET|POST /v1/groups/{groupID}/messages...`
- `POST|DELETE /v1/groups/{groupID}/messages/{messageID}/reactions...`
- `POST /v1/groups/{groupID}/messages/{messageID}/report`
- `POST /v1/groups/{groupID}/read`
- `GET /v1/ws` — WebSocket (`?access_token=...` в браузере)

## Переменные окружения

- `GC_DATABASE_DSN` — PostgreSQL DSN (обязательно)
- `GC_JWT_SECRET` — секрет подписи JWT (обязательно)
- `GC_JWT_ISSUER` — issuer (`qgramm-backend` по умолчанию)
- `GC_ACCESS_TOKEN_TTL_HOURS` — срок жизни токена (default `168`)
- `GC_SERVER_HOST` — host (`0.0.0.0`)
- `GC_SERVER_PORT` — port (`8090`)
- `GC_PULSE_BASE_URL` — URL PulseCore
- `GC_PULSE_TASK_TIMEOUT_SEC` — timeout polling PulseCore

## Локальный запуск

```bash
cd QmsgCore/backend
go mod download

# Пример ENV
# GC_DATABASE_DSN=postgres://postgres:postgres@localhost:5432/comit
# GC_JWT_SECRET=change-me
# GC_PULSE_BASE_URL=http://localhost:8091

go run ./cmd/server/main.go
```

Сервис при старте применяет SQL-миграции из `migrations/`.

## Docker

```bash
docker build -t comit-qmsg-core ./QmsgCore/backend
docker run --rm -p 8090:8090 \
  -e GC_DATABASE_DSN="postgres://..." \
  -e GC_JWT_SECRET="..." \
  -e GC_PULSE_BASE_URL="http://host.docker.internal:8091" \
  comit-qmsg-core
```

## Интеграция с backend

В основном backend интеграция вынесена в:

- `backend/app/modules/groupchat/client.py`

Она используется для:

- выдачи токена QmsgCore для пользователя,
- создания групп проектов,
- добавления участников,
- удаления групп при удалении проекта.

`backend` передаёт базовый URL через `QMSG_CORE_BASE_URL`.

## Документация

- Полное описание протокола и моделей: `docs/QMSGCORE_MESSAGING_SYSTEM.md`
- Практический гайд интеграции: `docs/integration.md`
