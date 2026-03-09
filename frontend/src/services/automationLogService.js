const API_URL = process.env.REACT_APP_BACKEND_URL || '';

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
  TIKTOK_IMPORT: 'tiktok_import',
  AMAZON_IMPORT: 'amazon_import',
  SUPPLIER_IMPORT: 'supplier_import',
  FULL_DATA_SYNC: 'full_data_sync',
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
 * Create a new automation log entry via backend API
 * @param {Object} logData - Log data
 * @returns {Object} Created log entry
 */
export const createAutomationLog = async (logData) => {
  // For now, logs are created by backend during automation runs
  // This creates a local placeholder for UI tracking
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

  return { data: log, error: null };
};

/**
 * Update an existing automation log
 * @param {string} logId - Log ID
 * @param {Object} updates - Fields to update
 */
export const updateAutomationLog = async (logId, updates) => {
  // Backend handles log updates automatically
  // This is a no-op for frontend-initiated updates
  return { error: null };
};

/**
 * Get automation logs from backend API
 * @param {Object} options - Query options
 */
export const getAutomationLogs = async (options = {}) => {
  const { limit = 50 } = options;

  try {
    const response = await fetch(`${API_URL}/api/automation/logs?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch automation logs');
    }
    
    const result = await response.json();
    return { data: result.data || [], error: null };
  } catch (error) {
    console.error('Error fetching automation logs:', error);
    return { data: [], error: error.message };
  }
};

/**
 * Get automation stats from backend API
 */
export const getAutomationStats = async () => {
  try {
    const response = await fetch(`${API_URL}/api/automation/stats`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch automation stats');
    }
    
    const stats = await response.json();
    
    // Transform backend stats to frontend format
    return {
      data: {
        totalRuns: stats.total_runs || 0,
        runsLast24h: 0, // Not tracked by backend currently
        productsProcessed: stats.products_processed || 0,
        alertsGenerated: stats.alerts_generated || 0,
        successRate: stats.success_rate || 0,
        lastRun: stats.last_run || null,
        byType: {},
      },
      error: null,
    };
  } catch (error) {
    console.error('Error fetching automation stats:', error);
    return { 
      data: {
        totalRuns: 0,
        runsLast24h: 0,
        productsProcessed: 0,
        alertsGenerated: 0,
        successRate: 0,
        lastRun: null,
        byType: {},
      }, 
      error: error.message 
    };
  }
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
