# PulseAI — Frontend Integration Guide

Документация для фронтенд-разработчика. Описывает все API-эндпоинты, форматы данных и паттерн интеграции чата.

---

## Base URL

```
http://chat.droidje-cloud.ru
```

При локальной разработке: `http://localhost:8083`

---

## Идентификация пользователя

Каждый запрос требует параметр `uid` — строковый идентификатор пользователя, который **генерирует и хранит фронтенд**.

```js
let uid = localStorage.getItem('uid');
if (!uid) {
  uid = crypto.randomUUID();
  localStorage.setItem('uid', uid);
}
```

`uid` передаётся как query-параметр (`?uid=...`) во все запросы.

---

## Архитектура обработки запросов

Обработка каждого сообщения **асинхронная**:

```
1. POST /api/comit/chat       → получить task_id
2. GET  /api/task/{task_id}   → поллить каждые ~1s до status == "READY" | "FAILED"
3. Отобразить result
```

Параллельно с шагом 2 можно поллить `/api/status?uid=...` для отображения прогресс-индикатора.

---

## Классификация запросов

Бэкенд автоматически определяет тип входящего сообщения и выбирает нужный pipeline:

| Тип | Описание | Что вернёт `result` |
|-----|----------|---------------------|
| `question` | Вопрос об учёбе, курсах, платформе | Текстовый ответ |
| `search` | Поиск контента по платформе | Текстовый ответ + source-кнопки |
| `task` | Действие на платформе (запись на курс и т.п.) | Объект с планом + action-кнопки подтверждения |
| `other` | Оффтоп / непонятный запрос | Текстовый ответ |

Фронтенд не передаёт тип — только текст сообщения. Классификация происходит на бэкенде.

---

## Эндпоинты

### POST `/api/comit/chat`

Отправить сообщение пользователя.

**Query:** `uid` (обязательный)

**Body:**
```json
{
  "message": "Запиши меня на курс по Python"
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Немедленно начни поллинг задачи.

---

### GET `/api/task/{task_id}`

Получить статус и результат задачи.

**Пока обрабатывается (`PENDING`):**
```json
{
  "task_id": "550e8400-...",
  "status": "PENDING"
}
```

**Готово (`READY`):**
```json
{
  "task_id": "550e8400-...",
  "status": "READY",
  "result": { ... }
}
```

**Ошибка (`FAILED`):**
```json
{
  "task_id": "550e8400-...",
  "status": "FAILED",
  "result": { "error": "описание ошибки" }
}
```

> При `FAILED` поле `result` присутствует. При `PENDING` — `result` отсутствует.

---

### GET `/api/status`

Текущий статус выполнения задачи для данного пользователя (прогресс-индикатор).

**Query:** `uid` (обязательный)

**Response:**
```json
{
  "model": "SearchAgent",
  "status": "Выполняю поиск на платформе",
  "statusColor": "#C62741",
  "progress": 40
}
```

**Idle (нет активной задачи):**
```json
{
  "model": "Multi-Agent",
  "status": "Ожидание",
  "statusColor": "#3CF0F0",
  "progress": 0
}
```

| Поле | Тип | Описание |
|------|-----|----------|
| `model` | string | Название активного агента |
| `status` | string | Человекочитаемый статус (RU) |
| `statusColor` | string | HEX-цвет для визуализации |
| `progress` | number | 0–100 |

**Цвета и статусы агентов:**

| Агент | Цвет | Текст статуса |
|-------|------|---------------|
| RequestClassifier | `#2444B6` | Анализирую запрос |
| ConversationAgent | `#aa42bd` | Вызываю LLM |
| TaskSetupAgent    | `#67c0d8` | Формулирую задачу |
| UserAgent         | `#743bc5` | Выполняю задание |
| PlannerAgent      | `#ff9800` | Записываю план |
| SearchAgent       | `#C62741` | Выполняю поиск на платформе |
| SearchResultsAgent| `#C5520F` | Обрабатываю результаты |
| READY             | `#4caf50` | Печатает... |

---

### GET `/api/history/{uid}`

История сообщений пользователя (загружай при инициализации чата).

**Response:**
```json
[
  {
    "role": "user",
    "content": "Есть ли курсы по машинному обучению?",
    "buttons": [],
    "created_at": "2026-03-22T10:15:00"
  },
  {
    "role": "ai",
    "content": "Да, вот что нашёл...",
    "buttons": [
      { "label": "Курс: Введение в ML", "type": "course", "url": "/courses/intro-ml" }
    ],
    "created_at": "2026-03-22T10:15:03"
  }
]
```

Отсортировано по `created_at` по возрастанию.

---

### POST `/api/comit/execute`

Подтвердить выполнение задачи (пользователь нажал «Запустить агента»).

**Query:** `uid` (обязательный). Body не нужен.

**Response:**
```json
{
  "status": "ok",
  "message": "Готово. Выполнено: enroll_course."
}
```

**Ошибка если нет pending-задачи:**
```json
{ "detail": "No pending task" }
```
HTTP 400.

---

### POST `/api/comit/cancel`

Отменить задачу (пользователь нажал «Отмена»).

**Query:** `uid` (обязательный). Body не нужен.

**Response:**
```json
{
  "status": "cancelled",
  "message": "Задача отменена."
}
```

---

### GET `/api/tokens`

Заглушка биллинга (пока не используется по-настоящему).

**Query:** `uid` (обязательный)

**Response:**
```json
{
  "tokens": 15,
  "cost": 0
}
```

---

## Структура `result`

`result` из `/api/task/{task_id}` имеет два формата в зависимости от типа запроса.

---

### Формат A — текстовый ответ

Для типов `question`, `search`, `other`.

```json
{
  "role": "ai",
  "content": "Курс по Python длится 6 недель.",
  "buttons": []
}
```

При типе `search` — `buttons` содержит массив source-объектов:

```json
{
  "role": "ai",
  "content": "По запросу нашёл следующие материалы:",
  "buttons": [
    { "label": "Курс: Введение в Python", "type": "course", "url": "/courses/python-intro" },
    { "label": "Статья: Основы алгоритмов",  "type": "article", "url": "/articles/algorithms-101" }
  ]
}
```

Source-кнопки — ссылки для навигации по платформе. Открывай по полю `url`.

---

### Формат B — агентская задача

Для типа `task`. Требует подтверждения от пользователя.

```json
{
  "role": "ai",
  "content": {
    "explanation": "Вот что планирую сделать:\n1. Записать тебя на курс «Python с нуля»\n2. Открыть страницу курса",
    "to_show": [
      { "action": "open_course_page", "params": { "course_id": "python-intro" } },
      { "action": "enroll_course",    "params": { "course_id": "python-intro" } }
    ]
  },
  "buttons": ["Запустить агента", "Отмена"]
}
```

| Поле | Тип | Описание |
|------|-----|----------|
| `content.explanation` | string | Текст для показа пользователю |
| `content.to_show` | array | Список планируемых UI-действий (для отображения) |
| `buttons` | string[] | Всегда `["Запустить агента", "Отмена"]` |

После выбора пользователя:
- «Запустить агента» → `POST /api/comit/execute?uid=...`
- «Отмена» → `POST /api/comit/cancel?uid=...`

---

## Шпаргалка по кнопкам

| Ситуация | `buttons` | Как обрабатывать |
|----------|-----------|-----------------|
| Обычный ответ / вопрос | `[]` | Кнопок нет |
| Результаты поиска | `[{ label, type, url }, ...]` | Открыть `url` |
| Агентская задача | `["Запустить агента", "Отмена"]` | POST execute / cancel |

Как отличить source-кнопки от action-кнопок:
```js
if (typeof buttons[0] === 'object') {
  // source-кнопки: { label, type, url }
} else {
  // action-кнопки: строки "Запустить агента" / "Отмена"
}
```

---

## Пример полной интеграции (JS)

```js
const BASE = 'http://chat.droidje-cloud.ru';

// uid — инициализация
let uid = localStorage.getItem('uid') || (() => {
  const id = crypto.randomUUID();
  localStorage.setItem('uid', id);
  return id;
})();

// ── Отправить сообщение ──────────────────────────────────────────
async function sendMessage(text) {
  const res = await fetch(`${BASE}/api/comit/chat?uid=${uid}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text }),
  });
  const { task_id } = await res.json();
  return task_id;
}

// ── Поллинг задачи ───────────────────────────────────────────────
async function pollTask(task_id, timeoutMs = 120_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    await sleep(1000);
    const res = await fetch(`${BASE}/api/task/${task_id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.status === 'READY')  return data.result;
    if (data.status === 'FAILED') throw new Error(data.result?.error || 'Unknown error');
    // PENDING → продолжаем
  }
  throw new Error('Timeout');
}

// ── Поллинг статуса ──────────────────────────────────────────────
function startStatusPolling(onUpdate) {
  const id = setInterval(async () => {
    try {
      const res = await fetch(`${BASE}/api/status?uid=${uid}`);
      onUpdate(await res.json()); // { model, status, statusColor, progress }
    } catch {}
  }, 1000);
  return () => clearInterval(id);
}

// ── Рендер result ────────────────────────────────────────────────
function renderResult(result) {
  const { content, buttons } = result;

  if (typeof content === 'string') {
    showAiMessage(content);

    if (buttons.length && typeof buttons[0] === 'object') {
      // source-кнопки (поиск): { label, type, url }
      showSourceButtons(buttons);
    }

  } else if (typeof content === 'object') {
    // агентская задача — нужно подтверждение
    showAiMessage(content.explanation);
    showActionButtons(['Запустить агента', 'Отмена'], handleActionButton);
  }
}

// ── Action-кнопки ────────────────────────────────────────────────
async function handleActionButton(label) {
  const endpoint = label === 'Запустить агента' ? 'execute' : 'cancel';
  const res = await fetch(`${BASE}/api/comit/${endpoint}?uid=${uid}`, { method: 'POST' });
  const data = await res.json();
  showAiMessage(data.message);
}

// ── Полный flow ──────────────────────────────────────────────────
async function handleUserInput(text) {
  showUserMessage(text);

  const task_id = await sendMessage(text);
  const stopStatus = startStatusPolling(updateStatusBar);

  try {
    const result = await pollTask(task_id);
    renderResult(result);
  } catch (err) {
    showError(err.message);
  } finally {
    stopStatus();
    resetStatusBar();
  }
}

// ── Загрузка истории ─────────────────────────────────────────────
async function loadHistory() {
  const res = await fetch(`${BASE}/api/history/${uid}`);
  const messages = await res.json();
  messages.forEach(m => {
    if (m.role === 'user') showUserMessage(m.content);
    else renderResult(m);
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
```

---

## Типичные ошибки

| Ситуация | Причина | Что делать |
|----------|---------|------------|
| `404` на `/api/task/{id}` | Неверный или устаревший `task_id` | Показать ошибку пользователю |
| `400` на `/api/comit/execute` | Нет pending-задачи для `uid` | Игнорировать или обновить UI |
| `status: "FAILED"` | Ошибка агентского pipeline | Показать `result.error`, разблокировать ввод |
| Поллинг без ответа >2 мин | Зависание бэкенда | Показать fallback-сообщение, разблокировать ввод |
| `content` — объект вместо строки | Тип запроса = `task` | Рендерить `content.explanation`, показать action-кнопки |
