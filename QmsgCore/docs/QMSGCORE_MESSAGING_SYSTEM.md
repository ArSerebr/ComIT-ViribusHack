# QmsgCore — Система отправки сообщений: полное описание

---

## Содержание

1. [Определения и терминология](#1-определения-и-терминология)
2. [Высокоуровневая архитектура](#2-высокоуровневая-архитектура)
3. [Технологии и библиотеки](#3-технологии-и-библиотеки)
4. [Протоколы](#4-протоколы)
5. [Модели данных и схема БД](#5-модели-данных-и-схема-бд)
6. [Алгоритмы](#6-алгоритмы)
7. [Полный жизненный цикл сообщения](#7-полный-жизненный-цикл-сообщения)
8. [Реальное время — Hub и WebSocket](#8-реальное-время--hub-и-websocket)
9. [AI-сообщения и интеграция с PulseAI](#9-ai-сообщения-и-интеграция-с-pulseai)
10. [Права доступа и безопасность](#10-права-доступа-и-безопасность)
11. [База данных — пулы и индексы](#11-база-данных--пулы-и-индексы)
12. [Конфигурация и деплой](#12-конфигурация-и-деплой)
13. [Карта файлов по ответственности](#13-карта-файлов-по-ответственности)
14. [Возможные вопросы и ответы](#14-возможные-вопросы-и-ответы)

---

## 1. Определения и терминология

| Термин | Определение |
|--------|-------------|
| **QmsgCore** | Backend-сервис на Go, реализующий групповые чаты с поддержкой реального времени и AI |
| **Group (группа)** | Именованное пространство для общения, содержащее участников и историю сообщений |
| **Member (участник)** | Пользователь, состоящий в группе. Роли: `owner`, `admin`, `member` |
| **Message (сообщение)** | Атомарная единица коммуникации. Может быть текстом, медиа, AI-запросом и т.д. |
| **MessageType** | Перечисление типов: `text`, `voice_note`, `circular_video`, `media`, `file`, `system`, `ai_request`, `ai_message` |
| **Hub** | In-memory менеджер WebSocket-соединений. Знает о всех подключённых клиентах |
| **Client** | Одно WebSocket-соединение (один браузер/устройство одного пользователя) |
| **Event** | JSON-пакет, который сервер рассылает по WebSocket при изменениях состояния |
| **PulseAI** | Внешний AI-сервис, к которому QmsgCore обращается для генерации ответов |
| **JWT** | JSON Web Token — механизм аутентификации. Алгоритм HS256 |
| **AES-GCM** | Симметричное шифрование с аутентификацией, используемое для тела сообщений |
| **DSN** | Data Source Name — строка подключения к PostgreSQL |
| **Qgmsg Protocol** | Совокупность REST-эндпоинтов и WebSocket-событий, составляющих API QmsgCore |

---

## 2. Высокоуровневая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                       Внешний мир                               │
│                                                                 │
│   Платформа (QGramm Backend)                                    │
│        │                                                        │
│        │  POST /v1/auth/token  (выдача JWT)                     │
│        ▼                                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      QmsgCore                             │  │
│  │                                                           │  │
│  │  ┌─────────────┐   ┌──────────────┐   ┌───────────────┐  │  │
│  │  │  HTTP API   │   │  WebSocket   │   │   PulseAI     │  │  │
│  │  │  (Chi)      │   │  Hub         │   │   Client      │  │  │
│  │  │  :8090      │   │  (Gorilla)   │   │   (HTTP)      │  │  │
│  │  └──────┬──────┘   └──────┬───────┘   └───────┬───────┘  │  │
│  │         │                 │                   │           │  │
│  │         └────────┬────────┘                   │           │  │
│  │                  ▼                            │           │  │
│  │          ┌───────────────┐                   │           │  │
│  │          │  Core Service │◄──────────────────┘           │  │
│  │          │  (groups.go)  │                               │  │
│  │          └───────┬───────┘                               │  │
│  │                  ▼                                       │  │
│  │          ┌───────────────┐                               │  │
│  │          │  PostgreSQL   │                               │  │
│  │          │  (pgx pool)   │                               │  │
│  │          └───────────────┘                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│   Frontend (браузер)                                            │
│        │ REST + WebSocket                                       │
└────────┼────────────────────────────────────────────────────────┘
         ▼
      QmsgCore :8090
```

### Компоненты

| Компонент | Файл | Ответственность |
|-----------|------|-----------------|
| **Entry point** | `cmd/server/main.go` | Запуск, инициализация зависимостей |
| **Config** | `internal/config/config.go` | Чтение ENV-переменных |
| **JWT Auth** | `internal/auth/jwt.go` | Подписание и верификация токенов (HS256) |
| **DB Pool** | `internal/db/postgres.go` | Настройка пула pgx |
| **Core Service** | `internal/services/core.go` | Общая логика, хелперы, валидация |
| **Group Service** | `internal/services/groups.go` | CRUD групп, участники, сообщения, реакции |
| **PulseAI Client** | `internal/services/pulse.go` | HTTP-запросы к AI, polling статуса задачи |
| **Router** | `internal/httpapi/router.go` | Определение маршрутов |
| **Handlers** | `internal/httpapi/handler.go` | Обработчики HTTP-запросов |
| **Middleware** | `internal/httpapi/middleware.go` | Извлечение и верификация JWT |
| **Hub** | `internal/realtime/hub.go` | Реестр WebSocket-соединений, рассылка событий |

---

## 3. Технологии и библиотеки

| Уровень | Технология | Версия | Для чего |
|---------|-----------|--------|----------|
| **Язык** | Go | 1.24 | Основной язык сервиса |
| **HTTP роутер** | `go-chi/chi/v5` | 5.2.1 | Маршрутизация REST-запросов |
| **CORS** | `go-chi/cors` | 1.2.1 | Разрешение кросс-доменных запросов (`*`) |
| **WebSocket** | `gorilla/websocket` | 1.5.3 | Постоянные соединения реального времени |
| **JWT** | `golang-jwt/jwt/v5` | 5.2.3 | Аутентификация через токены |
| **PostgreSQL** | `jackc/pgx/v5` | 5.7.4 | Хранение данных, пул соединений |
| **UUID** | `google/uuid` | 1.6.0 | Генерация идентификаторов |
| **Crypto** | `golang.org/x/crypto` | 0.36.0 | Дополнительные криптографические примитивы |
| **БД** | PostgreSQL | — | Хранение групп, сообщений, реакций |
| **Контейнеризация** | Docker / docker-compose | — | Запуск сервиса + PostgreSQL |

---

## 4. Протоколы

### 4.1 REST API (Qgmsg Protocol — HTTP-слой)

**Транспорт:** HTTP/1.1 (chi-router на порту 8090)
**Формат:** JSON (`Content-Type: application/json`)
**Аутентификация:** Bearer-токен в заголовке `Authorization: Bearer <token>` или query-параметр `?access_token=<token>`

#### Эндпоинты групп

| Метод | Путь | Описание | Роль |
|-------|------|----------|------|
| `POST` | `/v1/auth/token` | Выдача JWT для пользователя | Внешний backend |
| `POST` | `/v1/groups` | Создать группу | Любой авторизованный |
| `GET` | `/v1/groups` | Список групп пользователя | Member |
| `GET` | `/v1/groups/{id}` | Данные конкретной группы | Member |
| `PATCH` | `/v1/groups/{id}` | Обновить группу | Owner/Admin |
| `DELETE` | `/v1/groups/{id}` | Удалить группу | Owner |

#### Эндпоинты участников

| Метод | Путь | Описание | Роль |
|-------|------|----------|------|
| `POST` | `/v1/groups/{id}/members` | Добавить участника | Owner/Admin |
| `DELETE` | `/v1/groups/{id}/members/{userID}` | Удалить/покинуть группу | Self / Owner / Admin |

#### Эндпоинты сообщений

| Метод | Путь | Описание | Роль |
|-------|------|----------|------|
| `POST` | `/v1/groups/{id}/messages` | Отправить сообщение | Member |
| `GET` | `/v1/groups/{id}/messages` | История сообщений | Member |
| `POST` | `/v1/groups/{id}/read` | Сбросить счётчик непрочитанных | Member |

#### Эндпоинты реакций

| Метод | Путь | Описание | Роль |
|-------|------|----------|------|
| `POST` | `/v1/groups/{id}/messages/{msgID}/reactions` | Поставить реакцию | Member |
| `DELETE` | `/v1/groups/{id}/messages/{msgID}/reactions/{emoji}` | Убрать реакцию | Member |

#### Коды ответов

| Код | Значение |
|-----|----------|
| `200 OK` | Успех (GET, PATCH, DELETE) |
| `201 Created` | Ресурс создан (POST) |
| `400 Bad Request` | Некорректное тело запроса |
| `401 Unauthorized` | Токен отсутствует или истёк |
| `403 Forbidden` | Нет прав (не участник / недостаточная роль) |
| `404 Not Found` | Ресурс не существует |
| `500 Internal Server Error` | Ошибка сервера |

---

### 4.2 WebSocket-протокол (Qgmsg Protocol — реального времени)

**URL подключения:** `wss://host/v1/ws?access_token=<token>`
**Причина query-параметра:** браузеры не позволяют устанавливать заголовки при WebSocket-соединении.

#### Формат события

```json
{
  "type": "message.created",
  "timestamp": "2026-03-22T10:01:30.123Z",
  "payload": { ... }
}
```

#### Таблица событий

| Событие | Кому | Payload |
|---------|------|---------|
| `message.created` | Все участники группы | `{ "message": MessageView }` |
| `ai.thinking` | Все участники группы | `{ "group_id": "gr_..." }` |
| `reaction.updated` | Все участники группы | `{ "group_id", "message_id", "emoji", "user_id", "action": "add"\|"remove" }` |
| `group.updated` | Все участники группы | `{ "group": GroupView }` |
| `group.deleted` | Все участники группы | `{ "group_id": "gr_..." }` |
| `member.joined` | Все участники группы | `{ "group_id", "user_id" }` |
| `member.left` | Все участники группы | `{ "group_id", "user_id" }` |

#### WebSocket-параметры

| Параметр | Значение |
|----------|----------|
| Максимальный размер фрейма | 2 MB |
| Read deadline | 2 минуты |
| Ping интервал | 30 секунд |
| Write deadline | 10 секунд |
| Send-буфер на соединение | 64 сообщения |

---

### 4.3 JWT (Authentication Protocol)

**Алгоритм:** HMAC-SHA256 (HS256)
**Секрет:** Общий с QGramm Backend (`GC_JWT_SECRET`)
**Срок жизни:** 168 часов по умолчанию (7 дней)

**Claims:**

```json
{
  "uid": "uuid-пользователя",
  "sid": "uuid-сессии",
  "root": false,
  "iss": "qmsgcore",
  "sub": "uuid-пользователя",
  "iat": 1740000000,
  "exp": 1740604800,
  "nbf": 1740000000,
  "jti": "uuid-токена"
}
```

**Валидация:** Проверяется только подпись и срок жизни — без запросов в БД.

---

### 4.4 PulseAI Protocol

**Транспорт:** HTTP/1.1
**Base URL:** `GC_PULSE_BASE_URL`

#### Шаг 1 — отправка задачи

```
POST {base_url}/api/comit/chat?uid={groupID}
Content-Type: application/json

{ "message": "текст вопроса пользователя" }
```

**Ответ:**

```json
{ "task_id": "abc123" }
```

#### Шаг 2 — polling статуса

```
GET {base_url}/api/task/{taskID}
```

**Ответ (PENDING):**

```json
{ "task_id": "abc123", "status": "PENDING" }
```

**Ответ (READY):**

```json
{
  "task_id": "abc123",
  "status": "READY",
  "result": {
    "content": "Ответ AI",
    "buttons": [{ "label": "Подробнее", "action": "..." }]
  }
}
```

**Ответ (FAILED):**

```json
{ "task_id": "abc123", "status": "FAILED" }
```

**Интервал polling:** 1 секунда
**Таймаут:** 120 секунд (`GC_PULSE_TASK_TIMEOUT_SEC`)

---

## 5. Модели данных и схема БД

### 5.1 Таблица `group_chats`

```sql
CREATE TABLE group_chats (
    id              TEXT PRIMARY KEY,          -- "gr_" + UUID
    name            TEXT NOT NULL,
    avatar_url      TEXT,
    created_by_user_id UUID NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB
);

-- Автоматическое обновление updated_at
CREATE TRIGGER set_group_chats_updated_at
    BEFORE UPDATE ON group_chats
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
```

**JSON-представление (GroupView):**

```json
{
  "id": "gr_550e8400-e29b-41d4-a716-446655440000",
  "name": "Команда разработки",
  "avatar_url": "https://...",
  "created_by_user_id": "uuid",
  "created_at": "2026-03-01T12:00:00Z",
  "updated_at": "2026-03-22T09:30:00Z",
  "member_ids": ["uuid1", "uuid2"],
  "unread_count": 3
}
```

---

### 5.2 Таблица `group_members`

```sql
CREATE TABLE group_members (
    group_id        TEXT REFERENCES group_chats(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('owner','admin','member')),
    joined_at       TIMESTAMPTZ DEFAULT NOW(),
    unread_count    INTEGER DEFAULT 0,
    last_read_message_id UUID,
    PRIMARY KEY (group_id, user_id)
);

CREATE INDEX idx_group_members_user_id ON group_members(user_id);
```

---

### 5.3 Таблица `group_messages`

```sql
CREATE TABLE group_messages (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id                    TEXT REFERENCES group_chats(id) ON DELETE CASCADE,
    sender_user_id              UUID,    -- NULL для AI-сообщений
    message_type                TEXT NOT NULL CHECK (message_type IN (
                                    'text','voice_note','circular_video',
                                    'media','file','system','ai_request','ai_message'
                                )),
    -- Зашифрованное тело
    body_ciphertext             TEXT,
    body_nonce                  TEXT,
    body_tag                    TEXT,
    -- Зашифрованная цитата
    quoted_ciphertext           TEXT,
    quoted_nonce                TEXT,
    quoted_tag                  TEXT,
    -- Ссылки
    reply_to_message_id         UUID REFERENCES group_messages(id),
    forwarded_from_message_id   UUID REFERENCES group_messages(id),
    forwarded_from_group_id     TEXT REFERENCES group_chats(id),
    attachment_id               UUID,
    metadata                    JSONB,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    edited_at                   TIMESTAMPTZ,
    deleted_at                  TIMESTAMPTZ,
    report_count                INTEGER DEFAULT 0
);

CREATE INDEX idx_group_messages_group_id_created_at
    ON group_messages(group_id, created_at DESC);

CREATE INDEX idx_group_messages_sender_created_at
    ON group_messages(sender_user_id, created_at DESC);
```

**JSON-представление (MessageView):**

```json
{
  "id": "uuid",
  "group_id": "gr_...",
  "sender_user_id": "uuid",
  "message_type": "text",
  "body_ciphertext": "base64...",
  "body_nonce": "base64...",
  "body_tag": "base64...",
  "reply_to_message_id": null,
  "forwarded_from_message_id": null,
  "forwarded_from_group_id": null,
  "attachment_id": null,
  "metadata": {},
  "reactions": [
    { "emoji": "👍", "user_ids": ["uuid1", "uuid2"] }
  ],
  "created_at": "2026-03-22T10:00:00Z",
  "report_count": 0
}
```

---

### 5.4 Таблица `group_message_reactions`

```sql
CREATE TABLE group_message_reactions (
    message_id  UUID REFERENCES group_messages(id) ON DELETE CASCADE,
    emoji       TEXT NOT NULL,
    user_id     UUID NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (message_id, emoji, user_id)
);
```

---

## 6. Алгоритмы

### 6.1 Отправка сообщения (транзакционный алгоритм)

```
SendMessage(groupID, senderID, messageData):

1. Проверить: участник ли sender в группе?
   SELECT EXISTS(SELECT 1 FROM group_members WHERE group_id=$1 AND user_id=$2)
   → 403 если нет

2. Начать транзакцию (TX BEGIN)

3. Вставить сообщение:
   INSERT INTO group_messages (...) VALUES (...) RETURNING *

4. Обновить метку активности группы:
   UPDATE group_chats SET updated_at = NOW() WHERE id = $1

5. Инкрементировать unread_count всем участникам КРОМЕ отправителя:
   UPDATE group_members
   SET unread_count = unread_count + 1
   WHERE group_id = $1 AND user_id != $2

6. TX COMMIT

7. Загрузить реакции для нового сообщения (пустой список)

8. Получить список всех участников группы:
   SELECT user_id FROM group_members WHERE group_id = $1

9. Сформировать событие:
   { type: "message.created", payload: { message: MessageView } }

10. Hub.BroadcastToUsers(memberIDs, event)

RETURN MessageView (201 Created)
```

**Почему транзакция?**
Если между шагом 3 и 5 упадёт сервер — сообщение окажется в БД без обновления счётчиков. Транзакция гарантирует атомарность: либо всё произошло, либо ничего.

---

### 6.2 Пагинация истории сообщений

```
GetMessages(groupID, userID, before *time.Time, limit int):

1. Проверить членство

2. Если before == nil: before = NOW()

3. Запрос:
   SELECT * FROM group_messages
   WHERE group_id = $1
     AND created_at < $2
     AND deleted_at IS NULL
   ORDER BY created_at DESC
   LIMIT $3

4. Загрузить реакции для полученных сообщений:
   SELECT * FROM group_message_reactions
   WHERE message_id = ANY($1)

5. Объединить реакции с сообщениями

6. Реверсировать массив (DESC → ASC для UI)

RETURN []MessageView
```

**Курсорная пагинация:**
Клиент берёт `created_at` самого старого сообщения из ответа и передаёт как `?before=<timestamp>` в следующем запросе. Это устойчиво к вставке новых сообщений в отличие от OFFSET-пагинации.

---

### 6.3 Управление непрочитанными сообщениями

```
Инкремент (при получении сообщения):
  UPDATE group_members
  SET unread_count = unread_count + 1
  WHERE group_id = $1 AND user_id != $sender_id

Сброс (при вызове POST /read):
  UPDATE group_members
  SET unread_count = 0,
      last_read_message_id = (последнее сообщение в группе)
  WHERE group_id = $1 AND user_id = $2
```

---

### 6.4 Реакции — дедупликация

```
AddReaction(messageID, emoji, userID):

  INSERT INTO group_message_reactions (message_id, emoji, user_id)
  VALUES ($1, $2, $3)
  ON CONFLICT (message_id, emoji, user_id) DO NOTHING

  BroadcastToGroup: { action: "add", emoji, user_id }

RemoveReaction(messageID, emoji, userID):

  DELETE FROM group_message_reactions
  WHERE message_id = $1 AND emoji = $2 AND user_id = $3

  BroadcastToGroup: { action: "remove", emoji, user_id }
```

`ON CONFLICT DO NOTHING` — гарантирует что дважды лайкнуть невозможно даже при параллельных запросах.

---

### 6.5 Broadcast алгоритм (Hub)

```
BroadcastToUsers(userIDs []UUID, event Event):

  data = json.Marshal(event)

  for each userID in userIDs:
    mu.RLock()
    clients = hub.clients[userID]   // map[*client]struct{}
    mu.RUnlock()

    for each client in clients:
      select:
        case client.send <- data:    // неблокирующая отправка
          // успешно поставлено в очередь
        default:
          // буфер заполнен — пакет дропается
          // клиент слишком медленный
```

**Почему `default` (дроп)?**
Блокирующая отправка заблокировала бы всю рассылку. Медленный клиент не должен тормозить остальных. Клиент восстановит состояние при следующем GET /messages.

---

### 6.6 WebSocket Ping/Pong (keepalive)

```
Каждые 30 секунд от сервера:
  conn.SetWriteDeadline(now + 10s)
  conn.WriteMessage(PingMessage, nil)

Клиент отвечает Pong автоматически (браузер).

При получении Pong:
  conn.SetReadDeadline(now + 2 minutes)   // сдвиг таймаута
```

Если клиент не отвечает на Ping — соединение закрывается через 2 минуты.

---

### 6.7 AI polling алгоритм

```
HandleAIRequest(groupID, question):

  // 1. Сохранить запрос пользователя
  SaveMessage(ai_request, metadata={text: question})

  // 2. Уведомить группу (горутина)
  go func():
    BroadcastToGroup: { type: "ai.thinking" }

    // 3. Отправить запрос в PulseAI
    taskID = POST /api/comit/chat?uid={groupID} { message: question }

    // 4. Polling с timeout
    deadline = now + 120s
    for now < deadline:
      sleep(1 second)
      response = GET /api/task/{taskID}

      if response.status == "READY":
        SaveAIMessage(response.result)
        BroadcastToGroup: { type: "message.created", message: AIMessage }
        return

      if response.status == "FAILED":
        SaveAIErrorMessage()
        BroadcastToGroup: { type: "message.created", message: ErrorMessage }
        return

    // 5. Таймаут
    SaveAIErrorMessage("timeout")
    BroadcastToGroup: { type: "message.created", message: TimeoutMessage }
```

---

## 7. Полный жизненный цикл сообщения

### 7.1 Обычное текстовое сообщение

```
Пользователь A                  QmsgCore                 Пользователь B
     │                              │                           │
     │  POST /v1/groups/gr_.../     │                           │
     │  messages                    │                           │
     │  {                           │                           │
     │    message_type: "text",     │                           │
     │    body_ciphertext: "...",   │                           │
     │    body_nonce: "...",        │                           │
     │    body_tag: "..."           │                           │
     │  }                           │                           │
     │─────────────────────────────►│                           │
     │                              │                           │
     │                              │ TX BEGIN                  │
     │                              │ INSERT message            │
     │                              │ UPDATE group updated_at   │
     │                              │ UPDATE unread_counts      │
     │                              │ TX COMMIT                 │
     │                              │                           │
     │  201 Created                 │                           │
     │  { message: MessageView }    │                           │
     │◄─────────────────────────────│                           │
     │                              │                           │
     │                              │ BroadcastToUsers([A, B])  │
     │                              │──────────────────────────►│
     │                              │  WS: {                    │
     │                              │    type: "message.created"│
     │                              │    payload: { message }   │
     │                              │  }                        │
     │  (тоже получает по WS)       │                           │
     │◄─────────────────────────────│                           │
```

---

### 7.2 AI-запрос

```
Пользователь                QmsgCore                    PulseAI
     │                          │                           │
     │  POST /v1/groups/.../    │                           │
     │  messages                │                           │
     │  {                       │                           │
     │    message_type:         │                           │
     │    "ai_request",         │                           │
     │    metadata: {           │                           │
     │      text: "Вопрос?"     │                           │
     │    }                     │                           │
     │  }                       │                           │
     │─────────────────────────►│                           │
     │                          │ Сохранить ai_request      │
     │  201 Created             │                           │
     │◄─────────────────────────│                           │
     │                          │                           │
     │                          │ go func():               │
     │                          │   BroadcastToGroup:      │
     │  WS: ai.thinking         │   ai.thinking            │
     │◄─────────────────────────│                           │
     │                          │                           │
     │                          │  POST /api/comit/chat    │
     │                          │─────────────────────────►│
     │                          │  { task_id: "abc" }      │
     │                          │◄─────────────────────────│
     │                          │                           │
     │                          │  polling каждую секунду  │
     │                          │  GET /api/task/abc ──────►│
     │                          │◄──── { status: PENDING } │
     │                          │  GET /api/task/abc ──────►│
     │                          │◄──── { status: READY,   │
     │                          │        result: {...} }    │
     │                          │                           │
     │                          │ Сохранить ai_message      │
     │                          │ BroadcastToGroup          │
     │  WS: message.created     │                           │
     │  { ai_message }          │                           │
     │◄─────────────────────────│                           │
```

---

### 7.3 Реакция на сообщение

```
Пользователь                QmsgCore
     │                          │
     │  POST /messages/{id}/    │
     │  reactions               │
     │  { emoji: "👍" }          │
     │─────────────────────────►│
     │                          │ INSERT ON CONFLICT DO NOTHING
     │  200 OK                  │
     │◄─────────────────────────│
     │                          │ BroadcastToGroup:
     │  WS: reaction.updated    │ { action:"add", emoji, user_id }
     │◄─────────────────────────│
```

---

## 8. Реальное время — Hub и WebSocket

### 8.1 Структура Hub

```go
type Hub struct {
    mu      sync.RWMutex
    clients map[uuid.UUID]map[*Client]struct{}
    // uuid.UUID = user_id
    // map[*Client] = набор соединений пользователя (разные вкладки/устройства)
}

type Client struct {
    conn   *websocket.Conn
    send   chan []byte     // буфер 64 сообщения
    userID uuid.UUID
    hub    *Hub
}
```

### 8.2 Жизненный цикл соединения

```
1. GET /v1/ws?access_token=<token>
   ├── Middleware: извлечь и верифицировать JWT
   ├── Upgrade HTTP → WebSocket
   ├── Создать Client{userID, send: make(chan []byte, 64)}
   └── hub.register(client)

2. Запустить две горутины:
   ├── readPump():  читать пинги/понги, обнаруживать закрытие
   └── writePump(): отправлять из channel send, слать Ping каждые 30с

3. При закрытии соединения:
   └── hub.unregister(client): удалить из map
```

### 8.3 Потокобезопасность

- `sync.RWMutex` защищает `hub.clients`
- Читаем (поиск клиентов) → `RLock` (несколько горутин параллельно)
- Пишем (регистрация/удаление) → `Lock` (эксклюзивно)
- Отправка в `client.send` — неблокирующая (`select { default: drop }`)

---

## 9. AI-сообщения и интеграция с PulseAI

### 9.1 Как распознать AI-сообщение

| Поле | Значение |
|------|----------|
| `message_type` | `"ai_message"` |
| `sender_user_id` | `null` |
| `metadata.ai_type` | тип AI-ответа |
| `metadata.ai_content` | текст ответа |
| `metadata.ai_buttons` | интерактивные кнопки |
| `metadata.ai_error` | текст ошибки (если FAILED) |

### 9.2 Изоляция AI-запросов

- Каждый `ai_request` создаёт отдельную горутину
- Горутины независимы — несколько AI-запросов могут обрабатываться параллельно
- `groupID` передаётся как `uid` в PulseAI — изоляция контекста по группе

---

## 10. Права доступа и безопасность

### 10.1 Ролевая модель

| Действие | member | admin | owner |
|----------|--------|-------|-------|
| Читать сообщения | ✓ | ✓ | ✓ |
| Отправлять сообщения | ✓ | ✓ | ✓ |
| Ставить реакции | ✓ | ✓ | ✓ |
| Добавлять участников | — | ✓ | ✓ |
| Удалять участников | — | ✓ | ✓ |
| Обновлять группу | — | ✓ | ✓ |
| Удалить группу | — | — | ✓ |
| Покинуть группу | ✓ | ✓ | ✓ |

### 10.2 Шифрование сообщений

- Тело сообщения (`body_ciphertext`, `body_nonce`, `body_tag`) — AES-GCM
- Ключи хранятся на клиенте — сервер хранит только зашифрованный ciphertext
- QmsgCore не может читать содержимое сообщений (E2E-шифрование)
- AI-сообщения (`ai_request`) содержат plaintext в `metadata.text` — исключение из E2E

### 10.3 Проверка членства

Все операции с группой и сообщениями требуют:

```sql
SELECT EXISTS(
  SELECT 1 FROM group_members
  WHERE group_id = $1 AND user_id = $2
)
```

→ `403 Forbidden` если пользователь не участник.

---

## 11. База данных — пулы и индексы

### 11.1 Параметры пула pgx

| Параметр | Значение |
|----------|----------|
| `MaxConns` | 25 |
| `MinConns` | 3 |
| `MaxConnIdleTime` | 10 минут |
| `MaxConnLifetime` | 60 минут |
| `HealthCheckPeriod` | 30 секунд |

### 11.2 Индексы и их назначение

| Таблица | Индекс | Запросы, которые ускоряет |
|---------|--------|--------------------------|
| `group_members` | `(user_id)` | Получить все группы пользователя |
| `group_messages` | `(group_id, created_at DESC)` | История сообщений с пагинацией |
| `group_messages` | `(sender_user_id, created_at DESC)` | Сообщения конкретного пользователя |
| `group_chats` | `(updated_at DESC)` | Сортировка групп по активности |

### 11.3 Каскадные удаления

```
group_chats (удалить группу)
  → group_members (ON DELETE CASCADE)
  → group_messages (ON DELETE CASCADE)
    → group_message_reactions (ON DELETE CASCADE)
```

Удаление группы — одна операция, БД сама очистит все связанные данные.

---

## 12. Конфигурация и деплой

### 12.1 Переменные окружения

| ENV | Описание | По умолчанию |
|-----|----------|-------------|
| `GC_DATABASE_DSN` | PostgreSQL connection string | обязательно |
| `GC_JWT_SECRET` | Секрет для HS256 (должен совпадать с QGramm) | обязательно |
| `GC_SERVER_HOST` | Адрес bind | `0.0.0.0` |
| `GC_SERVER_PORT` | Порт | `8090` |
| `GC_ACCESS_TOKEN_TTL_HOURS` | Срок жизни JWT (часов) | `168` |
| `GC_PULSE_BASE_URL` | URL PulseAI-сервиса | обязательно |
| `GC_PULSE_TASK_TIMEOUT_SEC` | Таймаут polling AI (сек) | `120` |

### 12.2 HTTP Server таймауты

| Таймаут | Значение |
|---------|----------|
| `ReadHeaderTimeout` | 10 секунд |
| `ReadTimeout` | 60 секунд |
| `WriteTimeout` | 60 секунд |
| `IdleTimeout` | 90 секунд |

### 12.3 docker-compose

```yaml
services:
  postgres:
    image: postgres:16
    environment: [POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]
    volumes: [postgres_data:/var/lib/postgresql/data]

  qmsgcore:
    build: .
    ports: ["8090:8090"]
    environment:
      GC_DATABASE_DSN: postgres://...
      GC_JWT_SECRET: ...
      GC_PULSE_BASE_URL: ...
    depends_on: [postgres]
```

Миграции применяются при старте через `migrations/001_init.sql`.

---

## 13. Карта файлов по ответственности

| Файл | Что делает |
|------|-----------|
| `cmd/server/main.go` | Точка входа: читает конфиг, инициализирует БД/Hub/Сервисы/Роутер, запускает HTTP-сервер |
| `internal/config/config.go` | Загружает ENV → структура Config |
| `internal/auth/jwt.go` | `IssueToken()`, `ParseToken()` — HS256 |
| `internal/db/postgres.go` | Создаёт pgxpool.Pool с параметрами |
| `internal/services/core.go` | Общие хелперы: проверка членства, извлечение userID из контекста |
| `internal/services/groups.go` | `CreateGroup`, `SendMessage`, `GetMessages`, `AddReaction` и весь CRUD |
| `internal/services/pulse.go` | `SubmitChat()`, `PollTask()` — HTTP-клиент для PulseAI |
| `internal/httpapi/router.go` | `chi.NewRouter()` + все `r.Route(...)` |
| `internal/httpapi/handler.go` | По одной функции на каждый эндпоинт: decode JSON → вызвать сервис → encode response |
| `internal/httpapi/middleware.go` | `AuthMiddleware`: достать токен из заголовка/query → `ParseToken` → положить userID в контекст |
| `internal/realtime/hub.go` | `Hub.Register`, `Hub.Unregister`, `Hub.BroadcastToUsers`, `Client.readPump`, `Client.writePump` |
| `migrations/001_init.sql` | Полная схема БД (таблицы, индексы, триггеры) |

---

## 14. Возможные вопросы и ответы

**Q: Почему сообщения шифруются на клиенте (AES-GCM), а не на сервере?**
A: End-to-End encryption — сервер хранит только зашифрованный ciphertext и не может читать содержимое. Ключи живут только у клиентов. Это защищает сообщения даже при компрометации БД.

---

**Q: Почему AI-запросы (`ai_request`) не шифруются?**
A: AI-сервис (PulseAI) должен получить plaintext для генерации ответа. Поэтому `metadata.text` хранится в открытом виде. Это известный компромисс между E2E и AI-функциональностью.

---

**Q: Что произойдёт, если клиент медленно читает WebSocket и буфер (64 сообщения) переполнится?**
A: Пакет дропается (инструкция `default` в select). Клиент не получит событие. При следующем открытии чата он подтянет пропущенные сообщения через `GET /messages`.

---

**Q: Поддерживает ли система несколько вкладок/устройств одного пользователя?**
A: Да. Hub хранит `map[uuid.UUID]map[*Client]struct{}` — для одного `user_id` может быть несколько Client. Broadcast доставляется во все соединения пользователя.

---

**Q: Как работает пагинация истории — почему не OFFSET?**
A: OFFSET-пагинация нестабильна: если в момент загрузки второй страницы добавится новое сообщение, пользователь пропустит или увидит дублирование. Курсорная пагинация (`created_at < $before`) стабильна независимо от новых вставок.

---

**Q: Что происходит, если транзакция (`SendMessage`) упадёт на середине?**
A: Вся транзакция откатывается (ROLLBACK). Ни сообщение, ни счётчики не будут частично изменены. Клиент получит 500, пользователь увидит ошибку отправки.

---

**Q: Как PulseAI идентифицирует контекст разговора?**
A: Через `uid={groupID}` в query-параметре запроса. Это позволяет PulseAI поддерживать контекст отдельно для каждой группы.

---

**Q: Что будет, если PulseAI не ответит за 120 секунд?**
A: В группу будет сохранено и разослано сообщение типа `ai_message` с `metadata.ai_error = "timeout"`. Пользователи увидят что AI не смог обработать запрос.

---

**Q: Как сервер понимает, что WebSocket-клиент отвалился?**
A: Каждые 30 секунд сервер отправляет Ping. Клиент должен ответить Pong. При получении Pong deadline сдвигается на 2 минуты. Если Pong не приходит — read deadline истекает, соединение закрывается.

---

**Q: Может ли один пользователь поставить одну реакцию дважды?**
A: Нет. Первичный ключ таблицы `(message_id, emoji, user_id)` + `ON CONFLICT DO NOTHING` гарантируют уникальность на уровне БД.

---

**Q: Как авторизоваться во frontend?**
A: Backend-платформа (QGramm) вызывает `POST /v1/auth/token` с user_id и получает JWT. Этот токен передаётся во frontend. Frontend использует его в `Authorization: Bearer <token>` для REST и `?access_token=<token>` для WebSocket.

---

**Q: Можно ли удалить одно сообщение, не удаляя группу?**
A: Поле `deleted_at` в `group_messages` предусмотрено для soft-delete, но публичного эндпоинта удаления одного сообщения в текущей версии нет. Удаление группы каскадно удаляет все сообщения.

---

**Q: Что значит `root: true` в JWT?**
A: Флаг суперпользователя/администратора сервиса. Позволяет выполнять административные операции, обходя обычные проверки роли в группах.

---

**Q: Почему для WebSocket используется query-параметр, а не заголовок Authorization?**
A: Спецификация WebSocket не позволяет браузерам устанавливать произвольные HTTP-заголовки при установке соединения. Query-параметр — стандартный обходной путь.

---

*Документ описывает состояние системы на основе кодовой базы ветки `dev`, коммит `d3df264` (Qgmsg protocol for groups added).*
