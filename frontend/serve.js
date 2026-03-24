/**
 * Static server for TrendScout.
 *
 * Serves prerendered HTML from the build directory:
 * 1. Tries to serve exact file (e.g., /static/js/main.js)
 * 2. Tries to serve directory index.html (e.g., /pricing → build/pricing/index.html)
 * 3. Falls back to root build/index.html (SPA fallback for app routes)
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

const server = http.createServer((req, res) => {
  const urlPath = req.url.split('?')[0].split('#')[0];
  const decodedPath = decodeURIComponent(urlPath);

  // 1. Try exact file match
  const exactFile = path.join(BUILD_DIR, decodedPath);
  if (fs.existsSync(exactFile) && fs.statSync(exactFile).isFile()) {
    return serveFile(res, exactFile);
  }

  // 2. Try directory index.html (prerendered pages)
  const dirIndex = path.join(BUILD_DIR, decodedPath, 'index.html');
  if (fs.existsSync(dirIndex) && fs.statSync(dirIndex).isFile()) {
    return serveFile(res, dirIndex);
  }

  // 3. SPA fallback: serve root index.html for all other routes
  if (fs.existsSync(ROOT_HTML)) {
    return serveFile(res, ROOT_HTML);
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not Found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[trendscout] Static server running on http://0.0.0.0:${PORT}`);
  console.log(`[trendscout] Serving from ${BUILD_DIR}`);
});
