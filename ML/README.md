# ML

`ML/` — подсистема рекомендаций ComIT.

Включает продовый API (`api_server.py`) и отдельные R&D-подпроекты (News / Projects / Hack / TODO_candidate_search).

## Что делает ML API

FastAPI-сервис (`api_server.py`) предоставляет:

- `GET /health`
- `GET /recommend/news?user_id=<id>&limit=<n>`
- `GET /recommend/events?user_id=<id>&limit=<n>`
- `POST /feedback` — запись реакции пользователя

API используется основным backend через `backend/app/modules/recommendations/ml_client.py`.

## Структура каталога

- `api_server.py` — вход в ML HTTP API
- `Dockerfile` — контейнеризация сервиса (`uvicorn`, порт `9000`)
- `tests/test_api_smoke.py` — smoke-тест API
- `scripts/sync_from_db.py` — синхронизация новостей из PostgreSQL в `News/data/raw/news.csv`
- `News/` — рекомендательная модель для новостей
- `Projects/` — модель рекомендаций проектов/возможностей
- `Hack/` — альтернативный пайплайн рекомендаций
- `TODO_candidate_search/` — модуль подбора кандидатов по задачам

## Локальный запуск ML API

```bash
cd ML
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -e ./Projects
pip install requests fastapi uvicorn psycopg2-binary
uvicorn api_server:app --host 0.0.0.0 --port 9000 --reload
```

Проверка:

```bash
curl http://localhost:9000/health
```

## Docker

```bash
docker build -t comit-ml ./ML
docker run --rm -p 9000:9000 comit-ml
```

## Переменные окружения

- `GIGACHAT_AUTH_KEY` — ключ для GigaChat embeddings (если используется)
- `GIGACHAT_SCOPE` — scope (опционально)
- `GIGACHAT_EMBEDDING_MODEL` — модель embeddings (опционально)
- `GIGACHAT_VERIFY_SSL` — проверка SSL (опционально)
- `GIGACHAT_TIMEOUT_SECONDS` — timeout запросов к GigaChat (опционально)
- `DATABASE_URL` — нужен для `scripts/sync_from_db.py`

## Тестирование

```bash
python -m pytest ML/tests/test_api_smoke.py -v
```

## Кратко по подпроектам

### `News/`

- персонализация ленты новостей,
- датасеты в `News/data/raw/*`,
- ранжирование по релевантности/свежести,
- инструкции: `News/README.md`.

### `Projects/`

- генерация и обучение модели рекомендации проектов,
- пакет `student_recsys` в `Projects/src/`,
- скрипты генерации/обучения в `Projects/scripts/`,
- инструкции: `Projects/README.md`.

### `Hack/`

- альтернативная ветка рекомендательной модели,
- аналогичная структура `src/`, `scripts/`, `config/`,
- инструкции: `Hack/README.md`.

### `TODO_candidate_search/`

- подбор кандидатов под задачи,
- локальный запуск через `main.py`,
- отдельный README: `TODO_candidate_search/README.md`.

## Интеграция с backend

`backend` ожидает ML endpoint по `ML_SERVICE_URL` (обычно `http://ml:9000` в Docker-сети).

Для новостей/ивентов backend может запрашивать рекомендации и отправлять feedback по реакциям пользователей.
