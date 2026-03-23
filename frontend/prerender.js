/**
 * Content-injecting prerender script for TrendScout.
 *
 * Instead of copying the same index.html shell to every route,
 * this script injects page-specific content into each HTML file:
 * - Unique <title>, <meta description>, <link canonical>
 * - Unique OG tags
 * - JSON-LD structured data
 * - Visible prerender content (headings, body copy, CTAs, links)
 *
 * The React app hides #prerender-content on mount via CSS.
 * Crawlers see real, differentiated content on first response.
 */
const fs = require('fs');
const path = require('path');
const { PAGES, ALIASES, SITE, commonLinks } = require('./prerender-data');

const buildDir = path.join(__dirname, 'build');
const baseHtml = fs.readFileSync(path.join(buildDir, 'index.html'), 'utf8');

// Collect all routes: explicit pages + aliases + extra routes
const allRoutes = new Set([
  ...Object.keys(PAGES),
  ...Object.keys(ALIASES),
]);

console.log(`[prerender] Starting content-injecting prerender for ${allRoutes.size} routes...`);

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function buildPageHtml(route) {
  // Resolve aliases
  const canonicalRoute = ALIASES[route] || route;
  const pageData = PAGES[canonicalRoute];

  if (!pageData) {
    // No content data — just copy the shell with route-specific noscript nav
    return baseHtml;
  }

  let html = baseHtml;

  // 1. Replace <title>
  html = html.replace(
    /<title>[^<]*<\/title>/,
    `<title>${escapeHtml(pageData.title)}</title>`
  );

  // 2. Replace meta description
  html = html.replace(
    /<meta name="description" content="[^"]*"/,
    `<meta name="description" content="${escapeHtml(pageData.description)}"`
  );

  // 3. Add/replace canonical
  const canonicalUrl = SITE + pageData.canonical;
  if (html.includes('<link rel="canonical"')) {
    html = html.replace(/<link rel="canonical" href="[^"]*"/, `<link rel="canonical" href="${canonicalUrl}"`);
  } else {
    html = html.replace('</head>', `    <link rel="canonical" href="${canonicalUrl}" />\n    </head>`);
  }

  // 4. Replace OG tags
  html = html.replace(
    /<meta property="og:title" content="[^"]*"/,
    `<meta property="og:title" content="${escapeHtml(pageData.title)}"`
  );
  html = html.replace(
    /<meta property="og:description" content="[^"]*"/,
    `<meta property="og:description" content="${escapeHtml(pageData.description)}"`
  );

  // 5. Replace Twitter tags
  html = html.replace(
    /<meta name="twitter:title" content="[^"]*"/,
    `<meta name="twitter:title" content="${escapeHtml(pageData.title)}"`
  );
  html = html.replace(
    /<meta name="twitter:description" content="[^"]*"/,
    `<meta name="twitter:description" content="${escapeHtml(pageData.description)}"`
  );

  // 6. Inject JSON-LD structured data
  if (pageData.schema && pageData.schema.length > 0) {
    const schemaScripts = pageData.schema
      .map(s => `<script type="application/ld+json">${JSON.stringify(s)}</script>`)
      .join('\n    ');
    html = html.replace('</head>', `    ${schemaScripts}\n    </head>`);
  }

  // 7. Inject prerender content div before <div id="root">
  // This is visible to crawlers. React app hides it on mount.
  const prerenderBlock = `
    <div id="prerender-content" style="max-width:760px;margin:0 auto;padding:40px 24px;font-family:Manrope,Inter,system-ui,sans-serif;color:#1e293b;line-height:1.7;">
      <style>#prerender-content h1{font-size:28px;font-weight:800;margin:0 0 12px;color:#0f172a}#prerender-content h2{font-size:20px;font-weight:700;margin:28px 0 8px;color:#1e293b}#prerender-content h3{font-size:17px;font-weight:600;margin:20px 0 6px;color:#334155}#prerender-content p{font-size:15px;color:#475569;margin:0 0 12px}#prerender-content ul,#prerender-content ol{padding-left:24px;margin:0 0 16px;color:#475569;font-size:15px}#prerender-content li{margin-bottom:6px}#prerender-content a{color:#4f46e5;text-decoration:underline;text-underline-offset:2px}#prerender-content strong{color:#1e293b}#prerender-content .pr-faq{margin:24px 0}#prerender-content .pr-faq details{border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;margin-bottom:8px}#prerender-content .pr-faq summary{cursor:pointer;font-size:15px;font-weight:600;color:#1e293b}#prerender-content .pr-faq p{margin:8px 0 0;font-size:14px}#prerender-content .pr-links ul{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px}#prerender-content .pr-links a{display:inline-block;padding:6px 14px;background:#eef2ff;border-radius:6px;font-size:13px;font-weight:500;text-decoration:none;color:#4f46e5}#prerender-content nav.pr-footer{border-top:1px solid #e2e8f0;padding-top:20px;margin-top:32px}#prerender-content nav.pr-footer a{color:#64748b;font-size:13px;margin-right:16px;text-decoration:none}</style>
      ${pageData.body}
      <nav class="pr-footer">
        <a href="/">Home</a>
        <a href="/pricing">Pricing</a>
        <a href="/how-it-works">How It Works</a>
        <a href="/trending-products">Trending Products</a>
        <a href="/sample-product-analysis">Sample Analysis</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
        <a href="/terms">Terms</a>
        <a href="/privacy">Privacy</a>
      </nav>
    </div>`;

  html = html.replace('<div id="root"></div>', `${prerenderBlock}\n        <div id="root"></div>`);

  return html;
}

// Process all routes
let count = 0;
for (const route of allRoutes) {
  const routePath = route === '/' ? '' : route;
  const dir = path.join(buildDir, routePath);

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const filePath = path.join(dir, 'index.html');
  const pageHtml = buildPageHtml(route);

  // For root route, overwrite the main index.html
  if (route === '/') {
    fs.writeFileSync(path.join(buildDir, 'index.html'), pageHtml);
    console.log(`[prerender] / -> build/index.html (root, content-injected)`);
  } else {
    fs.writeFileSync(filePath, pageHtml);
    console.log(`[prerender] ${route} -> ${filePath}`);
  }
  count++;
}

console.log(`[prerender] Done. ${count} pages with unique content generated.`);
