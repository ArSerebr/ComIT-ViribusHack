import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { assets } from "./assets";

const MENU_ITEMS = [
  { id: "home", label: "Главная", icon: assets.barsSortIcon },
  { id: "ai", label: "ИИ", icon: [assets.sparklesIconA, assets.sparklesIconB] },
  { id: "projects", label: "Проекты", icon: assets.folderOpenIcon },
  { id: "news", label: "Новости", icon: assets.newspaperOpenIcon },
  { id: "library", label: "Библиотека", icon: assets.diaryBookmarkIcon }
];

const RECOMMENDATIONS = [
  {
    id: "hackathon",
    title: "Хакатон 2026",
    subtitle: "Погружение в ML + Frontend",
    image: assets.posterHackathon,
    link: "https://example.com/hackathon"
  },
  {
    id: "web3",
    title: "Web3 Design",
    subtitle: "Интенсив по продукту",
    image: assets.posterWeb3,
    link: "https://example.com/web3-design"
  },
  {
    id: "tech-conf",
    title: "Tech Conference",
    subtitle: "Frontend engineering",
    image: assets.posterTechConf,
    link: "https://example.com/tech-conference"
  },
  {
    id: "tech-talk",
    title: "Tech Talk",
    subtitle: "Современный стек разработчика",
    image: assets.posterTechTalk,
    link: "https://example.com/tech-talk"
  }
];

const INITIAL_CHAT = [
  {
    id: "m-1",
    role: "assistant",
    content:
      "Привет. Я **ComIT AI**.\n\nМогу помочь:\n- подобрать курс\n- разобрать roadmap\n- собрать стек под цель",
    actions: [
      { label: "Подобрать курс", prompt: "Подбери мне курс по ML на 3 месяца" },
      { label: "Собрать roadmap", prompt: "Собери roadmap для Junior Frontend" }
    ]
  }
];

const QUICK_PROMPTS = ["Расскажи мне про ML", "Какой стек мне нужен?"];

const NAV_LINKS = {
  courses: "/courses",
  events: "/events",
  projects: "/projects",
  news: "/news",
  chat: "/chat"
};

function nextAssistantMessage(text) {
  const normalized = text.toLowerCase();

  if (normalized.includes("ml")) {
    return {
      content:
        "### План по ML на 3 месяца\n\n1. Python + NumPy/Pandas\n2. Классические модели\n3. Pet-проект с деплоем\n\n`Совет:` фиксируй прогресс каждую неделю.",
      actions: [
        { label: "Дай курсы", prompt: "Покажи 3 курса по ML для новичка" },
        { label: "Нужен проект", prompt: "Дай идею pet-проекта для ML портфолио" }
      ]
    };
  }

  if (normalized.includes("frontend") || normalized.includes("стек")) {
    return {
      content:
        "Рекомендуемый **Frontend-стек**:\n\n- `HTML/CSS`\n- `JavaScript`\n- `React`\n- `TypeScript`\n- `Vite`\n\nПосле этого переходи к тестам (`Vitest`, `Playwright`).",
      actions: [
        { label: "Roadmap на 8 недель", prompt: "Сделай roadmap frontend на 8 недель" }
      ]
    };
  }

  return {
    content:
      "Принял запрос. Могу развернуть ответ в виде:\n\n- подробного плана\n- списка ресурсов\n- практического задания",
    actions: [{ label: "Дай практику", prompt: "Дай практическое задание по теме" }]
  };
}

function App() {
  const [activeTab, setActiveTab] = useState("home");
  const [aiAssistantEnabled, setAiAssistantEnabled] = useState(true);
  const [aiMode, setAiMode] = useState(true);
  const [newsLiked, setNewsLiked] = useState(false);
  const [likedRecommendations, setLikedRecommendations] = useState({});
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState(INITIAL_CHAT);
  const [deck, setDeck] = useState(
    RECOMMENDATIONS.map((item, index) => ({ ...item, instanceId: `${item.id}-${index}` }))
  );
  const [dismissDirection, setDismissDirection] = useState(null);

  const chatListRef = useRef(null);
  const wheelLockRef = useRef(false);

  const topCard = deck[0];
  const stackedCards = deck.slice(1, 3);
  const canDismiss = !dismissDirection;

  const navigateTo = (path) => {
    window.location.hash = path;
  };

  const sendLikeSignal = (entity, id) => {
    const payload = JSON.stringify({ entity, id, ts: Date.now() });
    try {
      if (navigator.sendBeacon) {
        const blob = new Blob([payload], { type: "application/json" });
        navigator.sendBeacon("/api/recommendations/like", blob);
      }
    } catch {
      // no-op
    }
  };

  const rotateDeck = () => {
    setDeck((prev) => {
      if (prev.length < 2) {
        return prev;
      }
      const [first, ...rest] = prev;
      return [...rest, { ...first, instanceId: `${first.id}-${Date.now()}` }];
    });
  };

  const dismissTopCard = (direction) => {
    if (!canDismiss) {
      return;
    }
    setDismissDirection(direction);
  };

  const toggleRecommendationLike = (recommendationId) => {
    setLikedRecommendations((prev) => {
      const next = !prev[recommendationId];
      sendLikeSignal("recommendation", recommendationId);
      return { ...prev, [recommendationId]: next };
    });
  };

  const shareRecommendation = async (recommendation) => {
    const isMobile = window.matchMedia("(max-width: 1023px)").matches;

    try {
      if (isMobile && navigator.share) {
        await navigator.share({
          title: recommendation.title,
          text: recommendation.subtitle,
          url: recommendation.link
        });
        return;
      }

      await navigator.clipboard.writeText(recommendation.link);
    } catch {
      window.prompt("Скопируйте ссылку:", recommendation.link);
    }
  };

  const handleAiMenuClick = () => {
    if (!aiAssistantEnabled) {
      setAiAssistantEnabled(true);
      setAiMode(true);
      return;
    }
    setActiveTab("chat");
    navigateTo(NAV_LINKS.chat);
  };

  const handleMenuClick = (itemId) => {
    if (itemId === "ai") {
      handleAiMenuClick();
      return;
    }

    setActiveTab(itemId);
    switch (itemId) {
      case "home":
        navigateTo("/");
        break;
      case "projects":
        navigateTo(NAV_LINKS.projects);
        break;
      case "news":
        navigateTo(NAV_LINKS.news);
        break;
      case "library":
        navigateTo("/library");
        break;
      default:
        break;
    }
  };

  const toggleNewsLike = () => {
    setNewsLiked((prev) => {
      const next = !prev;
      sendLikeSignal("news", "main-news");
      return next;
    });
  };

  const sendMessage = (rawText) => {
    const text = rawText.trim();
    if (!text) {
      return;
    }

    const userMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: text
    };

    setMessages((prev) => [...prev, userMessage]);
    setChatInput("");

    const reply = nextAssistantMessage(text);
    window.setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          content: reply.content,
          actions: reply.actions
        }
      ]);
    }, 260);
  };

  useEffect(() => {
    if (chatListRef.current) {
      chatListRef.current.scrollTop = chatListRef.current.scrollHeight;
    }
  }, [messages]);

  const topCardExitAnimation = useMemo(() => {
    if (dismissDirection === "right") {
      return { x: 760, y: 120, rotate: 22, opacity: 0 };
    }
    if (dismissDirection === "left") {
      return { x: -760, y: 120, rotate: -22, opacity: 0 };
    }
    if (dismissDirection === "down") {
      return { x: 0, y: 760, rotate: 12, opacity: 0 };
    }
    return { x: 0, y: 0, rotate: 0, opacity: 1 };
  }, [dismissDirection]);

  return (
    <div className="viewport-frame">
      <div className="design-canvas">
        <div className="app-shell">
          <img className="bg-shape bg-shape-top" src={assets.backgroundShape} alt="" />
          <img className="bg-shape bg-shape-bottom" src={assets.backgroundShape} alt="" />

          <header className="top-bar">
            <button
              className="logo-wrap"
              onClick={() => {
                setActiveTab("home");
                navigateTo("/");
              }}
              type="button"
              aria-label="На главную"
            >
              <img src={assets.untitledLogo} alt="" className="logo-icon" />
              <span className="logo-text">ComIT</span>
            </button>

            <nav className="menu-nav" aria-label="Основное меню">
              {MENU_ITEMS.map((item) => {
                const isAi = item.id === "ai";
                const isActive = !isAi && activeTab === item.id;
                const aiActive = isAi && aiAssistantEnabled;

                return (
                  <button
                    key={item.id}
                    className={`menu-item ${isActive ? "menu-item-active" : ""} ${
                      aiActive ? "menu-item-ai-active" : ""
                    }`}
                    onClick={() => handleMenuClick(item.id)}
                    type="button"
                    aria-pressed={isActive || aiActive}
                  >
                    {isAi ? (
                      <span className="menu-ai-icon">
                        <img src={item.icon[0]} alt="" />
                        <img src={item.icon[1]} alt="" />
                      </span>
                    ) : (
                      <img src={item.icon} alt="" className="menu-icon" />
                    )}
                    {!isAi && <span className="menu-label">{item.label}</span>}
                  </button>
                );
              })}
            </nav>

            <div className="top-actions">
              <button className="glass-icon-button notify-btn" type="button" aria-label="Уведомления">
                <img src={assets.bellIcon} alt="" className="notify-icon" />
                <span className="notify-dot" />
              </button>
              <button className="account-btn" type="button" aria-label="Аккаунт">
                <img src={assets.ellipse194} alt="" className="account-ring" />
                <img src={assets.avatarPhoto} alt="Профиль" className="account-photo" />
              </button>
            </div>
          </header>

          <main className="dashboard-layout">
            <section className="left-content">
              <h1 className="page-title">Главная панель</h1>

              <div className="summary-grid">
                <motion.article
                  className="glass-card for-you-card"
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.06, duration: 0.36 }}
                >
                  <h2>Для вас</h2>
                  <p>Подходящие курсы обучения</p>
                  <button className="small-arrow-btn" onClick={() => navigateTo(NAV_LINKS.courses)} type="button">
                    <img src={assets.alignCenterIcon} alt="" />
                  </button>
                  <button className="for-you-course" type="button" onClick={() => navigateTo("/courses/data-science-ml")}>
                    <img src={assets.courseImage} alt="" className="for-you-course-img" />
                    <span className="for-you-course-pill">Data Science + ML</span>
                    <img src={assets.group124Icon} alt="" className="for-you-course-arrow" />
                  </button>
                </motion.article>

                <motion.article
                  className="glass-card stats-card"
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.12, duration: 0.36 }}
                  onClick={() => navigateTo(NAV_LINKS.events)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      navigateTo(NAV_LINKS.events);
                    }
                  }}
                >
                  <h2>Мероприятия</h2>
                  <p>Статистика за последний месяц</p>
                  <button className="small-arrow-btn" type="button">
                    <img src={assets.alignCenterIcon} alt="" />
                  </button>
                  <div className="events-info">
                    <div>
                      <strong>16</strong>
                      <span>+2 за месяц</span>
                    </div>
                    <div className="event-avatars">
                      <span className="avatar-chip chip-gray">
                        <img src={assets.gigachatLogo} alt="" />
                      </span>
                      <span className="avatar-chip chip-light">
                        <img src={assets.cloudIcon} alt="" />
                      </span>
                      <span className="avatar-chip chip-white">
                        <img src={assets.grokLogo} alt="" />
                      </span>
                      <span className="avatar-chip chip-glass">+13</span>
                    </div>
                  </div>
                </motion.article>

                <motion.article
                  className="glass-card stats-card productivity-card"
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.18, duration: 0.36 }}
                >
                  <h2>Продуктивность</h2>
                  <p>Статистика за последний месяц</p>
                  <div className="productivity-content">
                    <div>
                      <strong>80%</strong>
                      <span>+60% за месяц</span>
                    </div>
                    <img src={assets.nodeJsIcon} alt="Node.js" />
                  </div>
                </motion.article>
              </div>

              <div className="bottom-cards">
                <motion.article
                  className="glass-card news-card"
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.24, duration: 0.36 }}
                  onClick={() => navigateTo("/news/yandex-meetup")}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      navigateTo("/news/yandex-meetup");
                    }
                  }}
                >
                  <div className="news-image-wrap">
                    <img src={assets.newsPhoto} alt="" />
                  </div>
                  <p className="news-text">
                    Недавно яндекс провёл митап конференцию по фронтенду, а также бесплатные вебинары по javascript и
                    typescript
                  </p>
                  <button
                    className="news-like-btn"
                    type="button"
                    aria-label="Лайк новости"
                    onClick={(event) => {
                      event.stopPropagation();
                      toggleNewsLike();
                    }}
                  >
                    <img src={newsLiked ? assets.heartFilledIcon : assets.heartOutlineIcon} alt="" />
                  </button>
                  <button className="news-link-btn" type="button" onClick={() => navigateTo("/news/yandex-meetup")}>
                    Подробнее
                    <img src={assets.arrow16Icon} alt="" />
                  </button>
                </motion.article>

                <motion.article
                  className="glass-card projects-card"
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.36 }}
                  onClick={() => navigateTo(NAV_LINKS.projects)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      navigateTo(NAV_LINKS.projects);
                    }
                  }}
                >
                  <div className="projects-head">
                    <h2 className="projects-title">
                      Актуальные проекты
                      <img src={assets.sparklesIconA} alt="" className="title-spark" />
                    </h2>
                    <button className="small-arrow-btn" type="button">
                      <img src={assets.alignCenterIcon} alt="" />
                    </button>
                  </div>
                  <a className="project-link" href="#/projects/api-delivery">
                    API для доставки еды
                    <img src={assets.arrow15Icon} alt="" />
                  </a>
                  <div className="progress-track">
                    <div className="progress-fill" />
                  </div>
                  <ul className="tasks-list">
                    <li>
                      <span className="task-dot" />
                      <div>
                        <strong>Завершить расчет LTV, ARPU и CAC</strong>
                        <p>2 часа назад</p>
                      </div>
                    </li>
                    <li className="task-muted">
                      <span className="task-dot task-dot-muted" />
                      <div>
                        <strong>Завершить расчет LTV, ARPU и CAC</strong>
                        <p>2 часа назад</p>
                      </div>
                    </li>
                  </ul>
                  <img src={assets.heartIllustration} alt="" className="project-side-art" />
                </motion.article>
              </div>
            </section>

            <aside className="recommendations-side">
              <div className="deck-wrap">
                {stackedCards
                  .slice()
                  .reverse()
                  .map((card, index) => (
                    <motion.article
                      key={card.instanceId}
                      className={`recommendation-card stacked-card stacked-${index + 1}`}
                      initial={{ opacity: 0, scale: 0.96 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.22 }}
                    >
                      <img className="recommendation-image" src={card.image} alt={card.title} />
                    </motion.article>
                  ))}

                <AnimatePresence mode="wait">
                  <motion.article
                    key={topCard.instanceId}
                    className="recommendation-card top-card"
                    drag={canDismiss}
                    dragElastic={0.18}
                    dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
                    onDragEnd={(_, info) => {
                      if (!canDismiss) {
                        return;
                      }

                      if (Math.abs(info.offset.x) > 110) {
                        dismissTopCard(info.offset.x > 0 ? "right" : "left");
                        return;
                      }

                      if (Math.abs(info.offset.y) > 110) {
                        dismissTopCard("down");
                      }
                    }}
                    onWheel={(event) => {
                      if (wheelLockRef.current || !canDismiss) {
                        return;
                      }
                      if (event.deltaY > 28) {
                        wheelLockRef.current = true;
                        dismissTopCard("right");
                        window.setTimeout(() => {
                          wheelLockRef.current = false;
                        }, 340);
                      }
                    }}
                    initial={{ opacity: 0, y: 25, rotate: 8 }}
                    animate={dismissDirection ? topCardExitAnimation : { x: 0, y: 0, rotate: 0, opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ type: "spring", stiffness: 230, damping: 24 }}
                    onAnimationComplete={() => {
                      if (dismissDirection) {
                        rotateDeck();
                        setDismissDirection(null);
                      }
                    }}
                  >
                    <img className="recommendation-image" src={topCard.image} alt={topCard.title} />
                    <div className="recommendation-actions">
                      <button
                        className="action-btn"
                        type="button"
                        aria-label="Лайкнуть"
                        onClick={() => toggleRecommendationLike(topCard.id)}
                      >
                        <img
                          src={likedRecommendations[topCard.id] ? assets.heartFilledIcon : assets.heartOutlineIcon}
                          alt=""
                        />
                      </button>
                      <button
                        className="action-btn"
                        type="button"
                        aria-label="Открыть ссылку"
                        onClick={() => window.open(topCard.link, "_blank", "noopener,noreferrer")}
                      >
                        <img src={assets.linkAltIcon} alt="" />
                      </button>
                      <button
                        className="action-btn"
                        type="button"
                        aria-label="Поделиться"
                        onClick={() => shareRecommendation(topCard)}
                      >
                        <img src={assets.shareIcon} alt="" />
                      </button>
                    </div>
                  </motion.article>
                </AnimatePresence>
              </div>
            </aside>
          </main>

          {aiMode && (
            <motion.section
              className="ai-chat-shell"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.34 }}
            >
              <button
                className="ai-close-btn"
                type="button"
                aria-label="Закрыть ИИ режим"
                onClick={() => {
                  setAiMode(false);
                  setAiAssistantEnabled(false);
                  if (activeTab === "chat") {
                    setActiveTab("home");
                  }
                }}
              >
                <img src={assets.group12021Icon} alt="" />
              </button>

              <div className="ai-suggestions">
                {QUICK_PROMPTS.map((prompt) => (
                  <button key={prompt} type="button" className="suggestion-pill" onClick={() => sendMessage(prompt)}>
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
                          <button key={action.label} type="button" onClick={() => sendMessage(action.prompt)}>
                            {action.label}
                          </button>
                        ))}
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>

              <form
                className="chat-input-wrap"
                onSubmit={(event) => {
                  event.preventDefault();
                  sendMessage(chatInput);
                }}
              >
                <button className="chat-logo-btn" type="button" onClick={() => sendMessage("Помоги начать обучение")}>
                  <img src={assets.sparklesMiniA} alt="" />
                  <img src={assets.sparklesMiniB} alt="" />
                </button>
                <input
                  value={chatInput}
                  onChange={(event) => setChatInput(event.target.value)}
                  placeholder="Спроси меня о чем нибудь..."
                  aria-label="Ввод сообщения"
                />
                <button className="chat-send-btn" type="submit" aria-label="Отправить">
                  <img src={assets.arrowSmallLeftIcon} alt="" />
                </button>
              </form>
            </motion.section>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
