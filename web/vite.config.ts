import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { panoramaMiddleware } from "./server/panorama";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const base = env.VITE_BASE || "/world-spot/";

  function panoramaPlugin() {
    const mountPath = `${base.replace(/\/$/, "")}/panorama`;
    const mount = (server: { middlewares: { use: (path: string, handler: typeof panoramaMiddleware) => void } }) => {
      server.middlewares.use(mountPath, (req, res, next) => {
        panoramaMiddleware(req, res, next);
      });
    };
    return {
      name: "panorama-proxy",
      configureServer: mount,
      configurePreviewServer: mount,
    };
  }

  return {
    base,
    plugins: [react(), panoramaPlugin()],
    server: { port: 5173, host: true },
    build: { outDir: "dist" },
  };
});
