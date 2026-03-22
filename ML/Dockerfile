FROM python:3.12-slim

WORKDIR /app

COPY . .

# ML/Projects — рекомендации проектов
RUN pip install --no-cache-dir -e ./Projects

# Общие зависимости для News, TODO_candidate_search
RUN pip install --no-cache-dir requests

# API server + sync script
RUN pip install --no-cache-dir uvicorn fastapi psycopg2-binary

EXPOSE 9000

# API server (порт 9000)
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "9000"]
