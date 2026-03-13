import api from '@/lib/api';

// Get user's saved workspace products
export const getSavedProducts = async (userId, status = null) => {
  try {
    const params = status ? `?status=${status}` : '';
    const response = await api.get(`/api/workspace/products${params}`);
    return { data: response.data.items || [], error: null };
  } catch (error) {
    console.error('Failed to fetch workspace products:', error);
    return { data: [], error: error.message };
  }
};

// Check if product is saved
export const isProductSaved = async (userId, productId) => {
  try {
    const response = await api.get(`/api/workspace/products/${productId}/check`);
    return { data: response.data.saved, item: response.data.item, error: null };
  } catch {
    return { data: false, item: null, error: null };
  }
};

// Save a product
export const saveProduct = async (userId, productId, productData = null) => {
  try {
    await api.post('/api/workspace/products', { product_id: productId });
    return { error: null };
  } catch (error) {
    return { error: error.message };
  }
};

// Unsave a product
export const unsaveProduct = async (userId, productId) => {
  try {
    await api.delete(`/api/workspace/products/${productId}`);
    return { error: null };
  } catch (error) {
    return { error: error.message };
  }
};

// Toggle save status
export const toggleSaveProduct = async (userId, productId, productData = null) => {
  const { data: isSaved } = await isProductSaved(userId, productId);
  if (isSaved) {
    return unsaveProduct(userId, productId);
  } else {
    return saveProduct(userId, productId, productData);
  }
};

// Update note for a saved product
export const updateProductNote = async (productId, note) => {
  try {
    await api.put(`/api/workspace/products/${productId}/note`, { note });
    return { error: null };
  } catch (error) {
    return { error: error.message };
  }
};

// Update launch status for a saved product
export const updateProductStatus = async (productId, launchStatus) => {
  try {
    await api.put(`/api/workspace/products/${productId}/status`, { launch_status: launchStatus });
    return { error: null };
  } catch (error) {
    return { error: error.message };
  }
};
