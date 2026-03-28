/**
 * Production start script for TrendScout frontend.
 * Runs prerender (fast, ~2s) then starts the static server.
 * Skips craco build — that happens during Docker image creation.
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const buildDir = path.join(__dirname, 'build');
const indexHtml = path.join(buildDir, 'index.html');

// If no build exists, do a full build (local dev only)
if (!fs.existsSync(indexHtml)) {
  console.log('[start] No build found, running craco build...');
  execSync('CI=false npx craco build', { stdio: 'inherit', cwd: __dirname });
}

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
