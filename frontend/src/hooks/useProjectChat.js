import { useCallback, useEffect, useRef, useState } from "react";
import {
  fetchGroupChatToken,
  fetchUserDisplayInfo,
  getQmsgBaseUrl,
} from "../api/groupchatApi";

/**
 * @typedef {Object} ChatMessage
 * @property {string} id
 * @property {string} group_id
 * @property {string | null} sender_user_id
 * @property {string} message_type
 * @property {string} body_ciphertext
 * @property {string} created_at
 * @property {Object[]} reactions
 * @property {Object} [metadata]
 */

const WS_RECONNECT_BASE_MS = 1000;
const WS_RECONNECT_MAX_MS = 30000;

function buildQmsgUrl(path) {
  const base = getQmsgBaseUrl();
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (!base) {
    return normalized;
  }
  return `${base.replace(/\/$/, "")}${normalized}`;
}

function buildWsUrl(qmsgToken) {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  const path = buildQmsgUrl("/qmsg/v1/ws");
  const fullPath = path.startsWith("/") ? path : `/${path}`;
  return `${protocol}//${host}${fullPath}?access_token=${encodeURIComponent(qmsgToken)}`;
}

/**
 * Hook for project group chat: token, messages, WebSocket, send, user resolution.
 * @param {Object} opts
 * @param {string} sessionToken - ComIT JWT (required for token fetch)
 * @param {string} groupChatId - QmsgCore group ID (gr_...)
 * @param {boolean} enabled - whether to connect (e.g. panel visible and has both ids)
 */
export function useProjectChat({ sessionToken, groupChatId, enabled }) {
  const [qmsgToken, setQmsgToken] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [userNames, setUserNames] = useState(/** @type {Record<string, string>} */ ({}));
  const wsRef = useRef(/** @type {WebSocket | null} */ (null));
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptRef = useRef(0);

  const resolveUserNames = useCallback(
    async (userIds) => {
      if (!sessionToken || !userIds?.length) return;
      const unique = [...new Set(userIds.filter(Boolean))];
      if (unique.length === 0) return;
      try {
        const infos = await fetchUserDisplayInfo(sessionToken, unique);
        setUserNames((prev) => {
          const next = { ...prev };
          for (const u of infos) {
            const name = u.display_name ?? (u.email ? u.email.split("@")[0] : u.user_id);
            next[u.user_id] = name;
          }
          return next;
        });
      } catch {
        // ignore
      }
    },
    [sessionToken],
  );

  const loadMessages = useCallback(async () => {
    if (!qmsgToken || !groupChatId) return;
    try {
      const url = buildQmsgUrl(`/qmsg/v1/groups/${groupChatId}/messages?limit=100`);
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${qmsgToken}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const list = Array.isArray(data) ? data : [];
      setMessages(list);

      const senderIds = [...new Set(list.map((m) => m.sender_user_id).filter(Boolean))];
      if (senderIds.length && sessionToken) {
        resolveUserNames(senderIds);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setIsLoading(false);
    }
  }, [qmsgToken, groupChatId, sessionToken, resolveUserNames]);

  const markRead = useCallback(async () => {
    if (!qmsgToken || !groupChatId) return;
    try {
      const url = buildQmsgUrl(`/qmsg/v1/groups/${groupChatId}/read`);
      await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${qmsgToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
    } catch {
      // ignore
    }
  }, [qmsgToken, groupChatId]);

  const sendMessage = useCallback(
    async (text) => {
      if (!qmsgToken || !groupChatId || !text?.trim()) return;
      try {
        const url = buildQmsgUrl(`/qmsg/v1/groups/${groupChatId}/messages`);
        const res = await fetch(url, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${qmsgToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message_type: "text",
            body_ciphertext: text.trim(),
            body_nonce: "",
            body_tag: "",
          }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const msg = await res.json();
        setMessages((prev) => {
          const exists = prev.some((m) => m.id === msg.id);
          if (exists) return prev;
          return [...prev, msg];
        });
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [qmsgToken, groupChatId],
  );

  const sendAiRequest = useCallback(
    async (text) => {
      if (!qmsgToken || !groupChatId || !text?.trim()) return;
      try {
        const url = buildQmsgUrl(`/qmsg/v1/groups/${groupChatId}/messages`);
        const res = await fetch(url, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${qmsgToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message_type: "ai_request",
            metadata: { text: text.trim() },
            body_ciphertext: "",
            body_nonce: "",
            body_tag: "",
          }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const msg = await res.json();
        setMessages((prev) => {
          const exists = prev.some((m) => m.id === msg.id);
          if (exists) return prev;
          return [...prev, msg];
        });
        setIsAiThinking(true);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [qmsgToken, groupChatId],
  );

  // Fetch QmsgCore token when enabled
  useEffect(() => {
    if (!enabled || !sessionToken) {
      setQmsgToken(null);
      return;
    }
    let cancelled = false;
    fetchGroupChatToken(sessionToken)
      .then((data) => {
        if (!cancelled && data?.access_token) {
          setQmsgToken(data.access_token);
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [enabled, sessionToken]);

  // Load messages when we have token and group
  useEffect(() => {
    if (!qmsgToken || !groupChatId || !enabled) return;
    setIsLoading(true);
    setError(null);
    loadMessages();
    markRead();
  }, [qmsgToken, groupChatId, enabled, loadMessages, markRead]);

  // WebSocket: connect and handle events
  useEffect(() => {
    if (!enabled || !qmsgToken || !groupChatId) return;

    const connect = () => {
      const wsUrl = buildWsUrl(qmsgToken);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const envelope = JSON.parse(event.data);
          const { type, payload } = envelope || {};
          if (type === "message.created" && payload?.message) {
            const msg = payload.message;
            if (msg.group_id === groupChatId) {
              setMessages((prev) => {
                const exists = prev.some((m) => m.id === msg.id);
                if (exists) return prev;
                const next = [...prev, msg];
                if (msg.sender_user_id && sessionToken) {
                  resolveUserNames([msg.sender_user_id]);
                }
                return next;
              });
              if (msg.sender_user_id === null) {
                setIsAiThinking(false);
              }
            }
          } else if (type === "ai.thinking" && payload?.group_id === groupChatId) {
            setIsAiThinking(true);
          }
        } catch {
          // ignore parse errors
        }
      };

      ws.onclose = () => {
        wsRef.current = null;
        if (!enabled) return;
        const delay = Math.min(
          WS_RECONNECT_BASE_MS * 2 ** reconnectAttemptRef.current,
          WS_RECONNECT_MAX_MS,
        );
        reconnectAttemptRef.current += 1;
        reconnectTimeoutRef.current = window.setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    reconnectAttemptRef.current = 0;
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [enabled, qmsgToken, groupChatId, sessionToken, resolveUserNames]);

  const getDisplayName = useCallback(
    (userId) => {
      if (!userId) return "AI";
      return userNames[userId] ?? userId.slice(0, 8);
    },
    [userNames],
  );

  return {
    messages,
    isLoading,
    error,
    isAiThinking,
    sendMessage,
    sendAiRequest,
    getDisplayName,
    markRead,
  };
}
