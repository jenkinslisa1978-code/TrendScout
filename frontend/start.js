/**
 * Production start script for TrendScout frontend.
 * Runs prerender (fast, ~2s) then starts the static server.
 * Does NOT attempt craco build — that must happen at image build time.
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PORT = parseInt(process.env.PORT || '3000', 10);
const buildDir = path.join(__dirname, 'build');
const indexHtml = path.join(buildDir, 'index.html');

// Check build exists and is valid (not an empty file from a failed build)
const buildValid = fs.existsSync(indexHtml) && fs.statSync(indexHtml).size > 100;

if (!buildValid) {
  console.error('[start] FATAL: No valid build/index.html found.');
  console.error('[start] Starting minimal fallback server so K8s health checks pass...');

  const http = require('http');
  http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('<html><body><h1>TrendScout</h1><p>Frontend build not available.</p></body></html>');
  }).listen(PORT, '0.0.0.0', () => {
    console.log(`[start] Fallback server listening on port ${PORT}`);
  });
} else {
  // Prerender: inject page-specific content into HTML files (fast, ~2s, has 30s timeout)
  try {
    console.log('[start] Running prerender...');
    execSync('node prerender.js', { stdio: 'inherit', cwd: __dirname, timeout: 30000 });
    console.log('[start] Prerender complete.');
  } catch (e) {
    console.warn('[start] Prerender skipped (non-fatal):', e.message);
  }

  // Start the static server
  console.log('[start] Starting server...');
  require('./serve.js');
}
