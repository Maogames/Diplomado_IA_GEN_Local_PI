import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En desarrollo, /api y /health se reenvían al backend FastAPI (puerto 8000).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
