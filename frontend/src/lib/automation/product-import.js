/**
 * Product Import Pipeline Module
 * 
 * Handles product data ingestion from multiple sources.
 * 
 * Current sources:
 * - Manual entry
 * - CSV upload
 * - API placeholder (future)
 * 
 * Future sources: TikTok API, Amazon API, AliExpress API, Web scraping
 */

import { calculateTrendScore } from './trend-score';
import { calculateOpportunityRating } from './opportunity-score';
import { calculateTrendStage } from './trend-stage';
import { generateAISummary } from './ai-summary';
import { generateAlert } from './alerts';

// CSV column mapping
const CSV_COLUMN_MAP = {
  'product_name': ['product_name', 'name', 'title', 'product', 'product title'],
  'category': ['category', 'cat', 'product_category', 'type'],
  'short_description': ['short_description', 'description', 'desc', 'summary'],
  'supplier_cost': ['supplier_cost', 'cost', 'buy_price', 'wholesale_price', 'supplier_price'],
  'estimated_retail_price': ['estimated_retail_price', 'retail_price', 'sell_price', 'price', 'retail'],
  'tiktok_views': ['tiktok_views', 'views', 'tiktok', 'social_views'],
  'ad_count': ['ad_count', 'ads', 'ad_count', 'active_ads', 'competitor_ads'],
  'competition_level': ['competition_level', 'competition', 'comp_level'],
  'supplier_link': ['supplier_link', 'supplier_url', 'source_url', 'alibaba_link'],
  'is_premium': ['is_premium', 'premium', 'pro_only'],
};

// Valid competition levels
const VALID_COMPETITION_LEVELS = ['low', 'medium', 'high'];

/**
 * Parse CSV string to array of products
 * @param {string} csvString - Raw CSV content
 * @returns {Object} { products: [], errors: [], warnings: [] }
 */
export function parseCSV(csvString) {
  const results = {
    products: [],
    errors: [],
    warnings: [],
  };

  try {
    const lines = csvString.trim().split('\n');
    if (lines.length < 2) {
      results.errors.push('CSV must have at least a header row and one data row');
      return results;
    }

    // Parse header
    const headers = parseCSVLine(lines[0]).map(h => h.toLowerCase().trim());
    const columnMapping = mapColumns(headers);

    if (!columnMapping.product_name) {
      results.errors.push('CSV must have a product_name column');
      return results;
    }

    // Parse data rows
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      try {
        const values = parseCSVLine(line);
        const product = parseProductRow(values, headers, columnMapping, i);
        
        if (product.errors.length > 0) {
          results.warnings.push(...product.errors.map(e => `Row ${i + 1}: ${e}`));
        }
        
        if (product.data) {
          results.products.push(product.data);
        }
      } catch (err) {
        results.errors.push(`Row ${i + 1}: Failed to parse - ${err.message}`);
      }
    }

    results.warnings.push(`Parsed ${results.products.length} products from ${lines.length - 1} rows`);
  } catch (err) {
    results.errors.push(`CSV parsing failed: ${err.message}`);
  }

  return results;
}

/**
 * Parse a single CSV line, handling quoted values
 */
function parseCSVLine(line) {
  const values = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      values.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  values.push(current.trim());

  return values;
}

/**
 * Map CSV columns to our schema
 */
function mapColumns(headers) {
  const mapping = {};

  for (const [field, aliases] of Object.entries(CSV_COLUMN_MAP)) {
    const index = headers.findIndex(h => aliases.includes(h));
    if (index !== -1) {
      mapping[field] = index;
    }
  }

  return mapping;
}

/**
 * Parse a single product row
 */
function parseProductRow(values, headers, columnMapping, rowIndex) {
  const errors = [];
  
  const getString = (field) => {
    const idx = columnMapping[field];
    return idx !== undefined ? values[idx]?.trim() || '' : '';
  };

  const getNumber = (field, defaultVal = 0) => {
    const idx = columnMapping[field];
    if (idx === undefined) return defaultVal;
    const val = parseFloat(values[idx]?.replace(/[£$,]/g, ''));
    return isNaN(val) ? defaultVal : val;
  };

  const getBoolean = (field) => {
    const idx = columnMapping[field];
    if (idx === undefined) return false;
    const val = values[idx]?.toLowerCase().trim();
    return ['true', 'yes', '1', 'y'].includes(val);
  };

  // Required field
  const productName = getString('product_name');
  if (!productName) {
    errors.push('Missing product name');
    return { data: null, errors };
  }

  // Build product object
  let competitionLevel = getString('competition_level').toLowerCase();
  if (!VALID_COMPETITION_LEVELS.includes(competitionLevel)) {
    competitionLevel = 'medium';
    if (getString('competition_level')) {
      errors.push(`Invalid competition level "${getString('competition_level')}", defaulting to "medium"`);
    }
  }

  const product = {
    product_name: productName,
    category: getString('category') || 'General',
    short_description: getString('short_description'),
    supplier_cost: getNumber('supplier_cost'),
    estimated_retail_price: getNumber('estimated_retail_price'),
    tiktok_views: Math.floor(getNumber('tiktok_views')),
    ad_count: Math.floor(getNumber('ad_count')),
    competition_level: competitionLevel,
    supplier_link: getString('supplier_link'),
    is_premium: getBoolean('is_premium'),
  };

  // Validate prices
  if (product.estimated_retail_price <= product.supplier_cost) {
    errors.push('Retail price should be higher than supplier cost');
  }

  return { data: product, errors };
}

/**
 * Process imported products - add calculated fields
 * @param {Array} products - Raw imported products
 * @returns {Array} Products with all calculated fields
 */
export function processImportedProducts(products) {
  return products.map(product => {
    // Calculate trend stage first (other calcs may depend on it)
    const trend_stage = calculateTrendStage(product);
    const productWithStage = { ...product, trend_stage };

    // Calculate trend score
    const trend_score = calculateTrendScore(productWithStage);
    const productWithScore = { ...productWithStage, trend_score };

    // Calculate opportunity rating
    const opportunity_rating = calculateOpportunityRating(productWithScore);
    const productWithOpportunity = { ...productWithScore, opportunity_rating };

    // Generate AI summary
    const ai_summary = generateAISummary(productWithOpportunity);

    // Calculate margin
    const estimated_margin = product.estimated_retail_price - product.supplier_cost;

    return {
      ...productWithOpportunity,
      ai_summary,
      estimated_margin,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  });
}

/**
 * Validate a single product for import
 */
export function validateProduct(product) {
  const errors = [];
  const warnings = [];

  // Required fields
  if (!product.product_name?.trim()) {
    errors.push('Product name is required');
  }

  if (!product.category?.trim()) {
    warnings.push('Category not specified, will default to "General"');
  }

  // Price validation
  if (product.supplier_cost < 0) {
    errors.push('Supplier cost cannot be negative');
  }

  if (product.estimated_retail_price < 0) {
    errors.push('Retail price cannot be negative');
  }

  if (product.estimated_retail_price <= product.supplier_cost) {
    warnings.push('Retail price is not higher than supplier cost - no profit margin');
  }

  // Views/ads validation
  if (product.tiktok_views < 0) {
    errors.push('TikTok views cannot be negative');
  }

  if (product.ad_count < 0) {
    errors.push('Ad count cannot be negative');
  }

  // Competition level
  if (product.competition_level && 
      !VALID_COMPETITION_LEVELS.includes(product.competition_level)) {
    warnings.push(`Invalid competition level "${product.competition_level}", will default to "medium"`);
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Generate import report
 */
export function generateImportReport(originalCount, processedProducts, errors, warnings) {
  return {
    timestamp: new Date().toISOString(),
    summary: {
      totalRows: originalCount,
      successfullyImported: processedProducts.length,
      failed: originalCount - processedProducts.length,
      errors: errors.length,
      warnings: warnings.length,
    },
    products: processedProducts.map(p => ({
      name: p.product_name,
      category: p.category,
      trend_score: p.trend_score,
      opportunity_rating: p.opportunity_rating,
      trend_stage: p.trend_stage,
    })),
    errors,
    warnings,
  };
}

/**
 * PLACEHOLDER: Future API import sources
 */
export const ImportSources = {
  MANUAL: 'manual',
  CSV: 'csv',
  TIKTOK_API: 'tiktok_api',      // Future
  AMAZON_API: 'amazon_api',      // Future
  ALIEXPRESS_API: 'aliexpress_api', // Future
  WEB_SCRAPE: 'web_scrape',      // Future
};

/**
 * PLACEHOLDER: Future automated import function
 */
export async function importFromSource(source, config = {}) {
  switch (source) {
    case ImportSources.MANUAL:
    case ImportSources.CSV:
      // Handled by parseCSV and processImportedProducts
      return { success: true, message: 'Use parseCSV for manual/CSV imports' };
    
    case ImportSources.TIKTOK_API:
      // TODO: Implement TikTok Creative Center API integration
      return { success: false, message: 'TikTok API integration not yet implemented' };
    
    case ImportSources.AMAZON_API:
      // TODO: Implement Amazon Product API integration
      return { success: false, message: 'Amazon API integration not yet implemented' };
    
    case ImportSources.ALIEXPRESS_API:
      // TODO: Implement AliExpress API integration
      return { success: false, message: 'AliExpress API integration not yet implemented' };
    
    case ImportSources.WEB_SCRAPE:
      // TODO: Implement web scraping service
      return { success: false, message: 'Web scraping not yet implemented' };
    
    default:
      return { success: false, message: `Unknown import source: ${source}` };
  }
}
