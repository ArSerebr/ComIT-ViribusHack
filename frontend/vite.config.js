import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";
import { createReadStream } from "node:fs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
/** Корень репозитория — один общий `.env` с backend и compose. */
const repoRoot = path.resolve(__dirname, "..");

const MIME = {
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".webp": "image/webp",
  ".woff": "font/woff",
  ".woff2": "font/woff2"
};

/** Отдаёт frontend/img по URL /img/* (совпадает с путями из API). */
function serveFrontendImg() {
  return {
    name: "serve-frontend-img",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const raw = req.url?.split("?")[0] ?? "";
        if (!raw.startsWith("/img/")) {
          return next();
        }
        const rel = decodeURIComponent(raw.slice(5));
        if (!rel || rel.includes("..")) {
          res.statusCode = 403;
          res.end();
          return;
        }
        const filePath = path.join(__dirname, "img", rel);
        fs.stat(filePath, (err, st) => {
          if (err || !st.isFile()) {
            return next();
          }
          const ext = path.extname(filePath).toLowerCase();
          res.setHeader("Content-Type", MIME[ext] ?? "application/octet-stream");
          const stream = createReadStream(filePath);
          stream.on("error", () => next());
          stream.pipe(res);
        });
      });
    }
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, repoRoot, "");
  const apiProxyTarget =
    env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [react(), serveFrontendImg()],
    server: {
      proxy: {
        "/api": {
          target: apiProxyTarget,
          changeOrigin: true
        }
      }
    }
  };
});
