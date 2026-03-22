import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, repoRoot, "");
  const apiProxyTarget =
    env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";
  const qmsgProxyTarget =
    env.VITE_QMSG_PROXY_TARGET || "http://127.0.0.1:8090";

  return {
    plugins: [react()],
    // Monorepo: load `.env` from repo root (same as Docker / backend tooling).
    envDir: repoRoot,
    server: {
      proxy: {
        "^/api": {
          target: apiProxyTarget,
          changeOrigin: true,
        },
        "^/qmsg": {
          target: qmsgProxyTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
