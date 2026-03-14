/**
 * API Client - Centralized API calls with authentication.
 * Includes automatic token refresh on 401.
 */

import { API_URL } from '@/lib/config';

const TOKEN_KEY = 'trendscout_token';

/**
 * Get the current access token for API requests
 */
export const getAccessToken = async () => {
  return localStorage.getItem(TOKEN_KEY) || null;
};

/**
 * Attempt to refresh the access token via the refresh cookie
 */
const tryRefreshToken = async () => {
  try {
    const res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem(TOKEN_KEY, data.token);
      return data.token;
    }
  } catch {}
  return null;
};

/**
 * Get headers for authenticated API requests
 */
export const getAuthHeaders = async () => {
  const token = await getAccessToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

/**
 * Make an authenticated API request with auto-refresh on 401
 */
export const apiRequest = async (endpoint, options = {}) => {
  const authHeaders = await getAuthHeaders();
  const config = {
    ...options,
    credentials: 'include',
    headers: { ...authHeaders, ...options.headers },
  };
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
  let response = await fetch(url, config);

  // If 401, try to refresh the token and retry once
  if (response.status === 401 && !options._retried) {
    const newToken = await tryRefreshToken();
    if (newToken) {
      config.headers['Authorization'] = `Bearer ${newToken}`;
      config._retried = true;
      response = await fetch(url, config);
    }
  }

  return response;
};

export const apiGet = async (endpoint) => apiRequest(endpoint, { method: 'GET' });

export const apiPost = async (endpoint, data = {}) =>
  apiRequest(endpoint, { method: 'POST', body: JSON.stringify(data) });

export const apiPut = async (endpoint, data = {}) =>
  apiRequest(endpoint, { method: 'PUT', body: JSON.stringify(data) });

export const apiDelete = async (endpoint) =>
  apiRequest(endpoint, { method: 'DELETE' });

const api = {
  getAccessToken,
  getAuthHeaders,
  apiRequest,
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  get: async (endpoint) => {
    const response = await apiGet(endpoint);
    const data = await response.json().catch(() => ({}));
    return { data, status: response.status, ok: response.ok };
  },
  post: async (endpoint, body = {}) => {
    const response = await apiPost(endpoint, body);
    const data = await response.json().catch(() => ({}));
    return { data, status: response.status, ok: response.ok };
  },
  put: async (endpoint, body = {}) => {
    const response = await apiPut(endpoint, body);
    const data = await response.json().catch(() => ({}));
    return { data, status: response.status, ok: response.ok };
  },
  delete: async (endpoint) => {
    const response = await apiDelete(endpoint);
    const data = await response.json().catch(() => ({}));
    return { data, status: response.status, ok: response.ok };
  },
};

export default api;
