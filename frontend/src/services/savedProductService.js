import { supabase, isSupabaseConfigured } from '@/lib/supabase';

// Helper to get saved products from localStorage in demo mode
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
  if (!isSupabaseConfigured()) {
    return { data: getDemoSavedProducts(), error: null };
  }

  const { data, error } = await supabase
    .from('saved_products')
    .select(`
      id,
      created_at,
      products (*)
    `)
    .eq('user_id', userId)
    .order('created_at', { ascending: false });

  return { data, error };
};

// Check if product is saved
export const isProductSaved = async (userId, productId) => {
  if (!isSupabaseConfigured()) {
    const savedProducts = getDemoSavedProducts();
    return { 
      data: savedProducts.some(sp => sp.product_id === productId), 
      error: null 
    };
  }

  const { data, error } = await supabase
    .from('saved_products')
    .select('id')
    .eq('user_id', userId)
    .eq('product_id', productId)
    .single();

  return { data: !!data, error: error?.code === 'PGRST116' ? null : error };
};

// Save a product
export const saveProduct = async (userId, productId, productData = null) => {
  if (!isSupabaseConfigured()) {
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
  }

  const { error } = await supabase
    .from('saved_products')
    .insert([{ user_id: userId, product_id: productId }]);

  return { error };
};

// Unsave a product
export const unsaveProduct = async (userId, productId) => {
  if (!isSupabaseConfigured()) {
    const savedProducts = getDemoSavedProducts();
    const filtered = savedProducts.filter(sp => sp.product_id !== productId);
    setDemoSavedProducts(filtered);
    return { error: null };
  }

  const { error } = await supabase
    .from('saved_products')
    .delete()
    .eq('user_id', userId)
    .eq('product_id', productId);

  return { error };
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
