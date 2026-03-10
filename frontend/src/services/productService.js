import { runFullAutomation, batchRunAutomation } from '@/lib/automation';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Get all products from backend API
export const getProducts = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    if (filters.category) params.append('category', filters.category);
    if (filters.trend_stage) params.append('trend_stage', filters.trend_stage);
    if (filters.opportunity_rating) params.append('opportunity_rating', filters.opportunity_rating);
    if (filters.early_trend_label) params.append('early_trend_label', filters.early_trend_label);
    if (filters.search) params.append('search', filters.search);
    if (filters.sortBy) params.append('sort_by', filters.sortBy);
    if (filters.sortOrder) params.append('sort_order', filters.sortOrder);
    if (filters.limit) params.append('limit', filters.limit);
    
    const queryString = params.toString();
    const url = `${API_URL}/api/products${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch products');
    }
    
    const result = await response.json();
    return { data: result.data || [], error: null };
  } catch (error) {
    console.error('Error fetching products:', error);
    return { data: [], error: error.message };
  }
};

// Get single product by ID from backend API
export const getProductById = async (id) => {
  try {
    const response = await fetch(`${API_URL}/api/products/${id}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        return { data: null, error: { message: 'Product not found' } };
      }
      throw new Error('Failed to fetch product');
    }
    
    const result = await response.json();
    return { data: result.data, error: null };
  } catch (error) {
    console.error('Error fetching product:', error);
    return { data: null, error: { message: error.message } };
  }
};

// Get unique categories from backend
export const getCategories = async () => {
  try {
    const { data: products } = await getProducts({});
    if (products) {
      const categories = [...new Set(products.map(p => p.category))];
      return { data: categories, error: null };
    }
    return { data: [], error: null };
  } catch (error) {
    return { data: [], error: error.message };
  }
};

// Create product via backend API - with automation
export const createProduct = async (productData, runAutomation = true) => {
  try {
    const response = await fetch(`${API_URL}/api/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(productData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create product');
    }
    
    const result = await response.json();
    return { data: result.data, error: null, alert: result.alert };
  } catch (error) {
    console.error('Error creating product:', error);
    return { data: null, error: { message: error.message }, alert: null };
  }
};

// Update product via backend API - with automation
export const updateProduct = async (id, productData, runAutomation = true) => {
  try {
    const response = await fetch(`${API_URL}/api/products/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(productData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to update product');
    }
    
    const result = await response.json();
    return { data: result.data, error: null, alert: result.alert };
  } catch (error) {
    console.error('Error updating product:', error);
    return { data: null, error: { message: error.message }, alert: null };
  }
};

// Delete product via backend API
export const deleteProduct = async (id) => {
  try {
    const response = await fetch(`${API_URL}/api/products/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete product');
    }
    
    return { error: null };
  } catch (error) {
    console.error('Error deleting product:', error);
    return { error: { message: error.message } };
  }
};

// Get dashboard stats from backend
export const getDashboardStats = async () => {
  try {
    const { data: products } = await getProducts({});
    
    if (!products || products.length === 0) {
      return {
        data: {
          totalProducts: 0,
          avgTrendScore: 0,
          highOpportunityCount: 0,
          risingProducts: 0,
          totalTikTokViews: 0
        },
        error: null
      };
    }

    return {
      data: {
        totalProducts: products.length,
        avgTrendScore: Math.round(products.reduce((sum, p) => sum + (p.trend_score || 0), 0) / products.length),
        highOpportunityCount: products.filter(p => ['high', 'very high'].includes(p.opportunity_rating)).length,
        risingProducts: products.filter(p => p.trend_stage === 'rising').length,
        totalTikTokViews: products.reduce((sum, p) => sum + (p.tiktok_views || 0), 0)
      },
      error: null
    };
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    return { data: null, error: error.message };
  }
};


// Run automation on all products via backend API
export const runAutomationOnAllProducts = async () => {
  try {
    const response = await fetch(`${API_URL}/api/automation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_type: 'full_pipeline' }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to run automation');
    }
    
    const result = await response.json();
    
    // Fetch updated products
    const { data: products } = await getProducts({});
    
    return { 
      data: products, 
      alerts: [],
      summary: {
        processed: result.processed || 0,
        alertsGenerated: result.alerts_generated || 0,
      },
      error: null 
    };
  } catch (error) {
    console.error('Error running automation:', error);
    return { data: null, alerts: [], summary: { processed: 0, alertsGenerated: 0 }, error: error.message };
  }
};

// Bulk import products via backend CSV endpoint
export const bulkImportProducts = async (products) => {
  // For CSV imports, the AdminAutomationPage already handles this via the data ingestion API
  // This function runs local automation for immediate feedback
  const result = batchRunAutomation(products);
  
  return { 
    data: result.products, 
    alerts: result.alerts,
    summary: result.summary,
    error: null 
  };
};

// Get all products (raw access for automation page)
export const getAllProductsRaw = async () => {
  return await getProducts({ limit: 1000 });
};
