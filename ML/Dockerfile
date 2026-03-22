FROM python:3.12-slim

WORKDIR /app

COPY . .

# ML/Projects — рекомендации проектов
RUN pip install --no-cache-dir -e ./Projects

# Общие зависимости для News, TODO_candidate_search
RUN pip install --no-cache-dir requests

EXPOSE 9000

# Контейнер живёт для docker exec (скрипты, обучение)
CMD ["sleep", "infinity"]
