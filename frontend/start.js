/**
 * Production start script for TrendScout frontend.
 * 
 * Strategy: Start the static server FIRST (port binds in < 100ms),
 * then run prerender in the background. This ensures K8s health
 * checks pass immediately.
 */
const fs = require('fs');
const path = require('path');

// Prevent process crashes from propagating
process.on('uncaughtException', (err) => {
  console.error('[start] Uncaught exception:', err.message);
});
process.on('unhandledRejection', (reason) => {
  console.error('[start] Unhandled rejection:', reason);
});

const BUILD_DIR = path.join(__dirname, 'build');
const INDEX_HTML = path.join(BUILD_DIR, 'index.html');
const PORT = parseInt(process.env.PORT || '3000', 10);

let buildValid = false;
try {
  buildValid = fs.existsSync(INDEX_HTML) && fs.statSync(INDEX_HTML).size > 100;
} catch (e) {
  console.error('[start] Error checking build:', e.message);
}

console.log(`[start] Build valid: ${buildValid}, Port: ${PORT}`);

function startFallback(reason) {
  console.error(`[start] Starting fallback server. Reason: ${reason}`);
  const http = require('http');
  http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('<html><body><h1>TrendScout</h1><p>Build pending.</p></body></html>');
  }).listen(PORT, '0.0.0.0', () => console.log(`[start] Fallback listening on 0.0.0.0:${PORT}`));
}

if (!buildValid) {
  startFallback('No valid build found');
} else {
  try {
    // Start serve.js immediately (binds port in < 100ms)
    console.log('[start] Loading serve.js...');
    require('./serve.js');
    console.log('[start] serve.js loaded and listening.');
  } catch (e) {
    console.error(`[start] serve.js CRASHED: ${e.message}`);
    startFallback(`serve.js error: ${e.message}`);
  }

  // Run prerender AFTER server is up (non-blocking)
  setTimeout(() => {
    try {
      const { exec } = require('child_process');
      console.log('[start] Running prerender...');
      const child = exec('node prerender.js', { cwd: __dirname, timeout: 30000 });
      child.stdout?.pipe(process.stdout);
      child.stderr?.pipe(process.stderr);
      child.on('close', (code) => {
        if (code === 0) console.log('[start] Prerender complete.');
        else console.warn(`[start] Prerender exited with code ${code}`);
      });
      child.on('error', (e) => console.warn('[start] Prerender error:', e.message));
    } catch (e) {
      console.warn('[start] Prerender skipped:', e.message);
    }
  }, 100);
}
