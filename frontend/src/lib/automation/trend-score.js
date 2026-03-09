/**
 * Trend Score Calculation Module
 * 
 * Calculates a trend score (0-100) based on product signals.
 * Structure ready for future AI/API-driven scoring.
 * 
 * Current algorithm: Rules-based weighted scoring
 * Future: Can be replaced with ML model or external API
 */

// Scoring weights (adjust these to tune the algorithm)
const WEIGHTS = {
  tiktokViews: 0.35,      // TikTok viral potential
  adCount: 0.20,          // Market activity indicator
  competitionLevel: 0.20, // Inverse - low competition = higher score
  margin: 0.25,           // Profit potential
};

// Thresholds for normalization
const THRESHOLDS = {
  tiktokViews: {
    excellent: 50000000,  // 50M+ views
    good: 10000000,       // 10M+ views
    moderate: 1000000,    // 1M+ views
    low: 100000,          // 100K+ views
  },
  adCount: {
    high: 500,            // Many competitors
    moderate: 200,
    low: 50,
  },
  margin: {
    excellent: 50,        // £50+ margin
    good: 25,             // £25+ margin
    moderate: 10,         // £10+ margin
  }
};

/**
 * Calculate trend score for a product
 * @param {Object} product - Product data
 * @returns {number} Trend score 0-100
 */
export function calculateTrendScore(product) {
  const {
    tiktok_views = 0,
    ad_count = 0,
    competition_level = 'medium',
    supplier_cost = 0,
    estimated_retail_price = 0,
  } = product;

  const margin = estimated_retail_price - supplier_cost;

  // Calculate individual component scores (0-100)
  const tiktokScore = calculateTikTokScore(tiktok_views);
  const adScore = calculateAdScore(ad_count);
  const competitionScore = calculateCompetitionScore(competition_level);
  const marginScore = calculateMarginScore(margin);

  // Weighted average
  const weightedScore = 
    (tiktokScore * WEIGHTS.tiktokViews) +
    (adScore * WEIGHTS.adCount) +
    (competitionScore * WEIGHTS.competitionLevel) +
    (marginScore * WEIGHTS.margin);

  // Round to nearest integer, ensure 0-100 range
  return Math.min(100, Math.max(0, Math.round(weightedScore)));
}

/**
 * TikTok views scoring
 */
function calculateTikTokScore(views) {
  if (views >= THRESHOLDS.tiktokViews.excellent) return 100;
  if (views >= THRESHOLDS.tiktokViews.good) return 80;
  if (views >= THRESHOLDS.tiktokViews.moderate) return 60;
  if (views >= THRESHOLDS.tiktokViews.low) return 40;
  return Math.min(40, (views / THRESHOLDS.tiktokViews.low) * 40);
}

/**
 * Ad count scoring - moderate activity is best
 * Too few = no market validation, too many = saturated
 */
function calculateAdScore(adCount) {
  if (adCount === 0) return 30; // No market validation
  if (adCount < THRESHOLDS.adCount.low) return 60; // Early market
  if (adCount < THRESHOLDS.adCount.moderate) return 100; // Sweet spot
  if (adCount < THRESHOLDS.adCount.high) return 70; // Getting competitive
  return 40; // Saturated
}

/**
 * Competition level scoring (inverse)
 */
function calculateCompetitionScore(level) {
  const scores = {
    low: 100,
    medium: 60,
    high: 30,
  };
  return scores[level] || 50;
}

/**
 * Margin scoring
 */
function calculateMarginScore(margin) {
  if (margin >= THRESHOLDS.margin.excellent) return 100;
  if (margin >= THRESHOLDS.margin.good) return 80;
  if (margin >= THRESHOLDS.margin.moderate) return 60;
  if (margin > 0) return 40;
  return 0;
}

/**
 * Batch calculate trend scores for multiple products
 * @param {Array} products - Array of product objects
 * @returns {Array} Products with updated trend_score
 */
export function batchCalculateTrendScores(products) {
  return products.map(product => ({
    ...product,
    trend_score: calculateTrendScore(product),
  }));
}

/**
 * Get score breakdown for analysis/debugging
 */
export function getTrendScoreBreakdown(product) {
  const {
    tiktok_views = 0,
    ad_count = 0,
    competition_level = 'medium',
    supplier_cost = 0,
    estimated_retail_price = 0,
  } = product;

  const margin = estimated_retail_price - supplier_cost;

  return {
    tiktokScore: calculateTikTokScore(tiktok_views),
    adScore: calculateAdScore(ad_count),
    competitionScore: calculateCompetitionScore(competition_level),
    marginScore: calculateMarginScore(margin),
    weights: WEIGHTS,
    finalScore: calculateTrendScore(product),
  };
}
