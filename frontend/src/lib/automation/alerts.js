/**
 * Trend Alerts Generation Module
 * 
 * Automatically generates alerts for high-opportunity products.
 * 
 * Current: Local alert generation
 * Future: Supabase integration, push notifications, email alerts
 */

// Alert thresholds
const ALERT_CONFIG = {
  trendScoreThreshold: 75,           // Minimum trend score for alert
  opportunityRatings: ['high', 'very high'], // Qualifying opportunity ratings
  alertTypes: {
    NEW_OPPORTUNITY: 'new_opportunity',
    RISING_TREND: 'rising_trend',
    EARLY_STAGE: 'early_stage',
    HIGH_MARGIN: 'high_margin',
  },
  priorities: {
    CRITICAL: 'critical',    // Score 90+, very high opportunity
    HIGH: 'high',            // Score 80+, high/very high opportunity
    MEDIUM: 'medium',        // Score 75+, high opportunity
  }
};

/**
 * Check if a product qualifies for a trend alert
 * @param {Object} product - Product data
 * @returns {boolean}
 */
export function shouldGenerateAlert(product) {
  const { trend_score = 0, opportunity_rating = 'low' } = product;

  return (
    trend_score >= ALERT_CONFIG.trendScoreThreshold &&
    ALERT_CONFIG.opportunityRatings.includes(opportunity_rating)
  );
}

/**
 * Generate alert for a qualifying product
 * @param {Object} product - Product data
 * @returns {Object|null} Alert object or null if not qualifying
 */
export function generateAlert(product) {
  if (!shouldGenerateAlert(product)) {
    return null;
  }

  const alertType = determineAlertType(product);
  const priority = determineAlertPriority(product);
  const title = generateAlertTitle(product, alertType);
  const body = generateAlertBody(product, alertType);

  return {
    id: `alert-${product.id}-${Date.now()}`,
    product_id: product.id,
    product_name: product.product_name,
    alert_type: alertType,
    priority,
    title,
    body,
    trend_score: product.trend_score,
    opportunity_rating: product.opportunity_rating,
    created_at: new Date().toISOString(),
    read: false,
    dismissed: false,
  };
}

/**
 * Determine the type of alert based on product characteristics
 */
function determineAlertType(product) {
  const { trend_stage, trend_score, opportunity_rating } = product;

  if (trend_stage === 'early' && trend_score >= 80) {
    return ALERT_CONFIG.alertTypes.EARLY_STAGE;
  }
  
  if (trend_stage === 'rising') {
    return ALERT_CONFIG.alertTypes.RISING_TREND;
  }

  const margin = (product.estimated_retail_price || 0) - (product.supplier_cost || 0);
  if (margin >= 40) {
    return ALERT_CONFIG.alertTypes.HIGH_MARGIN;
  }

  return ALERT_CONFIG.alertTypes.NEW_OPPORTUNITY;
}

/**
 * Determine alert priority
 */
function determineAlertPriority(product) {
  const { trend_score, opportunity_rating } = product;

  if (trend_score >= 90 && opportunity_rating === 'very high') {
    return ALERT_CONFIG.priorities.CRITICAL;
  }
  
  if (trend_score >= 80 && ['high', 'very high'].includes(opportunity_rating)) {
    return ALERT_CONFIG.priorities.HIGH;
  }

  return ALERT_CONFIG.priorities.MEDIUM;
}

/**
 * Generate alert title
 */
function generateAlertTitle(product, alertType) {
  const titles = {
    [ALERT_CONFIG.alertTypes.EARLY_STAGE]: `Early Stage Winner: ${product.product_name}`,
    [ALERT_CONFIG.alertTypes.RISING_TREND]: `Rising Trend Alert: ${product.product_name}`,
    [ALERT_CONFIG.alertTypes.HIGH_MARGIN]: `High Margin Opportunity: ${product.product_name}`,
    [ALERT_CONFIG.alertTypes.NEW_OPPORTUNITY]: `New Opportunity: ${product.product_name}`,
  };
  return titles[alertType] || `Alert: ${product.product_name}`;
}

/**
 * Generate alert body
 */
function generateAlertBody(product, alertType) {
  const { trend_score, opportunity_rating, category, trend_stage } = product;
  const margin = (product.estimated_retail_price || 0) - (product.supplier_cost || 0);

  const bodies = {
    [ALERT_CONFIG.alertTypes.EARLY_STAGE]: 
      `Detected early-stage product with ${trend_score} trend score. Low competition with ${opportunity_rating} opportunity rating. First-mover advantage available in ${category}.`,
    
    [ALERT_CONFIG.alertTypes.RISING_TREND]: 
      `${product.product_name} is showing rising momentum with a ${trend_score} trend score. Currently at ${trend_stage} stage with ${opportunity_rating} opportunity. Consider testing this product soon.`,
    
    [ALERT_CONFIG.alertTypes.HIGH_MARGIN]: 
      `High margin opportunity detected: £${margin.toFixed(2)} potential profit per unit. Combined with ${trend_score} trend score and ${opportunity_rating} opportunity rating.`,
    
    [ALERT_CONFIG.alertTypes.NEW_OPPORTUNITY]: 
      `New product opportunity in ${category}. Trend score: ${trend_score}, Opportunity: ${opportunity_rating}. Stage: ${trend_stage}.`,
  };

  return bodies[alertType] || `Product alert for ${product.product_name}`;
}

/**
 * Batch generate alerts for multiple products
 * @param {Array} products - Array of products
 * @returns {Array} Array of generated alerts
 */
export function batchGenerateAlerts(products) {
  const alerts = [];
  
  for (const product of products) {
    const alert = generateAlert(product);
    if (alert) {
      alerts.push(alert);
    }
  }

  // Sort by priority and date
  return alerts.sort((a, b) => {
    const priorityOrder = { critical: 0, high: 1, medium: 2 };
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
    if (priorityDiff !== 0) return priorityDiff;
    return new Date(b.created_at) - new Date(a.created_at);
  });
}

/**
 * Filter alerts by priority
 */
export function filterAlertsByPriority(alerts, priority) {
  return alerts.filter(alert => alert.priority === priority);
}

/**
 * Get unread alerts count
 */
export function getUnreadAlertsCount(alerts) {
  return alerts.filter(alert => !alert.read && !alert.dismissed).length;
}

/**
 * Mark alert as read
 */
export function markAlertAsRead(alerts, alertId) {
  return alerts.map(alert => 
    alert.id === alertId ? { ...alert, read: true } : alert
  );
}

/**
 * Dismiss alert
 */
export function dismissAlert(alerts, alertId) {
  return alerts.map(alert => 
    alert.id === alertId ? { ...alert, dismissed: true } : alert
  );
}

/**
 * Get alert statistics
 */
export function getAlertStats(alerts) {
  return {
    total: alerts.length,
    unread: alerts.filter(a => !a.read && !a.dismissed).length,
    critical: alerts.filter(a => a.priority === 'critical').length,
    high: alerts.filter(a => a.priority === 'high').length,
    medium: alerts.filter(a => a.priority === 'medium').length,
    byType: {
      early_stage: alerts.filter(a => a.alert_type === 'early_stage').length,
      rising_trend: alerts.filter(a => a.alert_type === 'rising_trend').length,
      high_margin: alerts.filter(a => a.alert_type === 'high_margin').length,
      new_opportunity: alerts.filter(a => a.alert_type === 'new_opportunity').length,
    }
  };
}
