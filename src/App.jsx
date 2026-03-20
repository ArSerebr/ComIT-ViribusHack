import { useEffect, useMemo, useRef, useState } from "react";
import { assets } from "./assets";
import { AiChatPanel } from "./components/chat/AiChatPanel";
import { ChatPage } from "./components/chat/ChatPage";
import { BottomCards } from "./components/dashboard/BottomCards";
import { SummaryCards } from "./components/dashboard/SummaryCards";
import { LibraryPage } from "./components/library/LibraryPage";
import { TopBar } from "./components/layout/TopBar";
import { NewsPage } from "./components/news/NewsPage";
import { ProjectDetailsPage } from "./components/projects/ProjectDetailsPage";
import { ProjectHubPage } from "./components/projects/ProjectHubPage";
import { RecommendationsPanel } from "./components/recommendations/RecommendationsPanel";
import { INITIAL_CHAT, NAV_LINKS, QUICK_PROMPTS, RECOMMENDATIONS } from "./data/dashboardData";
import {
  CHAT_PAGE_COMPOSER_PROMPTS,
  CHAT_PAGE_HERO_ACTIONS,
  CHAT_PAGE_HISTORY_ITEMS,
  CHAT_PAGE_STATUS_CARD
} from "./data/chatPageData";
import {
  createInitialLibraryInterestState,
  LIBRARY_ARTICLE_ITEMS,
  LIBRARY_HERO_RESOURCE,
  LIBRARY_INTEREST_OPTIONS,
  LIBRARY_SHOWCASE_ITEMS
} from "./data/libraryData";
import { PROJECT_DETAILS_BY_ID } from "./data/projectDetailsData";
import { FEATURED_NEWS_ITEMS, MINI_NEWS_ITEMS } from "./data/newsData";
import { PROJECT_HUB_COLUMNS } from "./data/projectHubData";
import { nextAssistantMessage } from "./utils/chatAssistant";

function mapRecommendationsWithInstanceId() {
  return RECOMMENDATIONS.map((item, index) => ({ ...item, instanceId: `${item.id}-${index}` }));
}

function resolvePathFromHash(hashValue) {
  return hashValue.replace(/^#/, "") || "/";
}

function resolveTabFromHash(hashValue) {
  const path = resolvePathFromHash(hashValue);

  if (path.startsWith(NAV_LINKS.news)) {
    return "news";
  }
  if (path.startsWith(NAV_LINKS.events)) {
    return "news";
  }
  if (path.startsWith(NAV_LINKS.projects)) {
    return "projects";
  }
  if (path.startsWith("/library")) {
    return "library";
  }
  if (path.startsWith(NAV_LINKS.chat)) {
    return "chat";
  }
  return "home";
}

function resolveProjectSlugFromPath(path) {
  const prefix = `${NAV_LINKS.projects}/`;
  if (!path.startsWith(prefix)) {
    return null;
  }

  const slug = path.slice(prefix.length).split("/")[0];
  if (!slug || slug === "create") {
    return null;
  }

  return slug;
}

function createInitialNewsLikes() {
  return MINI_NEWS_ITEMS.reduce((acc, item) => ({ ...acc, [item.id]: false }), {});
}

function App() {
  const [activeTab, setActiveTab] = useState(() => resolveTabFromHash(window.location.hash));
  const [currentPath, setCurrentPath] = useState(() => resolvePathFromHash(window.location.hash));
  const [aiAssistantEnabled, setAiAssistantEnabled] = useState(true);
  const [aiMode, setAiMode] = useState(true);
  const [isDeckOpen, setIsDeckOpen] = useState(false);
  const [activeLibraryShowcaseIndex, setActiveLibraryShowcaseIndex] = useState(0);
  const [selectedLibraryInterests, setSelectedLibraryInterests] = useState(createInitialLibraryInterestState);
  const [likedNews, setLikedNews] = useState(createInitialNewsLikes);
  const [likedRecommendations, setLikedRecommendations] = useState({});
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState(INITIAL_CHAT);
  const [deck, setDeck] = useState(mapRecommendationsWithInstanceId);
  const [dismissDirection, setDismissDirection] = useState(null);

  const chatListRef = useRef(null);

  const topCard = deck[0];
  const stackedCards = deck.slice(1, 3);
  const canDismiss = !dismissDirection;
  const isNewsPage = activeTab === "news";
  const isProjectsPage = activeTab === "projects";
  const isLibraryPage = activeTab === "library";
  const isChatPage = activeTab === "chat";
  const currentProjectSlug = resolveProjectSlugFromPath(currentPath);
  const currentProjectDetails = currentProjectSlug ? PROJECT_DETAILS_BY_ID[currentProjectSlug] : null;
  const isProjectDetailPage = Boolean(currentProjectDetails);
  const usesOverlayHeader = isNewsPage || isProjectsPage || isLibraryPage || isChatPage;
  const homeNewsItem = MINI_NEWS_ITEMS[0];
  const chatPageMessages = messages.some((message) => message.role === "user") ? messages.slice(1) : [];

  const navigateTo = (path) => {
    setCurrentPath(path);
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

  const toggleNewsLike = (newsId) => {
    setLikedNews((prev) => {
      const next = !prev[newsId];
      sendLikeSignal("news", newsId);
      return { ...prev, [newsId]: next };
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

  const openNewsList = () => {
    setActiveTab("news");
    navigateTo(NAV_LINKS.news);
  };

  const openProjectsHub = () => {
    setActiveTab("projects");
    navigateTo(NAV_LINKS.projects);
  };

  const openLibraryPage = () => {
    setActiveTab("library");
    navigateTo("/library");
  };

  const openMiniNews = (newsItem) => {
    setActiveTab("news");
    navigateTo(newsItem?.detailsUrl || NAV_LINKS.news);
  };

  const openProjectDetails = (project) => {
    setActiveTab("projects");
    navigateTo(project?.detailsUrl || NAV_LINKS.projects);
  };

  const openProjectCreate = () => {
    setActiveTab("projects");
    navigateTo(`${NAV_LINKS.projects}/create`);
  };

  const joinProject = () => {
    // API hook placeholder
  };

  const cycleLibraryShowcase = (direction) => {
    setActiveLibraryShowcaseIndex((prev) => {
      const offset = direction === "prev" ? -1 : 1;
      return (prev + offset + LIBRARY_SHOWCASE_ITEMS.length) % LIBRARY_SHOWCASE_ITEMS.length;
    });
  };

  const toggleLibraryInterest = (interestId) => {
    setSelectedLibraryInterests((prev) => ({
      ...prev,
      [interestId]: !prev[interestId]
    }));
  };

  const saveLibraryInterests = () => {
    const selectedIds = Object.entries(selectedLibraryInterests)
      .filter(([, isSelected]) => isSelected)
      .map(([id]) => id);

    const payload = JSON.stringify({ interests: selectedIds, ts: Date.now() });

    try {
      if (navigator.sendBeacon) {
        const blob = new Blob([payload], { type: "application/json" });
        navigator.sendBeacon("/api/library/interests", blob);
      }
    } catch {
      // no-op
    }
  };

  const openFeaturedEvent = (eventItem) => {
    navigateTo(eventItem?.detailsUrl || NAV_LINKS.events);
  };

  const handleAiMenuClick = () => {
    if (!aiAssistantEnabled) {
      setAiAssistantEnabled(true);
      setAiMode(true);
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
        openLibraryPage();
        break;
      default:
        break;
    }
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

  useEffect(() => {
    const syncTabWithHash = () => {
      setCurrentPath(resolvePathFromHash(window.location.hash));
      setActiveTab(resolveTabFromHash(window.location.hash));
    };

    window.addEventListener("hashchange", syncTabWithHash);
    return () => window.removeEventListener("hashchange", syncTabWithHash);
  }, []);

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
      navigateTo("/");
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
        <div className={`app-shell ${usesOverlayHeader ? "app-shell-news" : ""}`}>
          <img className="bg-shape bg-shape-top" src={assets.backgroundShape} alt="" />
          <img className="bg-shape bg-shape-bottom" src={assets.backgroundShape} alt="" />

          <TopBar
            activeTab={activeTab}
            aiAssistantEnabled={aiAssistantEnabled}
            onGoHome={handleGoHome}
            onMenuClick={handleMenuClick}
            isNewsView={usesOverlayHeader}
          />

          <main className={`dashboard-layout ${usesOverlayHeader ? "dashboard-layout-news" : ""}`}>
            {isNewsPage ? (
              <NewsPage
                miniNewsItems={MINI_NEWS_ITEMS}
                featuredNewsItems={FEATURED_NEWS_ITEMS}
                likedNews={likedNews}
                onToggleNewsLike={toggleNewsLike}
                onOpenMiniNews={openMiniNews}
                onParticipateInEvent={openFeaturedEvent}
                onBack={handleGoHome}
              />
            ) : isProjectsPage && isProjectDetailPage ? (
              <ProjectDetailsPage
                project={currentProjectDetails}
                onBack={openProjectsHub}
                onJoinProject={joinProject}
              />
            ) : isProjectsPage ? (
              <ProjectHubPage
                columns={PROJECT_HUB_COLUMNS}
                onBack={handleGoHome}
                onCreateProject={openProjectCreate}
                onOpenProject={openProjectDetails}
              />
            ) : isLibraryPage ? (
              <LibraryPage
                heroItem={LIBRARY_HERO_RESOURCE}
                showcaseItems={LIBRARY_SHOWCASE_ITEMS}
                activeShowcaseIndex={activeLibraryShowcaseIndex}
                interestOptions={LIBRARY_INTEREST_OPTIONS}
                selectedInterests={selectedLibraryInterests}
                articleItems={LIBRARY_ARTICLE_ITEMS}
                onBack={handleGoHome}
                onPrevShowcase={() => cycleLibraryShowcase("prev")}
                onNextShowcase={() => cycleLibraryShowcase("next")}
                onToggleInterest={toggleLibraryInterest}
                onSaveInterests={saveLibraryInterests}
              />
            ) : isChatPage ? (
              <ChatPage
                historyItems={CHAT_PAGE_HISTORY_ITEMS}
                composerPrompts={CHAT_PAGE_COMPOSER_PROMPTS}
                heroActions={CHAT_PAGE_HERO_ACTIONS}
                statusCard={CHAT_PAGE_STATUS_CARD}
                messages={chatPageMessages}
                chatInput={chatInput}
                chatListRef={chatListRef}
                onClose={handleCloseAi}
                onSendMessage={sendMessage}
                onChangeChatInput={setChatInput}
                onSubmit={handleChatSubmit}
              />
            ) : (
              <section className="left-content">
                <h1 className="page-title">Главная панель</h1>
                <SummaryCards
                  onOpenCourses={() => navigateTo(NAV_LINKS.courses)}
                  onOpenCourseDetails={() => navigateTo("/courses/data-science-ml")}
                  onOpenEvents={() => navigateTo(NAV_LINKS.events)}
                />
                <BottomCards
                  newsItem={homeNewsItem}
                  isNewsLiked={Boolean(likedNews[homeNewsItem.id])}
                  onToggleNewsLike={toggleNewsLike}
                  onOpenNews={openNewsList}
                  onOpenProjects={openProjectsHub}
                />
              </section>
            )}
          </main>

          {!usesOverlayHeader ? (
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
          ) : null}
        </div>

        <AiChatPanel
          isVisible={aiMode && !isProjectDetailPage && !isLibraryPage && !isChatPage}
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
