import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import { apiClient, resolveApiUrl } from "./api/client";
import {
  fetchDashboardHome,
  fetchDashboardRecommendations,
  fetchCurrentUserProfile,
  fetchLibraryBundle,
  fetchNewsFeatured,
  fetchNewsMini,
  fetchNotifications,
  createLibraryArticle,
  createProject,
  fetchUniversities,
  formatOpenApiError,
  fetchProfileMe,
  fetchProjectById,
  fetchProjectsHub,
  loginWithPassword,
  logoutCurrentUser,
  patchCurrentUserProfile,
  patchProfileMe,
  postFeaturedParticipate,
  postLibraryInterests,
  postRecommendationLike,
  registerWithEmail
} from "./api/publicApi";
import { ArticleCreatePage } from "./components/articles/ArticleCreatePage";
import { ArticleReaderPage } from "./components/articles/ArticleReaderPage";
import { AuthPage } from "./components/auth/AuthPage";
import { assets } from "./assets";
import { AiChatPanel } from "./components/chat/AiChatPanel";
import { ChatPage } from "./components/chat/ChatPage";
import { BottomCards } from "./components/dashboard/BottomCards";
import { SummaryCards } from "./components/dashboard/SummaryCards";
import { LibraryPage } from "./components/library/LibraryPage";
import { MobileShell } from "./components/layout/MobileShell";
import { TopBar } from "./components/layout/TopBar";
import { NewsPage } from "./components/news/NewsPage";
import { ProfilePage } from "./components/profile/ProfilePage";
import { ProjectDetailsPage } from "./components/projects/ProjectDetailsPage";
import { ProjectCreatePage } from "./components/projects/ProjectCreatePage";
import { ProjectHubPage } from "./components/projects/ProjectHubPage";
import { RecommendationsPanel } from "./components/recommendations/RecommendationsPanel";
import { ARTICLE_DETAILS_BY_SLUG, ARTICLE_SIDE_RECOMMENDATIONS, COURSE_DETAILS_BY_SLUG } from "./data/contentStudioData";
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
import {
  buildLibraryArticleCreateBody,
  buildTagIdLookupFromArticles,
  mapApiLibraryArticleToReaderArticle,
  resolveTagIdsFromUserTags
} from "./utils/libraryArticle";
import { createSlug } from "./utils/slug";

/** When not `"false"`, failed API requests fall back to `src/data/*` demo content (hackathon default). */
const STATIC_FALLBACK = import.meta.env.VITE_API_STATIC_FALLBACK !== "false";

function mapRecommendationsWithInstanceId() {
  return RECOMMENDATIONS.map((item, index) => ({ ...item, instanceId: `${item.id}-${index}` }));
}

function resolvePathFromHash(hashValue) {
  return hashValue.replace(/^#/, "") || "/";
}

function resolveTabFromPath(path) {
  if (path.startsWith(NAV_LINKS.auth)) {
    return "auth";
  }
  if (path.startsWith(NAV_LINKS.profile)) {
    return "profile";
  }
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
  if (path.startsWith(NAV_LINKS.articles)) {
    return "library";
  }
  if (path.startsWith(NAV_LINKS.courses)) {
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
  if (!slug || slug === "create" || slug === "view") {
    return null;
  }

  return slug;
}

const PAGE_ORDER = ["auth", "home", "projects", "news", "library", "chat", "profile"];

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

const AUTH_TOKEN_STORAGE_KEY = "comit.auth.token";
const ARTICLE_DRAFTS_STORAGE_KEY = "comit.article.drafts";
const PROJECT_DRAFTS_STORAGE_KEY = "comit.project.drafts";
const ARTICLE_TAG_TONES = ["green", "cyan", "coral", "yellow", "pink", "blue"];

function readFromLocalStorage(storageKey, fallbackValue) {
  if (typeof window === "undefined") {
    return fallbackValue;
  }

  try {
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) {
      return fallbackValue;
    }
    return JSON.parse(raw);
  } catch {
    return fallbackValue;
  }
}

function writeToLocalStorage(storageKey, value) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.localStorage.setItem(storageKey, JSON.stringify(value));
  } catch {
    // no-op
  }
}

function resolveArticleSlugFromPath(path) {
  const prefix = `${NAV_LINKS.articles}/`;
  if (!path.startsWith(prefix)) {
    return null;
  }

  const slug = path.slice(prefix.length).split("/")[0];
  if (!slug || slug === "create") {
    return null;
  }

  return slug;
}

function resolveCourseSlugFromPath(path) {
  const prefix = `${NAV_LINKS.courses}/`;
  if (!path.startsWith(prefix)) {
    return null;
  }

  const slug = path.slice(prefix.length).split("/")[0];
  return slug || null;
}

function resolveAuthModeFromPath(path) {
  return path.startsWith(`${NAV_LINKS.auth}/register`) ? "register" : "login";
}

function createArticleDraftRecord(payload) {
  const baseSlug = createSlug(payload.title) || "article";
  const slug = `${baseSlug}-${Date.now().toString(36).slice(-4)}`;
  const points = payload.content
    .split(/[.!?]\s+/)
    .map((point) => point.trim())
    .filter(Boolean)
    .slice(0, 5)
    .map((point) => (point.endsWith(".") ? point : `${point}.`));

  return {
    id: slug,
    slug,
    title: payload.title,
    summary: payload.summary,
    content: payload.content,
    tags: payload.tags || [],
    updatedLabel: "Только что",
    viewsLabel: "0",
    paragraphs: payload.content
      .split(/\n{2,}/)
      .map((paragraph) => paragraph.trim())
      .filter(Boolean)
      .slice(0, 4),
    points: points.length ? points : ["Материал сохранён как черновик и готов к доработке."],
    heroImageUrl: assets.posterTechConf,
    relatedCourseSlug: "machine-learning-from-zero"
  };
}

function mapArticleDraftToLibraryItem(draft) {
  const tags = (draft.tags?.length ? draft.tags : ["draft"]).slice(0, 3).map((tag, index) => ({
    id: `${draft.id}-${tag}-${index}`,
    label: `#${tag.replace(/^#/, "")}`,
    tone: ARTICLE_TAG_TONES[index % ARTICLE_TAG_TONES.length]
  }));

  return {
    id: draft.id,
    tags,
    title: draft.title,
    description: draft.summary,
    authorName: "Вы",
    authorAvatarUrl: assets.avatarPhoto,
    detailsUrl: `${NAV_LINKS.articles}/${draft.slug}`
  };
}

function createProjectDraftRecord(payload) {
  const idBase = createSlug(payload.title) || "project";
  const id = `${idBase}-${Date.now().toString(36).slice(-4)}`;
  return {
    id,
    code: `#DR${Math.floor(Math.random() * 9000 + 1000)}`,
    title: payload.title,
    description: payload.description,
    teamName: payload.teamName,
    visibility: payload.visibility,
    updatedLabel: "Только что",
    detailsUrl: `${NAV_LINKS.projects}/${id}`
  };
}

function mapProjectDraftToHubProject(draft) {
  return {
    id: draft.id,
    code: draft.code,
    title: draft.title,
    description: draft.description,
    teamName: draft.teamName,
    updatedLabel: draft.updatedLabel,
    teamAvatarUrl: assets.avatarPhoto,
    detailsUrl: draft.detailsUrl,
    visibility: draft.visibility || "private",
    isHot: false
  };
}

/** Тело `POST /api/projects` из черновика (колонка «идея» по умолчанию). */
function buildProjectCreateApiBody(draft) {
  const details = mapProjectDraftToDetails(draft);
  return {
    id: draft.id,
    columnId: "idea",
    code: draft.code,
    title: draft.title,
    description: draft.description,
    teamName: draft.teamName,
    updatedLabel: draft.updatedLabel,
    teamAvatarUrl: draft.teamAvatarUrl ?? assets.avatarPhoto,
    detailsUrl: draft.detailsUrl,
    visibility: draft.visibility === "public" ? "public" : "private",
    ownerName: draft.teamName,
    joinLabel: details.joinLabel,
    teamCaption: details.teamCaption,
    productivityCaption: details.productivityCaption,
    progressCaption: details.progressCaption,
    todoCaption: details.todoCaption,
    integrationCaption: details.integrationCaption,
    teamMembersPreview: details.teamMembersPreview,
    productivity: details.productivity,
    progress: details.progress,
    todo: details.todo,
    integrations: details.integrations,
    participants: details.participants
  };
}

function mapProjectDraftToDetails(draft) {
  return {
    id: draft.id,
    code: draft.code,
    title: draft.title,
    ownerName: draft.teamName,
    detailsUrl: draft.detailsUrl,
    joinLabel: "Присоединиться в команду",
    teamCaption: "Участники черновика проекта",
    productivityCaption: "Метрики будут доступны после публикации",
    progressCaption: "Оценка готовности по текущей версии",
    todoCaption: "Что нужно сделать для первого релиза",
    integrationCaption: "Подключите сервисы после публикации проекта",
    teamMembersPreview: [
      { id: `${draft.id}-member-1`, name: draft.teamName, avatarUrl: assets.avatarPhoto, avatarVariant: "default" },
      { id: `${draft.id}-member-2`, name: "Новый участник", avatarUrl: assets.avatarPhoto, avatarVariant: "warm" },
      { id: `${draft.id}-member-3`, name: "Новый участник", avatarUrl: assets.avatarPhoto, avatarVariant: "cool" }
    ],
    productivity: { value: "0%", delta: "Данные появятся после запуска" },
    progress: { value: "10%", percent: 10 },
    todo: { task: "Подготовить roadmap и распределить роли в команде", updatedLabel: "Только что" },
    integrations: [
      {
        id: `${draft.id}-github`,
        brand: "github",
        description: "Репозиторий для исходного кода",
        statusLabel: "Не подключено",
        connectedSince: "Ожидает настройки"
      },
      {
        id: `${draft.id}-hosting`,
        brand: "timeweb",
        description: "Хостинг и доменная конфигурация",
        statusLabel: "Не подключено",
        connectedSince: "Ожидает настройки"
      }
    ],
    participants: [
      {
        id: `${draft.id}-owner`,
        name: draft.teamName,
        avatarUrl: assets.avatarPhoto,
        avatarVariant: "default",
        comitId: "draft",
        timeInProject: "0 мин",
        role: "Инициатор",
        status: "Планирование",
        lastTask: "Создать структуру проекта"
      }
    ]
  };
}

function App() {
  const queryClient = useQueryClient();
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
  const [authToken, setAuthToken] = useState(() =>
    typeof window === "undefined" ? "" : window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || "",
  );
  const [authUser, setAuthUser] = useState(null);
  const [isAuthBusy, setIsAuthBusy] = useState(false);
  const [authErrorMessage, setAuthErrorMessage] = useState("");
  const [authSuccessMessage, setAuthSuccessMessage] = useState("");
  const [isProfileSaving, setIsProfileSaving] = useState(false);
  const [articleDrafts, setArticleDrafts] = useState(() => {
    const value = readFromLocalStorage(ARTICLE_DRAFTS_STORAGE_KEY, []);
    return Array.isArray(value) ? value : [];
  });
  const [projectDrafts, setProjectDrafts] = useState(() => {
    const value = readFromLocalStorage(PROJECT_DRAFTS_STORAGE_KEY, []);
    return Array.isArray(value) ? value : [];
  });
  const [isArticleSaving, setIsArticleSaving] = useState(false);
  const [isProjectSaving, setIsProjectSaving] = useState(false);
  const [participatedFeaturedIds, setParticipatedFeaturedIds] = useState(() => new Set());

  const chatListRef = useRef(null);
  const pendingAssistantRepliesRef = useRef(0);
  const routeStateRef = useRef({ tab: activeTab, path: currentPath });
  const libraryInterestsSyncedRef = useRef(false);
  const libraryProfileInterestsSyncedRef = useRef({ token: null, applied: false });

  const isHomePage = activeTab === "home";
  const isNewsPage = activeTab === "news";
  const isProjectsPage = activeTab === "projects";
  const isLibraryPage = activeTab === "library";
  const isChatPage = activeTab === "chat";
  const isAuthPage = currentPath.startsWith(NAV_LINKS.auth);
  const isProfilePage = currentPath.startsWith(NAV_LINKS.profile);
  const isArticleCreatePage = currentPath.startsWith(NAV_LINKS.articleCreate);
  const currentProjectSlug = resolveProjectSlugFromPath(currentPath);
  const currentArticleSlug = resolveArticleSlugFromPath(currentPath);
  const currentCourseSlug = resolveCourseSlugFromPath(currentPath);
  const isProjectCreatePage = currentPath === NAV_LINKS.projectsCreate;
  const authMode = resolveAuthModeFromPath(currentPath);
  const sessionToken =
    authToken?.trim() ||
    (typeof window !== "undefined" ? window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)?.trim() || "" : "");

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
    queryKey: ["news", "featured", sessionToken],
    queryFn: () => fetchNewsFeatured(sessionToken?.trim() || undefined),
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
    enabled: isLibraryPage || isArticleCreatePage || Boolean(currentArticleSlug),
    staleTime: 60_000,
  });

  const articlesForLibraryTagLookup = useMemo(() => {
    const api = libraryQuery.data?.articles;
    if (api && api.length > 0) {
      return api;
    }
    return STATIC_FALLBACK ? LIBRARY_ARTICLE_ITEMS : [];
  }, [libraryQuery.data?.articles]);

  const profileMeQuery = useQuery({
    queryKey: ["profile", "me", authToken],
    queryFn: () => fetchProfileMe(authToken),
    enabled: Boolean((isLibraryPage || isProfilePage) && authToken),
    staleTime: 60_000,
  });

  const universitiesQuery = useQuery({
    queryKey: ["profile", "universities", authToken],
    queryFn: () => fetchUniversities(authToken),
    enabled: Boolean(isProfilePage && authToken),
    staleTime: 60_000,
  });

  const projectDraftMap = useMemo(
    () =>
      projectDrafts.reduce((acc, draft) => {
        acc[draft.id] = draft;
        return acc;
      }, {}),
    [projectDrafts],
  );
  const currentProjectDraft = currentProjectSlug ? projectDraftMap[currentProjectSlug] || null : null;

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
  const hubColumns = useMemo(() => {
    const mappedColumns = hubColumnsRaw.map((column) => ({
      ...column,
      projects: column.projects.map((project) => ({
        ...project,
        teamAvatarUrl: project.teamAvatarUrl || assets.avatarPhoto,
      })),
    }));

    if (sessionToken || !projectDrafts.length) {
      return mappedColumns;
    }

    const draftProjects = projectDrafts.map(mapProjectDraftToHubProject);
    return mappedColumns.map((column) =>
      column.id === "idea"
        ? {
            ...column,
            count: column.projects.length + draftProjects.length,
            projects: [...draftProjects, ...column.projects]
          }
        : column,
    );
  }, [hubColumnsRaw, projectDrafts, sessionToken]);

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
  const libraryArticleItemsBase =
    libraryBundle?.articles?.length > 0
      ? libraryBundle.articles.map((article) => ({
          ...article,
          authorAvatarUrl: article.authorAvatarUrl?.trim() ? article.authorAvatarUrl : assets.avatarPhoto,
          detailsUrl: article.detailsUrl?.trim() ? article.detailsUrl : `${NAV_LINKS.articles}/${article.id}`,
        }))
      : STATIC_FALLBACK
        ? LIBRARY_ARTICLE_ITEMS
        : [];
  const draftLibraryArticleItems = articleDrafts.map(mapArticleDraftToLibraryItem);
  const filteredLibraryArticleItemsBase = useMemo(() => {
    const selectedIds = Object.entries(selectedLibraryInterests)
      .filter(([, isSelected]) => isSelected)
      .map(([id]) => id);
    if (selectedIds.length === 0) {
      return libraryArticleItemsBase;
    }
    return libraryArticleItemsBase.filter((article) => {
      const ids = article.interestIds ?? [];
      return ids.some((i) => selectedIds.includes(i));
    });
  }, [libraryArticleItemsBase, selectedLibraryInterests]);
  const libraryArticleItems = [...draftLibraryArticleItems, ...filteredLibraryArticleItemsBase];

  const topCard = deck[0];
  const stackedCards = deck.slice(1, 3);
  const canDismiss = !dismissDirection;
  const showProjectDetailRoute = Boolean(currentProjectSlug);
  const homeNewsItem = miniNewsItems[0];
  const chatPageMessages = messages.some((message) => message.role === "user") ? messages.slice(1) : [];
  const activeLibraryHero = libraryShowcaseItems[activeLibraryShowcaseIndex]?.hero || LIBRARY_HERO_RESOURCE;
  const shouldShowAiPopup = aiMode && !isAuthPage;
  const articleDraftMap = useMemo(
    () =>
      articleDrafts.reduce((acc, draft) => {
        acc[draft.slug] = draft;
        return acc;
      }, {}),
    [articleDrafts],
  );
  const currentArticleDraft = currentArticleSlug ? articleDraftMap[currentArticleSlug] || null : null;

  const libraryArticleFromApi = useMemo(() => {
    if (!currentArticleSlug || currentArticleDraft) {
      return null;
    }
    const articles = libraryQuery.data?.articles ?? [];
    return articles.find((a) => a.id === currentArticleSlug) ?? null;
  }, [currentArticleSlug, currentArticleDraft, libraryQuery.data?.articles]);

  const articleReaderLoading =
    Boolean(currentArticleSlug && !currentCourseSlug) &&
    !currentArticleDraft &&
    !ARTICLE_DETAILS_BY_SLUG[currentArticleSlug] &&
    !libraryArticleFromApi &&
    !STATIC_FALLBACK &&
    libraryQuery.isPending;

  const activeArticleDetails = currentArticleSlug
    ? currentArticleDraft ||
      (libraryArticleFromApi ? mapApiLibraryArticleToReaderArticle(libraryArticleFromApi) : null) ||
      ARTICLE_DETAILS_BY_SLUG[currentArticleSlug] ||
      (libraryQuery.isPending && !STATIC_FALLBACK ? null : ARTICLE_DETAILS_BY_SLUG["ml-ab-tests"])
    : null;
  const activeCourseDetails = currentCourseSlug
    ? COURSE_DETAILS_BY_SLUG[currentCourseSlug] || COURSE_DETAILS_BY_SLUG["machine-learning-from-zero"]
    : null;
  const isArticleReaderPage = Boolean(currentArticleSlug || currentCourseSlug);
  const shouldHideTopBar = isAuthPage;
  const mainContentKey =
    activeTab === "projects" ||
    activeTab === "chat" ||
    activeTab === "library" ||
    activeTab === "profile" ||
    activeTab === "auth"
      ? currentPath
      : activeTab;

  useEffect(() => {
    const items = recommendationsQuery.data;
    if (items?.length) {
      setDeck(items.map((item, index) => ({ ...item, instanceId: `${item.id}-${index}` })));
    }
  }, [recommendationsQuery.data]);

  useEffect(() => {
    libraryInterestsSyncedRef.current = false;
    libraryProfileInterestsSyncedRef.current = { token: null, applied: false };
  }, [authToken]);

  useEffect(() => {
    if (!libraryBundle?.interestOptions?.length) {
      return;
    }
    if (authToken) {
      if (!profileMeQuery.isSuccess || profileMeQuery.data === undefined) {
        return;
      }
      const prev = libraryProfileInterestsSyncedRef.current;
      if (prev.token === authToken && prev.applied) {
        return;
      }
      const selectedSet = new Set((profileMeQuery.data.interests ?? []).map((i) => i.id));
      setSelectedLibraryInterests(
        libraryBundle.interestOptions.reduce(
          (acc, option) => ({ ...acc, [option.id]: selectedSet.has(option.id) }),
          {},
        ),
      );
      libraryProfileInterestsSyncedRef.current = { token: authToken, applied: true };
      return;
    }
    if (libraryInterestsSyncedRef.current) {
      return;
    }
    setSelectedLibraryInterests(
      libraryBundle.interestOptions.reduce((acc, option) => ({ ...acc, [option.id]: option.selected }), {}),
    );
    libraryInterestsSyncedRef.current = true;
  }, [libraryBundle, authToken, profileMeQuery.isSuccess, profileMeQuery.data]);

  useEffect(() => {
    if (!libraryShowcaseItems.length) {
      return;
    }
    setActiveLibraryShowcaseIndex((prev) => (prev < libraryShowcaseItems.length ? prev : 0));
  }, [libraryShowcaseItems.length]);

  useEffect(() => {
    writeToLocalStorage(ARTICLE_DRAFTS_STORAGE_KEY, articleDrafts);
  }, [articleDrafts]);

  useEffect(() => {
    writeToLocalStorage(PROJECT_DRAFTS_STORAGE_KEY, projectDrafts);
  }, [projectDrafts]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (!authToken) {
      window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      return;
    }
    window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, authToken);
  }, [authToken]);

  useEffect(() => {
    let isDisposed = false;

    if (!authToken) {
      setAuthUser(null);
      return () => {
        isDisposed = true;
      };
    }

    setIsAuthBusy(true);
    void fetchCurrentUserProfile(authToken)
      .then((profile) => {
        if (isDisposed) {
          return;
        }
        setAuthUser(profile);
      })
      .catch(() => {
        if (isDisposed) {
          return;
        }
        setAuthUser(null);
        setAuthToken("");
      })
      .finally(() => {
        if (isDisposed) {
          return;
        }
        setIsAuthBusy(false);
      });

    return () => {
      isDisposed = true;
    };
  }, [authToken]);

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

  const openProfilePage = () => {
    openPath(NAV_LINKS.profile);
  };

  const openAuthPage = (mode = "login") => {
    setAuthErrorMessage("");
    setAuthSuccessMessage("");
    openPath(mode === "register" ? `${NAV_LINKS.auth}/register` : NAV_LINKS.auth);
  };

  const openArticleCreatePage = () => {
    openPath(NAV_LINKS.articleCreate);
  };

  const openMiniNews = (newsItem) => {
    openPath(newsItem?.detailsUrl || NAV_LINKS.news);
  };

  const openArticleDetails = (articleItem) => {
    const fallbackPath = `${NAV_LINKS.articles}/${articleItem?.id || "ml-ab-tests"}`;
    openPath(articleItem?.detailsUrl || fallbackPath);
  };

  const openCourseDetails = (courseItem) => {
    if (typeof courseItem === "string") {
      openPath(`${NAV_LINKS.courses}/${courseItem}`);
      return;
    }
    const slug = courseItem?.slug || courseItem?.id || "machine-learning-from-zero";
    openPath(`${NAV_LINKS.courses}/${slug}`);
  };

  const openProjectDetails = (project) => {
    const id = project?.id;
    const detailsUrl = typeof project?.detailsUrl === "string" ? project.detailsUrl.trim() : "";
    if (detailsUrl.startsWith("/")) {
      openPath(detailsUrl);
      return;
    }
    if (id) {
      openPath(`${NAV_LINKS.projects}/${id}`);
      return;
    }
    openPath(NAV_LINKS.projects);
  };

  const openProjectCreate = () => {
    openPath(NAV_LINKS.projectsCreate);
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
    if (authToken) {
      void patchProfileMe(authToken, { interestIds: selectedIds })
        .then(() => {
          queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
        })
        .catch(() => {});
    }
  };

  const openFeaturedEvent = async (eventItem) => {
    if (!eventItem?.id) {
      openPath(NAV_LINKS.events);
      return;
    }
    const alreadyParticipated =
      participatedFeaturedIds.has(eventItem.id) || Boolean(eventItem.participated);
    if (authToken && !alreadyParticipated) {
      try {
        await postFeaturedParticipate(authToken, eventItem.id);
        setParticipatedFeaturedIds((prev) => new Set([...prev, eventItem.id]));
        queryClient.invalidateQueries({ queryKey: ["news", "featured"] });
      } catch (error) {
        alert(formatOpenApiError(error));
        return;
      }
    }
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

  const handleAuthSubmit = async ({ mode, email, password }) => {
    setAuthErrorMessage("");
    setAuthSuccessMessage("");
    setIsAuthBusy(true);

    try {
      if (mode === "register") {
        await registerWithEmail({ email, password });
        setAuthSuccessMessage("Аккаунт создан. Выполняем вход...");
      }

      const loginData = await loginWithPassword({ email, password });
      if (!loginData?.access_token) {
        throw new Error("Сервер не вернул access token.");
      }

      setAuthToken(loginData.access_token);
      setAuthSuccessMessage("Вход выполнен.");
      openProfilePage();
    } catch (error) {
      const detailMessage =
        typeof error?.detail === "string"
          ? error.detail
          : Array.isArray(error?.detail) && error.detail[0]?.msg
            ? error.detail[0].msg
            : "";
      const message =
        detailMessage || (error instanceof Error && error.message ? error.message : "Не удалось выполнить авторизацию.");
      setAuthErrorMessage(message);
    } finally {
      setIsAuthBusy(false);
    }
  };

  const handleLogout = async () => {
    if (authToken) {
      try {
        await logoutCurrentUser(authToken);
      } catch {
        // no-op
      }
    }
    setAuthToken("");
    setAuthUser(null);
    setAuthErrorMessage("");
    setAuthSuccessMessage("");
    openPath("/");
  };

  const handleSaveProfile = async (payload) => {
    if (!authToken) {
      return false;
    }

    setIsProfileSaving(true);
    try {
      const updated = await patchCurrentUserProfile(authToken, payload);
      setAuthUser(updated);
      return true;
    } catch {
      return false;
    } finally {
      setIsProfileSaving(false);
    }
  };

  const handleSaveProfileModule = async (payload) => {
    if (!authToken) {
      return false;
    }
    try {
      await patchProfileMe(authToken, payload);
      queryClient.invalidateQueries({ queryKey: ["profile", "me"] });
      return true;
    } catch {
      return false;
    }
  };

  const handleCreateArticle = async (payload) => {
    setIsArticleSaving(true);
    const draft = createArticleDraftRecord(payload);
    const effectiveToken =
      (typeof window !== "undefined" && window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)?.trim()) ||
      authToken?.trim() ||
      "";
    const tagLookup = buildTagIdLookupFromArticles(articlesForLibraryTagLookup);
    const tagIds = resolveTagIdsFromUserTags(payload.tags || [], tagLookup);

    try {
      if (!effectiveToken) {
        setArticleDrafts((prev) => [draft, ...prev]);
        return { draft, savedToServer: false, errorMessage: null };
      }
      const authorName = authUser?.email ? authUser.email.split("@")[0] : "Автор";
      const body = buildLibraryArticleCreateBody({
        id: draft.id,
        title: payload.title.trim(),
        summary: payload.summary.trim(),
        content: payload.content.trim(),
        tagIds,
        authorName,
        authorAvatarUrl: assets.avatarPhoto
      });
      const created = await createLibraryArticle(effectiveToken, body);
      const merged = { ...createArticleDraftRecord(payload), id: created.id, slug: created.id };
      setArticleDrafts((prev) => [merged, ...prev]);
      queryClient.invalidateQueries({ queryKey: ["library"] });
      return { draft: merged, savedToServer: true, errorMessage: null };
    } catch (e) {
      setArticleDrafts((prev) => [draft, ...prev]);
      return { draft, savedToServer: false, errorMessage: formatOpenApiError(e) };
    } finally {
      setIsArticleSaving(false);
    }
  };

  const handleCreateProject = async (payload) => {
    setIsProjectSaving(true);
    const draft = createProjectDraftRecord(payload);
    const effectiveToken =
      (typeof window !== "undefined" && window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)?.trim()) ||
      authToken?.trim() ||
      "";
    try {
      if (!effectiveToken) {
        setProjectDrafts((prev) => [draft, ...prev]);
        return { draft, savedToServer: false, errorMessage: null };
      }
      const created = await createProject(effectiveToken, buildProjectCreateApiBody(draft));
      const merged = {
        ...draft,
        id: created.id,
        detailsUrl: created.detailsUrl ?? `${NAV_LINKS.projects}/${created.id}`
      };
      setProjectDrafts((prev) => [merged, ...prev]);
      queryClient.invalidateQueries({ queryKey: ["projects", "hub"] });
      return { draft: merged, savedToServer: true, errorMessage: null };
    } catch (e) {
      setProjectDrafts((prev) => [draft, ...prev]);
      return { draft, savedToServer: false, errorMessage: formatOpenApiError(e) };
    } finally {
      setIsProjectSaving(false);
    }
  };

  const openArticleDraft = (slug) => {
    openPath(`${NAV_LINKS.articles}/${slug}`);
  };

  const openProjectDraft = (projectId) => {
    openPath(`${NAV_LINKS.projects}/${projectId}`);
  };

  const openArticleRecommendation = (item) => {
    openPath(item?.detailsUrl || NAV_LINKS.news);
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

  const mainContent = isAuthPage ? (
    <AuthPage
      mode={authMode === "register" ? "register" : "login"}
      isSubmitting={isAuthBusy}
      errorMessage={authErrorMessage}
      successMessage={authSuccessMessage}
      onSubmitAuth={handleAuthSubmit}
      onSwitchMode={() => openAuthPage(authMode === "register" ? "login" : "register")}
      onBack={handleGoHome}
    />
  ) : isProfilePage ? (
    <ProfilePage
      user={authUser}
      profile={profileMeQuery.data}
      profileLoading={profileMeQuery.isPending}
      universities={universitiesQuery.data ?? []}
      universitiesLoading={universitiesQuery.isPending}
      isLoading={isAuthBusy || isProfileSaving}
      isAuthenticated={Boolean(sessionToken)}
      articleDraftCount={articleDrafts.length}
      projectDraftCount={projectDrafts.length}
      onBack={handleGoHome}
      onOpenAuth={() => openAuthPage("register")}
      onLogout={handleLogout}
      onSaveProfile={handleSaveProfile}
      onSaveProfileModule={handleSaveProfileModule}
      onOpenArticleCreate={openArticleCreatePage}
      onOpenProjectCreate={openProjectCreate}
      onOpenLibrary={openLibraryPage}
    />
  ) : isArticleCreatePage ? (
    <ArticleCreatePage
      onBack={openLibraryPage}
      onSubmitArticle={handleCreateArticle}
      isSubmitting={isArticleSaving}
      drafts={articleDrafts}
      onOpenDraft={openArticleDraft}
      isAuthenticated={Boolean(sessionToken)}
      onOpenAuth={() => openAuthPage("login")}
    />
  ) : isArticleReaderPage ? (
    articleReaderLoading ? (
      <section className="article-reader-page">
        <div className="library-page-head article-reader-head">
          <button type="button" className="news-back-btn library-back-btn" aria-label="Назад" onClick={openLibraryPage}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <h1 className="library-page-title">Статьи и курсы</h1>
        </div>
        <p className="article-create-status" style={{ padding: "24px 20px" }}>
          Загружаем материал…
        </p>
      </section>
    ) : (
      <ArticleReaderPage
        mode={currentCourseSlug ? "course" : "article"}
        article={activeArticleDetails}
        course={activeCourseDetails}
        recommendations={ARTICLE_SIDE_RECOMMENDATIONS}
        onBack={openLibraryPage}
        onOpenRecommendation={openArticleRecommendation}
        onOpenRelatedCourse={() => openCourseDetails(activeArticleDetails?.relatedCourseSlug)}
      />
    )
  ) : isNewsPage ? (
    <NewsPage
      miniNewsItems={miniNewsItems}
      featuredNewsItems={featuredNewsItems}
      likedNews={likedNews}
      participatedFeaturedIds={participatedFeaturedIds}
      onToggleNewsLike={toggleNewsLike}
      onOpenMiniNews={openMiniNews}
      onParticipateInEvent={openFeaturedEvent}
      onBack={handleGoHome}
      isLoading={newsPageLoading}
      showOfflineFallbackNotice={showNewsOfflineNotice}
    />
  ) : isProjectsPage && isProjectCreatePage ? (
    <ProjectCreatePage
      onBack={openProjectsHub}
      onSubmitProject={handleCreateProject}
      isSubmitting={isProjectSaving}
      drafts={projectDrafts}
      onOpenDraft={openProjectDraft}
      isAuthenticated={Boolean(sessionToken)}
      onOpenAuth={() => openAuthPage("login")}
    />
  ) : isProjectsPage && showProjectDetailRoute ? (
    currentProjectDraft && !sessionToken ? (
      <ProjectDetailsPage
        project={mapProjectDraftToDetails(currentProjectDraft)}
        onBack={openProjectsHub}
        onJoinProject={joinProject}
        sessionToken={null}
      />
    ) : projectDetailsQuery.isLoading ? (
      <section className="project-details-page">
        <div className="library-page-head">
          <button type="button" className="news-back-btn" aria-label="Назад к проектам" onClick={openProjectsHub}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <p className="page-title">Загрузка проекта...</p>
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
        sessionToken={sessionToken}
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
      onOpenArticle={openArticleDetails}
      onOpenCourse={openCourseDetails}
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
        onOpenCourseDetails={(path) => navigateTo(path || "/courses/machine-learning-from-zero")}
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
        <div className={`app-shell ${shouldHideTopBar ? "app-shell-auth" : "app-shell-news"}`}>
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

          {!shouldHideTopBar ? (
            <>
              <TopBar
                activeTab={activeTab}
                aiAssistantEnabled={aiAssistantEnabled}
                isAiOpen={aiMode}
                isNotificationsOpen={isNotificationsOpen}
                notificationItems={notificationItems}
                onCloseNotifications={() => setIsNotificationsOpen(false)}
                onGoHome={handleGoHome}
                onOpenProfile={openProfilePage}
                onMenuClick={handleMenuClick}
                onOpenNotification={handleOpenNotification}
                onToggleNotifications={() => setIsNotificationsOpen((prev) => !prev)}
                isNewsView
              />
              <MobileShell
                activeTab={activeTab}
                aiAssistantEnabled={aiAssistantEnabled}
                isAiOpen={aiMode}
                onMenuClick={handleMenuClick}
              />
            </>
          ) : null}

          <main className={`dashboard-layout dashboard-layout-news ${shouldHideTopBar ? "dashboard-layout-auth" : ""}`.trim()}>
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

          {isHomePage && !shouldHideTopBar ? (
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
          {shouldShowAiPopup && !shouldHideTopBar ? (
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



