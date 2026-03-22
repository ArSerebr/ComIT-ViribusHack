import { resolveApiUrl } from "./client";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * GET /api/groupchat/token — returns QmsgCore JWT for the current user.
 * Requires session token.
 * @param {string} token - ComIT session JWT
 * @returns {Promise<{ access_token: string }>}
 */
export async function fetchGroupChatToken(token) {
  const res = await fetch(resolveApiUrl("/api/groupchat/token"), {
    headers: { ...authHeaders(token), Accept: "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * POST /api/groupchat/users — batch lookup display_name/email by user IDs.
 * @param {string} token - ComIT session JWT
 * @param {string[]} userIds - UUIDs to resolve
 * @returns {Promise<Array<{ user_id: string; display_name: string | null; email: string }>>}
 */
export async function fetchUserDisplayInfo(token, userIds) {
  if (!userIds?.length) return [];
  const res = await fetch(resolveApiUrl("/api/groupchat/users"), {
    method: "POST",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ user_ids: userIds }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * Base URL for QmsgCore API. Empty = same-origin /qmsg (Vite proxy in dev, nginx in Docker).
 * Use with /qmsg/v1/... paths.
 * @returns {string}
 */
export function getQmsgBaseUrl() {
  return "";
}
