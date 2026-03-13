/**
 * Analytics Service — Tracks user events for conversion funnel analysis.
 * Events are batched and sent to /api/analytics/batch every 3 seconds.
 */

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Generate a session ID that persists for the browser session
const getSessionId = () => {
  let sid = sessionStorage.getItem('ts_session_id');
  if (!sid) {
    sid = `s_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    sessionStorage.setItem('ts_session_id', sid);
  }
  return sid;
};

let eventQueue = [];
let flushTimer = null;

const flushEvents = async () => {
  if (eventQueue.length === 0) return;
  const batch = [...eventQueue];
  eventQueue = [];

  try {
    const token = localStorage.getItem('ts_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    await fetch(`${API_URL}/api/analytics/batch`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ events: batch }),
    });
  } catch {
    // Silently fail — analytics should never break the app
  }
};

const scheduleFlush = () => {
  if (flushTimer) return;
  flushTimer = setTimeout(() => {
    flushTimer = null;
    flushEvents();
  }, 3000);
};

/**
 * Track a single analytics event.
 * @param {string} event - Event name (e.g., 'page_view', 'signup_click')
 * @param {object} properties - Optional event properties
 */
export const trackEvent = (event, properties = {}) => {
  eventQueue.push({
    event,
    properties,
    session_id: getSessionId(),
    page: window.location.pathname,
    referrer: document.referrer || '',
    timestamp: new Date().toISOString(),
  });
  scheduleFlush();
};

/**
 * Track a page view. Call on every route change.
 */
export const trackPageView = (path) => {
  trackEvent('page_view', { path: path || window.location.pathname });
};

// Flush on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', flushEvents);
}

// Event name constants
export const EVENTS = {
  PAGE_VIEW: 'page_view',
  SIGNUP_CLICK: 'signup_click',
  SIGNUP_COMPLETE: 'signup_complete',
  LOGIN_COMPLETE: 'login_complete',
  PRODUCT_VIEW: 'product_view',
  PRODUCT_SAVE: 'product_save',
  UPGRADE_CLICK: 'upgrade_click',
  CHECKOUT_START: 'checkout_start',
  AD_GENERATE: 'ad_generate',
  LAUNCH_SIMULATE: 'launch_simulate',
  CTA_CLICK: 'cta_click',
  PRICING_VIEW: 'pricing_view',
  TRENDING_VIEW: 'trending_view',
  BLOG_VIEW: 'blog_view',
};
