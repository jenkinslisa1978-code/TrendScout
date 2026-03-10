/**
 * Store Service - API calls for store management
 * Uses authenticated API client for secure requests
 */

import { apiGet, apiPost, apiPut, apiDelete } from '@/lib/api';
import { API_URL } from '@/lib/config';

/**
 * Get store limits for a plan (public endpoint)
 */
export const getStoreLimits = async (plan = 'free') => {
  try {
    const response = await fetch(`${API_URL}/api/stores/limits?plan=${plan}`);
    if (!response.ok) throw new Error('Failed to fetch store limits');
    return await response.json();
  } catch (error) {
    console.error('Error fetching store limits:', error);
    return { plan, limit: 1, all_limits: {} };
  }
};

/**
 * Get all stores for the authenticated user
 */
export const getUserStores = async (status = null) => {
  try {
    let url = `/api/stores`;
    if (status) url += `?status=${status}`;
    
    const response = await apiGet(url);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to fetch stores');
    }
    
    const result = await response.json();
    return { data: result.data || [], error: null };
  } catch (error) {
    console.error('Error fetching stores:', error);
    return { data: [], error: error.message };
  }
};

/**
 * Get a single store by ID
 */
export const getStore = async (storeId) => {
  try {
    const response = await apiGet(`/api/stores/${storeId}`);
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to fetch store');
    }
    
    const result = await response.json();
    return { data: result.data, error: null };
  } catch (error) {
    console.error('Error fetching store:', error);
    return { data: null, error: error.message };
  }
};

/**
 * Generate store content from a product (AI store builder)
 */
export const generateStore = async (productId, plan = 'free', storeName = null) => {
  try {
    const response = await apiPost(`/api/stores/generate`, {
      product_id: productId,
      plan,
      store_name: storeName,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to generate store');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error generating store:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Create a new store
 */
export const createStore = async (name, productId, plan = 'free') => {
  try {
    const response = await apiPost(`/api/stores`, {
      name,
      product_id: productId,
      plan,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to create store');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating store:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Update a store
 */
export const updateStore = async (storeId, updates) => {
  try {
    const response = await apiPut(`/api/stores/${storeId}`, updates);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to update store');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating store:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Delete a store
 */
export const deleteStore = async (storeId) => {
  try {
    const response = await apiDelete(`/api/stores/${storeId}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to delete store');
    }
    
    return { success: true };
  } catch (error) {
    console.error('Error deleting store:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Add product to store
 */
export const addProductToStore = async (storeId, productId) => {
  try {
    const response = await apiPost(`/api/stores/${storeId}/products`, {
      store_id: storeId,
      product_id: productId,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to add product');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error adding product to store:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Get store products (public if store is published)
 */
export const getStoreProducts = async (storeId) => {
  try {
    const response = await fetch(`${API_URL}/api/stores/${storeId}/products`);
    if (!response.ok) throw new Error('Failed to fetch store products');
    
    const result = await response.json();
    return { data: result.data || [], error: null };
  } catch (error) {
    console.error('Error fetching store products:', error);
    return { data: [], error: error.message };
  }
};

/**
 * Update store product
 */
export const updateStoreProduct = async (storeId, productId, updates) => {
  try {
    const response = await apiPut(`/api/stores/${storeId}/products/${productId}`, updates);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to update product');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating store product:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Regenerate product copy
 */
export const regenerateProductCopy = async (storeId, productId) => {
  try {
    const response = await apiPost(`/api/stores/${storeId}/regenerate/${productId}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to regenerate copy');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error regenerating copy:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Delete store product
 */
export const deleteStoreProduct = async (storeId, productId) => {
  try {
    const response = await apiDelete(`/api/stores/${storeId}/products/${productId}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to delete product');
    }
    
    return { success: true };
  } catch (error) {
    console.error('Error deleting store product:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Export store for Shopify
 */
export const exportStore = async (storeId, format = 'shopify') => {
  try {
    const response = await apiGet(`/api/stores/${storeId}/export?format=${format}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to export store');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error exporting store:', error);
    return { error: error.message };
  }
};

/**
 * Update store status
 */
export const updateStoreStatus = async (storeId, status) => {
  try {
    const response = await apiPut(`/api/stores/${storeId}/status`, { status });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to update status');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating store status:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Get store preview data (public endpoint)
 */
export const getStorePreview = async (storeId) => {
  try {
    const response = await fetch(`${API_URL}/api/stores/${storeId}/preview`);
    if (!response.ok) throw new Error('Failed to fetch store preview');
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching store preview:', error);
    return { store: null, featured_product: null, error: error.message };
  }
};
