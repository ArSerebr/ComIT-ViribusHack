# PulseAI — API Integration Guide

Документация для фронтенд-разработчика. Описывает как интегрировать чат-интерфейс с бэкендом PulseAI.

---

## Base URL

```
http://localhost:8083
```

> При деплое — заменить на актуальный хост. 

---

## Идентификация пользователя (uid)

Каждый пользователь идентифицируется по `uid` — произвольной строке, которую **генерирует и хранит фронтенд/основной бэкенд**.
Рекомендуется сохранять в `localStorage`, чтобы сессия сохранялась при перезагрузке.

```js
// Пример инициализации
let uid = localStorage.getItem('uid');
if (!uid) {
  uid = crypto.randomUUID(); // или любой другой uuid-генератор
  localStorage.setItem('uid', uid);
}
```

`uid` передаётся как query-параметр во все запросы.

---

## Общий flow чата

Обработка сообщения — **асинхронная**. Схема взаимодействия:

```
1. POST /api/comit/chat   → получить task_id
2. GET  /api/task/{task_id}    → поллить до status == "READY"
3. Показать result из ответа
```

Параллельно можно поллить `/api/status` для отображения прогресс-бара (отображает агента который выполняет таск).

---

## Эндпоинты

### 1. Отправить сообщение

```
POST /api/comit/chat?uid={uid}
Content-Type: application/json
```

**Body:**
```json
{
  "message": "Текст сообщения пользователя"
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Сохрани `task_id` и начни поллинг.

---

### 2. Поллинг задачи

```
GET /api/task/{task_id}
```

**Response пока задача выполняется:**
```json
{
  "task_id": "550e8400-...",
  "status": "PENDING"
}
```

**Response когда готово (`status == "READY"`):**
```json
{
  "task_id": "550e8400-...",
  "status": "READY",
  "result": { ... }  // см. структуру result ниже
}
```

**Response при ошибке:**
```json
{
  "task_id": "550e8400-...",
  "status": "FAILED",
  "result": { "error": "описание ошибки" }
}
```

Рекомендуемый интервал поллинга: **700ms**.

---

### 3. Структура `result`

`result` зависит от типа запроса пользователя. Возможны три варианта:

---

#### Вариант A — обычный ответ (вопрос / разговор / поиск)

`content` — строка с текстом ответа.
`buttons` — пустой массив **или** массив source-кнопок (только при поиске).

```json
{
  "role": "ai",
  "content": "Курс по ML длится 8 недель и ведётся преподавателем Ивановым А.С.",
  "buttons": []
}
```

**Пример с source-кнопками (результат поиска):**

```json
{
  "role": "ai",
  "content": "По вашему запросу нашёл следующие материалы...",
  "buttons": [
    { "label": "Курс: Введение в машинное обучение", "type": "course", "url": "/courses/intro-ml" },
    { "label": "Событие: Хакатон ML Weekend #3",     "type": "event",  "url": "/events/hackathon-ml-3" }
  ]
}
```

Source-кнопки — ссылки на материалы платформы. Открывай по `url`.

---

#### Вариант B — задача (агентский режим)

`content` — **объект**, не строка.
`buttons` — массив с двумя action-кнопками: `"Запустить агента"` и `"Отмена"`.

```json
{
  "role": "ai",
  "content": {
    "explanation": "Я проанализировал задачу. Вот что планирую сделать:\n1. Записать тебя на курс...",
    "to_show": [
      { "action": "enroll_course", "course_id": "intro-ml" }
    ]
  },
  "buttons": ["Запустить агента", "Отмена"]
}
```

- `explanation` — текст для отображения пользователю (что агент собирается сделать)
- `to_show` — массив действий на фронтенде (можно отобразить как список шагов)

**Пользователь должен подтвердить или отменить задачу.** После его выбора отправь один из запросов:

```
POST /api/comit/execute?uid={uid}   // Пользователь нажал "Запустить агента"
POST /api/comit/cancel?uid={uid}    // Пользователь нажал "Отмена"
```

Оба запроса не требуют body. Оба возвращают `{"status": "ok"|"cancelled", "message": "..."}` — текст для отображения в чате.

---

### 4. Статус агента (прогресс-бар)

```
GET /api/status?uid={uid}
```

**Response:**
```json
{
  "model": "SearchAgent",
  "status": "Ищу по платформе",
  "statusColor": "#2485B6",
  "progress": 60
}
```

| Поле | Описание |
|------|----------|
| `model` | Название активного агента |
| `status` | Текст для отображения (на русском) |
| `statusColor` | HEX-цвет для визуализации агента |
| `progress` | Прогресс от 0 до 100 |

Рекомендуемый интервал поллинга: **700ms**, только пока идёт обработка.

**Цвета агентов:**

| Агент | Цвет | Статус |
|-------|------|--------|
| RequestClassifier | `#2485B6` | Анализирую запрос |
| ConversationAgent | `#4caf50` | Отвечаю на вопрос |
| TaskSetupAgent    | `#2196f3` | Формулирую задачу |
| UserAgent         | `#9c27b0` | Выполняю действие |
| PlannerAgent      | `#ff9800` | Планирую шаги |
| SearchAgent       | `#2485B6` | Ищу по платформе |
| SearchResultsAgent| `#4caf50` | Обрабатываю результаты |

---

### 5. История сообщений

```
GET /api/history/{uid}
```

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
    "content": "Да, есть курс «Введение в машинное обучение»...",
    "buttons": [
      { "label": "Курс: Введение в машинное обучение", "type": "course", "url": "/courses/intro-ml" }
    ],
    "created_at": "2026-03-22T10:15:03"
  }
]
```

Загружай при инициализации чата, чтобы восстановить историю после перезагрузки страницы.

---

## Полный пример интеграции (JS)

```js
const BASE_URL = 'http://localhost:8083';

// ── UID ──────────────────────────────────────────────────────────
let uid = localStorage.getItem('uid');
if (!uid) {
  uid = crypto.randomUUID();
  localStorage.setItem('uid', uid);
}

// ── Отправить сообщение ──────────────────────────────────────────
async function sendMessage(text) {
  const res = await fetch(`${BASE_URL}/api/comit/chat?uid=${uid}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text }),
  });
  const { task_id } = await res.json();
  return task_id;
}

// ── Поллинг задачи ───────────────────────────────────────────────
async function pollTask(task_id) {
  while (true) {
    await sleep(700);
    const res = await fetch(`${BASE_URL}/api/task/${task_id}`);
    const data = await res.json();

    if (data.status === 'READY')  return data.result;
    if (data.status === 'FAILED') throw new Error(data.result?.error || 'Unknown error');
    // PENDING → продолжаем поллинг
  }
}

// ── Поллинг статуса (пока задача идёт) ──────────────────────────
async function pollStatus(onUpdate) {
  const interval = setInterval(async () => {
    const res = await fetch(`${BASE_URL}/api/status?uid=${uid}`);
    const data = await res.json();
    onUpdate(data); // { model, status, statusColor, progress }
  }, 700);
  return () => clearInterval(interval); // вернуть функцию остановки
}

// ── Рендер результата ────────────────────────────────────────────
function renderResult(result) {
  const { content, buttons } = result;

  if (typeof content === 'string') {
    // Вариант A: обычный ответ или поиск
    showMessage(content);
    if (buttons.length > 0 && typeof buttons[0] === 'object') {
      // Source-кнопки из поиска
      showSourceButtons(buttons); // { label, type, url }
    }

  } else if (typeof content === 'object') {
    // Вариант B: задача — требует подтверждения
    showMessage(content.explanation);
    showActionButtons(buttons); // ["Запустить агента", "Отмена"]
  }
}

// ── Обработка action-кнопок ──────────────────────────────────────
async function onActionButton(label) {
  if (label === 'Запустить агента') {
    const res = await fetch(`${BASE_URL}/api/comit/execute?uid=${uid}`, { method: 'POST' });
    const data = await res.json();
    showMessage(data.message);
  } else if (label === 'Отмена') {
    const res = await fetch(`${BASE_URL}/api/comit/cancel?uid=${uid}`, { method: 'POST' });
    const data = await res.json();
    showMessage(data.message);
  }
}

// ── Загрузка истории ─────────────────────────────────────────────
async function loadHistory() {
  const res = await fetch(`${BASE_URL}/api/history/${uid}`);
  const messages = await res.json();
  messages.forEach(msg => renderResult(msg));
}

// ── Полный flow ──────────────────────────────────────────────────
async function handleUserInput(text) {
  showMessage(text, 'user');

  const task_id = await sendMessage(text);
  const stopStatus = await pollStatus(updateStatusBar);

  try {
    const result = await pollTask(task_id);
    renderResult(result);
  } finally {
    stopStatus();
    clearStatusBar();
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
```

---

## Типы кнопок — шпаргалка

| Ситуация | Тип `buttons[i]` | Действие |
|----------|-----------------|----------|
| Обычный ответ | `[]` | кнопок нет |
| Поиск по платформе | `{ label, type, url }` | открыть ссылку `url` |
| Агентская задача | `"Запустить агента"` / `"Отмена"` | POST execute / cancel |

---

## Типичные ошибки

| Ситуация | Что делать |
|----------|------------|
| `404` на `/api/task/{id}` | task_id неверный или задача удалена |
| `400` на `/api/comit/execute` | нет pending-задачи для этого uid (уже выполнена или не было) |
| `status: "FAILED"` | показать пользователю сообщение об ошибке, не блокировать ввод |
| Долгий поллинг без ответа | ставь таймаут ~60 сек, показывай fallback-сообщение |
