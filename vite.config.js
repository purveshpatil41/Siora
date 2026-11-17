import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";

export default defineConfig({
  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: "manifest.json",
          dest: ".",
        },
        {
          src: "background.js",
          dest: ".",
        },
        {
          src: "content.js",
          dest: ".",
        },
      ],
    }),
  ],

  build: {
    rollupOptions: {
      input: "sidepanel.html",
    },
  },
});