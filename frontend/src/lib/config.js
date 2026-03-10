/**
 * Shared API URL configuration.
 * Uses REACT_APP_BACKEND_URL when running on the same host (preview environment),
 * falls back to relative paths for production (where backend serves frontend).
 */
const configuredUrl = process.env.REACT_APP_BACKEND_URL || '';
const isSameOrigin = typeof window !== 'undefined' && configuredUrl.includes(window.location.hostname);
export const API_URL = isSameOrigin ? configuredUrl : '';
