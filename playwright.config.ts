import { defineConfig } from "@playwright/test";
import { tmpdir } from "node:os";
import { join } from "node:path";
export default defineConfig({
  outputDir: join(process.env.LEXVIGIL_E2E_ARTIFACTS || join(tmpdir(), "lexvigil-e2e"), "test-results"),
  testDir: "./tests",
  workers: 1,
  timeout: 45000,
  use: {
    baseURL: "http://127.0.0.1:5173",
    channel: "chrome",
    trace: "retain-on-failure",
  },
});
