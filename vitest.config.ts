import path from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      "@shared": path.resolve(import.meta.dirname, "shared"),
      "server": path.resolve(import.meta.dirname, "server"),
      "@": path.resolve(import.meta.dirname, "client", "src"),
    },
  },
  test: {
    root: path.resolve(import.meta.dirname),
    include: ["server/**/*.test.ts", "tests/**/*.test.ts"],
    environment: "node",
    passWithNoTests: true,
  },
});
