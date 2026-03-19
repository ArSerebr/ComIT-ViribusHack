import { useEffect, useMemo, useRef, useState } from "react";
import { assets } from "./assets";
import { AiChatPanel } from "./components/chat/AiChatPanel";
import { BottomCards } from "./components/dashboard/BottomCards";
import { SummaryCards } from "./components/dashboard/SummaryCards";
import { TopBar } from "./components/layout/TopBar";
import { RecommendationsPanel } from "./components/recommendations/RecommendationsPanel";
import { INITIAL_CHAT, NAV_LINKS, QUICK_PROMPTS, RECOMMENDATIONS } from "./data/dashboardData";
import { nextAssistantMessage } from "./utils/chatAssistant";

function mapRecommendationsWithInstanceId() {
  return RECOMMENDATIONS.map((item, index) => ({ ...item, instanceId: `${item.id}-${index}` }));
}

function App() {
  const [activeTab, setActiveTab] = useState("home");
  const [aiAssistantEnabled, setAiAssistantEnabled] = useState(true);
  const [aiMode, setAiMode] = useState(true);
  const [isDeckOpen, setIsDeckOpen] = useState(false);
  const [newsLiked, setNewsLiked] = useState(false);
  const [likedRecommendations, setLikedRecommendations] = useState({});
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState(INITIAL_CHAT);
  const [deck, setDeck] = useState(mapRecommendationsWithInstanceId);
  const [dismissDirection, setDismissDirection] = useState(null);

  const chatListRef = useRef(null);

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

  const handleGoHome = () => {
    setActiveTab("home");
    navigateTo("/");
  };

  const handleCloseAi = () => {
    setAiMode(false);
    setAiAssistantEnabled(false);
    if (activeTab === "chat") {
      setActiveTab("home");
    }
  };

  const handleChatSubmit = (event) => {
    event.preventDefault();
    sendMessage(chatInput);
  };

  const handleTopCardExitComplete = () => {
    if (dismissDirection) {
      rotateDeck();
      setDismissDirection(null);
    }
  };

  return (
    <div className="viewport-frame">
      <div className="design-canvas">
        <div className="app-shell">
          <img className="bg-shape bg-shape-top" src={assets.backgroundShape} alt="" />
          <img className="bg-shape bg-shape-bottom" src={assets.backgroundShape} alt="" />

          <TopBar
            activeTab={activeTab}
            aiAssistantEnabled={aiAssistantEnabled}
            onGoHome={handleGoHome}
            onMenuClick={handleMenuClick}
          />

          <main className="dashboard-layout">
            <section className="left-content">
              <h1 className="page-title">Главная панель</h1>
              <SummaryCards
                onOpenCourses={() => navigateTo(NAV_LINKS.courses)}
                onOpenCourseDetails={() => navigateTo("/courses/data-science-ml")}
                onOpenEvents={() => navigateTo(NAV_LINKS.events)}
              />
              <BottomCards
                newsLiked={newsLiked}
                onToggleNewsLike={toggleNewsLike}
                onOpenNews={() => navigateTo("/news/yandex-meetup")}
                onOpenProjects={() => navigateTo(NAV_LINKS.projects)}
              />
            </section>
          </main>

          <RecommendationsPanel
            isOpen={isDeckOpen}
            onToggleOpen={() => setIsDeckOpen((prev) => !prev)}
            onClose={() => setIsDeckOpen(false)}
            stackedCards={stackedCards}
            topCard={topCard}
            canDismiss={canDismiss}
            dismissDirection={dismissDirection}
            topCardExitAnimation={topCardExitAnimation}
            onDismissTopCard={dismissTopCard}
            onTopCardExitComplete={handleTopCardExitComplete}
            likedRecommendations={likedRecommendations}
            onToggleRecommendationLike={toggleRecommendationLike}
            onShareRecommendation={shareRecommendation}
          />
        </div>

        <AiChatPanel
          isVisible={aiMode}
          quickPrompts={QUICK_PROMPTS}
          messages={messages}
          chatInput={chatInput}
          chatListRef={chatListRef}
          onClose={handleCloseAi}
          onSendMessage={sendMessage}
          onChangeChatInput={setChatInput}
          onSubmit={handleChatSubmit}
        />
      </div>
    </div>
  );
}

export default App;
