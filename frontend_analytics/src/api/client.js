/**
 * API base URL for fetch requests.
 * In dev: Vite proxy rewrites /api to backend.
 * In Docker: nginx proxies /api to backend.
 */
const getBaseUrl = () => {
  if (typeof window === "undefined") return "";
  return window.location.origin;
};

export const apiBase = getBaseUrl();
