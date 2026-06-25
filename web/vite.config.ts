import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { panoramaMiddleware } from "./server/panorama";

function panoramaPlugin() {
  const mount = (server: { middlewares: { use: (path: string, handler: typeof panoramaMiddleware) => void } }) => {
    server.middlewares.use("/panorama", (req, res, next) => {
      panoramaMiddleware(req, res, next);
    });
  };
  return {
    name: "panorama-proxy",
    configureServer: mount,
    configurePreviewServer: mount,
  };
}

export default defineConfig({
  plugins: [react(), panoramaPlugin()],
  server: { port: 5173, host: true },
  build: { outDir: "dist" },
});
