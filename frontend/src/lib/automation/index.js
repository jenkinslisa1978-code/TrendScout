/**
 * TrendScout Automation Module
 * 
 * Central export for all automation functionality.
 * Import from this file for clean access to all automation features.
 */

// Trend Score Calculation
export {
  calculateTrendScore,
  batchCalculateTrendScores,
  getTrendScoreBreakdown,
} from './trend-score';

// Opportunity Rating Calculation
export {
  calculateOpportunityRating,
  batchCalculateOpportunityRatings,
  getOpportunityBreakdown,
} from './opportunity-score';

// Trend Stage Classification
export {
  calculateTrendStage,
  batchCalculateTrendStages,
  getTrendStageAnalysis,
} from './trend-stage';

// AI Summary Generation
export {
  generateAISummary,
  batchGenerateAISummaries,
  generateAISummaryWithAPI,
} from './ai-summary';

// Alert Generation
export {
  shouldGenerateAlert,
  generateAlert,
  batchGenerateAlerts,
  filterAlertsByPriority,
  getUnreadAlertsCount,
  markAlertAsRead,
  dismissAlert,
  getAlertStats,
} from './alerts';

// Product Import Pipeline
export {
  parseCSV,
  processImportedProducts,
  validateProduct,
  generateImportReport,
  ImportSources,
  importFromSource,
} from './product-import';

/**
 * Run full automation pipeline on a product
 * Calculates all scores and generates summary
 */
export function runFullAutomation(product) {
  const { calculateTrendStage } = require('./trend-stage');
  const { calculateTrendScore } = require('./trend-score');
  const { calculateOpportunityRating } = require('./opportunity-score');
  const { generateAISummary } = require('./ai-summary');
  const { generateAlert } = require('./alerts');

  // Step 1: Calculate trend stage
  const trend_stage = calculateTrendStage(product);
  const step1 = { ...product, trend_stage };

  // Step 2: Calculate trend score
  const trend_score = calculateTrendScore(step1);
  const step2 = { ...step1, trend_score };

  // Step 3: Calculate opportunity rating
  const opportunity_rating = calculateOpportunityRating(step2);
  const step3 = { ...step2, opportunity_rating };

  // Step 4: Generate AI summary
  const ai_summary = generateAISummary(step3);
  const step4 = { ...step3, ai_summary };

  // Step 5: Generate alert if qualifying
  const alert = generateAlert(step4);

  // Calculate margin
  const estimated_margin = (product.estimated_retail_price || 0) - (product.supplier_cost || 0);

  return {
    product: {
      ...step4,
      estimated_margin,
      updated_at: new Date().toISOString(),
    },
    alert,
    automation_log: {
      timestamp: new Date().toISOString(),
      steps_completed: ['trend_stage', 'trend_score', 'opportunity_rating', 'ai_summary', 'alert_check'],
      alert_generated: !!alert,
    }
  };
}

/**
 * Batch run automation on multiple products
 */
export function batchRunAutomation(products) {
  const results = products.map(runFullAutomation);
  
  return {
    products: results.map(r => r.product),
    alerts: results.filter(r => r.alert).map(r => r.alert),
    summary: {
      processed: products.length,
      alertsGenerated: results.filter(r => r.alert).length,
      timestamp: new Date().toISOString(),
    }
  };
}
