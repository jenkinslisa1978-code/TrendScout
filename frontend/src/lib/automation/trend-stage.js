/**
 * Trend Stage Classification Module
 * 
 * Automatically assigns trend stage based on product signals.
 * Returns: 'early', 'rising', 'peak', 'saturated'
 * 
 * Current algorithm: Signal-based rules
 * Future: Can integrate time-series analysis, social listening APIs
 */

// Stage classification thresholds
const THRESHOLDS = {
  tiktokViews: {
    viral: 30000000,      // 30M+ = peak/saturated
    trending: 5000000,    // 5M+ = rising/peak
    growing: 500000,      // 500K+ = early/rising
    emerging: 50000,      // 50K+ = early
  },
  adCount: {
    saturated: 400,       // 400+ ads = saturated
    peak: 200,            // 200+ ads = peak
    rising: 50,           // 50+ ads = rising
    early: 10,            // <50 ads = early
  },
  competition: {
    high: 'saturated',    // High competition indicates saturation
    medium: 'peak',       // Medium could be peak or rising
    low: 'early',         // Low competition is early stage
  }
};

/**
 * Calculate trend stage for a product
 * @param {Object} product - Product data
 * @returns {string} 'early' | 'rising' | 'peak' | 'saturated'
 */
export function calculateTrendStage(product) {
  const {
    tiktok_views = 0,
    ad_count = 0,
    competition_level = 'medium',
  } = product;

  // Calculate individual signals
  const viewsSignal = getViewsStageSignal(tiktok_views);
  const adSignal = getAdCountStageSignal(ad_count);
  const competitionSignal = getCompetitionStageSignal(competition_level);

  // Weighted decision matrix
  const signals = {
    early: 0,
    rising: 0,
    peak: 0,
    saturated: 0,
  };

  // Views contribute to stage (weight: 40%)
  signals[viewsSignal] += 40;

  // Ad count contributes (weight: 35%)
  signals[adSignal] += 35;

  // Competition level contributes (weight: 25%)
  signals[competitionSignal] += 25;

  // Find dominant stage
  const stage = Object.entries(signals)
    .sort((a, b) => b[1] - a[1])[0][0];

  // Apply stage transitions logic
  return applyTransitionRules(stage, { tiktok_views, ad_count, competition_level });
}

/**
 * Get stage signal from TikTok views
 */
function getViewsStageSignal(views) {
  if (views >= THRESHOLDS.tiktokViews.viral) return 'peak';
  if (views >= THRESHOLDS.tiktokViews.trending) return 'rising';
  if (views >= THRESHOLDS.tiktokViews.growing) return 'rising';
  if (views >= THRESHOLDS.tiktokViews.emerging) return 'early';
  return 'early';
}

/**
 * Get stage signal from ad count
 */
function getAdCountStageSignal(adCount) {
  if (adCount >= THRESHOLDS.adCount.saturated) return 'saturated';
  if (adCount >= THRESHOLDS.adCount.peak) return 'peak';
  if (adCount >= THRESHOLDS.adCount.rising) return 'rising';
  return 'early';
}

/**
 * Get stage signal from competition level
 */
function getCompetitionStageSignal(level) {
  if (level === 'high') return 'saturated';
  if (level === 'medium') return 'rising';
  return 'early';
}

/**
 * Apply transition rules to handle edge cases
 */
function applyTransitionRules(stage, factors) {
  const { tiktok_views, ad_count, competition_level } = factors;

  // Rule: Very high views but few ads = early viral (rising)
  if (tiktok_views >= THRESHOLDS.tiktokViews.trending && 
      ad_count < THRESHOLDS.adCount.rising) {
    return 'rising';
  }

  // Rule: Many ads but low views = artificially pushed (saturated risk)
  if (ad_count >= THRESHOLDS.adCount.peak && 
      tiktok_views < THRESHOLDS.tiktokViews.growing) {
    return 'peak';
  }

  // Rule: High competition always caps at peak or saturated
  if (competition_level === 'high' && (stage === 'early' || stage === 'rising')) {
    return 'peak';
  }

  // Rule: Low competition with high views = rising opportunity
  if (competition_level === 'low' && 
      tiktok_views >= THRESHOLDS.tiktokViews.trending &&
      stage === 'peak') {
    return 'rising';
  }

  return stage;
}

/**
 * Batch calculate trend stages
 */
export function batchCalculateTrendStages(products) {
  return products.map(product => ({
    ...product,
    trend_stage: calculateTrendStage(product),
  }));
}

/**
 * Get stage analysis breakdown
 */
export function getTrendStageAnalysis(product) {
  const {
    tiktok_views = 0,
    ad_count = 0,
    competition_level = 'medium',
  } = product;

  return {
    viewsSignal: getViewsStageSignal(tiktok_views),
    adSignal: getAdCountStageSignal(ad_count),
    competitionSignal: getCompetitionStageSignal(competition_level),
    finalStage: calculateTrendStage(product),
    insights: generateStageInsights(product),
  };
}

/**
 * Generate human-readable insights about the stage
 */
function generateStageInsights(product) {
  const stage = calculateTrendStage(product);
  const { tiktok_views, ad_count, competition_level } = product;

  const insights = [];

  switch (stage) {
    case 'early':
      insights.push('Product is in early discovery phase');
      if (tiktok_views > 0) insights.push('Growing organic interest detected');
      if (ad_count < 50) insights.push('Low advertiser competition - good entry point');
      break;
    case 'rising':
      insights.push('Product momentum is building');
      insights.push('Increasing market validation');
      if (competition_level === 'low') insights.push('Window of opportunity before saturation');
      break;
    case 'peak':
      insights.push('Product at maximum visibility');
      insights.push('Competition intensifying');
      insights.push('Consider differentiation strategy');
      break;
    case 'saturated':
      insights.push('Market is highly competitive');
      insights.push('Profit margins likely compressed');
      insights.push('Requires strong brand or niche positioning');
      break;
  }

  return insights;
}
