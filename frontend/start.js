/**
 * Production start script for TrendScout frontend.
 * Runs prerender (fast, ~2s) then starts the static server.
 * Does NOT attempt craco build — that must happen at image build time.
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const buildDir = path.join(__dirname, 'build');
const indexHtml = path.join(buildDir, 'index.html');

if (!fs.existsSync(indexHtml)) {
  console.error('[start] FATAL: No build/index.html found. Run "yarn build" first.');
  console.error('[start] Starting minimal fallback server...');

  // Start a minimal server that returns 200 so K8s doesn't kill the pod
  const http = require('http');
  const PORT = parseInt(process.env.PORT || '3000', 10);
  http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('<html><body><h1>TrendScout</h1><p>Build not found. Deploying...</p></body></html>');
  }).listen(PORT, '0.0.0.0', () => {
    console.log(`[start] Fallback server on port ${PORT}`);
  });
} else {
  // Run prerender (fast — just injects content into existing HTML files)
  try {
    console.log('[start] Running prerender...');
    execSync('node prerender.js', { stdio: 'inherit', cwd: __dirname });
  } catch (e) {
    console.warn('[start] Prerender had warnings (non-fatal):', e.message);
  }

  // Start the server
  console.log('[start] Starting server...');
  require('./serve.js');
}
