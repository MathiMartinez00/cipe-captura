//vite.config.js
import { defineConfig } from "vite";
import { djangoVitePlugin } from "django-vite-plugin";

export default defineConfig({
  plugins: [djangoVitePlugin(["app/js/cipe.js"])],
  server: {
    host: "0.0.0.0",
    watch: {
      usePolling: true,
    },
  },
});
