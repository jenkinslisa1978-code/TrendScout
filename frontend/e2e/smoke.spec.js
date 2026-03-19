import { test, expect } from '@playwright/test';

const API = process.env.BASE_URL || 'https://measurable-proof.preview.emergentagent.com';

// --- P0: Crawlability ---

test('/ returns 200 with HTML', async ({ request }) => {
  const res = await request.get('/');
  expect(res.status()).toBe(200);
  const body = await res.text();
  expect(body).toContain('TrendScout');
});

test('/robots.txt returns 200', async ({ request }) => {
  const res = await request.get('/robots.txt');
  expect(res.status()).toBe(200);
  const body = await res.text();
  expect(body).toContain('User-agent');
  expect(body).toContain('Sitemap');
});

test('/sitemap.xml returns 200 with valid XML', async ({ request }) => {
  const res = await request.get('/sitemap.xml');
  expect(res.status()).toBe(200);
  const body = await res.text();
  expect(body).toContain('<urlset');
  expect(body).toContain('<loc>');
});

// --- Auth pages ---

test('/login renders login page', async ({ page }) => {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  expect(await page.title()).toContain('TrendScout');
});

test('/signup renders signup page', async ({ page }) => {
  await page.goto('/signup');
  await page.waitForLoadState('networkidle');
  expect(await page.title()).toContain('TrendScout');
});

test('server-rendered /api/auth/login-page works without JS', async ({ request }) => {
  const res = await request.get(`${API}/api/auth/login-page`);
  expect(res.status()).toBe(200);
  const body = await res.text();
  expect(body).toContain('<form');
  expect(body).toContain('email');
  expect(body).toContain('password');
  expect(body).toContain('TrendScout');
});

test('server-rendered /api/auth/signup-page works without JS', async ({ request }) => {
  const res = await request.get(`${API}/api/auth/signup-page`);
  expect(res.status()).toBe(200);
  const body = await res.text();
  expect(body).toContain('<form');
  expect(body).toContain('email');
  expect(body).toContain('Sign Up');
});

// --- Security headers ---

test('security headers present on API responses', async ({ request }) => {
  const res = await request.get(`${API}/api/health`);
  const headers = res.headers();
  expect(headers['strict-transport-security']).toBeDefined();
  expect(headers['referrer-policy']).toBe('strict-origin-when-cross-origin');
  expect(headers['x-frame-options']).toBe('DENY');
  expect(headers['x-content-type-options']).toBe('nosniff');
  expect(
    headers['content-security-policy-report-only'] || headers['content-security-policy']
  ).toBeDefined();
});

// --- Standardized errors ---

test('API 404 returns standardized error', async ({ request }) => {
  const res = await request.get(`${API}/api/nonexistent-route`);
  expect(res.status()).toBe(404);
  const body = await res.json();
  expect(body.success).toBe(false);
  expect(body.error.code).toBe('HTTP_404');
  expect(body.error.message).toBeDefined();
});

test('API 401 returns standardized error', async ({ request }) => {
  const res = await request.get(`${API}/api/auth/profile`);
  expect(res.status()).toBe(401);
  const body = await res.json();
  expect(body.success).toBe(false);
  expect(body.error.code).toBe('HTTP_401');
});

// --- Auth flow ---

test('login + refresh + logout flow', async ({ request }) => {
  // Login
  const loginRes = await request.post(`${API}/api/auth/login`, {
    data: { email: 'jenkinslisa1978@gmail.com', password: 'admin123456' },
  });
  expect(loginRes.status()).toBe(200);
  const loginBody = await loginRes.json();
  expect(loginBody.token).toBeDefined();

  // Check cookies were set
  const cookies = loginRes.headers()['set-cookie'];
  expect(cookies).toContain('__Host-refresh');
  expect(cookies).toContain('__Host-csrf');

  // Refresh
  const refreshRes = await request.post(`${API}/api/auth/refresh`);
  expect(refreshRes.status()).toBe(200);
  const refreshBody = await refreshRes.json();
  expect(refreshBody.token).toBeDefined();

  // Logout
  const logoutRes = await request.post(`${API}/api/auth/logout`);
  expect(logoutRes.status()).toBe(200);
  const logoutBody = await logoutRes.json();
  expect(logoutBody.success).toBe(true);
});

// --- Authenticated happy path ---

test('authenticated user can fetch profile', async ({ request }) => {
  // Login first
  const loginRes = await request.post(`${API}/api/auth/login`, {
    data: { email: 'jenkinslisa1978@gmail.com', password: 'admin123456' },
  });
  const { token } = await loginRes.json();

  // Fetch profile with token
  const profileRes = await request.get(`${API}/api/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(profileRes.status()).toBe(200);
  const profile = await profileRes.json();
  expect(profile.email).toBe('jenkinslisa1978@gmail.com');
});

// --- Product discovery ---

test('/trending-products page loads', async ({ page }) => {
  await page.goto('/trending-products');
  await page.waitForLoadState('networkidle');
  // Should show product cards
  const title = await page.title();
  expect(title).toContain('TrendScout');
});

test('/trending-products-today page loads with products', async ({ page }) => {
  await page.goto('/trending-products-today');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('[data-testid="seo-trending-page"]')).toBeVisible({ timeout: 10000 });
});

// --- Forgot/Reset password ---

test('forgot password flow works', async ({ request }) => {
  // Request reset
  const forgotRes = await request.post(`${API}/api/auth/forgot-password`, {
    data: { email: 'jenkinslisa1978@gmail.com' },
  });
  expect(forgotRes.status()).toBe(200);
  const forgotBody = await forgotRes.json();
  expect(forgotBody.success).toBe(true);

  // If email was sent, reset_link won't be in response — query DB directly via a test endpoint
  // For E2E: test the API contract is correct
  expect(forgotBody.message).toContain('reset link');
});

test('/forgot-password page renders', async ({ page }) => {
  await page.goto('/forgot-password');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('[data-testid="forgot-password-form"]')).toBeVisible({ timeout: 5000 });
});

test('/help page renders with FAQ', async ({ page }) => {
  await page.goto('/help');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('[data-testid="help-page"]')).toBeVisible({ timeout: 5000 });
  await expect(page.locator('[data-testid="faq-section"]')).toBeVisible();
});

test('/demo page renders with examples', async ({ page }) => {
  await page.goto('/demo');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('[data-testid="demo-page"]')).toBeVisible({ timeout: 5000 });
  await expect(page.locator('[data-testid="demo-analysis"]')).toBeVisible();
  await expect(page.locator('[data-testid="demo-launch-plan"]')).toBeVisible();
  await expect(page.locator('[data-testid="demo-ad-ideas"]')).toBeVisible();
});
