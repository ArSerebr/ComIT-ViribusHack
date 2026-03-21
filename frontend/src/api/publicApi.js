import { apiClient } from "./client";

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
