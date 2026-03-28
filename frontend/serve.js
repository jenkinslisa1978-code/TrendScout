/**
 * Static server for TrendScout.
 *
 * Serves prerendered HTML from the build directory:
 * 1. Tries to serve exact file (e.g., /static/js/main.js)
 * 2. Tries to serve directory index.html (e.g., /pricing → build/pricing/index.html)
 * 3. For dynamic SSR pages (e.g., /trending-products), fetches live data from API
 *    and injects it into HTML for crawlers
 * 4. Falls back to root build/index.html (SPA fallback for app routes)
 *
 * This ensures crawlers see unique, page-specific HTML for prerendered routes
 * while React app routes still work via SPA fallback.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = parseInt(process.env.PORT || '3000', 10);
const BUILD_DIR = path.join(__dirname, 'build');
const ROOT_HTML = path.join(BUILD_DIR, 'index.html');
const BACKEND_URL = 'http://localhost:8001';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.eot': 'application/vnd.ms-fontobject',
  '.otf': 'font/otf',
  '.map': 'application/json',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.webmanifest': 'application/manifest+json',
};

// Crawler user agents for dynamic SSR
const CRAWLER_UA = /googlebot|bingbot|yandex|baiduspider|duckduckbot|slurp|facebookexternalhit|twitterbot|linkedinbot|embedly|quora|pinterest|redditbot|applebot|semrushbot|ahrefsbot/i;

// Dynamic SSR routes: path -> API endpoint + renderer
const DYNAMIC_SSR_ROUTES = {
  '/trending-products': {
    api: '/api/public/trending-products',
    title: 'Trending Products in the UK Market Right Now | TrendScout',
    description: 'See what products are trending in the UK market. Live data on demand, margins, and competition — updated daily.',
    render: (data) => {
      const products = data?.products || [];
      if (products.length === 0) return '<p>No trending products found.</p>';
      let html = `<h1>Trending Products in the UK Market</h1>\n`;
      html += `<p>${products.length} products trending right now. Updated daily with live market data.</p>\n`;
      html += '<div class="ssr-products">\n';
      for (const p of products.slice(0, 20)) {
        html += `<article>\n`;
        html += `  <h2>${escapeHtml(p.product_name || p.title || '')}</h2>\n`;
        if (p.category) html += `  <p><strong>Category:</strong> ${escapeHtml(p.category)}</p>\n`;
        if (p.description) html += `  <p>${escapeHtml((p.description || '').substring(0, 200))}</p>\n`;
        if (p.metrics?.demand_score) html += `  <p>Demand Score: ${p.metrics.demand_score}/100</p>\n`;
        if (p.metrics?.trend_label) html += `  <p>Trend: ${escapeHtml(p.metrics.trend_label)}</p>\n`;
        html += `</article>\n`;
      }
      html += '</div>\n';
      return html;
    },
  },
  '/discover': {
    api: '/api/public/daily-picks',
    title: 'Discover Validated Product Ideas for the UK Market | TrendScout',
    description: 'Browse AI-validated product ideas with demand scores, margin estimates, and competition data. Updated daily.',
    render: (data) => {
      const products = data?.picks || data?.products || data || [];
      if (!Array.isArray(products) || products.length === 0) return '<p>No products found.</p>';
      let html = `<h1>Discover Validated Product Ideas</h1>\n`;
      html += `<p>Browse ${products.length} validated product opportunities for the UK market.</p>\n`;
      for (const p of products.slice(0, 15)) {
        html += `<article>\n`;
        html += `  <h2>${escapeHtml(p.product_name || p.title || '')}</h2>\n`;
        if (p.category) html += `  <p>Category: ${escapeHtml(p.category)}</p>\n`;
        if (p.metrics?.demand_score) html += `  <p>Demand: ${p.metrics.demand_score}/100</p>\n`;
        html += `</article>\n`;
      }
      return html;
    },
  },
  '/reports/weekly-winning-products': {
    api: '/api/public/top-trending',
    title: 'Weekly Winning Products Report - UK Market | TrendScout',
    description: 'This week\'s top performing product opportunities in the UK ecommerce market. Validated demand data and profit margins.',
    render: (data) => {
      const products = data?.products || data || [];
      if (!Array.isArray(products) || products.length === 0) return '<p>Report not available.</p>';
      let html = `<h1>Weekly Winning Products - UK Market</h1>\n`;
      html += `<p>Top ${products.length} product opportunities this week.</p>\n`;
      for (const p of products.slice(0, 10)) {
        html += `<article>\n`;
        html += `  <h2>${escapeHtml(p.product_name || p.title || '')}</h2>\n`;
        if (p.category) html += `  <p>Category: ${escapeHtml(p.category)}</p>\n`;
        html += `</article>\n`;
      }
      return html;
    },
  },
};

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function getMime(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return MIME_TYPES[ext] || 'application/octet-stream';
}

function serveFile(res, filePath, statusCode = 200) {
  const mime = getMime(filePath);
  const isStatic = filePath.includes('/static/');

  res.writeHead(statusCode, {
    'Content-Type': mime,
    ...(isStatic ? { 'Cache-Control': 'public, max-age=31536000, immutable' } : {}),
    ...(!isStatic && mime.startsWith('text/html') ? { 'Cache-Control': 'no-cache' } : {}),
  });

  fs.createReadStream(filePath).pipe(res);
}

// Simple in-memory cache for SSR pages (5 min TTL)
const ssrCache = {};
const SSR_CACHE_TTL = 5 * 60 * 1000;

async function fetchAndRenderSSR(route, config) {
  const cacheKey = route;
  const cached = ssrCache[cacheKey];
  if (cached && (Date.now() - cached.time) < SSR_CACHE_TTL) {
    return cached.html;
  }

  try {
    const resp = await fetch(`${BACKEND_URL}${config.api}`);
    if (!resp.ok) throw new Error(`API returned ${resp.status}`);
    const data = await resp.json();

    const baseHtml = fs.readFileSync(ROOT_HTML, 'utf8');
    const renderedContent = config.render(data);

    // Inject meta tags + SSR content
    let html = baseHtml;
    html = html.replace(/<title>[^<]*<\/title>/, `<title>${escapeHtml(config.title)}</title>`);
    html = html.replace(
      /<meta name="description"[^>]*>/,
      `<meta name="description" content="${escapeHtml(config.description)}">`
    );

    // Inject visible content for crawlers (hidden by React on mount)
    const ssrBlock = `<div id="ssr-content" style="padding:20px;max-width:1200px;margin:0 auto">${renderedContent}</div>`;
    html = html.replace('<div id="root">', `${ssrBlock}\n<div id="root">`);

    // Add JSON-LD for products
    if (route === '/trending-products') {
      const products = data?.products || [];
      const jsonLd = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        name: 'Trending Products in the UK Market',
        numberOfItems: products.length,
        itemListElement: products.slice(0, 10).map((p, i) => ({
          '@type': 'ListItem',
          position: i + 1,
          item: {
            '@type': 'Product',
            name: p.product_name || p.title || '',
            description: (p.description || '').substring(0, 200),
            category: p.category || '',
          },
        })),
      };
      html = html.replace('</head>', `<script type="application/ld+json">${JSON.stringify(jsonLd)}</script>\n</head>`);
    }

    ssrCache[cacheKey] = { html, time: Date.now() };
    return html;
  } catch (err) {
    console.error(`[ssr] Error rendering ${route}: ${err.message}`);
    return null;
  }
}

const server = http.createServer(async (req, res) => {
  const urlPath = req.url.split('?')[0].split('#')[0];
  const decodedPath = decodeURIComponent(urlPath);
  const userAgent = req.headers['user-agent'] || '';

  // 1. Try exact file match
  const exactFile = path.join(BUILD_DIR, decodedPath);
  if (fs.existsSync(exactFile) && fs.statSync(exactFile).isFile()) {
    return serveFile(res, exactFile);
  }

  // 2. Dynamic SSR for crawlers on specific routes (before prerendered fallback)
  const ssrConfig = DYNAMIC_SSR_ROUTES[decodedPath];
  if (ssrConfig && CRAWLER_UA.test(userAgent)) {
    const html = await fetchAndRenderSSR(decodedPath, ssrConfig);
    if (html) {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache' });
      return res.end(html);
    }
  }

  // 3. Try directory index.html (prerendered pages)
  const dirIndex = path.join(BUILD_DIR, decodedPath, 'index.html');
  if (fs.existsSync(dirIndex) && fs.statSync(dirIndex).isFile()) {
    return serveFile(res, dirIndex);
  }

  // 4. SPA fallback: serve root index.html for all other routes
  if (fs.existsSync(ROOT_HTML)) {
    return serveFile(res, ROOT_HTML);
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not Found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[trendscout] Static server running on http://0.0.0.0:${PORT}`);
  console.log(`[trendscout] Serving from ${BUILD_DIR}`);
  console.log(`[trendscout] Dynamic SSR enabled for: ${Object.keys(DYNAMIC_SSR_ROUTES).join(', ')}`);
});
