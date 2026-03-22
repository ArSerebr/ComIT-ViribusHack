import { resolveApiUrl } from "./client";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * POST /api/pulse/chat — submit message to PulseCore AI. Returns task_id.
 * @param {string} token - ComIT session JWT
 * @param {string} message - User message text
 * @returns {Promise<{ task_id: string }>}
 */
export async function sendMessage(token, message) {
  const res = await fetch(resolveApiUrl("/api/pulse/chat"), {
    method: "POST",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ message: message.trim() }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  const data = await res.json();
  return data.task_id;
}

/**
 * GET /api/pulse/task/{task_id} — poll task status. Returns { status, result? }.
 * @param {string} token - ComIT session JWT
 * @param {string} taskId - Task ID from sendMessage
 * @returns {Promise<{ status: string, result?: object }>}
 */
export async function pollTask(token, taskId) {
  const res = await fetch(resolveApiUrl(`/api/pulse/task/${taskId}`), {
    headers: { ...authHeaders(token), Accept: "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * GET /api/pulse/status — get current AI processing status.
 * @param {string} token - ComIT session JWT
 * @returns {Promise<{ model: string, status: string, statusColor: string, progress: number }>}
 */
export async function getStatus(token) {
  const res = await fetch(resolveApiUrl("/api/pulse/status"), {
    headers: { ...authHeaders(token), Accept: "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * GET /api/pulse/history — get chat history.
 * @param {string} token - ComIT session JWT
 * @returns {Promise<Array<{ role: string, content: string|object, buttons: array, created_at?: string }>>}
 */
export async function getHistory(token) {
  const res = await fetch(resolveApiUrl("/api/pulse/history"), {
    headers: { ...authHeaders(token), Accept: "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * POST /api/pulse/execute — confirm task execution.
 * @param {string} token - ComIT session JWT
 * @returns {Promise<{ status: string, message: string, frontend_actions?: array }>}
 */
export async function executeTask(token) {
  const res = await fetch(resolveApiUrl("/api/pulse/execute"), {
    method: "POST",
    headers: { ...authHeaders(token), Accept: "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * POST /api/pulse/cancel — cancel pending task.
 * @param {string} token - ComIT session JWT
 * @returns {Promise<{ status: string, message: string }>}
 */
export async function cancelTask(token) {
  const res = await fetch(resolveApiUrl("/api/pulse/cancel"), {
    method: "POST",
    headers: { ...authHeaders(token), Accept: "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}
