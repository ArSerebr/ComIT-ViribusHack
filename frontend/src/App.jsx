import { useQuery } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import { apiClient, resolveApiUrl } from "./api/client";
import {
  fetchDashboardHome,
  fetchDashboardRecommendations,
  fetchLibraryBundle,
  fetchNewsFeatured,
  fetchNewsMini,
  fetchNotifications,
  fetchProjectById,
  fetchProjectsHub,
  postLibraryInterests,
  postRecommendationLike
} from "./api/publicApi";
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
import { NOTIFICATION_ITEMS } from "./data/notificationsData";
import { FEATURED_NEWS_ITEMS, mapApiFeaturedNews, mapApiMiniNews, MINI_NEWS_ITEMS } from "./data/newsData";
import { PROJECT_HUB_COLUMNS } from "./data/projectHubData";
import { nextAssistantMessage } from "./utils/chatAssistant";

/** When not `"false"`, failed API requests fall back to `src/data/*` demo content (hackathon default). */
const STATIC_FALLBACK = import.meta.env.VITE_API_STATIC_FALLBACK !== "false";

function mapRecommendationsWithInstanceId() {
  return RECOMMENDATIONS.map((item, index) => ({ ...item, instanceId: `${item.id}-${index}` }));
}

function resolvePathFromHash(hashValue) {
  return hashValue.replace(/^#/, "") || "/";
}

function resolveTabFromPath(path) {
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

function resolveTabFromHash(hashValue) {
  return resolveTabFromPath(resolvePathFromHash(hashValue));
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

const PAGE_ORDER = ["home", "projects", "news", "library", "chat"];

const PAGE_STAGE_VARIANTS = {
  enter: (direction) => ({
    opacity: 0,
    x: direction === 0 ? 0 : direction > 0 ? 56 : -56,
    y: direction === 0 ? 14 : 0,
    filter: "blur(10px)"
  }),
  center: {
    opacity: 1,
    x: 0,
    y: 0,
    filter: "blur(0px)"
  },
  exit: (direction) => ({
    opacity: 0,
    x: direction === 0 ? 0 : direction > 0 ? -56 : 56,
    y: direction === 0 ? -12 : 0,
    filter: "blur(8px)"
  })
};

const PAGE_STAGE_TRANSITION = {
  type: "spring",
  stiffness: 320,
  damping: 30,
  mass: 0.9
};

function resolveRouteDepth(path) {
  return path.split("/").filter(Boolean).length;
}

function resolveRouteDirection(previousRoute, nextRoute) {
  if (!previousRoute || previousRoute.path === nextRoute.path) {
    return 0;
  }

  if (previousRoute.tab === nextRoute.tab) {
    const previousDepth = resolveRouteDepth(previousRoute.path);
    const nextDepth = resolveRouteDepth(nextRoute.path);

    if (previousDepth !== nextDepth) {
      return nextDepth > previousDepth ? 1 : -1;
    }

    return nextRoute.path > previousRoute.path ? 1 : -1;
  }

  const previousIndex = PAGE_ORDER.indexOf(previousRoute.tab);
  const nextIndex = PAGE_ORDER.indexOf(nextRoute.tab);

  if (previousIndex === -1 || nextIndex === -1) {
    return 1;
  }

  return nextIndex > previousIndex ? 1 : -1;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function createInitialNewsLikes() {
  return MINI_NEWS_ITEMS.reduce((acc, item) => ({ ...acc, [item.id]: false }), {});
}

function normalizeNotificationItem(item) {
  const type =
    item.type === "invite" || item.type === "article"
      ? item.type
      : item.type === "project_invite"
        ? "invite"
        : "article";
  return { ...item, type };
}

function App() {
  const [activeTab, setActiveTab] = useState(() => resolveTabFromHash(window.location.hash));
  const [currentPath, setCurrentPath] = useState(() => resolvePathFromHash(window.location.hash));
  const [aiAssistantEnabled, setAiAssistantEnabled] = useState(false);
  const [aiMode, setAiMode] = useState(false);
  const [isAiResponding, setIsAiResponding] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isDeckOpen, setIsDeckOpen] = useState(false);
  const [activeLibraryShowcaseIndex, setActiveLibraryShowcaseIndex] = useState(0);
  const [selectedLibraryInterests, setSelectedLibraryInterests] = useState(createInitialLibraryInterestState);
  const [libraryShowcaseDirection, setLibraryShowcaseDirection] = useState(1);
  const [likedNews, setLikedNews] = useState(createInitialNewsLikes);
  const [likedRecommendations, setLikedRecommendations] = useState({});
  const [chatInput, setChatInput] = useState("");
  const [messages, setMessages] = useState(INITIAL_CHAT);
  const [deck, setDeck] = useState(mapRecommendationsWithInstanceId);
  const [dismissDirection, setDismissDirection] = useState(null);
  const [pageTransitionDirection, setPageTransitionDirection] = useState(0);

  const chatListRef = useRef(null);
  const pendingAssistantRepliesRef = useRef(0);
  const routeStateRef = useRef({ tab: activeTab, path: currentPath });
  const libraryInterestsSyncedRef = useRef(false);

  const isHomePage = activeTab === "home";
  const isNewsPage = activeTab === "news";
  const isProjectsPage = activeTab === "projects";
  const isLibraryPage = activeTab === "library";
  const isChatPage = activeTab === "chat";
  const currentProjectSlug = resolveProjectSlugFromPath(currentPath);

  const dashboardHomeQuery = useQuery({
    queryKey: ["dashboard", "home"],
    queryFn: fetchDashboardHome,
    staleTime: 60_000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["dashboard", "recommendations"],
    queryFn: fetchDashboardRecommendations,
    staleTime: 60_000,
  });

  const newsMiniQuery = useQuery({
    queryKey: ["news", "mini"],
    queryFn: fetchNewsMini,
    staleTime: 60_000,
  });

  const newsFeaturedQuery = useQuery({
    queryKey: ["news", "featured"],
    queryFn: fetchNewsFeatured,
    staleTime: 60_000,
  });

  const notificationsQuery = useQuery({
    queryKey: ["notifications"],
    queryFn: fetchNotifications,
    staleTime: 30_000,
  });

  const projectsHubQuery = useQuery({
    queryKey: ["projects", "hub"],
    queryFn: fetchProjectsHub,
    staleTime: 60_000,
  });

  const libraryQuery = useQuery({
    queryKey: ["library"],
    queryFn: fetchLibraryBundle,
    enabled: isLibraryPage,
    staleTime: 60_000,
  });

  const projectDetailsQuery = useQuery({
    queryKey: ["projects", "detail", currentProjectSlug],
    queryFn: () => fetchProjectById(currentProjectSlug),
    enabled: Boolean(isProjectsPage && currentProjectSlug),
    staleTime: 60_000,
  });

  const miniNewsItems = (() => {
    if (newsMiniQuery.isError) {
      return STATIC_FALLBACK ? MINI_NEWS_ITEMS : [];
    }
    const mapped = mapApiMiniNews(newsMiniQuery.data ?? []);
    if (mapped.length) return mapped;
    return STATIC_FALLBACK ? MINI_NEWS_ITEMS : [];
  })();

  const featuredNewsItems = (() => {
    if (newsFeaturedQuery.isError) {
      return STATIC_FALLBACK ? FEATURED_NEWS_ITEMS : [];
    }
    const mapped = mapApiFeaturedNews(newsFeaturedQuery.data ?? []);
    if (mapped.length) return mapped;
    return STATIC_FALLBACK ? FEATURED_NEWS_ITEMS : [];
  })();

  const notificationItems = (() => {
    if (notificationsQuery.isError) {
      return STATIC_FALLBACK ? NOTIFICATION_ITEMS.map(normalizeNotificationItem) : [];
    }
    return (notificationsQuery.data ?? []).map(normalizeNotificationItem);
  })();

  const hubColumnsRaw = (() => {
    if (projectsHubQuery.isError) {
      return STATIC_FALLBACK ? PROJECT_HUB_COLUMNS : [];
    }
    const data = projectsHubQuery.data;
    if (data && data.length > 0) return data;
    if (projectsHubQuery.isPending && !STATIC_FALLBACK) {
      return [];
    }
    return STATIC_FALLBACK ? PROJECT_HUB_COLUMNS : [];
  })();
  const hubColumns = hubColumnsRaw.map((column) => ({
    ...column,
    projects: column.projects.map((project) => ({
      ...project,
      teamAvatarUrl: project.teamAvatarUrl || assets.avatarPhoto,
    })),
  }));

  const summaryHome =
    dashboardHomeQuery.isError && !STATIC_FALLBACK ? null : dashboardHomeQuery.data;

  const newsPageLoading =
    !STATIC_FALLBACK &&
    ((newsMiniQuery.isPending && newsMiniQuery.data === undefined) ||
      (newsFeaturedQuery.isPending && newsFeaturedQuery.data === undefined));

  const showNewsOfflineNotice =
    STATIC_FALLBACK && (newsMiniQuery.isError || newsFeaturedQuery.isError);

  const recommendationsDeckLoading =
    recommendationsQuery.isPending &&
    recommendationsQuery.data === undefined &&
    !STATIC_FALLBACK;

  const libraryPageLoading =
    isLibraryPage &&
    libraryQuery.isPending &&
    libraryQuery.data === undefined &&
    !STATIC_FALLBACK;

  const showLibraryOfflineNotice = STATIC_FALLBACK && libraryQuery.isError;

  const firstHubProject = hubColumns[0]?.projects?.[0];
  const projectHighlight = firstHubProject
    ? {
        title: firstHubProject.title,
        detailsUrl: firstHubProject.detailsUrl || `${NAV_LINKS.projects}/${firstHubProject.id}`,
        updatedLabel: firstHubProject.updatedLabel,
      }
    : null;

  const libraryBundle = libraryQuery.isError ? null : libraryQuery.data;
  const libraryShowcaseItems =
    libraryBundle?.showcaseItems?.length > 0
      ? libraryBundle.showcaseItems
      : STATIC_FALLBACK
        ? LIBRARY_SHOWCASE_ITEMS
        : [];
  const libraryInterestOptionsFromApi =
    libraryBundle?.interestOptions?.length > 0
      ? libraryBundle.interestOptions
      : STATIC_FALLBACK
        ? LIBRARY_INTEREST_OPTIONS
        : [];
  const libraryArticleItems =
    libraryBundle?.articles?.length > 0
      ? libraryBundle.articles.map((article) => ({
          ...article,
          authorAvatarUrl: article.authorAvatarUrl?.trim() ? article.authorAvatarUrl : assets.avatarPhoto,
        }))
      : STATIC_FALLBACK
        ? LIBRARY_ARTICLE_ITEMS
        : [];

  const topCard = deck[0];
  const stackedCards = deck.slice(1, 3);
  const canDismiss = !dismissDirection;
  const showProjectDetailRoute = Boolean(currentProjectSlug);
  const homeNewsItem = miniNewsItems[0];
  const chatPageMessages = messages.some((message) => message.role === "user") ? messages.slice(1) : [];
  const activeLibraryHero = libraryShowcaseItems[activeLibraryShowcaseIndex]?.hero || LIBRARY_HERO_RESOURCE;
  const shouldShowAiPopup = aiMode;
  const mainContentKey = activeTab === "projects" || activeTab === "chat" ? currentPath : activeTab;

  useEffect(() => {
    const items = recommendationsQuery.data;
    if (items?.length) {
      setDeck(items.map((item, index) => ({ ...item, instanceId: `${item.id}-${index}` })));
    }
  }, [recommendationsQuery.data]);

  useEffect(() => {
    if (!libraryBundle?.interestOptions?.length || libraryInterestsSyncedRef.current) {
      return;
    }
    setSelectedLibraryInterests(
      libraryBundle.interestOptions.reduce((acc, option) => ({ ...acc, [option.id]: option.selected }), {}),
    );
    libraryInterestsSyncedRef.current = true;
  }, [libraryBundle]);

  useEffect(() => {
    if (!libraryShowcaseItems.length) {
      return;
    }
    setActiveLibraryShowcaseIndex((prev) => (prev < libraryShowcaseItems.length ? prev : 0));
  }, [libraryShowcaseItems.length]);

  const syncRouteState = (path) => {
    const nextRoute = {
      tab: resolveTabFromPath(path),
      path
    };

    setPageTransitionDirection(resolveRouteDirection(routeStateRef.current, nextRoute));
    routeStateRef.current = nextRoute;
    setCurrentPath(path);
    setActiveTab(nextRoute.tab);
  };

  const navigateTo = (path) => {
    setIsNotificationsOpen(false);
    syncRouteState(path);
    window.location.hash = path;
  };

  const openPath = (path) => {
    navigateTo(path);
  };

  const setAssistantPendingDelta = (delta) => {
    pendingAssistantRepliesRef.current = Math.max(0, pendingAssistantRepliesRef.current + delta);
    setIsAiResponding(pendingAssistantRepliesRef.current > 0);
  };

  const resetAssistantPendingState = () => {
    pendingAssistantRepliesRef.current = 0;
    setIsAiResponding(false);
  };

  const sendLikeSignal = (entity, id) => {
    const body = { entity, id, ts: Date.now() };
    if (typeof fetch !== "function") {
      try {
        if (typeof navigator !== "undefined" && navigator.sendBeacon) {
          const blob = new Blob([JSON.stringify(body)], { type: "application/json" });
          navigator.sendBeacon(resolveApiUrl("/api/recommendations/like"), blob);
        }
      } catch {
        // no-op
      }
      return;
    }
    void postRecommendationLike(body).catch(() => {});
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

  const dismissTopCard = (gesture) => {
    if (!canDismiss) {
      return;
    }

    if (typeof gesture === "string") {
      const presets = {
        left: { x: -220, y: 42 },
        right: { x: 220, y: 42 },
        down: { x: 0, y: 240 },
        up: { x: 0, y: -240 }
      };

      setDismissDirection(presets[gesture] || { x: 220, y: 42 });
      return;
    }

    setDismissDirection(gesture);
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
    openPath(NAV_LINKS.news);
  };

  const openProjectsHub = () => {
    openPath(NAV_LINKS.projects);
  };

  const openLibraryPage = () => {
    openPath("/library");
  };

  const openMiniNews = (newsItem) => {
    openPath(newsItem?.detailsUrl || NAV_LINKS.news);
  };

  const openProjectDetails = (project) => {
    openPath(project?.detailsUrl || NAV_LINKS.projects);
  };

  const openProjectCreate = () => {
    openPath(`${NAV_LINKS.projects}/create`);
  };

  const joinProject = async (project) => {
    const projectId = project?.id;
    if (!projectId) {
      return;
    }
    const { error } = await apiClient.POST("/api/projects/{project_id}/join", {
      params: { path: { project_id: projectId } },
      body: { message: null },
    });
    if (error) {
      window.alert("Не удалось отправить заявку. Попробуйте позже.");
    }
  };

  const cycleLibraryShowcase = (direction) => {
    setLibraryShowcaseDirection(direction === "prev" ? -1 : 1);
    setActiveLibraryShowcaseIndex((prev) => {
      const offset = direction === "prev" ? -1 : 1;
      const len = libraryShowcaseItems.length || 1;
      return (prev + offset + len) % len;
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

    const body = { interests: selectedIds, ts: Date.now() };

    if (typeof fetch !== "function") {
      try {
        if (typeof navigator !== "undefined" && navigator.sendBeacon) {
          const blob = new Blob([JSON.stringify(body)], { type: "application/json" });
          navigator.sendBeacon(resolveApiUrl("/api/library/interests"), blob);
        }
      } catch {
        // no-op
      }
      return;
    }
    void postLibraryInterests(body).catch(() => {});
  };

  const openFeaturedEvent = (eventItem) => {
    openPath(eventItem?.detailsUrl || NAV_LINKS.events);
  };

  const closeAiExperience = (navigateHome = false) => {
    setAiMode(false);
    setAiAssistantEnabled(false);
    resetAssistantPendingState();

    if (navigateHome && activeTab === "chat") {
      openPath("/");
    }
  };

  const handleAiMenuClick = () => {
    setIsNotificationsOpen(false);

    if (aiMode) {
      closeAiExperience(activeTab === "chat");
      return;
    }

    setAiAssistantEnabled(true);
    setAiMode(true);
  };

  const handleOpenNotification = (notificationItem) => {
    if (notificationItem.path) {
      openPath(notificationItem.path);
      return;
    }

    setIsNotificationsOpen(false);
  };

  const handleMenuClick = (itemId) => {
    if (itemId === "ai") {
      handleAiMenuClick();
      return;
    }

    switch (itemId) {
      case "home":
        openPath("/");
        break;
      case "projects":
        openPath(NAV_LINKS.projects);
        break;
      case "news":
        openPath(NAV_LINKS.news);
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

    setAiAssistantEnabled(true);
    setAiMode(true);
    setMessages((prev) => [...prev, userMessage]);
    setChatInput("");
    setAssistantPendingDelta(1);

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
      setAssistantPendingDelta(-1);
    }, 260);
  };

  useEffect(() => {
    if (chatListRef.current) {
      chatListRef.current.scrollTop = chatListRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    const syncTabWithHash = () => {
      const nextPath = resolvePathFromHash(window.location.hash);

      if (nextPath === routeStateRef.current.path) {
        return;
      }

      setIsNotificationsOpen(false);
      syncRouteState(nextPath);
    };

    window.addEventListener("hashchange", syncTabWithHash);
    return () => window.removeEventListener("hashchange", syncTabWithHash);
  }, []);

  const topCardExitAnimation = useMemo(() => {
    if (!dismissDirection) {
      return { x: 0, y: 0, rotate: 0, opacity: 1, scale: 1 };
    }

    if (typeof dismissDirection === "string") {
      if (dismissDirection === "right") {
        return { x: 760, y: 120, rotate: 22, opacity: 0, scale: 0.96 };
      }
      if (dismissDirection === "left") {
        return { x: -760, y: 120, rotate: -22, opacity: 0, scale: 0.96 };
      }
      if (dismissDirection === "down") {
        return { x: 0, y: 760, rotate: 12, opacity: 0, scale: 0.96 };
      }
      if (dismissDirection === "up") {
        return { x: 0, y: -760, rotate: -12, opacity: 0, scale: 0.96 };
      }
    }

    const offsetX = dismissDirection.x || 0;
    const offsetY = dismissDirection.y || 0;
    const magnitude = Math.max(1, Math.hypot(offsetX, offsetY));
    const normalizedX = offsetX / magnitude;
    const normalizedY = offsetY / magnitude;

    return {
      x: offsetX + normalizedX * 880,
      y: offsetY + normalizedY * 880,
      rotate: clamp(offsetX / 16 + offsetY / 28, -26, 26),
      opacity: 0,
      scale: 0.96
    };
  }, [dismissDirection]);

  const handleGoHome = () => {
    openPath("/");
  };

  const handleCloseAiOverlay = () => {
    closeAiExperience(false);
  };

  const handleCloseAiPage = () => {
    closeAiExperience(true);
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

  const mainContent = isNewsPage ? (
    <NewsPage
      miniNewsItems={miniNewsItems}
      featuredNewsItems={featuredNewsItems}
      likedNews={likedNews}
      onToggleNewsLike={toggleNewsLike}
      onOpenMiniNews={openMiniNews}
      onParticipateInEvent={openFeaturedEvent}
      onBack={handleGoHome}
      isLoading={newsPageLoading}
      showOfflineFallbackNotice={showNewsOfflineNotice}
    />
  ) : isProjectsPage && showProjectDetailRoute ? (
    projectDetailsQuery.isLoading ? (
      <section className="project-details-page">
        <div className="library-page-head">
          <button type="button" className="news-back-btn" aria-label="Назад к проектам" onClick={openProjectsHub}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <p className="page-title">Загрузка проекта…</p>
        </div>
      </section>
    ) : projectDetailsQuery.isError ? (
      <section className="project-details-page">
        <div className="library-page-head">
          <button type="button" className="news-back-btn" aria-label="Назад к проектам" onClick={openProjectsHub}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <p className="page-title">Проект не найден или недоступен.</p>
        </div>
      </section>
    ) : (
      <ProjectDetailsPage
        project={projectDetailsQuery.data}
        onBack={openProjectsHub}
        onJoinProject={joinProject}
      />
    )
  ) : isProjectsPage ? (
    <ProjectHubPage
      columns={hubColumns}
      onBack={handleGoHome}
      onCreateProject={openProjectCreate}
      onOpenProject={openProjectDetails}
      isLoading={projectsHubQuery.isPending && !STATIC_FALLBACK}
      isError={projectsHubQuery.isError}
      useStaticFallback={STATIC_FALLBACK}
    />
  ) : isLibraryPage ? (
    <LibraryPage
      heroItem={activeLibraryHero}
      showcaseItems={libraryShowcaseItems}
      activeShowcaseIndex={activeLibraryShowcaseIndex}
      showcaseDirection={libraryShowcaseDirection}
      interestOptions={libraryInterestOptionsFromApi}
      selectedInterests={selectedLibraryInterests}
      articleItems={libraryArticleItems}
      onBack={handleGoHome}
      onPrevShowcase={() => cycleLibraryShowcase("prev")}
      onNextShowcase={() => cycleLibraryShowcase("next")}
      onToggleInterest={toggleLibraryInterest}
      onSaveInterests={saveLibraryInterests}
      isLoading={libraryPageLoading}
      showOfflineFallbackNotice={showLibraryOfflineNotice}
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
      onClose={handleCloseAiPage}
      onSendMessage={sendMessage}
      onChangeChatInput={setChatInput}
      onSubmit={handleChatSubmit}
    />
  ) : (
    <section className="left-content">
      <h1 className="page-title">Главная панель</h1>
      <SummaryCards
        home={summaryHome}
        isLoading={dashboardHomeQuery.isLoading}
        isError={dashboardHomeQuery.isError}
        useStaticFallback={STATIC_FALLBACK}
        onOpenCourses={() => navigateTo(NAV_LINKS.courses)}
        onOpenCourseDetails={(path) => navigateTo(path || "/courses/data-science-ml")}
        onOpenEvents={() => navigateTo(NAV_LINKS.events)}
      />
      <BottomCards
        newsItem={homeNewsItem}
        projectHighlight={projectHighlight}
        isNewsLiked={Boolean(homeNewsItem && likedNews[homeNewsItem.id])}
        onToggleNewsLike={toggleNewsLike}
        onOpenNews={openNewsList}
        onOpenProjects={openProjectsHub}
        onOpenProjectLink={openProjectDetails}
        isNewsLoading={newsMiniQuery.isPending && !STATIC_FALLBACK}
        isNewsError={newsMiniQuery.isError}
        useStaticFallback={STATIC_FALLBACK}
      />
    </section>
  );

  return (
    <div className="viewport-frame">
      <div className="design-canvas">
        <div className="app-shell app-shell-news">
          <motion.img
            className="bg-shape bg-shape-top"
            src={assets.backgroundShape}
            alt=""
            animate={{ x: [0, 28, 0], y: [0, -18, 0], rotate: [4.07, 6.3, 4.07] }}
            transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.img
            className="bg-shape bg-shape-bottom"
            src={assets.backgroundShape}
            alt=""
            animate={{ x: [0, -34, 0], y: [0, 24, 0], rotate: [156, 152, 156] }}
            transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          />

          <TopBar
            activeTab={activeTab}
            aiAssistantEnabled={aiAssistantEnabled}
            isAiOpen={aiMode}
            isNotificationsOpen={isNotificationsOpen}
            notificationItems={notificationItems}
            onCloseNotifications={() => setIsNotificationsOpen(false)}
            onGoHome={handleGoHome}
            onMenuClick={handleMenuClick}
            onOpenNotification={handleOpenNotification}
            onToggleNotifications={() => setIsNotificationsOpen((prev) => !prev)}
            isNewsView
          />

          <main className="dashboard-layout dashboard-layout-news">
            <AnimatePresence mode="wait" initial={false} custom={pageTransitionDirection}>
              <motion.div
                key={mainContentKey}
                className={`page-stage ${isHomePage ? "page-stage-home" : ""}`}
                custom={pageTransitionDirection}
                variants={PAGE_STAGE_VARIANTS}
                initial="enter"
                animate="center"
                exit="exit"
                transition={PAGE_STAGE_TRANSITION}
              >
                {mainContent}
              </motion.div>
            </AnimatePresence>
          </main>

          {isHomePage ? (
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
              isLoading={recommendationsDeckLoading}
            />
          ) : null}
        </div>

        <AnimatePresence>
          {shouldShowAiPopup ? (
            <AiChatPanel
              isVisible={shouldShowAiPopup}
              isAgentActive={isAiResponding}
              quickPrompts={QUICK_PROMPTS}
              messages={messages}
              chatInput={chatInput}
              chatListRef={chatListRef}
              onClose={handleCloseAiOverlay}
              onSendMessage={sendMessage}
              onChangeChatInput={setChatInput}
              onSubmit={handleChatSubmit}
            />
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
