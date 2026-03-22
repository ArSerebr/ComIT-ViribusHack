import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { assets } from "../../assets";

function renderMessageButtons(message, onSendMessage, onExecutePendingTask, onCancelPendingTask) {
  const buttons = message.buttons ?? message.actions ?? [];
  if (!buttons.length) return null;
  const first = buttons[0];
  if (typeof first === "object" && first !== null && "url" in first) {
    return (
      <div className="chat-actions">
        {buttons.map((btn) => (
          <a key={btn.label} href={btn.url} className="chat-action-link" target="_blank" rel="noopener noreferrer">
            {btn.label}
          </a>
        ))}
      </div>
    );
  }
  if (typeof first === "string") {
    return (
      <div className="chat-actions">
        {buttons.map((label) => (
          <button
            key={label}
            type="button"
            onClick={() =>
              label === "Запустить агента" ? onExecutePendingTask?.() : onCancelPendingTask?.()
            }
          >
            {label}
          </button>
        ))}
      </div>
    );
  }
  if (typeof first === "object" && "prompt" in first) {
    return (
      <div className="chat-actions">
        {buttons.map((action) => (
          <button key={action.label} type="button" onClick={() => onSendMessage(action.prompt)}>
            {action.label}
          </button>
        ))}
      </div>
    );
  }
  return null;
}

export function AiChatPanel({
  isVisible,
  isAgentActive = false,
  quickPrompts,
  messages,
  chatInput,
  chatListRef,
  needsAuth = false,
  onClose,
  onSendMessage,
  onChangeChatInput,
  onSubmit,
  onExecutePendingTask,
  onCancelPendingTask,
}) {
  if (!isVisible) {
    return null;
  }

  return (
    <motion.div
      className={`ai-chat-layer ${isAgentActive ? "ai-chat-layer-agent" : ""}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.28 }}
    >
      <div className={`ai-chat-bottom-blur ${isAgentActive ? "ai-chat-bottom-blur-agent" : ""}`} aria-hidden="true" />

      <motion.section
        className={`ai-chat-shell ${isAgentActive ? "ai-chat-shell-agent" : ""}`}
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.34 }}
      >
        <button className="ai-close-btn" type="button" aria-label="Закрыть ИИ-режим" onClick={onClose}>
          <img src={assets.group12021Icon} alt="" />
        </button>

        <div className="ai-suggestions">
          {!needsAuth &&
            quickPrompts.map((prompt) => (
              <button key={prompt} type="button" className="suggestion-pill" onClick={() => onSendMessage(prompt)}>
                {prompt}
              </button>
            ))}
        </div>

        <div className="chat-messages" ref={chatListRef}>
          {needsAuth ? (
            <p className="ai-chat-auth-prompt">Войдите для использования чата с ИИ</p>
          ) : (
            <>
              {messages.map((message) => (
                <div key={message.id} className={`chat-message chat-${message.role}`}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content || "—"}</ReactMarkdown>
                  {renderMessageButtons(message, onSendMessage, onExecutePendingTask, onCancelPendingTask)}
                </div>
              ))}
              {isAgentActive ? (
                <div className="chat-message chat-ai chat-message-thinking">
                  <span className="chat-typing-indicator">
                    <span />
                    <span />
                    <span />
                  </span>
                </div>
              ) : null}
            </>
          )}
        </div>

        <form className="chat-input-wrap" onSubmit={onSubmit}>
          <button
            className="chat-logo-btn"
            type="button"
            onClick={() => !needsAuth && onSendMessage("Помоги начать обучение")}
          >
            <img src={assets.aiActiveIcon} alt="" />
          </button>
          <input
            value={chatInput}
            onChange={(event) => onChangeChatInput(event.target.value)}
            placeholder={needsAuth ? "Войдите для чата с ИИ" : "Спроси меня о чем нибудь..."}
            aria-label="Ввод сообщения"
            disabled={needsAuth}
          />
          <button className="chat-send-btn" type="submit" aria-label="Отправить" disabled={needsAuth}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
        </form>
      </motion.section>
    </motion.div>
  );
}
