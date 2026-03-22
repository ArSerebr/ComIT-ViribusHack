import { useCallback, useEffect, useRef, useState } from "react";
import {
  sendMessage as apiSendMessage,
  pollTask,
  getStatus,
  getHistory,
  executeTask,
  cancelTask,
} from "../api/pulseApi";

const POLL_INTERVAL_MS = 1000;
const TASK_TIMEOUT_MS = 120_000;

/**
 * Normalize PulseCore result into UI message format.
 * @param {object} result - { role, content, buttons }
 * @returns {{ content: string, buttons: array }}
 */
function normalizeResult(result) {
  if (!result) return { content: "", buttons: [] };
  const { content, buttons = [] } = result;
  const text =
    typeof content === "string"
      ? content
      : content?.explanation ?? "";
  return { content: text, buttons };
}

/**
 * Convert history item to UI message format.
 */
function historyToMessage(item, index) {
  const { role, content, buttons = [] } = item;
  const text =
    typeof content === "string"
      ? content
      : content?.explanation ?? "";
  return {
    id: `h-${index}-${item.created_at || index}`,
    role: role === "user" ? "user" : "ai",
    content: text,
    buttons,
  };
}

/**
 * Hook for PulseCore AI chat: messages, send, history, status, execute/cancel.
 * @param {Object} opts
 * @param {string} sessionToken - ComIT JWT (required for API calls)
 * @param {boolean} enabled - whether chat is active (load history, allow send)
 */
export function usePulseChat({ sessionToken, enabled }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);
  const [isPending, setIsPending] = useState(false);
  const statusIntervalRef = useRef(null);
  const abortRef = useRef(false);

  const loadHistory = useCallback(async () => {
    if (!sessionToken || !enabled) return;
    setIsLoading(true);
    setError(null);
    try {
      const history = await getHistory(sessionToken);
      const msgs = (history || []).map(historyToMessage);
      setMessages(msgs);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setIsLoading(false);
    }
  }, [sessionToken, enabled]);

  const stopStatusPolling = useCallback(() => {
    if (statusIntervalRef.current) {
      clearInterval(statusIntervalRef.current);
      statusIntervalRef.current = null;
    }
    setStatus(null);
  }, []);

  const startStatusPolling = useCallback(() => {
    if (!sessionToken || statusIntervalRef.current) return;
    const poll = async () => {
      try {
        const s = await getStatus(sessionToken);
        setStatus(s);
      } catch {
        // ignore
      }
    };
    poll();
    statusIntervalRef.current = setInterval(poll, POLL_INTERVAL_MS);
  }, [sessionToken]);

  const sendMessage = useCallback(
    async (text) => {
      const trimmed = text?.trim();
      if (!sessionToken || !enabled || !trimmed) return;

      const userMsg = {
        id: `u-${Date.now()}`,
        role: "user",
        content: trimmed,
      };
      setMessages((prev) => [...prev, userMsg]);
      setError(null);
      setIsPending(true);
      startStatusPolling();
      abortRef.current = false;

      try {
        const taskId = await apiSendMessage(sessionToken, trimmed);
        const deadline = Date.now() + TASK_TIMEOUT_MS;

        while (Date.now() < deadline && !abortRef.current) {
          await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
          const data = await pollTask(sessionToken, taskId);

          if (data.status === "READY") {
            const { content, buttons } = normalizeResult(data.result);
            setMessages((prev) => [
              ...prev,
              {
                id: `a-${Date.now()}`,
                role: "ai",
                content,
                buttons,
              },
            ]);
            break;
          }
          if (data.status === "FAILED") {
            const errMsg = data.result?.error ?? "Ошибка обработки запроса";
            setError(errMsg);
            break;
          }
        }
        if (Date.now() >= deadline && !abortRef.current) {
          setError("Превышено время ожидания ответа");
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setIsPending(false);
        stopStatusPolling();
      }
    },
    [sessionToken, enabled, startStatusPolling, stopStatusPolling],
  );

  const executePendingTask = useCallback(
    async () => {
      if (!sessionToken) return null;
      try {
        const data = await executeTask(sessionToken);
        setMessages((prev) => [
          ...prev,
          {
            id: `a-${Date.now()}`,
            role: "ai",
            content: data.message ?? "Готово.",
            buttons: [],
          },
        ]);
        return data;
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
        return null;
      }
    },
    [sessionToken],
  );

  const cancelPendingTask = useCallback(
    async () => {
      if (!sessionToken) return;
      try {
        const data = await cancelTask(sessionToken);
        setMessages((prev) => [
          ...prev,
          {
            id: `a-${Date.now()}`,
            role: "ai",
            content: data.message ?? "Задача отменена.",
            buttons: [],
          },
        ]);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      }
    },
    [sessionToken],
  );

  useEffect(() => {
    if (enabled && sessionToken) {
      loadHistory();
    }
    return () => {
      abortRef.current = true;
      stopStatusPolling();
    };
  }, [enabled, sessionToken, loadHistory, stopStatusPolling]);

  return {
    messages,
    isLoading,
    error,
    status,
    isPending,
    sendMessage,
    loadHistory,
    executePendingTask,
    cancelPendingTask,
  };
}
