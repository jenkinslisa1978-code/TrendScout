import { runFullAutomation, batchRunAutomation } from '@/lib/automation';
import { API_URL } from '@/lib/config';
import { getAuthHeaders, apiPost, apiDelete as apiDeleteFn } from '@/lib/api';

// Get all products from backend API
export const getProducts = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    if (filters.category) params.append('category', filters.category);
    if (filters.trend_stage) params.append('trend_stage', filters.trend_stage);
    if (filters.opportunity_rating) params.append('opportunity_rating', filters.opportunity_rating);
    if (filters.early_trend_label) params.append('early_trend_label', filters.early_trend_label);
    if (filters.market_label) params.append('market_label', filters.market_label);
    if (filters.competition_level) params.append('competition_level', filters.competition_level);
    if (filters.min_trend_score != null) params.append('min_trend_score', filters.min_trend_score);
    if (filters.max_trend_score != null) params.append('max_trend_score', filters.max_trend_score);
    if (filters.min_price != null) params.append('min_price', filters.min_price);
    if (filters.max_price != null) params.append('max_price', filters.max_price);
    if (filters.search) params.append('search', filters.search);
    if (filters.sortBy) params.append('sort_by', filters.sortBy);
    if (filters.sortOrder) params.append('sort_order', filters.sortOrder);
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.includeIntegrity) params.append('include_integrity', 'true');
    
    const queryString = params.toString();
    const url = `${API_URL}/api/products${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch products');
    }
    
    const result = await response.json();
    return { 
      data: result.data || [], 
      metadata: result.metadata || null,
      error: null 
    };
  } catch (error) {
    console.error('Error fetching products:', error);
    return { data: [], metadata: null, error: error.message };
  }
};

// Get single product by ID from backend API
export const getProductById = async (id, includeIntegrity = false) => {
  try {
    const url = `${API_URL}/api/products/${id}${includeIntegrity ? '?include_integrity=true' : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      if (response.status === 404) {
        return { data: null, error: { message: 'Product not found' } };
      }
      throw new Error('Failed to fetch product');
    }
    
    const result = await response.json();
    return { 
      data: result.data, 
      dataIntegrity: result.data_integrity || null,
      warnings: result.warnings || [],
      displayHints: result.display_hints || {},
      error: null 
    };
  } catch (error) {
    console.error('Error fetching product:', error);
    return { data: null, dataIntegrity: null, warnings: [], displayHints: {}, error: error.message };
  }
};

// Get product data integrity info
export const getProductDataIntegrity = async (productId) => {
  try {
    const response = await fetch(`${API_URL}/api/data-integrity/product/${productId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch data integrity');
    }
    
    const result = await response.json();
    return { data: result, error: null };
  } catch (error) {
    console.error('Error fetching data integrity:', error);
    return { data: null, error: error.message };
  }
};

// Get platform data health
export const getPlatformHealth = async () => {
  try {
    const response = await fetch(`${API_URL}/api/data-integrity/platform-health`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch platform health');
    }
    
    const result = await response.json();
    return { data: result, error: null };
  } catch (error) {
    console.error('Error fetching platform health:', error);
    return { data: null, error: error.message };
  }
};

// Get source health status
export const getSourceHealth = async () => {
  try {
    const response = await fetch(`${API_URL}/api/data-integrity/source-health`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch source health');
    }
    
    const result = await response.json();
    return { data: result, error: null };
  } catch (error) {
    console.error('Error fetching source health:', error);
    return { data: null, error: error.message };
  }
};

// Get simulated data report
export const getSimulatedDataReport = async () => {
  try {
    const response = await fetch(`${API_URL}/api/data-integrity/simulated-data-report`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch simulated data report');
    }
    
    const result = await response.json();
    return { data: result, error: null };
  } catch (error) {
    console.error('Error fetching simulated data report:', error);
    return { data: null, error: error.message };
  }
};

// Get proven winning products
export const getProvenWinners = async (limit = 10) => {
  try {
    const response = await fetch(`${API_URL}/api/products/proven-winners/list?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch proven winners');
    }
    
    const result = await response.json();
    return { data: result.data || [], stats: result.stats || {}, error: null };
  } catch (error) {
    console.error('Error fetching proven winners:', error);
    return { data: [], stats: {}, error: error.message };
  }
};

// Get market opportunities
export const getMarketOpportunities = async (limit = 10) => {
  try {
    const response = await fetch(`${API_URL}/api/products/market-opportunities/list?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch market opportunities');
    }
    
    const result = await response.json();
    return { data: result.data || [], stats: result.stats || {}, error: null };
  } catch (error) {
    console.error('Error fetching market opportunities:', error);
    return { data: [], stats: {}, error: error.message };
  }
};

// Get competitor data for a product
export const getProductCompetitors = async (productId) => {
  try {
    const response = await fetch(`${API_URL}/api/products/${productId}/competitors`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch competitor data');
    }
    
    const result = await response.json();
    return { data: result, error: null };
  } catch (error) {
    console.error('Error fetching competitors:', error);
    return { data: null, error: error.message };
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
    const response = await apiPost('/api/products', productData);
    const result = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(result.detail || 'Failed to create product');
    }
    
    return { data: result.data, error: null, alert: result.alert };
  } catch (error) {
    console.error('Error creating product:', error);
    return { data: null, error: { message: error.message }, alert: null };
  }
};

// Update product via backend API - with automation
export const updateProduct = async (id, productData, runAutomation = true) => {
  try {
    const response = await apiPost(`/api/products/${id}`, productData);
    const result = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(result.detail || 'Failed to update product');
    }
    
    return { data: result.data, error: null, alert: result.alert };
  } catch (error) {
    console.error('Error updating product:', error);
    return { data: null, error: { message: error.message }, alert: null };
  }
};

// Delete product via backend API
export const deleteProduct = async (id) => {
  try {
    const response = await apiDeleteFn(`/api/products/${id}`);
    
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
    const response = await apiPost('/api/automation/run', { job_type: 'full_pipeline' });
    const result = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(result.detail || 'Failed to run automation');
    }
    
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
