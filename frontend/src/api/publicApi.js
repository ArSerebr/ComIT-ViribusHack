import { apiClient, resolveApiUrl } from "./client";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Сообщение из тела ошибки openapi-fetch / FastAPI (detail строка или массив). */
export function formatOpenApiError(error) {
  if (error == null || error === false) {
    return "Неизвестная ошибка";
  }
  if (typeof error === "string") {
    return error;
  }
  if (typeof error === "object" && error !== null) {
    const d = error.detail;
    if (typeof d === "string" && d.trim()) {
      return d.trim();
    }
    if (Array.isArray(d) && d.length > 0) {
      const first = d[0];
      if (typeof first === "string") {
        return first;
      }
      if (first && typeof first.msg === "string") {
        return first.msg;
      }
    }
    if (typeof error.message === "string" && error.message.trim()) {
      return error.message.trim();
    }
  }
  try {
    return JSON.stringify(error);
  } catch {
    return String(error);
  }
}

async function extractErrorMessage(response, fallbackMessage) {
  try {
    const data = await response.json();
    const detail = data?.detail;
    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
    if (typeof data?.message === "string" && data.message.trim()) {
      return data.message;
    }
  } catch {
    // no-op
  }
  return fallbackMessage;
}

export async function fetchDashboardHome() {
  const { data, error } = await apiClient.GET("/api/dashboard/home");
  if (error) throw error;
  return data;
}

export async function fetchDashboardRecommendations() {
  const { data, error } = await apiClient.GET("/api/dashboard/recommendations");
  if (error) throw error;
  return data ?? [];
}

export async function fetchNewsMini() {
  const { data, error } = await apiClient.GET("/api/news/mini");
  if (error) throw error;
  return data ?? [];
}

export async function fetchNewsFeatured() {
  const { data, error } = await apiClient.GET("/api/news/featured");
  if (error) throw error;
  return data ?? [];
}

export async function fetchNotifications() {
  const { data, error } = await apiClient.GET("/api/notifications");
  if (error) throw error;
  return data ?? [];
}

export async function fetchLibraryBundle() {
  const { data, error } = await apiClient.GET("/api/library");
  if (error) throw error;
  return data;
}

/** Создание статьи в БД (требуется JWT). Ответ — `LibraryArticle`. */
export async function createLibraryArticle(token, body) {
  const { data, error } = await apiClient.POST("/api/library/articles", {
    headers: authHeaders(token),
    body
  });
  if (error) throw error;
  return data;
}

export async function fetchProjectsHub() {
  const { data, error } = await apiClient.GET("/api/projects/hub");
  if (error) throw error;
  return data ?? [];
}

export async function fetchProjectById(projectId) {
  const { data, error } = await apiClient.GET("/api/projects/{project_id}", {
    params: { path: { project_id: projectId } },
  });
  if (error) throw error;
  return data;
}

/** Создание проекта в БД (требуется JWT). Ответ — `ProjectDetails` с каноническим `id`. */
export async function createProject(token, body) {
  const { data, error } = await apiClient.POST("/api/projects", {
    headers: authHeaders(token),
    body
  });
  if (error) throw error;
  return data;
}

/** Analytics: POST `LikePayload` (openapi). */
export async function postRecommendationLike(body) {
  const { error } = await apiClient.POST("/api/recommendations/like", { body });
  if (error) throw error;
}

/** Analytics: POST `InterestsPayload` (openapi). */
export async function postLibraryInterests(body) {
  const { error } = await apiClient.POST("/api/library/interests", { body });
  if (error) throw error;
}

export async function loginWithPassword({ email, password }) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  form.set("grant_type", "password");
  form.set("scope", "");

  const response = await fetch(resolveApiUrl("/api/auth/jwt/login"), {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString()
  });

  if (!response.ok) {
    const message = await extractErrorMessage(response, "Не удалось выполнить вход.");
    throw new Error(message);
  }

  return response.json();
}

export async function registerWithEmail({ email, password }) {
  const { data, error } = await apiClient.POST("/api/auth/register", {
    body: {
      email,
      password,
      is_active: true,
      is_superuser: false,
      is_verified: false
    }
  });
  if (error) throw error;
  return data;
}

export async function fetchCurrentUserProfile(token) {
  const { data, error } = await apiClient.GET("/api/users/me", {
    headers: authHeaders(token)
  });
  if (error) throw error;
  return data;
}

export async function patchCurrentUserProfile(token, body) {
  const { data, error } = await apiClient.PATCH("/api/users/me", {
    headers: authHeaders(token),
    body
  });
  if (error) throw error;
  return data;
}

/** Profile (interests, bio): GET `/api/profile/me` (OpenAPI `ProfileMe`). */
export async function fetchProfileMe(token) {
  const { data, error } = await apiClient.GET("/api/profile/me", {
    headers: authHeaders(token)
  });
  if (error) throw error;
  return data;
}

/** PATCH `/api/profile/me` (`ProfileMePatch`, e.g. `interestIds`). */
export async function patchProfileMe(token, body) {
  const { data, error } = await apiClient.PATCH("/api/profile/me", {
    headers: authHeaders(token),
    body
  });
  if (error) throw error;
  return data;
}

export async function logoutCurrentUser(token) {
  const { error } = await apiClient.POST("/api/auth/jwt/logout", {
    headers: authHeaders(token)
  });
  if (error) throw error;
}

