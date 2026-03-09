import { supabase, isSupabaseConfigured } from '@/lib/supabase';

// Mock saved products for demo mode
let MOCK_SAVED_PRODUCTS = [];

// Get user's saved products
export const getSavedProducts = async (userId) => {
  if (!isSupabaseConfigured()) {
    return { data: MOCK_SAVED_PRODUCTS, error: null };
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
    return { 
      data: MOCK_SAVED_PRODUCTS.some(sp => sp.product_id === productId), 
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
    const existing = MOCK_SAVED_PRODUCTS.find(sp => sp.product_id === productId);
    if (!existing) {
      MOCK_SAVED_PRODUCTS.push({
        id: String(MOCK_SAVED_PRODUCTS.length + 1),
        user_id: userId,
        product_id: productId,
        products: productData,
        created_at: new Date().toISOString()
      });
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
    MOCK_SAVED_PRODUCTS = MOCK_SAVED_PRODUCTS.filter(sp => sp.product_id !== productId);
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
