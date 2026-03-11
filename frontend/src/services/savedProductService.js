// Helper to get saved products from localStorage
const getDemoSavedProducts = () => {
  try {
    const saved = localStorage.getItem('trendscout_saved_products');
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
};

// Helper to set saved products in localStorage for demo mode
const setDemoSavedProducts = (products) => {
  try {
    localStorage.setItem('trendscout_saved_products', JSON.stringify(products));
  } catch {
    // Ignore localStorage errors
  }
};

// Get user's saved products
export const getSavedProducts = async (userId) => {
  return { data: getDemoSavedProducts(), error: null };
};

// Check if product is saved
export const isProductSaved = async (userId, productId) => {
  const savedProducts = getDemoSavedProducts();
  return { 
    data: savedProducts.some(sp => sp.product_id === productId), 
    error: null 
  };
};

// Save a product
export const saveProduct = async (userId, productId, productData = null) => {
  const savedProducts = getDemoSavedProducts();
  const existing = savedProducts.find(sp => sp.product_id === productId);
  if (!existing) {
    savedProducts.push({
      id: String(Date.now()),
      user_id: userId,
      product_id: productId,
      products: productData,
      created_at: new Date().toISOString()
    });
    setDemoSavedProducts(savedProducts);
  }
  return { error: null };
};

// Unsave a product
export const unsaveProduct = async (userId, productId) => {
  const savedProducts = getDemoSavedProducts();
  const filtered = savedProducts.filter(sp => sp.product_id !== productId);
  setDemoSavedProducts(filtered);
  return { error: null };
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
