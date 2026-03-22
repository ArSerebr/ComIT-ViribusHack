import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion } from "framer-motion";
import { assets } from "../../assets";
import { useProjectChat } from "../../hooks/useProjectChat";

function getMessageBody(msg) {
  if (msg.message_type === "ai_message" && msg.metadata?.ai_content) {
    return msg.metadata.ai_content;
  }
  if (msg.message_type === "text" && msg.body_ciphertext) {
    return msg.body_ciphertext;
  }
  if (msg.message_type === "ai_request" && msg.metadata?.text) {
    return msg.metadata.text;
  }
  return "";
}

export function ProjectChatPanel({ project, sessionToken }) {
  const groupChatId = project?.groupChatId ?? null;
  const enabled = Boolean(sessionToken && groupChatId);

  const {
    messages,
    isLoading,
    error,
    isAiThinking,
    sendMessage,
    sendAiRequest,
    getDisplayName,
    markRead,
  } = useProjectChat({
    sessionToken: sessionToken || "",
    groupChatId: groupChatId || "",
    enabled,
  });

  const [inputValue, setInputValue] = useState("");
  const [useAi, setUseAi] = useState(false);
  const listRef = useRef(null);

  useEffect(() => {
    if (messages.length > 0) {
      markRead();
    }
  }, [messages.length, markRead]);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const text = inputValue.trim();
    if (!text) return;
    if (useAi) {
      sendAiRequest(text);
    } else {
      sendMessage(text);
    }
    setInputValue("");
  };

  if (!enabled) return null;

  return (
    <motion.section
      className="glass-card project-chat-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
    >
      <header className="project-chat-panel-head">
        <h2 className="project-chat-panel-title">
          Чат проекта
          <span className="project-details-title-icon project-details-title-icon-team" aria-hidden="true" />
        </h2>
      </header>

      <div className="project-chat-panel-body">
        {error ? (
          <p className="project-chat-panel-error">{error}</p>
        ) : isLoading ? (
          <p className="project-chat-panel-loading">Загрузка чата...</p>
        ) : (
          <div className="project-chat-panel-messages" ref={listRef}>
            {messages.map((msg) => {
              const isAi = msg.sender_user_id === null;
              const body = getMessageBody(msg);
              return (
                <div
                  key={msg.id}
                  className={`project-chat-message ${isAi ? "project-chat-message-ai" : "project-chat-message-user"}`}
                >
                  <div className="project-chat-message-meta">
                    <span className="project-chat-message-author">
                      {isAi ? "AI" : getDisplayName(msg.sender_user_id)}
                    </span>
                    <span className="project-chat-message-time">
                      {msg.created_at
                        ? new Date(msg.created_at).toLocaleTimeString("ru-RU", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : ""}
                    </span>
                  </div>
                  <div className="project-chat-message-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{body || "—"}</ReactMarkdown>
                  </div>
                </div>
              );
            })}
            {isAiThinking && (
              <div className="project-chat-message project-chat-message-ai project-chat-message-thinking">
                <div className="project-chat-message-meta">
                  <span className="project-chat-message-author">AI</span>
                </div>
                <div className="project-chat-message-body">
                  <span className="project-chat-typing-indicator">
                    <span />
                    <span />
                    <span />
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        <form className="project-chat-panel-form" onSubmit={handleSubmit}>
          <div className="project-chat-panel-input-row">
            <button
              type="button"
              className={`project-chat-ai-toggle ${useAi ? "project-chat-ai-toggle-on" : ""}`}
              onClick={() => setUseAi(!useAi)}
              aria-label={useAi ? "Режим AI включён" : "Включить режим AI"}
              title={useAi ? "Отправить как AI-запрос" : "Отправить в чат"}
            >
              <img src={assets.aiGenerateIcon} alt="" />
              <span>{useAi ? "AI" : "Чат"}</span>
            </button>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={useAi ? "Спросить AI..." : "Сообщение..."}
              aria-label="Ввод сообщения"
              className="project-chat-panel-input"
            />
            <button type="submit" className="project-chat-panel-send" aria-label="Отправить">
              <img src={assets.arrowSmallLeftIcon} alt="" />
            </button>
          </div>
        </form>
      </div>
    </motion.section>
  );
}
