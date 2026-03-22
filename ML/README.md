# ML — Сервис рекомендаций ComIT

FastAPI-сервис персонализации: рекомендации новостей и хакатонов на основе GigaChat-эмбеддингов и профиля студента.

## API

| Метод | Endpoint | Описание |
|-------|---------|---------|
| GET | `/health` | Healthcheck |
| GET | `/recommend/news?user_id=&limit=` | Рекомендации новостей |
| GET | `/recommend/events?user_id=&limit=` | Рекомендации хакатонов |
| POST | `/feedback` | Записать реакцию пользователя |

## Запуск

```bash
cd ML
pip install -e ./Projects && pip install fastapi uvicorn psycopg2-binary
uvicorn api_server:app --host 0.0.0.0 --port 9000 --reload
```

```bash
docker build -t comit-ml ./ML && docker run --rm -p 9000:9000 comit-ml
```

## Переменные окружения

- `GIGACHAT_AUTH_KEY` — ключ для эмбеддингов (без него падбэк на локальный генератор)
- `DATABASE_URL` — нужен для `scripts/sync_from_db.py`

## Подпроекты

| Папка | Что делает |
|-------|-----------|
| `News/` | Персонализация ленты новостей с учётом свежести и авторитетности источника |
| `Projects/` | Рекомендации проектов и возможностей (пакет `student_recsys`) |
| `Hack/` | Альтернативный пайплайн рекомендаций хакатонов |
| `TODO_candidate_search/` | Подбор участника команды под конкретную задачу |

Детали по каждому — в их `README.md`.
