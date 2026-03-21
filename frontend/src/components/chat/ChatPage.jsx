import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { assets } from "../../assets";

function SearchIcon() {
  return <img src={assets.searchIcon} alt="" className="chat-page-search-icon" />;
}

function PinIcon() {
  return <img src={assets.diaryBookmarkIcon} alt="" className="chat-page-pin-icon" />;
}

export function ChatPage({
  historyItems,
  composerPrompts,
  heroActions,
  statusCard,
  messages,
  chatInput,
  chatListRef,
  onClose,
  onSendMessage,
  onChangeChatInput,
  onSubmit
}) {
  const [searchValue, setSearchValue] = useState("");
  const [isStatusVisible, setIsStatusVisible] = useState(true);

  const filteredHistoryItems = useMemo(() => {
    const normalizedQuery = searchValue.trim().toLowerCase();
    if (!normalizedQuery) {
      return historyItems;
    }

    return historyItems.filter((item) => item.title.toLowerCase().includes(normalizedQuery));
  }, [historyItems, searchValue]);

  const hasConversation = messages.length > 0;

  return (
    <section className="chat-page">
      <aside className="glass-card chat-page-sidebar">
        <div className="chat-page-sidebar-head">
          <span className="chat-page-sidebar-logo">ComIT</span>
          <button className="chat-page-sidebar-pin" type="button" aria-label="Закреплённые чаты">
            <PinIcon />
          </button>
        </div>

        <label className="chat-page-search">
          <SearchIcon />
          <input
            type="text"
            value={searchValue}
            onChange={(event) => setSearchValue(event.target.value)}
            placeholder="Поиск в чатах"
            aria-label="Поиск в чатах"
          />
        </label>

        <div className="chat-page-history">
          {filteredHistoryItems.map((item, index) => (
            <motion.button
              key={item.id}
              type="button"
              className="chat-page-history-item"
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.04 + index * 0.03, duration: 0.24 }}
              onClick={() => onSendMessage(item.prompt)}
            >
              {item.title}
            </motion.button>
          ))}
        </div>

        <button className="chat-page-support-link" type="button">
          Написать в поддержку
        </button>
      </aside>

      <div className="chat-page-main">
        {isStatusVisible ? (
          <motion.aside
            className="glass-card chat-page-status-card"
            initial={{ opacity: 0, x: 18 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.12, duration: 0.3 }}
          >
            <div className="chat-page-status-head">
              <div className="chat-page-status-brand">
                <span className="chat-page-status-logo-wrap">
                  <img src={assets.untitledLogo} alt="" className="chat-page-status-logo" />
                </span>

                <div className="chat-page-status-copy">
                  <div className="chat-page-status-title-row">
                    <strong>{statusCard.title}</strong>
                    <span>{statusCard.version}</span>
                  </div>
                </div>
              </div>

              <button
                className="chat-page-status-close"
                type="button"
                aria-label="Закрыть карточку статуса"
                onClick={() => setIsStatusVisible(false)}
              >
                <img src={assets.group12021Icon} alt="" />
              </button>
            </div>

            <div className="chat-page-status-progress">
              <div className="chat-page-status-track">
                <span className="chat-page-status-fill" style={{ width: `${statusCard.progress}%` }} />
              </div>
              <p>{statusCard.etaLabel}</p>
            </div>
          </motion.aside>
        ) : null}

        <div className="chat-page-center">
          {hasConversation ? (
            <motion.div
              className="chat-page-thread"
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.28 }}
              ref={chatListRef}
            >
              {messages.map((message) => (
                <div key={message.id} className={`chat-message chat-page-message chat-${message.role}`}>
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
            </motion.div>
          ) : (
            <motion.div
              className="chat-page-empty-state"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <img src={assets.untitledLogo} alt="" className="chat-page-empty-logo" />
              <h1 className="chat-page-empty-title">Чем могу помочь сегодня?</h1>
            </motion.div>
          )}

          <motion.div
            className="chat-page-composer-shell"
            initial={{ opacity: 0, y: 22 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08, duration: 0.32 }}
          >
            <div className="chat-page-composer-top">
              <div className="chat-page-composer-pills">
                {composerPrompts.map((prompt) => (
                  <button key={prompt} type="button" className="suggestion-pill chat-page-prompt-pill" onClick={() => onSendMessage(prompt)}>
                    {prompt}
                  </button>
                ))}
              </div>

              <button className="chat-page-composer-close" type="button" aria-label="Закрыть чат" onClick={onClose}>
                <img src={assets.group12021Icon} alt="" />
              </button>
            </div>

            <form className="chat-input-wrap chat-page-input-wrap" onSubmit={onSubmit}>
              <button className="chat-logo-btn" type="button" onClick={() => onSendMessage("Расскажи мне про ML")}>
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
          </motion.div>

          {!hasConversation ? (
            <div className="chat-page-hero-actions">
              {heroActions.map((item) => (
                <button key={item} type="button" className="chat-page-hero-action" onClick={() => onSendMessage(item)}>
                  {item}
                </button>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
