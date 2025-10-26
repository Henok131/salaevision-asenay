import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: 'tests/e2e',
  timeout: 30 * 1000,
  use: {
    baseURL: process.env.VITE_FRONTEND_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    headless: true,
  },
  reporter: [['list']]
})
