import { supabase, isSupabaseConfigured } from '@/lib/supabase';
import { runFullAutomation, batchRunAutomation } from '@/lib/automation';

// Mock products for demo mode
const MOCK_PRODUCTS = [
  {
    id: '1',
    product_name: 'Portable Neck Fan',
    category: 'Electronics',
    short_description: 'Hands-free personal cooling device with LED display and 3 speed settings',
    supplier_cost: 8.50,
    estimated_retail_price: 29.99,
    estimated_margin: 21.49,
    tiktok_views: 15400000,
    ad_count: 234,
    competition_level: 'medium',
    trend_score: 87,
    trend_stage: 'rising',
    opportunity_rating: 'very high',
    ai_summary: 'Strong summer seasonal product with consistent year-over-year growth. TikTok virality driven by creative usage scenarios. Low barrier to entry but differentiation possible through branding.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: false,
    created_at: new Date().toISOString()
  },
  {
    id: '2',
    product_name: 'Magnetic Phone Mount',
    category: 'Mobile Accessories',
    short_description: 'MagSafe compatible car mount with 360° rotation and strong magnets',
    supplier_cost: 4.20,
    estimated_retail_price: 24.99,
    estimated_margin: 20.79,
    tiktok_views: 8200000,
    ad_count: 156,
    competition_level: 'high',
    trend_score: 72,
    trend_stage: 'peak',
    opportunity_rating: 'medium',
    ai_summary: 'Evergreen product with steady demand. High competition requires strong differentiation through quality and branding. Consider bundling with other car accessories.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: false,
    created_at: new Date().toISOString()
  },
  {
    id: '3',
    product_name: 'Sunset Projection Lamp',
    category: 'Home Decor',
    short_description: 'USB-powered ambient light projector creating viral sunset aesthetics',
    supplier_cost: 6.80,
    estimated_retail_price: 32.99,
    estimated_margin: 26.19,
    tiktok_views: 28900000,
    ad_count: 89,
    competition_level: 'low',
    trend_score: 94,
    trend_stage: 'early',
    opportunity_rating: 'very high',
    ai_summary: 'Exceptional viral potential with low current competition. Perfect for content creators and Gen Z bedroom aesthetics. Act fast before market saturation.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: true,
    created_at: new Date().toISOString()
  },
  {
    id: '4',
    product_name: 'LED Strip Lights RGB',
    category: 'Home Decor',
    short_description: 'App-controlled smart LED strips with music sync and 16M colors',
    supplier_cost: 5.40,
    estimated_retail_price: 19.99,
    estimated_margin: 14.59,
    tiktok_views: 45000000,
    ad_count: 412,
    competition_level: 'high',
    trend_score: 45,
    trend_stage: 'saturated',
    opportunity_rating: 'low',
    ai_summary: 'Market is highly saturated with many established players. Difficult to differentiate without significant brand investment. Consider niche variations like under-cabinet or gaming-specific.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: false,
    created_at: new Date().toISOString()
  },
  {
    id: '5',
    product_name: 'Wireless Earbuds Pro',
    category: 'Audio',
    short_description: 'ANC wireless earbuds with 40hr battery life and premium sound',
    supplier_cost: 12.00,
    estimated_retail_price: 49.99,
    estimated_margin: 37.99,
    tiktok_views: 12300000,
    ad_count: 278,
    competition_level: 'high',
    trend_score: 68,
    trend_stage: 'peak',
    opportunity_rating: 'medium',
    ai_summary: 'Competitive market dominated by major brands. Success requires exceptional quality claims and strong social proof. Consider targeting specific niches like sports or gaming.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: false,
    created_at: new Date().toISOString()
  },
  {
    id: '6',
    product_name: 'Cloud Slippers',
    category: 'Fashion',
    short_description: 'Ultra-soft EVA sole slippers with pressure-relief technology',
    supplier_cost: 3.80,
    estimated_retail_price: 22.99,
    estimated_margin: 19.19,
    tiktok_views: 67000000,
    ad_count: 523,
    competition_level: 'high',
    trend_score: 78,
    trend_stage: 'peak',
    opportunity_rating: 'medium',
    ai_summary: 'Massive TikTok presence but market becoming crowded. Focus on unique colors/patterns or eco-friendly materials for differentiation.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: false,
    created_at: new Date().toISOString()
  },
  {
    id: '7',
    product_name: 'Aesthetic Desk Organizer',
    category: 'Home Office',
    short_description: 'Minimalist acrylic desk organizer with multiple compartments',
    supplier_cost: 7.20,
    estimated_retail_price: 34.99,
    estimated_margin: 27.79,
    tiktok_views: 4500000,
    ad_count: 67,
    competition_level: 'low',
    trend_score: 82,
    trend_stage: 'rising',
    opportunity_rating: 'high',
    ai_summary: 'Growing demand in WFH segment. Clean aesthetic appeals to productivity content creators. Low competition with good margin potential.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: true,
    created_at: new Date().toISOString()
  },
  {
    id: '8',
    product_name: 'Smart Water Bottle',
    category: 'Health & Fitness',
    short_description: 'Temperature display water bottle with hydration reminders',
    supplier_cost: 9.50,
    estimated_retail_price: 39.99,
    estimated_margin: 30.49,
    tiktok_views: 9800000,
    ad_count: 145,
    competition_level: 'medium',
    trend_score: 76,
    trend_stage: 'rising',
    opportunity_rating: 'high',
    ai_summary: 'Health-conscious consumers driving demand. Tech features justify premium pricing. Good for fitness influencer partnerships.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: false,
    created_at: new Date().toISOString()
  },
  {
    id: '9',
    product_name: 'Portable Blender',
    category: 'Kitchen',
    short_description: 'USB-C rechargeable personal blender for smoothies on-the-go',
    supplier_cost: 11.00,
    estimated_retail_price: 44.99,
    estimated_margin: 33.99,
    tiktok_views: 31000000,
    ad_count: 389,
    competition_level: 'high',
    trend_score: 65,
    trend_stage: 'peak',
    opportunity_rating: 'medium',
    ai_summary: 'Established product category with strong demand. Differentiate through power/capacity specs or unique colors. Quality consistency is key.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: false,
    created_at: new Date().toISOString()
  },
  {
    id: '10',
    product_name: 'Mini Projector',
    category: 'Electronics',
    short_description: 'Pocket-sized 1080p projector with WiFi casting and built-in speaker',
    supplier_cost: 45.00,
    estimated_retail_price: 149.99,
    estimated_margin: 104.99,
    tiktok_views: 18700000,
    ad_count: 198,
    competition_level: 'medium',
    trend_score: 85,
    trend_stage: 'rising',
    opportunity_rating: 'very high',
    ai_summary: 'High-ticket item with excellent margins. Growing demand for portable entertainment. Target movie nights and outdoor cinema content creators.',
    supplier_link: 'https://alibaba.com/example',
    is_premium: true,
    created_at: new Date().toISOString()
  }
];

// Get all products
export const getProducts = async (filters = {}) => {
  if (!isSupabaseConfigured()) {
    // Demo mode - return mock data with filtering
    let products = [...MOCK_PRODUCTS];
    
    if (filters.category) {
      products = products.filter(p => p.category === filters.category);
    }
    if (filters.trend_stage) {
      products = products.filter(p => p.trend_stage === filters.trend_stage);
    }
    if (filters.opportunity_rating) {
      products = products.filter(p => p.opportunity_rating === filters.opportunity_rating);
    }
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      products = products.filter(p => 
        p.product_name.toLowerCase().includes(searchLower) ||
        p.category.toLowerCase().includes(searchLower)
      );
    }
    if (filters.sortBy) {
      products.sort((a, b) => {
        const aVal = a[filters.sortBy];
        const bVal = b[filters.sortBy];
        return filters.sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      });
    }
    
    return { data: products, error: null };
  }

  let query = supabase.from('products').select('*');

  if (filters.category) {
    query = query.eq('category', filters.category);
  }
  if (filters.trend_stage) {
    query = query.eq('trend_stage', filters.trend_stage);
  }
  if (filters.opportunity_rating) {
    query = query.eq('opportunity_rating', filters.opportunity_rating);
  }
  if (filters.search) {
    query = query.ilike('product_name', `%${filters.search}%`);
  }
  if (filters.sortBy) {
    query = query.order(filters.sortBy, { ascending: filters.sortOrder === 'asc' });
  } else {
    query = query.order('trend_score', { ascending: false });
  }

  const { data, error } = await query;
  return { data, error };
};

// Get single product by ID
export const getProductById = async (id) => {
  if (!isSupabaseConfigured()) {
    const product = MOCK_PRODUCTS.find(p => p.id === id);
    return { data: product || null, error: product ? null : { message: 'Product not found' } };
  }

  const { data, error } = await supabase
    .from('products')
    .select('*')
    .eq('id', id)
    .single();

  return { data, error };
};

// Get unique categories
export const getCategories = async () => {
  if (!isSupabaseConfigured()) {
    const categories = [...new Set(MOCK_PRODUCTS.map(p => p.category))];
    return { data: categories, error: null };
  }

  const { data, error } = await supabase
    .from('products')
    .select('category')
    .order('category');

  if (data) {
    const categories = [...new Set(data.map(p => p.category))];
    return { data: categories, error: null };
  }

  return { data: [], error };
};

// Create product (admin only) - with automation
export const createProduct = async (productData, runAutomation = true) => {
  let processedData = productData;
  let generatedAlert = null;

  // Run automation pipeline if enabled
  if (runAutomation) {
    const automationResult = runFullAutomation(productData);
    processedData = automationResult.product;
    generatedAlert = automationResult.alert;
  } else {
    // Just calculate margin
    processedData = {
      ...productData,
      estimated_margin: productData.estimated_retail_price - productData.supplier_cost
    };
  }

  if (!isSupabaseConfigured()) {
    const newProduct = {
      ...processedData,
      id: String(Date.now()),
      created_at: new Date().toISOString(),
    };
    MOCK_PRODUCTS.push(newProduct);
    return { data: newProduct, error: null, alert: generatedAlert };
  }

  const { data, error } = await supabase
    .from('products')
    .insert([processedData])
    .select()
    .single();

  return { data, error, alert: generatedAlert };
};

// Update product (admin only) - with automation
export const updateProduct = async (id, productData, runAutomation = true) => {
  let processedData = productData;
  let generatedAlert = null;

  // Run automation pipeline if enabled
  if (runAutomation) {
    const automationResult = runFullAutomation(productData);
    processedData = automationResult.product;
    generatedAlert = automationResult.alert;
  }

  if (!isSupabaseConfigured()) {
    const index = MOCK_PRODUCTS.findIndex(p => p.id === id);
    if (index !== -1) {
      MOCK_PRODUCTS[index] = { ...MOCK_PRODUCTS[index], ...processedData, updated_at: new Date().toISOString() };
      return { data: MOCK_PRODUCTS[index], error: null, alert: generatedAlert };
    }
    return { data: null, error: { message: 'Product not found' }, alert: null };
  }

  const { data, error } = await supabase
    .from('products')
    .update(processedData)
    .eq('id', id)
    .select()
    .single();

  return { data, error, alert: generatedAlert };
};

// Delete product (admin only)
export const deleteProduct = async (id) => {
  if (!isSupabaseConfigured()) {
    const index = MOCK_PRODUCTS.findIndex(p => p.id === id);
    if (index !== -1) {
      MOCK_PRODUCTS.splice(index, 1);
      return { error: null };
    }
    return { error: { message: 'Product not found' } };
  }

  const { error } = await supabase
    .from('products')
    .delete()
    .eq('id', id);

  return { error };
};

// Get dashboard stats
export const getDashboardStats = async () => {
  if (!isSupabaseConfigured()) {
    const products = MOCK_PRODUCTS;
    return {
      data: {
        totalProducts: products.length,
        avgTrendScore: Math.round(products.reduce((sum, p) => sum + p.trend_score, 0) / products.length),
        highOpportunityCount: products.filter(p => ['high', 'very high'].includes(p.opportunity_rating)).length,
        risingProducts: products.filter(p => p.trend_stage === 'rising').length,
        totalTikTokViews: products.reduce((sum, p) => sum + p.tiktok_views, 0)
      },
      error: null
    };
  }

  const { data: products, error } = await supabase.from('products').select('*');
  
  if (error) return { data: null, error };

  return {
    data: {
      totalProducts: products.length,
      avgTrendScore: Math.round(products.reduce((sum, p) => sum + p.trend_score, 0) / products.length),
      highOpportunityCount: products.filter(p => ['high', 'very high'].includes(p.opportunity_rating)).length,
      risingProducts: products.filter(p => p.trend_stage === 'rising').length,
      totalTikTokViews: products.reduce((sum, p) => sum + p.tiktok_views, 0)
    },
    error: null
  };
};


// Run automation on all products (recalculate scores)
export const runAutomationOnAllProducts = async () => {
  if (!isSupabaseConfigured()) {
    const result = batchRunAutomation(MOCK_PRODUCTS);
    
    // Update mock products with new calculated values
    result.products.forEach((updatedProduct, index) => {
      if (MOCK_PRODUCTS[index]) {
        Object.assign(MOCK_PRODUCTS[index], updatedProduct);
      }
    });

    return { 
      data: result.products, 
      alerts: result.alerts,
      summary: result.summary,
      error: null 
    };
  }

  // Get all products
  const { data: products, error: fetchError } = await supabase
    .from('products')
    .select('*');

  if (fetchError) return { data: null, error: fetchError };

  // Run automation
  const result = batchRunAutomation(products);

  // Update products in database (batch update)
  for (const product of result.products) {
    await supabase
      .from('products')
      .update({
        trend_score: product.trend_score,
        trend_stage: product.trend_stage,
        opportunity_rating: product.opportunity_rating,
        ai_summary: product.ai_summary,
        estimated_margin: product.estimated_margin,
        updated_at: product.updated_at,
      })
      .eq('id', product.id);
  }

  return { 
    data: result.products, 
    alerts: result.alerts,
    summary: result.summary,
    error: null 
  };
};

// Bulk import products from CSV
export const bulkImportProducts = async (products) => {
  const result = batchRunAutomation(products);

  if (!isSupabaseConfigured()) {
    // Add to mock products with IDs
    result.products.forEach(product => {
      const newProduct = {
        ...product,
        id: String(Date.now() + Math.random()),
        created_at: new Date().toISOString(),
      };
      MOCK_PRODUCTS.push(newProduct);
    });

    return { 
      data: result.products, 
      alerts: result.alerts,
      summary: result.summary,
      error: null 
    };
  }

  // Insert all products
  const { data, error } = await supabase
    .from('products')
    .insert(result.products)
    .select();

  return { 
    data, 
    alerts: result.alerts,
    summary: result.summary,
    error 
  };
};

// Get all products (raw access for automation page)
export const getAllProductsRaw = async () => {
  if (!isSupabaseConfigured()) {
    return { data: [...MOCK_PRODUCTS], error: null };
  }

  const { data, error } = await supabase
    .from('products')
    .select('*')
    .order('created_at', { ascending: false });

  return { data, error };
};
