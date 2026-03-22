# Frontend — ComIT

React SPA на Vite. Стек: React 18, Framer Motion, TanStack Query, openapi-fetch.

## Запуск

```bash
npm ci && npm run dev
```

Vite проксирует `/api` → `VITE_API_PROXY_TARGET` и `/qmsg` → `VITE_QMSG_PROXY_TARGET`.

## Полезные команды

```bash
npm run build          # production-сборка
npm run generate:api   # перегенерировать типы из openapi/openapi.yaml
```

## Переменные окружения

| Переменная | Описание |
|-----------|---------|
| `VITE_API_PROXY_TARGET` | Backend для dev-прокси (обычно `http://127.0.0.1:8000`) |
| `VITE_QMSG_PROXY_TARGET` | QmsgCore для dev-прокси |
| `VITE_API_BASE_URL` | Base URL для production-сборки |
| `VITE_API_STATIC_FALLBACK` | `true` → использовать demo-данные вместо API |
