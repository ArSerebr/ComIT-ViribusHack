FROM python:3.12-slim

WORKDIR /app

COPY . .

# ML/Projects — рекомендации проектов
RUN pip install --no-cache-dir -e ./Projects

# Общие зависимости для News, TODO_candidate_search
RUN pip install --no-cache-dir requests

# API server + sync script
RUN pip install --no-cache-dir uvicorn fastapi psycopg2-binary

RUN sed -i 's/\r$//' docker-entrypoint.sh && chmod +x docker-entrypoint.sh

EXPOSE 9000

ENTRYPOINT ["./docker-entrypoint.sh"]
