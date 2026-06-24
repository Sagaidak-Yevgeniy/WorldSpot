import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { panoramaMiddleware } from "./server/panorama";

export default defineConfig({
  plugins: [
    react(),
    {
      name: "panorama-proxy",
      configureServer(server) {
        server.middlewares.use("/panorama", (req, res, next) => {
          panoramaMiddleware(req, res, next);
        });
      },
    },
  ],
  server: { port: 5173, host: true },
  build: { outDir: "dist" },
});
