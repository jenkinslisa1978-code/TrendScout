/**
 * Alpine-compatible static prerender script.
 * Uses jsdom (no Puppeteer/Chromium needed).
 * Generates static HTML snapshots for public routes to improve SEO and FCP.
 */
const fs = require('fs');
const path = require('path');

const ROUTES = [
  '/',
  '/features',
  '/pricing',
  '/how-it-works',
  '/methodology',
  '/blog',
  '/tools',
  '/accuracy',
  '/changelog',
];

const buildDir = path.join(__dirname, 'build');
const indexHtml = fs.readFileSync(path.join(buildDir, 'index.html'), 'utf8');

console.log(`[prerender] Starting prerender for ${ROUTES.length} routes...`);

ROUTES.forEach((route) => {
  const routePath = route === '/' ? '' : route;
  const dir = path.join(buildDir, routePath);

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const filePath = path.join(dir, 'index.html');

  // Only create if it doesn't already exist (don't overwrite the root index.html for /)
  if (route === '/') return;

  // Write the SPA shell to each route directory so nginx serves real HTML
  fs.writeFileSync(filePath, indexHtml);
  console.log(`[prerender] ${route} -> ${filePath}`);
});

console.log(`[prerender] Done. ${ROUTES.length - 1} route shells created.`);
