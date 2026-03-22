# Task Assignment MVP

Автоматический подбор участника команды под задачу. Модель использует GigaChat-эмбеддинги, пересечение навыков и текущую загрузку кандидата.

## Как работает

1. Для каждой задачи и участника строится текстовый профиль
2. Профили переводятся в эмбеддинги через GigaChat API
3. Итоговый score = semantic similarity + пересечение навыков + бонус за роль + бонус за загрузку
4. Выдаётся лучший кандидат с объяснением

## Запуск

```bash
python generate_data.py
set GIGACHAT_AUTH_KEY=your_authorization_key
python main.py --project-id P001
python main.py --project-id P001 --format json
```

## Данные

- `data/projects.json` — 100 проектов с задачами
- `data/team.json` — 18 участников с ролями и навыками

## Переменные окружения

- `GIGACHAT_AUTH_KEY` — обязательно для эмбеддингов
- `GIGACHAT_SCOPE` — по умолчанию `GIGACHAT_API_PERS`
- `GIGACHAT_EMBEDDING_MODEL` — по умолчанию `EmbeddingsGigaR`
