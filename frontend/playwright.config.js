import { defineConfig } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'https://scout-alerts-live.preview.emergentagent.com';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: BASE_URL,
    headless: true,
  },
  reporter: [['list'], ['json', { outputFile: '../test_reports/playwright_smoke.json' }]],
});
