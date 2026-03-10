/**
 * Store Service - API calls for store management
 */

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Get store limits for a plan
 */
export const getStoreLimits = async (plan = 'starter') => {
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
 * Get all stores for a user
 */
export const getUserStores = async (userId, status = null) => {
  try {
    let url = `${API_URL}/api/stores?user_id=${userId}`;
    if (status) url += `&status=${status}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch stores');
    
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
export const getStore = async (storeId, userId = null) => {
  try {
    let url = `${API_URL}/api/stores/${storeId}`;
    if (userId) url += `?user_id=${userId}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch store');
    
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
export const generateStore = async (productId, userId, plan = 'starter', storeName = null) => {
  try {
    const response = await fetch(`${API_URL}/api/stores/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_id: productId,
        user_id: userId,
        plan,
        store_name: storeName,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
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
export const createStore = async (name, productId, userId, plan = 'starter') => {
  try {
    const response = await fetch(`${API_URL}/api/stores`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        product_id: productId,
        user_id: userId,
        plan,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
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
export const updateStore = async (storeId, updates, userId) => {
  try {
    const response = await fetch(`${API_URL}/api/stores/${storeId}?user_id=${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) throw new Error('Failed to update store');
    
    return await response.json();
  } catch (error) {
    console.error('Error updating store:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Delete a store
 */
export const deleteStore = async (storeId, userId) => {
  try {
    const response = await fetch(`${API_URL}/api/stores/${storeId}?user_id=${userId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) throw new Error('Failed to delete store');
    
    return { success: true };
  } catch (error) {
    console.error('Error deleting store:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Add product to store
 */
export const addProductToStore = async (storeId, productId, userId) => {
  try {
    const response = await fetch(`${API_URL}/api/stores/${storeId}/products?user_id=${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        store_id: storeId,
        product_id: productId,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add product');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error adding product to store:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Get store products
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
export const updateStoreProduct = async (storeId, productId, updates, userId) => {
  try {
    const response = await fetch(
      `${API_URL}/api/stores/${storeId}/products/${productId}?user_id=${userId}`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      }
    );
    
    if (!response.ok) throw new Error('Failed to update product');
    
    return await response.json();
  } catch (error) {
    console.error('Error updating store product:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Regenerate product copy
 */
export const regenerateProductCopy = async (storeId, productId, userId) => {
  try {
    const response = await fetch(
      `${API_URL}/api/stores/${storeId}/regenerate/${productId}?user_id=${userId}`,
      { method: 'POST' }
    );
    
    if (!response.ok) throw new Error('Failed to regenerate copy');
    
    return await response.json();
  } catch (error) {
    console.error('Error regenerating copy:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Delete store product
 */
export const deleteStoreProduct = async (storeId, productId, userId) => {
  try {
    const response = await fetch(
      `${API_URL}/api/stores/${storeId}/products/${productId}?user_id=${userId}`,
      { method: 'DELETE' }
    );
    
    if (!response.ok) throw new Error('Failed to delete product');
    
    return { success: true };
  } catch (error) {
    console.error('Error deleting store product:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Export store for Shopify
 */
export const exportStore = async (storeId, userId, format = 'shopify') => {
  try {
    const response = await fetch(
      `${API_URL}/api/stores/${storeId}/export?user_id=${userId}&format=${format}`
    );
    
    if (!response.ok) throw new Error('Failed to export store');
    
    return await response.json();
  } catch (error) {
    console.error('Error exporting store:', error);
    return { error: error.message };
  }
};

/**
 * Update store status
 */
export const updateStoreStatus = async (storeId, status, userId) => {
  try {
    const response = await fetch(`${API_URL}/api/stores/${storeId}/status?user_id=${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    
    if (!response.ok) throw new Error('Failed to update status');
    
    return await response.json();
  } catch (error) {
    console.error('Error updating store status:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Get store preview data
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
