import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { assets } from "../../assets";

export function AiChatPanel({
  isVisible,
  isAgentActive = false,
  quickPrompts,
  messages,
  chatInput,
  chatListRef,
  onClose,
  onSendMessage,
  onChangeChatInput,
  onSubmit
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
          {quickPrompts.map((prompt) => (
            <button key={prompt} type="button" className="suggestion-pill" onClick={() => onSendMessage(prompt)}>
              {prompt}
            </button>
          ))}
        </div>

        <div className="chat-messages" ref={chatListRef}>
          {messages.map((message) => (
            <div key={message.id} className={`chat-message chat-${message.role}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
              {message.actions?.length ? (
                <div className="chat-actions">
                  {message.actions.map((action) => (
                    <button key={action.label} type="button" onClick={() => onSendMessage(action.prompt)}>
                      {action.label}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
        </div>

        <form className="chat-input-wrap" onSubmit={onSubmit}>
          <button className="chat-logo-btn" type="button" onClick={() => onSendMessage("Помоги начать обучение")}>
            <img src={assets.aiGenerateIcon} alt="" />
          </button>
          <input
            value={chatInput}
            onChange={(event) => onChangeChatInput(event.target.value)}
            placeholder="Спроси меня о чем нибудь..."
            aria-label="Ввод сообщения"
          />
          <button className="chat-send-btn" type="submit" aria-label="Отправить">
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
        </form>
      </motion.section>
    </motion.div>
  );
}
