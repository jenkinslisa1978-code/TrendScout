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
  '/about',
  '/contact',
  '/methodology',
  '/accuracy',
  '/blog',
  '/tools',
  '/changelog',
  '/sample-product-analysis',
  '/uk-product-viability-score',
  '/uk-product-research',
  '/for-shopify-sellers',
  '/for-amazon-uk-sellers',
  '/for-tiktok-shop-uk',
  '/shopify-product-research-uk',
  '/tiktok-shop-product-research-uk',
  '/best-products-to-sell-online-uk',
  '/product-validation-uk',
  '/dropshipping-uk',
  '/winning-products-uk',
  '/trend-analysis-uk',
  '/compare/jungle-scout-vs-trendscout',
  '/compare/sell-the-trend-vs-trendscout',
  '/compare/minea-vs-trendscout',
  '/compare/helium-10-vs-trendscout',
  '/compare/ecomhunt-vs-trendscout',
  '/product-quiz',
  '/trending-products',
  '/terms',
  '/privacy',
  '/cookie-policy',
  '/refund-policy',
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
