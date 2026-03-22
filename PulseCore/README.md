# PulseCore — AI-ассистент ComIT

FastAPI-сервис для AI-чата и генерации план-задач проекта. Работает асинхронно: запрос возвращает `task_id`, результат — через polling.

## API

| Метод | Endpoint | Описание |
|-------|---------|---------|
| POST | `/api/comit/chat?uid=` | Отправить сообщение → `{ task_id }` |
| POST | `/api/comit/work-plan?uid=` | Сгенерировать план задач проекта |
| GET | `/api/task/{task_id}` | Статус задачи (`PENDING / READY / FAILED`) |
| GET | `/api/status?uid=` | Прогресс активного агента |
| GET | `/api/history/{uid}` | История сообщений |
| POST | `/api/comit/execute?uid=` | Подтвердить агентское действие |
| POST | `/api/comit/cancel?uid=` | Отменить |

## Запуск

```bash
cd PulseCore && pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8091 --reload
```

```bash
docker build -t comit-pulse-core ./PulseCore
docker run --rm -p 8091:8091 -e MONGO_URL="mongodb://localhost:27017/" comit-pulse-core
```

## Переменные окружения

- `MONGO_URL` — URL MongoDB
- `DB_NAME` — имя базы (по умолчанию `agent_chat`)

Backend подключается через `PULSE_CORE_BASE_URL`. Подробный API-гайд: `docs.md`.
