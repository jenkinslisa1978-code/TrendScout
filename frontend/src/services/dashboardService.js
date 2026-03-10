/**
 * Dashboard Service
 * 
 * API calls for dashboard intelligence features:
 * - Daily Winning Products
 * - Watchlist management
 * - Opportunity Alerts
 * - Market Radar
 */

import { apiGet, apiPost, apiDelete } from '@/lib/api';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Get dashboard summary (daily winners, radar, stats)
 */
export const getDashboardSummary = async () => {
  try {
    const response = await fetch(`${API_URL}/api/dashboard/summary`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch dashboard summary');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching dashboard summary:', error);
    return {
      daily_winners: [],
      market_radar: [],
      watchlist_preview: [],
      unread_alerts: 0,
      stats: {},
    };
  }
};

/**
 * Get daily winning products
 */
export const getDailyWinners = async (limit = 10) => {
  try {
    const response = await fetch(`${API_URL}/api/dashboard/daily-winners?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch daily winners');
    }
    
    const data = await response.json();
    return { data: data.daily_winners, count: data.count, error: null };
  } catch (error) {
    console.error('Error fetching daily winners:', error);
    return { data: [], count: 0, error: error.message };
  }
};

/**
 * Get user's watchlist
 */
export const getWatchlist = async () => {
  try {
    const response = await apiGet('/api/dashboard/watchlist');
    
    if (!response.ok) {
      throw new Error('Failed to fetch watchlist');
    }
    
    const data = await response.json();
    return { data: data.watchlist, count: data.count, error: null };
  } catch (error) {
    console.error('Error fetching watchlist:', error);
    return { data: [], count: 0, error: error.message };
  }
};

/**
 * Add product to watchlist
 */
export const addToWatchlist = async (productId, notes = null) => {
  try {
    const response = await apiPost('/api/dashboard/watchlist', {
      product_id: productId,
      notes,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add to watchlist');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error adding to watchlist:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Remove product from watchlist
 */
export const removeFromWatchlist = async (productId) => {
  try {
    const response = await apiDelete(`/api/dashboard/watchlist/${productId}`);
    
    if (!response.ok) {
      throw new Error('Failed to remove from watchlist');
    }
    
    return { success: true };
  } catch (error) {
    console.error('Error removing from watchlist:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Check if product is in watchlist
 */
export const checkWatchlistStatus = async (productId) => {
  try {
    const response = await apiGet(`/api/dashboard/watchlist/check/${productId}`);
    
    if (!response.ok) {
      return { inWatchlist: false };
    }
    
    const data = await response.json();
    return { inWatchlist: data.in_watchlist, item: data.watchlist_item };
  } catch (error) {
    return { inWatchlist: false };
  }
};

/**
 * Get user alerts
 */
export const getAlerts = async (unreadOnly = false, limit = 50) => {
  try {
    const response = await apiGet(`/api/dashboard/alerts?unread_only=${unreadOnly}&limit=${limit}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch alerts');
    }
    
    const data = await response.json();
    return { data: data.alerts, count: data.count, unreadCount: data.unread_count, error: null };
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return { data: [], count: 0, unreadCount: 0, error: error.message };
  }
};

/**
 * Mark alert as read
 */
export const markAlertRead = async (alertId) => {
  try {
    const response = await apiPost(`/api/dashboard/alerts/${alertId}/read`);
    return { success: response.ok };
  } catch (error) {
    return { success: false };
  }
};

/**
 * Mark all alerts as read
 */
export const markAllAlertsRead = async () => {
  try {
    const response = await apiPost('/api/dashboard/alerts/read-all');
    return { success: response.ok };
  } catch (error) {
    return { success: false };
  }
};

/**
 * Get market opportunity radar
 */
export const getMarketRadar = async (limit = 10) => {
  try {
    const response = await fetch(`${API_URL}/api/dashboard/market-radar?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch market radar');
    }
    
    const data = await response.json();
    return { data: data.market_radar, count: data.count, error: null };
  } catch (error) {
    console.error('Error fetching market radar:', error);
    return { data: [], count: 0, error: error.message };
  }
};

/**
 * Get products in a market cluster
 */
export const getClusterProducts = async (clusterName, limit = 20) => {
  try {
    const response = await fetch(
      `${API_URL}/api/dashboard/market-radar/${encodeURIComponent(clusterName)}?limit=${limit}`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch cluster products');
    }
    
    const data = await response.json();
    return { data: data.products, count: data.count, error: null };
  } catch (error) {
    console.error('Error fetching cluster products:', error);
    return { data: [], count: 0, error: error.message };
  }
};

export default {
  getDashboardSummary,
  getDailyWinners,
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  checkWatchlistStatus,
  getAlerts,
  markAlertRead,
  markAllAlertsRead,
  getMarketRadar,
  getClusterProducts,
};
