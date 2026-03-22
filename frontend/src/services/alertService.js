import { batchGenerateAlerts, getAlertStats } from '@/lib/automation/alerts';
import { API_URL } from '@/lib/config';
import { apiPut } from '@/lib/api';

/**
 * Get all alerts from backend API
 */
export const getAlerts = async (userId, options = {}) => {
  const { limit = 50, unreadOnly = false } = options;

  try {
    const url = `${API_URL}/api/alerts?limit=${limit}${unreadOnly ? '&unread_only=true' : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch alerts');
    }
    
    const result = await response.json();
    
    return { 
      data: result.data || [], 
      error: null,
      stats: result.stats || getAlertStats(result.data || [])
    };
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return { data: [], error: error.message, stats: null };
  }
};

/**
 * Create alerts for products that qualify
 * Triggers backend automation which handles alert creation
 * @param {Array} products - Products to check for alerts
 */
export const createAlertsForProducts = async (products) => {
  // Backend handles alert creation during automation runs
  // This generates alerts locally for immediate feedback
  const alerts = batchGenerateAlerts(products);
  return { data: alerts, error: null, count: alerts.length };
};

/**
 * Mark an alert as read via backend API
 */
export const markAlertRead = async (alertId) => {
  try {
    const response = await apiPut(`/api/alerts/${alertId}/read`);
    
    if (!response.ok) {
      throw new Error('Failed to mark alert as read');
    }
    
    return { error: null };
  } catch (error) {
    console.error('Error marking alert read:', error);
    return { error: error.message };
  }
};

/**
 * Dismiss an alert via backend API
 */
export const dismissAlertById = async (alertId) => {
  try {
    const response = await apiPut(`/api/alerts/${alertId}/dismiss`);
    
    if (!response.ok) {
      throw new Error('Failed to dismiss alert');
    }
    
    return { error: null };
  } catch (error) {
    console.error('Error dismissing alert:', error);
    return { error: error.message };
  }
};

/**
 * Mark all alerts as read
 */
export const markAllAlertsRead = async () => {
  // Would need a backend endpoint for bulk update
  // For now, this is a placeholder
  return { error: null };
};

/**
 * Delete old alerts (cleanup)
 */
export const cleanupOldAlerts = async (daysOld = 30) => {
  // Would need a backend endpoint for cleanup
  return { deleted: 0, error: null };
};

/**
 * Get alert count for badge display from backend
 */
export const getUnreadAlertCount = async () => {
  try {
    const response = await fetch(`${API_URL}/api/alerts?limit=1`);
    
    if (!response.ok) {
      return 0;
    }
    
    const result = await response.json();
    return result.stats?.unread || 0;
  } catch (error) {
    console.error('Error fetching unread alert count:', error);
    return 0;
  }
};
