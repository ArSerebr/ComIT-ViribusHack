<div align="center">

<br/>

<img src="https://img.shields.io/badge/ComIT-010101?style=for-the-badge&logoColor=white" height="42" alt="ComIT" />

<h3>Платформа для студентов нового поколения</h3>

<p>Командные проекты · Хакатоны · Новости · AI-ассистент · Групповые чаты</p>

<br/>

[![Открыть сайт](https://img.shields.io/badge/Открыть_сайт-f43f5e?style=for-the-badge&logoColor=white)](https://comit.robofirst.ru/)
[![Figma](https://img.shields.io/badge/Figma-a855f7?style=for-the-badge&logo=figma&logoColor=white)](https://www.figma.com/design/4ferZ0muDwZe9Qh8iPRtiO/%D0%A5%D0%90%D0%9A%D0%90%D0%A2%D0%9E%D0%9D?node-id=0-1&p=f&t=xwQ1RNWlXpxzycK2-0)
[![Презентация](https://img.shields.io/badge/Презентация-6366f1?style=for-the-badge&logo=googleslides&logoColor=white)](https://docs.google.com/presentation/d/1NHAbkkhbvQBN345mIWRH_dMzHc0q7kk20pPSl6MKEZY/edit?slide=id.p#slide=id.p)

<br/><br/>

</div>

---

## Стек

<div align="center">

| Слой | Технологии |
|:----:|:-----------|
| **Frontend** | ![React](https://img.shields.io/badge/React_18-1c1c1e?style=flat-square&logo=react&logoColor=61dafb) ![Vite](https://img.shields.io/badge/Vite-1c1c1e?style=flat-square&logo=vite&logoColor=a78bfa) ![Framer](https://img.shields.io/badge/Framer_Motion-1c1c1e?style=flat-square&logo=framer&logoColor=white) |
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-1c1c1e?style=flat-square&logo=fastapi&logoColor=00d084) ![Python](https://img.shields.io/badge/Python_3.12-1c1c1e?style=flat-square&logo=python&logoColor=ffd43b) ![Postgres](https://img.shields.io/badge/PostgreSQL_16-1c1c1e?style=flat-square&logo=postgresql&logoColor=4169e1) ![Redis](https://img.shields.io/badge/Redis_7-1c1c1e?style=flat-square&logo=redis&logoColor=ff4438) |
| **Чаты** | ![Go](https://img.shields.io/badge/Go_1.24-1c1c1e?style=flat-square&logo=go&logoColor=00add8) ![WebSocket](https://img.shields.io/badge/WebSocket-1c1c1e?style=flat-square&logoColor=white) |
| **AI** | ![FastAPI](https://img.shields.io/badge/PulseCore-1c1c1e?style=flat-square&logo=openai&logoColor=a855f7) ![MongoDB](https://img.shields.io/badge/MongoDB-1c1c1e?style=flat-square&logo=mongodb&logoColor=47a248) |
| **ML** | ![GigaChat](https://img.shields.io/badge/GigaChat_Embeddings-1c1c1e?style=flat-square&logoColor=white) ![Sklearn](https://img.shields.io/badge/scikit--learn-1c1c1e?style=flat-square&logo=scikitlearn&logoColor=f7931e) |
| **Инфра** | ![Docker](https://img.shields.io/badge/Docker_Compose-1c1c1e?style=flat-square&logo=docker&logoColor=2496ed) ![Drone](https://img.shields.io/badge/Drone_CI-1c1c1e?style=flat-square&logo=drone&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-1c1c1e?style=flat-square&logo=nginx&logoColor=009639) |

</div>

---

## Архитектура

```
                     ┌─────────────────────────────────────────────┐
                     │              backend  (FastAPI)              │
    frontend ───────▶│                                              │◀──── frontend_analytics
                     │  /api/auth   /api/projects   /api/pulse      │
                     │  /api/news   /api/groupchat  /api/recommend  │
                     └──────┬──────────┬───────┬──────────┬────────┘
                            │          │       │          │
                     ┌──────▼──┐  ┌────▼───┐  │    ┌─────▼──────┐
                     │PostgreSQL│  │ Redis  │  │    │  ML API    │
                     └──────▲──┘  └────────┘  │    │ (port 9000)│
                            │                 │    └────────────┘
              ┌─────────────┤      ┌──────────▼──────────────┐
              │             │      │       PulseCore          │
    hackathon-│             │      │   AI-агент · MongoDB     │
    parser    │             │      └──────────────────────────┘
              │      ┌──────┴──────────────┐
              │      │     QmsgCore (Go)    │
              └─────▶│  WebSocket · Groups  │
                     └─────────────────────┘
```

---

## Быстрый старт

```bash
# 1. Настрой окружение
cp .env.example .env

# 2. Подними весь стек одной командой
docker compose --profile core up -d --build
```

| Сервис | URL |
|--------|-----|
| 🌐 Frontend | http://localhost:8080 |
| 📖 Backend API (Swagger) | http://localhost:8000/docs |
| 🛠 Admin panel | http://localhost:8010/admin/ |
| 📊 Analytics | http://localhost:8081 |

---

## Структура репозитория

```
ComIT-ViribusHack/
├── backend/              FastAPI backend · миграции Alembic · seed
├── frontend/             React SPA · основной интерфейс
├── frontend_analytics/   Аналитика университетов
├── admin-panel/          Django admin
├── hackathon-parser/     Парсер хакатонов и IT-новостей → PostgreSQL
├── ML/                   Сервис персонализированных рекомендаций
│   ├── News/             Рекомендации новостей (freshness + relevance)
│   ├── Projects/         Рекомендации проектов (student_recsys)
│   ├── Hack/             Рекомендации хакатонов
│   └── TODO_candidate_search/  Подбор кандидатов под задачи
├── PulseCore/            AI-агент · RAG · пайплайны · MongoDB
├── QmsgCore/             Групповые чаты на Go
├── openapi/              OpenAPI spec (авто-экспорт при старте)
└── deploy/               Nginx-конфиг · прод-инструкции
```

---

## Локальная разработка

<details>
<summary><b>Backend</b></summary>

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head && python -m scripts.seed_db
uvicorn app.main:app --reload
```

</details>

<details>
<summary><b>Frontend</b></summary>

```bash
cd frontend
npm ci && npm run dev

# Перегенерировать TypeScript-типы из OpenAPI
npm run generate:api
```

Vite проксирует `/api` → `VITE_API_PROXY_TARGET` и `/qmsg` → `VITE_QMSG_PROXY_TARGET`.

</details>

<details>
<summary><b>ML / PulseCore / QmsgCore</b></summary>

```bash
# ML
cd ML && pip install -e ./Projects fastapi uvicorn psycopg2-binary
uvicorn api_server:app --port 9000

# PulseCore
cd PulseCore && pip install -r requirements.txt
uvicorn main:app --port 8091

# QmsgCore
cd QmsgCore/backend && go mod download && go run ./cmd/server/main.go
```

</details>

---

## Ключевые переменные окружения

| Переменная | Описание |
|-----------|---------|
| `DATABASE_URL` · `REDIS_URL` | Подключение к PostgreSQL и Redis |
| `JWT_SECRET` | Должен совпадать с `GC_JWT_SECRET` в QmsgCore |
| `PULSE_CORE_BASE_URL` | URL AI-агента PulseCore |
| `QMSG_CORE_BASE_URL` | URL сервиса групповых чатов |
| `ML_SERVICE_URL` | URL ML-сервиса рекомендаций |
| `VITE_API_BASE_URL` | Задать **до** `docker compose build frontend` |
| `GIGACHAT_AUTH_KEY` | Ключ для GigaChat embeddings |

---

<div align="center">

**ComIT · ViribusHack 2025**

</div>
