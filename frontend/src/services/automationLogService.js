import { supabase, isSupabaseConfigured } from '@/lib/supabase';

// LocalStorage key for demo mode
const LOGS_STORAGE_KEY = 'trendscout_automation_logs';

/**
 * Automation Log Types
 */
export const AutomationJobTypes = {
  FULL_PIPELINE: 'full_pipeline',
  TREND_SCORING: 'trend_scoring',
  OPPORTUNITY_RATING: 'opportunity_rating',
  TREND_STAGE: 'trend_stage',
  AI_SUMMARY: 'ai_summary',
  ALERT_GENERATION: 'alert_generation',
  PRODUCT_IMPORT: 'product_import',
  CSV_IMPORT: 'csv_import',
  SCHEDULED_DAILY: 'scheduled_daily',
};

/**
 * Automation Log Status
 */
export const AutomationStatus = {
  STARTED: 'started',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  PARTIAL: 'partial',
};

/**
 * Get logs from localStorage (demo mode)
 */
const getDemoLogs = () => {
  try {
    const logs = localStorage.getItem(LOGS_STORAGE_KEY);
    return logs ? JSON.parse(logs) : [];
  } catch {
    return [];
  }
};

/**
 * Save logs to localStorage (demo mode)
 */
const setDemoLogs = (logs) => {
  try {
    localStorage.setItem(LOGS_STORAGE_KEY, JSON.stringify(logs));
  } catch {
    // Ignore localStorage errors
  }
};

/**
 * Create a new automation log entry
 * @param {Object} logData - Log data
 * @returns {Object} Created log entry
 */
export const createAutomationLog = async (logData) => {
  const log = {
    id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    job_type: logData.job_type,
    status: logData.status || AutomationStatus.STARTED,
    started_at: new Date().toISOString(),
    completed_at: null,
    products_processed: 0,
    alerts_generated: 0,
    import_source: logData.import_source || null,
    error_message: null,
    metadata: logData.metadata || {},
  };

  if (!isSupabaseConfigured()) {
    const logs = getDemoLogs();
    logs.unshift(log);
    setDemoLogs(logs.slice(0, 100)); // Keep max 100 logs
    return { data: log, error: null };
  }

  const { data, error } = await supabase
    .from('automation_logs')
    .insert([log])
    .select()
    .single();

  return { data: data || log, error };
};

/**
 * Update an existing automation log
 * @param {string} logId - Log ID
 * @param {Object} updates - Fields to update
 */
export const updateAutomationLog = async (logId, updates) => {
  const updateData = {
    ...updates,
    completed_at: updates.status === AutomationStatus.COMPLETED || 
                  updates.status === AutomationStatus.FAILED ? 
                  new Date().toISOString() : undefined,
  };

  if (!isSupabaseConfigured()) {
    const logs = getDemoLogs();
    const index = logs.findIndex(l => l.id === logId);
    if (index !== -1) {
      logs[index] = { ...logs[index], ...updateData };
      setDemoLogs(logs);
    }
    return { error: null };
  }

  const { error } = await supabase
    .from('automation_logs')
    .update(updateData)
    .eq('id', logId);

  return { error };
};

/**
 * Get automation logs
 * @param {Object} options - Query options
 */
export const getAutomationLogs = async (options = {}) => {
  const { limit = 50, jobType = null, status = null } = options;

  if (!isSupabaseConfigured()) {
    let logs = getDemoLogs();
    
    if (jobType) {
      logs = logs.filter(l => l.job_type === jobType);
    }
    if (status) {
      logs = logs.filter(l => l.status === status);
    }
    
    return { data: logs.slice(0, limit), error: null };
  }

  let query = supabase
    .from('automation_logs')
    .select('*')
    .order('started_at', { ascending: false })
    .limit(limit);

  if (jobType) {
    query = query.eq('job_type', jobType);
  }
  if (status) {
    query = query.eq('status', status);
  }

  const { data, error } = await query;
  return { data, error };
};

/**
 * Get automation stats
 */
export const getAutomationStats = async () => {
  if (!isSupabaseConfigured()) {
    const logs = getDemoLogs();
    const last24h = new Date();
    last24h.setHours(last24h.getHours() - 24);

    const recentLogs = logs.filter(l => new Date(l.started_at) > last24h);
    
    return {
      data: {
        totalRuns: logs.length,
        runsLast24h: recentLogs.length,
        productsProcessed: logs.reduce((sum, l) => sum + (l.products_processed || 0), 0),
        alertsGenerated: logs.reduce((sum, l) => sum + (l.alerts_generated || 0), 0),
        successRate: logs.length > 0 ? 
          Math.round((logs.filter(l => l.status === AutomationStatus.COMPLETED).length / logs.length) * 100) : 0,
        lastRun: logs[0]?.started_at || null,
        byType: Object.values(AutomationJobTypes).reduce((acc, type) => {
          acc[type] = logs.filter(l => l.job_type === type).length;
          return acc;
        }, {}),
      },
      error: null,
    };
  }

  const { data: logs, error } = await supabase
    .from('automation_logs')
    .select('*')
    .order('started_at', { ascending: false });

  if (error) return { data: null, error };

  const last24h = new Date();
  last24h.setHours(last24h.getHours() - 24);
  const recentLogs = logs.filter(l => new Date(l.started_at) > last24h);

  return {
    data: {
      totalRuns: logs.length,
      runsLast24h: recentLogs.length,
      productsProcessed: logs.reduce((sum, l) => sum + (l.products_processed || 0), 0),
      alertsGenerated: logs.reduce((sum, l) => sum + (l.alerts_generated || 0), 0),
      successRate: logs.length > 0 ? 
        Math.round((logs.filter(l => l.status === AutomationStatus.COMPLETED).length / logs.length) * 100) : 0,
      lastRun: logs[0]?.started_at || null,
      byType: Object.values(AutomationJobTypes).reduce((acc, type) => {
        acc[type] = logs.filter(l => l.job_type === type).length;
        return acc;
      }, {}),
    },
    error: null,
  };
};

/**
 * Log a complete automation run with tracking
 */
export const logAutomationRun = async (jobType, runFn) => {
  // Create initial log
  const { data: log } = await createAutomationLog({
    job_type: jobType,
    status: AutomationStatus.RUNNING,
  });

  try {
    // Execute the automation function
    const result = await runFn();

    // Update log with results
    await updateAutomationLog(log.id, {
      status: AutomationStatus.COMPLETED,
      products_processed: result.productsProcessed || 0,
      alerts_generated: result.alertsGenerated || 0,
      metadata: result.metadata || {},
    });

    return { success: true, result, logId: log.id };
  } catch (error) {
    // Log failure
    await updateAutomationLog(log.id, {
      status: AutomationStatus.FAILED,
      error_message: error.message || 'Unknown error',
    });

    return { success: false, error: error.message, logId: log.id };
  }
};
