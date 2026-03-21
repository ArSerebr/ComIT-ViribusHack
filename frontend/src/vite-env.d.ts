/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_API_PROXY_TARGET?: string;
  /** Set to `"false"` to hide static demo data when API requests fail (default: use fallback). */
  readonly VITE_API_STATIC_FALLBACK?: string;
}
