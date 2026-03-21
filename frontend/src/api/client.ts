import createClient from "openapi-fetch";
import type { paths } from "./schema";

/**
 * Base URL for API requests. Empty string = same-origin `/api/...`
 * (Vite proxy in dev, nginx in Docker). Set `VITE_API_BASE_URL` for a full origin when needed.
 */
export function getApiBaseUrl(): string {
  const base = import.meta.env.VITE_API_BASE_URL;
  return base === undefined || base === "" ? "" : String(base);
}

/** Absolute URL for same-origin fetches or sendBeacon when `VITE_API_BASE_URL` is set. */
export function resolveApiUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (!base) {
    return normalized;
  }
  return `${base.replace(/\/$/, "")}${normalized}`;
}

export const apiClient = createClient<paths>({
  baseUrl: getApiBaseUrl(),
});
