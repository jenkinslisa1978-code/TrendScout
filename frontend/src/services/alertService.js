import { supabase, isSupabaseConfigured } from '@/lib/supabase';
import { batchGenerateAlerts, getAlertStats } from '@/lib/automation/alerts';

// LocalStorage key for demo mode
const ALERTS_STORAGE_KEY = 'trendscout_alerts';

/**
 * Get alerts from localStorage (demo mode)
 */
const getDemoAlerts = () => {
  try {
    const alerts = localStorage.getItem(ALERTS_STORAGE_KEY);
    return alerts ? JSON.parse(alerts) : [];
  } catch {
    return [];
  }
};

/**
 * Save alerts to localStorage (demo mode)
 */
const setDemoAlerts = (alerts) => {
  try {
    localStorage.setItem(ALERTS_STORAGE_KEY, JSON.stringify(alerts));
  } catch {
    // Ignore localStorage errors
  }
};

/**
 * Get all alerts for the current user
 */
export const getAlerts = async (userId, options = {}) => {
  const { limit = 50, unreadOnly = false } = options;

  if (!isSupabaseConfigured()) {
    let alerts = getDemoAlerts();
    if (unreadOnly) {
      alerts = alerts.filter(a => !a.read && !a.dismissed);
    }
    return { 
      data: alerts.slice(0, limit), 
      error: null,
      stats: getAlertStats(alerts)
    };
  }

  let query = supabase
    .from('trend_alerts')
    .select('*, products(*)')
    .order('created_at', { ascending: false })
    .limit(limit);

  if (unreadOnly) {
    query = query.eq('read', false).eq('dismissed', false);
  }

  const { data, error } = await query;
  return { 
    data, 
    error,
    stats: data ? getAlertStats(data) : null
  };
};

/**
 * Create alerts for products that qualify
 * @param {Array} products - Products to check for alerts
 */
export const createAlertsForProducts = async (products) => {
  const alerts = batchGenerateAlerts(products);
  
  if (alerts.length === 0) {
    return { data: [], error: null, count: 0 };
  }

  if (!isSupabaseConfigured()) {
    const existingAlerts = getDemoAlerts();
    // Avoid duplicate alerts for same product
    const existingProductIds = new Set(existingAlerts.map(a => a.product_id));
    const newAlerts = alerts.filter(a => !existingProductIds.has(a.product_id));
    
    setDemoAlerts([...newAlerts, ...existingAlerts].slice(0, 100)); // Keep max 100 alerts
    return { data: newAlerts, error: null, count: newAlerts.length };
  }

  // Supabase insert
  const alertsForDb = alerts.map(alert => ({
    product_id: alert.product_id,
    title: alert.title,
    body: alert.body,
    alert_type: alert.alert_type,
    priority: alert.priority,
    read: false,
    dismissed: false,
  }));

  const { data, error } = await supabase
    .from('trend_alerts')
    .insert(alertsForDb)
    .select();

  return { data, error, count: data?.length || 0 };
};

/**
 * Mark an alert as read
 */
export const markAlertRead = async (alertId) => {
  if (!isSupabaseConfigured()) {
    const alerts = getDemoAlerts();
    const updated = alerts.map(a => 
      a.id === alertId ? { ...a, read: true } : a
    );
    setDemoAlerts(updated);
    return { error: null };
  }

  const { error } = await supabase
    .from('trend_alerts')
    .update({ read: true })
    .eq('id', alertId);

  return { error };
};

/**
 * Dismiss an alert
 */
export const dismissAlertById = async (alertId) => {
  if (!isSupabaseConfigured()) {
    const alerts = getDemoAlerts();
    const updated = alerts.map(a => 
      a.id === alertId ? { ...a, dismissed: true } : a
    );
    setDemoAlerts(updated);
    return { error: null };
  }

  const { error } = await supabase
    .from('trend_alerts')
    .update({ dismissed: true })
    .eq('id', alertId);

  return { error };
};

/**
 * Mark all alerts as read
 */
export const markAllAlertsRead = async () => {
  if (!isSupabaseConfigured()) {
    const alerts = getDemoAlerts();
    const updated = alerts.map(a => ({ ...a, read: true }));
    setDemoAlerts(updated);
    return { error: null };
  }

  const { error } = await supabase
    .from('trend_alerts')
    .update({ read: true })
    .eq('read', false);

  return { error };
};

/**
 * Delete old alerts (cleanup)
 */
export const cleanupOldAlerts = async (daysOld = 30) => {
  if (!isSupabaseConfigured()) {
    const alerts = getDemoAlerts();
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - daysOld);
    
    const filtered = alerts.filter(a => new Date(a.created_at) > cutoff);
    setDemoAlerts(filtered);
    return { deleted: alerts.length - filtered.length, error: null };
  }

  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysOld);

  const { error, count } = await supabase
    .from('trend_alerts')
    .delete()
    .lt('created_at', cutoffDate.toISOString());

  return { deleted: count, error };
};

/**
 * Get alert count for badge display
 */
export const getUnreadAlertCount = async () => {
  if (!isSupabaseConfigured()) {
    const alerts = getDemoAlerts();
    return alerts.filter(a => !a.read && !a.dismissed).length;
  }

  const { count, error } = await supabase
    .from('trend_alerts')
    .select('*', { count: 'exact', head: true })
    .eq('read', false)
    .eq('dismissed', false);

  return count || 0;
};
