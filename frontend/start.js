/**
 * Production start script for TrendScout frontend.
 * 
 * Strategy: Start the static server FIRST (port binds in < 100ms),
 * then run prerender in the background. This ensures K8s health
 * checks pass immediately.
 */
const fs = require('fs');
const path = require('path');

const BUILD_DIR = path.join(__dirname, 'build');
const INDEX_HTML = path.join(BUILD_DIR, 'index.html');

const buildValid = fs.existsSync(INDEX_HTML) && fs.statSync(INDEX_HTML).size > 100;

if (!buildValid) {
  // No build exists — start a minimal HTTP server so K8s doesn't kill the pod
  console.error('[start] No valid build found. Starting fallback server.');
  const http = require('http');
  const PORT = parseInt(process.env.PORT || '3000', 10);
  http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('<html><body><h1>TrendScout</h1><p>Build pending.</p></body></html>');
  }).listen(PORT, '0.0.0.0', () => console.log(`[start] Fallback on port ${PORT}`));
} else {
  // Start serve.js immediately (binds port in < 100ms)
  console.log('[start] Starting static server...');
  require('./serve.js');

  // Run prerender AFTER server is up (non-blocking, updates HTML files in-place)
  setTimeout(() => {
    try {
      const { execSync } = require('child_process');
      console.log('[start] Running prerender...');
      execSync('node prerender.js', { cwd: __dirname, stdio: 'inherit', timeout: 30000 });
      console.log('[start] Prerender complete.');
    } catch (e) {
      console.warn('[start] Prerender skipped:', e.message);
    }
  }, 100);
}
