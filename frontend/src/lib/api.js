/**
 * API Client - Centralized API calls with authentication
 * Uses stored JWT token from backend auth.
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
 * Make an authenticated API request
 */
export const apiRequest = async (endpoint, options = {}) => {
  const authHeaders = await getAuthHeaders();
  const config = {
    ...options,
    headers: { ...authHeaders, ...options.headers },
  };
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
  return fetch(url, config);
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
