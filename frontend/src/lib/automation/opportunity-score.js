/**
 * Opportunity Rating Calculation Module
 * 
 * Calculates opportunity rating based on multiple factors.
 * Returns: 'low', 'medium', 'high', 'very high'
 * 
 * Current algorithm: Rules-based matrix scoring
 * Future: Can integrate market data APIs or ML predictions
 */

// Rating thresholds
const THRESHOLDS = {
  veryHigh: 85,  // Score >= 85 = very high opportunity
  high: 70,      // Score >= 70 = high opportunity
  medium: 50,    // Score >= 50 = medium opportunity
  // Below 50 = low opportunity
};

/**
 * Calculate opportunity rating for a product
 * @param {Object} product - Product data with trend_score, margin, competition, stage
 * @returns {string} 'low' | 'medium' | 'high' | 'very high'
 */
export function calculateOpportunityRating(product) {
  const {
    trend_score = 0,
    supplier_cost = 0,
    estimated_retail_price = 0,
    competition_level = 'medium',
    trend_stage = 'rising',
  } = product;

  const margin = estimated_retail_price - supplier_cost;
  const marginPercent = estimated_retail_price > 0 
    ? (margin / estimated_retail_price) * 100 
    : 0;

  // Calculate opportunity score (0-100)
  let opportunityScore = 0;

  // Factor 1: Trend Score (40% weight)
  opportunityScore += (trend_score / 100) * 40;

  // Factor 2: Margin Quality (25% weight)
  const marginScore = calculateMarginQuality(margin, marginPercent);
  opportunityScore += (marginScore / 100) * 25;

  // Factor 3: Competition Advantage (20% weight)
  const competitionScore = getCompetitionScore(competition_level);
  opportunityScore += (competitionScore / 100) * 20;

  // Factor 4: Trend Stage Timing (15% weight)
  const stageScore = getStageScore(trend_stage);
  opportunityScore += (stageScore / 100) * 15;

  // Apply bonuses/penalties for exceptional combinations
  opportunityScore = applyModifiers(opportunityScore, {
    trend_score,
    competition_level,
    trend_stage,
    marginPercent,
  });

  // Convert score to rating
  return scoreToRating(opportunityScore);
}

/**
 * Calculate margin quality score
 */
function calculateMarginQuality(margin, marginPercent) {
  // Both absolute margin and percentage matter
  let score = 0;
  
  // Absolute margin scoring
  if (margin >= 50) score += 50;
  else if (margin >= 25) score += 40;
  else if (margin >= 15) score += 30;
  else if (margin >= 5) score += 20;
  else score += 10;

  // Margin percentage scoring
  if (marginPercent >= 70) score += 50;
  else if (marginPercent >= 50) score += 40;
  else if (marginPercent >= 30) score += 30;
  else if (marginPercent >= 20) score += 20;
  else score += 10;

  return score;
}

/**
 * Competition level to score
 */
function getCompetitionScore(level) {
  const scores = {
    low: 100,     // Low competition = high opportunity
    medium: 60,
    high: 25,     // High competition = lower opportunity
  };
  return scores[level] || 50;
}

/**
 * Trend stage timing score
 */
function getStageScore(stage) {
  const scores = {
    early: 100,      // Best time to enter
    rising: 85,      // Still good opportunity
    peak: 50,        // Risky, but can still work
    saturated: 15,   // Very difficult
  };
  return scores[stage] || 50;
}

/**
 * Apply bonuses/penalties for specific combinations
 */
function applyModifiers(score, factors) {
  const { trend_score, competition_level, trend_stage, marginPercent } = factors;

  // BONUS: High trend + Low competition + Early stage = golden opportunity
  if (trend_score >= 80 && competition_level === 'low' && trend_stage === 'early') {
    score += 10;
  }

  // BONUS: Rising trend with good margins
  if (trend_stage === 'rising' && marginPercent >= 50) {
    score += 5;
  }

  // PENALTY: Saturated market with high competition
  if (trend_stage === 'saturated' && competition_level === 'high') {
    score -= 10;
  }

  // PENALTY: Peak stage with thin margins
  if (trend_stage === 'peak' && marginPercent < 30) {
    score -= 5;
  }

  return Math.min(100, Math.max(0, score));
}

/**
 * Convert numeric score to rating string
 */
function scoreToRating(score) {
  if (score >= THRESHOLDS.veryHigh) return 'very high';
  if (score >= THRESHOLDS.high) return 'high';
  if (score >= THRESHOLDS.medium) return 'medium';
  return 'low';
}

/**
 * Batch calculate opportunity ratings
 */
export function batchCalculateOpportunityRatings(products) {
  return products.map(product => ({
    ...product,
    opportunity_rating: calculateOpportunityRating(product),
  }));
}

/**
 * Get opportunity breakdown for analysis
 */
export function getOpportunityBreakdown(product) {
  const {
    trend_score = 0,
    supplier_cost = 0,
    estimated_retail_price = 0,
    competition_level = 'medium',
    trend_stage = 'rising',
  } = product;

  const margin = estimated_retail_price - supplier_cost;
  const marginPercent = estimated_retail_price > 0 
    ? (margin / estimated_retail_price) * 100 
    : 0;

  return {
    trendScoreContribution: (trend_score / 100) * 40,
    marginContribution: (calculateMarginQuality(margin, marginPercent) / 100) * 25,
    competitionContribution: (getCompetitionScore(competition_level) / 100) * 20,
    stageContribution: (getStageScore(trend_stage) / 100) * 15,
    finalRating: calculateOpportunityRating(product),
  };
}
