/**
 * API Client - Centralized API calls with authentication
 * 
 * This module provides a secure way to make API calls with the user's
 * Supabase JWT token automatically attached to requests.
 */

import { supabase, isSupabaseConfigured } from '@/lib/supabase';
import { API_URL } from '@/lib/config';

// Demo mode token prefix
const DEMO_TOKEN_PREFIX = 'demo_';
const DEMO_USER_ID = 'demo-user-id';

/**
 * Get the current access token for API requests
 * Returns demo token in demo mode, or Supabase JWT in live mode
 */
export const getAccessToken = async () => {
  if (!isSupabaseConfigured()) {
    // Demo mode - return demo token
    return `${DEMO_TOKEN_PREFIX}${DEMO_USER_ID}`;
  }

  try {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  } catch (error) {
    console.error('Error getting access token:', error);
    return null;
  }
};

/**
 * Get headers for authenticated API requests
 */
export const getAuthHeaders = async () => {
  const token = await getAccessToken();
  const headers = {
    'Content-Type': 'application/json',
  };

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
    headers: {
      ...authHeaders,
      ...options.headers,
    },
  };

  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
  const response = await fetch(url, config);
  
  return response;
};

/**
 * GET request with authentication
 */
export const apiGet = async (endpoint) => {
  return apiRequest(endpoint, { method: 'GET' });
};

/**
 * POST request with authentication
 */
export const apiPost = async (endpoint, data = {}) => {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
};

/**
 * PUT request with authentication
 */
export const apiPut = async (endpoint, data = {}) => {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
};

/**
 * DELETE request with authentication
 */
export const apiDelete = async (endpoint) => {
  return apiRequest(endpoint, { method: 'DELETE' });
};

/**
 * API methods matching common axios/fetch patterns
 * These wrap the underlying functions to provide a cleaner API
 */
const api = {
  getAccessToken,
  getAuthHeaders,
  apiRequest,
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  // Axios-like interface methods
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
