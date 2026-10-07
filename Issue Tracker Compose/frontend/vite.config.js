import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, forward /api and /health to the backend so the browser only ever talks to one origin.
// In the container, nginx does the same job (see nginx.conf).
const target = process.env.VITE_API_TARGET || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": target,
      "/health": target,
      "/ready": target,
    },
  },
});
