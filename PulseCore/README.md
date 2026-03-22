# PulseCore

PulseCore — отдельный FastAPI-сервис для асинхронной обработки сообщений ComIT-ассистента и генерации проектных work-plan задач.

## Назначение

Сервис принимает запрос пользователя, создаёт асинхронную задачу (`task_id`), выполняет пайплайн агентов в фоне и отдаёт результат через polling.

Ключевые сценарии:

- диалоговый режим (`/api/comit/chat`),
- агентский режим с подтверждением (`execute`/`cancel`),
- поиск по платформе (RAG-пайплайн),
- генерация плана задач проекта (`/api/comit/work-plan`),
- хранение истории сообщений и статуса агента.

## Технологии

- Python 3.12
- FastAPI + Uvicorn
- MongoDB (состояние, задачи, история)

## Структура

- `main.py` — точка входа FastAPI
- `config.py` — конфиг подключения к Mongo
- `routes/` — HTTP API (`chat`, `work-plan`, `task`, `status`, `history`, `tokens`)
- `agents/` — реестр и промпты агентов
- `pipelines/` — бизнес-пайплайны (`comit_agent_pipeline`, `comit_search_pipeline`, `comit_work_plan_pipeline`)
- `state/` — менеджер состояния/задач и контекста
- `services/` — интеграции LLM/RAG-поиска
- `db/` — Mongo-клиент
- `static/` — простая HTML-страница на `/`

## API

### 1. Чат и агентский режим

- `POST /api/comit/chat?uid=<user_id>`
  - body: `{ "message": "..." }`
  - response: `{ "task_id": "..." }`
- `POST /api/comit/execute?uid=<user_id>`
- `POST /api/comit/cancel?uid=<user_id>`

### 2. Work plan

- `POST /api/comit/work-plan?uid=<user_id>`
  - body: `project_title`, `project_description`, `project_deadline`, `project_id_hint`
  - response: `{ "task_id": "..." }`

### 3. Polling и UI-данные

- `GET /api/task/{task_id}` — статус задачи (`PENDING` / `READY` / `FAILED`)
- `GET /api/status?uid=<user_id>` — прогресс активного агента
- `GET /api/history/{uid}` — история сообщений
- `GET /api/tokens?uid=<user_id>` — текущая заглушка биллинга

## Переменные окружения

- `MONGO_URL` — URL MongoDB (`mongodb://...`)
- `DB_NAME` — имя БД (в коде по умолчанию `agent_chat`)

## Локальный запуск

```bash
cd PulseCore
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8091 --reload
```

Проверка:

- `GET http://localhost:8091/` — отдаётся `static/index.html`
- `GET http://localhost:8091/api/status?uid=test-user`

## Docker

```bash
docker build -t comit-pulse-core ./PulseCore
docker run --rm -p 8091:8091 -e MONGO_URL="mongodb://localhost:27017/" comit-pulse-core
```

## Интеграция с основным backend

Основной backend обращается к PulseCore через `backend/app/modules/pulse/client.py`:

- отправка сообщения в чат,
- polling статуса задачи,
- получение истории,
- execute/cancel,
- генерация project work plan.

URL интеграции задаётся переменной `PULSE_CORE_BASE_URL` в backend.

## Примечания

- `task_id` возвращается сразу; фактический результат получается через polling.
- Для долгих операций фронту нужно запрашивать `/api/status` и `/api/task/{task_id}`.
- Подробный API-гайд и форматы payload: `docs.md`.
