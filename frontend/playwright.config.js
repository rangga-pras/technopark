import { defineConfig } from "@playwright/test";
const python =
  process.platform === "win32"
    ? ".venv\\Scripts\\python.exe"
    : ".venv/bin/python";
export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  timeout: 45000,
  expect: { timeout: 15000 },
  use: {
    baseURL: "http://127.0.0.1:5174",
    channel: process.env.PW_CHANNEL || "msedge",
    headless: true,
    trace: "retain-on-failure",
  },
  reporter: "list",
  webServer: [
    {
      command: `${python} tests/serve_e2e.py`,
      cwd: "../backend",
      url: "http://127.0.0.1:8001/api/health",
      timeout: 60000,
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --port 5174 --strictPort",
      url: "http://127.0.0.1:5174",
      env: { VITE_API_BASE_URL: "http://127.0.0.1:8001/api" },
      timeout: 30000,
      reuseExistingServer: false,
    },
  ],
});
