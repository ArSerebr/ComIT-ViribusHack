# Group Chat Service — Integration Guide

This document is written for an agent or developer integrating the Group Chat service
into an existing platform that already has its own users, authentication, and frontend.

---

## What This Service Does

The Group Chat service is a standalone backend that adds multi-participant group
conversations to your platform. It handles:

- Group CRUD (create, rename, delete)
- Member management (add, remove, roles)
- Message storage and delivery (text, media references, AI requests)
- Real-time push via WebSocket
- PulseAI integration (async AI responses inside groups)

It does **not** manage users, names, authentication, or file uploads — those stay on
your platform.

---

## Architecture

```
Your Platform Backend
  │
  ├── POST /v1/auth/token  ──►  Group Chat Service  ──►  returns JWT
  │         (uid)
  │
  └── returns JWT to your frontend

Your Platform Frontend
  │
  ├── REST calls with JWT  ──►  Group Chat Service
  └── WebSocket with JWT   ──►  Group Chat Service (real-time events)
```

The Group Chat service connects only to its own PostgreSQL database.
It does not call back into your platform — all coupling is one-directional.

---

## Authentication Flow

The Group Chat service uses its own JWT (HS256, same secret you configure).
Your platform is responsible for issuing these tokens to your users.

### Step 1 — Your backend issues a Group Chat token

Call this from your **backend** (server-to-server), not from the frontend:

```
POST /v1/auth/token
Content-Type: application/json

{ "uid": "<your platform's user UUID>" }
```

Response:
```json
{ "access_token": "eyJhbGci..." }
```

The `uid` must be a valid UUID. It is the identity the Group Chat service uses
for all subsequent operations (message authorship, membership, permissions).

### Step 2 — Your backend passes the token to your frontend

Include the `access_token` in your page's initial data, session, or a dedicated
endpoint your frontend fetches after login. Never expose your backend-to-backend
call to the browser.

### Step 3 — Your frontend uses the token

Pass it as a header on all REST calls:
```
Authorization: Bearer <access_token>
```

Or as a query parameter for WebSocket (browsers cannot set headers on WS):
```
wss://your-groupchat-host/v1/ws?access_token=<access_token>
```

### Token lifetime

Configured by `GC_ACCESS_TOKEN_TTL_HOURS` (default: 168 h = 7 days).
Re-issue a new token on your platform's session refresh.

---

## Name Resolution

The Group Chat service stores and returns only UUIDs — it has no concept of
display names. Your platform must resolve UIDs to names.

**Pattern:**
1. After loading group members (`GET /v1/groups/{id}/members`), you receive a list
   of `user_id` UUIDs.
2. Pass those UUIDs to your platform's user lookup API to get names/avatars.
3. Render names in your UI.

The same applies to `sender_user_id` in messages — look it up in your user store.
`sender_user_id` is `null` for AI-generated messages.

---

## REST API Reference

Base path: your deployed Group Chat host (e.g. `https://groupchat.yourplatform.com`).

All endpoints except `/healthz` and `/v1/auth/token` require:
```
Authorization: Bearer <access_token>
```

---

### Health

```
GET /healthz
```
No auth. Returns `{ "status": "ok", "service": "qgramm-groupchat" }`.
Use for container health checks.

---

### Token

```
POST /v1/auth/token
```
No auth. Called from your backend only.

**Request:**
```json
{ "uid": "550e8400-e29b-41d4-a716-446655440000" }
```

**Response 200:**
```json
{ "access_token": "eyJhbGci..." }
```

---

### Groups

#### Create group
```
POST /v1/groups
```
The caller becomes the owner and the first member.

**Request:**
```json
{ "name": "Team Alpha" }
```

**Response 201:** `GroupView`

---

#### List groups
```
GET /v1/groups
```
Returns all groups the authenticated user belongs to, newest first.

**Response 200:** `GroupView[]`

---

#### Get group
```
GET /v1/groups/{groupID}
```
Returns `403` if the user is not a member.

**Response 200:** `GroupView`

---

#### Update group
```
PATCH /v1/groups/{groupID}
```
Requires `owner` or `admin` role.

**Request:** (all fields optional)
```json
{ "name": "New Name", "avatar_url": "https://..." }
```

**Response 200:** Updated `GroupView`

---

#### Delete group
```
DELETE /v1/groups/{groupID}
```
Requires `owner` role. Deletes all messages and members.

**Response 200:** `{ "ok": true }`

---

### Members

#### List members
```
GET /v1/groups/{groupID}/members
```
Any member may call this.

**Response 200:**
```json
[
  { "user_id": "<uuid>", "role": "owner",  "joined_at": "2026-03-22T10:00:00Z" },
  { "user_id": "<uuid>", "role": "member", "joined_at": "2026-03-22T10:01:00Z" }
]
```

Roles: `owner` · `admin` · `member`

---

#### Add member
```
POST /v1/groups/{groupID}/members
```
Requires `owner` or `admin` role.

**Request:**
```json
{ "user_id": "<uuid>" }
```

**Response 200:** `{ "ok": true }`

Broadcasts `member.joined` event to all current members via WebSocket.

---

#### Remove member / Leave group
```
DELETE /v1/groups/{groupID}/members/{userID}
```
- Owner/admin may remove anyone.
- Any member may remove themselves (leave).

**Response 200:** `{ "ok": true }`

Broadcasts `member.left` event.

---

### Messages

#### Fetch history
```
GET /v1/groups/{groupID}/messages?limit=100&before=<RFC3339>
```

| Param    | Default | Notes |
|----------|---------|-------|
| `limit`  | 100     | Max 200 |
| `before` | –       | RFC 3339 timestamp, exclusive. Use `created_at` of oldest loaded message for pagination. |

Returns messages oldest→newest (already reversed for display).

**Response 200:** `MessageView[]`

---

#### Send message
```
POST /v1/groups/{groupID}/messages
```

**Request fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `message_type` | yes | See types below |
| `body_ciphertext` | for `text` | Ciphertext (or plaintext if not encrypting) |
| `body_nonce` | for `text` | AES-GCM nonce (base64), or empty string |
| `body_tag` | for `text` | AES-GCM tag (base64), or empty string |
| `quoted_ciphertext` | no | Quoted message body |
| `quoted_nonce` | no | |
| `quoted_tag` | no | |
| `reply_to_message_id` | no | UUID of message being replied to |
| `forwarded_from_message_id` | no | UUID of original message |
| `forwarded_from_group_id` | no | Group ID of original message |
| `attachment_id` | no | UUID of pre-uploaded attachment |
| `metadata` | no | Arbitrary JSON object |

**Message types:**

| Type | Notes |
|------|-------|
| `text` | Text message. `body_ciphertext` required. |
| `voice_note` | Audio. `attachment_id` required. |
| `circular_video` | Video note. `attachment_id` required. |
| `media` | Image or video. `attachment_id` required. |
| `file` | File. `attachment_id` required. |
| `system` | System notice. Use `metadata` for content. |
| `ai_request` | Triggers PulseAI. See AI section. |

**Response 201:** `MessageView` (the sent message, immediately)

The message is also broadcast to all group members via WebSocket `message.created`.

---

#### Add reaction
```
POST /v1/groups/{groupID}/messages/{messageID}/reactions
```

**Request:**
```json
{ "emoji": "👍" }
```

**Response 200:** `{ "ok": true }`

Broadcasts `reaction.updated` with `action: "add"`.

---

#### Remove reaction
```
DELETE /v1/groups/{groupID}/messages/{messageID}/reactions/{emoji}
```

**Response 200:** `{ "ok": true }`

Broadcasts `reaction.updated` with `action: "remove"`.

---

#### Report message
```
POST /v1/groups/{groupID}/messages/{messageID}/report
```

**Request:**
```json
{ "reason": "spam", "note": "optional comment" }
```

Valid reasons: `spam` · `insult` · `virus` · `scam` · `other`

**Response 201:** `{ "ok": true }`

Increments `report_count` on the message. Moderation logic is left to your platform.

---

#### Mark as read
```
POST /v1/groups/{groupID}/read
```
Resets `unread_count` for this user in this group.

**Request (optional):**
```json
{ "last_read_message_id": "<uuid>" }
```

If body is omitted or `last_read_message_id` is not set, the unread counter is
reset to 0 without recording a specific message.

**Response 200:** `{ "ok": true }`

Call this whenever the user opens a group or scrolls to the bottom.

---

## WebSocket

### Connect

```
GET /v1/ws
Upgrade: websocket
```

Auth via query param (required for browser WebSocket API):
```
wss://your-groupchat-host/v1/ws?access_token=<token>
```

Or via header (for non-browser clients):
```
Authorization: Bearer <token>
```

The connection is per-user. If the same user connects from multiple tabs/devices,
events are delivered to all connections.

### Sending from client

The server accepts arbitrary JSON from the client but currently ignores it.
Reserved for future use (e.g. typing indicators). Send an empty ping if needed.

### Event envelope

Every pushed event has this shape:

```json
{
  "type":      "message.created",
  "timestamp": "2026-03-22T10:01:30Z",
  "payload":   { … }
}
```

### Event types

| `type` | `payload` | When |
|--------|-----------|------|
| `message.created` | `{ "message": MessageView }` | New message (user or AI) sent to any group the user belongs to |
| `ai.thinking` | `{ "group_id": "gr_…" }` | PulseAI started processing an `ai_request` |
| `reaction.updated` | `{ "group_id", "message_id", "emoji", "user_id", "action": "add"\|"remove" }` | Reaction added or removed |
| `group.updated` | `{ "group": GroupView }` | Group name or avatar changed |
| `group.deleted` | `{ "group_id": "gr_…" }` | Group was deleted |
| `member.joined` | `{ "group_id": "gr_…", "user_id": "<uuid>" }` | Member added to a group |
| `member.left` | `{ "group_id": "gr_…", "user_id": "<uuid>" }` | Member removed or left |

**Important:** `message.created` fires for **all** groups the user is in, not just
the currently open one. Your frontend should check `message.group_id` and update
unread counters for groups that are not currently visible.

---

## PulseAI Integration

When a message with `message_type: "ai_request"` is sent:

1. The request message is saved and returned immediately (201).
2. `ai.thinking` is broadcast to all group members.
3. A background goroutine calls PulseAI (`POST /api/comit/chat`).
4. The result is polled (`GET /api/task/{id}`) until `READY` or `FAILED`.
5. An `ai_message` is saved with `sender_user_id: null` and broadcast via
   `message.created`.

**Sending an AI request:**
```json
{
  "message_type": "ai_request",
  "metadata": {
    "text": "What Python courses are available?"
  }
}
```

**AI response message shape** (`message_type: "ai_message"`):
```json
{
  "sender_user_id": null,
  "message_type": "ai_message",
  "metadata": {
    "ai_type":    "response",
    "ai_content": "Here are the available Python courses…",
    "ai_buttons": [ … ],
    "ai_error":   null
  }
}
```

`ai_type` values: `"response"` · `"error"`

When `ai_type` is `"error"`, show `metadata.ai_error` to the user.

Agent mode (task type with execute/cancel) is **not supported**.

---

## Data Structures

### GroupView

```json
{
  "id":                 "gr_550e8400-e29b-41d4-a716-446655440000",
  "name":               "Team Alpha",
  "avatar_url":         "https://…",
  "created_by_user_id": "<uuid>",
  "created_at":         "2026-03-22T10:00:00Z",
  "updated_at":         "2026-03-22T10:01:00Z",
  "member_ids":         ["<uuid>", "<uuid>"],
  "unread_count":       3
}
```

Group IDs always start with `gr_` to distinguish them from direct-chat conversation
IDs on other services.

### MessageView

```json
{
  "id":                        "<uuid>",
  "group_id":                  "gr_…",
  "sender_user_id":            "<uuid>",
  "message_type":              "text",
  "body_ciphertext":           "…",
  "body_nonce":                "…",
  "body_tag":                  "…",
  "quoted_ciphertext":         "…",
  "quoted_nonce":              "…",
  "quoted_tag":                "…",
  "reply_to_message_id":       "<uuid>",
  "forwarded_from_message_id": "<uuid>",
  "forwarded_from_group_id":   "gr_…",
  "attachment_id":             "<uuid>",
  "metadata":                  {},
  "reactions":                 [{ "emoji": "👍", "user_ids": ["<uuid>"] }],
  "created_at":                "2026-03-22T10:01:30Z",
  "report_count":              0
}
```

- `sender_user_id` is `null` for `ai_message` type.
- `reactions` is always an array (empty if no reactions).
- `body_ciphertext` / `body_nonce` / `body_tag` are empty strings for non-text types.

---

## Error Responses

All errors return:
```json
{ "error": "human-readable description" }
```

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Bad request / validation error |
| 401 | Missing or invalid token |
| 403 | Insufficient permissions (not a member, wrong role) |
| 404 | Group or message not found |
| 500 | Internal server error |

---

## Deployment

### Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GC_ENV` | no | `development` | Runtime label |
| `GC_SERVER_HOST` | no | `0.0.0.0` | Bind address |
| `GC_SERVER_PORT` | no | `8090` | Bind port |
| `GC_DATABASE_DSN` | **yes** | – | PostgreSQL DSN |
| `GC_JWT_SECRET` | **yes** | – | Secret for signing tokens. Keep private. |
| `GC_JWT_ISSUER` | no | `qgramm-backend` | JWT issuer claim |
| `GC_ACCESS_TOKEN_TTL_HOURS` | no | `168` | Token lifetime in hours |
| `GC_PULSE_BASE_URL` | no | `http://chat.droidje-cloud.ru` | PulseAI base URL |
| `GC_PULSE_TASK_TIMEOUT_SEC` | no | `120` | PulseAI polling timeout |

### Docker

```bash
cd groupchat/backend
cp .env.example .env
# Set GC_DATABASE_DSN and GC_JWT_SECRET
docker compose up -d
```

The service runs database migrations automatically on startup.

### Database

The service creates four tables in your PostgreSQL database on first start:
`group_chats`, `group_members`, `group_messages`, `group_message_reactions`.
These are fully additive — no existing tables are modified.

---

## Integration Checklist

### Backend
- [ ] `GC_JWT_SECRET` is set to a long random string and stored securely
- [ ] `GC_DATABASE_DSN` points to your PostgreSQL instance
- [ ] Add an internal endpoint on your backend: accepts the authenticated user's
      session, calls `POST /v1/auth/token` with the user's UUID, returns the
      `access_token` to the frontend
- [ ] Token endpoint is **not** publicly accessible (server-to-server only)
- [ ] Re-issue group chat tokens when your platform's session refreshes

### Frontend
- [ ] Fetch group chat token from your backend after login
- [ ] Connect WebSocket with `?access_token=<token>`
- [ ] On `message.created`: if `message.group_id !== currentGroup`, increment
      unread counter in the sidebar
- [ ] On `member.joined` / `member.left`: refresh member list
- [ ] After loading members, resolve `user_id` UUIDs to display names using
      your platform's user API
- [ ] Resolve `sender_user_id` in messages the same way
- [ ] Handle `sender_user_id: null` → show AI avatar/label
- [ ] Handle `ai.thinking` → show typing indicator in the group
- [ ] Call `POST /v1/groups/{id}/read` when user opens a group or scrolls to bottom
- [ ] On WebSocket disconnect, reconnect with exponential backoff
