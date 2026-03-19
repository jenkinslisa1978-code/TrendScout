/**
 * Analytics Service — Tracks user events via internal batch API + GA4 gtag bridge.
 * 
 * Internal events batch to /api/analytics/batch every 3 seconds.
 * GA4 events fire via window.gtag() when GA4 is configured.
 */

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

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
    // Analytics should never break the app
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
 * Send event to GA4 via gtag() if available.
 */
const sendToGA4 = (eventName, params = {}) => {
  if (typeof window !== 'undefined' && typeof window.gtag === 'function') {
    window.gtag('event', eventName, {
      ...params,
      page_path: window.location.pathname,
    });
  }
};

/**
 * Track a single analytics event. Fires to both internal API and GA4.
 */
export const trackEvent = (event, properties = {}) => {
  // Internal batch
  eventQueue.push({
    event,
    properties,
    session_id: getSessionId(),
    page: window.location.pathname,
    referrer: document.referrer || '',
    timestamp: new Date().toISOString(),
  });
  scheduleFlush();

  // GA4 bridge
  sendToGA4(event, properties);
};

/**
 * Track a page view.
 */
export const trackPageView = (path) => {
  const pagePath = path || window.location.pathname;
  trackEvent('page_view', { path: pagePath });
};

// Flush on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', flushEvents);
}

// Event name constants — comprehensive for conversion tracking
export const EVENTS = {
  PAGE_VIEW: 'page_view',
  // Homepage
  HOMEPAGE_PRIMARY_CTA: 'homepage_primary_cta_click',
  HOMEPAGE_SECONDARY_CTA: 'homepage_secondary_cta_click',
  // Signup / Auth
  SIGNUP_CLICK: 'signup_start',
  SIGNUP_COMPLETE: 'signup_complete',
  LOGIN_CLICK: 'login_click',
  LOGIN_COMPLETE: 'login_complete',
  // Pricing
  PRICING_VIEW: 'pricing_view',
  PRICING_CTA_CLICK: 'pricing_cta_click',
  PRICING_PLAN_SELECTED: 'pricing_plan_selected',
  PRICING_TOGGLE: 'pricing_toggle',
  CHECKOUT_START: 'checkout_start',
  // Upgrade
  UPGRADE_CLICK: 'upgrade_click',
  // Products
  PRODUCT_VIEW: 'product_view',
  PRODUCT_SAVE: 'product_save',
  TRENDING_VIEW: 'trending_view',
  TRENDING_PRODUCT_CARD_CLICK: 'trending_product_card_click',
  // Viability
  VIABILITY_BADGE_CLICK: 'viability_badge_interaction',
  // Free Tools
  FREE_TOOL_USED: 'free_tool_used',
  FREE_TOOL_RESULT: 'free_tool_result_generated',
  // Landing Pages
  UK_LANDING_CTA: 'uk_landing_page_cta_click',
  COMPARE_PAGE_CTA: 'compare_page_cta_click',
  // Features
  AD_GENERATE: 'ad_generate',
  LAUNCH_SIMULATE: 'launch_simulate',
  CTA_CLICK: 'cta_click',
  BLOG_VIEW: 'blog_view',
  CONTACT_SUBMIT: 'contact_form_submit',
};
