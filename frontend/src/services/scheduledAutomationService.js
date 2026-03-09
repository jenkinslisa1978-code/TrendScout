/**
 * Scheduled Automation Orchestrator
 * 
 * Central orchestration for all automation tasks.
 * Ready for cron/scheduled job integration.
 * 
 * This module provides:
 * - Single entry point for daily automation
 * - Individual task runners
 * - Logging and monitoring
 * - Error handling and recovery
 */

import { 
  runFullAutomation, 
  batchRunAutomation,
  batchCalculateTrendScores,
  batchCalculateOpportunityRatings,
  batchCalculateTrendStages,
  batchGenerateAISummaries,
  batchGenerateAlerts,
} from '@/lib/automation';
import { getAllProductsRaw, updateProduct } from './productService';
import { createAlertsForProducts } from './alertService';
import { 
  createAutomationLog, 
  updateAutomationLog, 
  AutomationJobTypes, 
  AutomationStatus 
} from './automationLogService';

/**
 * Run the full daily automation pipeline
 * 
 * This is the main entry point for scheduled automation.
 * Call this from a cron job or scheduled task.
 * 
 * Pipeline steps:
 * 1. Fetch all products
 * 2. Recalculate trend stages
 * 3. Recalculate trend scores  
 * 4. Recalculate opportunity ratings
 * 5. Regenerate AI summaries
 * 6. Generate alerts for qualifying products
 * 7. Log results
 * 
 * @returns {Object} Automation results
 */
export const runDailyAutomation = async () => {
  const results = {
    success: false,
    productsProcessed: 0,
    alertsGenerated: 0,
    errors: [],
    steps: {},
    duration: 0,
  };

  const startTime = Date.now();

  // Create log entry
  const { data: log } = await createAutomationLog({
    job_type: AutomationJobTypes.SCHEDULED_DAILY,
    status: AutomationStatus.RUNNING,
  });

  try {
    // Step 1: Fetch all products
    console.log('[Automation] Fetching all products...');
    const { data: products, error: fetchError } = await getAllProductsRaw();
    
    if (fetchError || !products) {
      throw new Error(`Failed to fetch products: ${fetchError?.message || 'Unknown error'}`);
    }

    results.steps.fetch = { success: true, count: products.length };
    console.log(`[Automation] Fetched ${products.length} products`);

    // Step 2: Run full automation on all products
    console.log('[Automation] Running automation pipeline...');
    const automationResult = batchRunAutomation(products);
    
    results.steps.automation = { 
      success: true, 
      processed: automationResult.products.length,
    };

    // Step 3: Update products in database
    console.log('[Automation] Updating products...');
    let updateErrors = 0;
    
    for (const product of automationResult.products) {
      const { error } = await updateProduct(product.id, {
        trend_score: product.trend_score,
        trend_stage: product.trend_stage,
        opportunity_rating: product.opportunity_rating,
        ai_summary: product.ai_summary,
        estimated_margin: product.estimated_margin,
      }, false); // Don't run automation again

      if (error) {
        updateErrors++;
        results.errors.push(`Failed to update product ${product.id}`);
      }
    }

    results.steps.update = { 
      success: updateErrors === 0, 
      updated: automationResult.products.length - updateErrors,
      errors: updateErrors,
    };

    // Step 4: Generate alerts
    console.log('[Automation] Generating alerts...');
    const { data: alerts, count: alertCount, error: alertError } = 
      await createAlertsForProducts(automationResult.products);
    
    if (alertError) {
      results.errors.push(`Alert generation error: ${alertError}`);
    }

    results.steps.alerts = { 
      success: !alertError, 
      generated: alertCount || 0,
    };

    // Compile final results
    results.success = true;
    results.productsProcessed = automationResult.products.length;
    results.alertsGenerated = alertCount || 0;
    results.duration = Date.now() - startTime;

    // Update log
    await updateAutomationLog(log.id, {
      status: AutomationStatus.COMPLETED,
      products_processed: results.productsProcessed,
      alerts_generated: results.alertsGenerated,
      metadata: { steps: results.steps, duration: results.duration },
    });

    console.log(`[Automation] Completed in ${results.duration}ms`);
    console.log(`[Automation] Processed: ${results.productsProcessed}, Alerts: ${results.alertsGenerated}`);

  } catch (error) {
    results.success = false;
    results.errors.push(error.message);
    results.duration = Date.now() - startTime;

    // Log failure
    await updateAutomationLog(log.id, {
      status: AutomationStatus.FAILED,
      error_message: error.message,
      metadata: { steps: results.steps, duration: results.duration },
    });

    console.error('[Automation] Failed:', error.message);
  }

  return results;
};

/**
 * Run trend scoring only
 */
export const runTrendScoringTask = async () => {
  const { data: log } = await createAutomationLog({
    job_type: AutomationJobTypes.TREND_SCORING,
    status: AutomationStatus.RUNNING,
  });

  try {
    const { data: products } = await getAllProductsRaw();
    const scored = batchCalculateTrendScores(products);
    
    for (const product of scored) {
      await updateProduct(product.id, { trend_score: product.trend_score }, false);
    }

    await updateAutomationLog(log.id, {
      status: AutomationStatus.COMPLETED,
      products_processed: scored.length,
    });

    return { success: true, processed: scored.length };
  } catch (error) {
    await updateAutomationLog(log.id, {
      status: AutomationStatus.FAILED,
      error_message: error.message,
    });
    return { success: false, error: error.message };
  }
};

/**
 * Run opportunity rating only
 */
export const runOpportunityRatingTask = async () => {
  const { data: log } = await createAutomationLog({
    job_type: AutomationJobTypes.OPPORTUNITY_RATING,
    status: AutomationStatus.RUNNING,
  });

  try {
    const { data: products } = await getAllProductsRaw();
    const rated = batchCalculateOpportunityRatings(products);
    
    for (const product of rated) {
      await updateProduct(product.id, { opportunity_rating: product.opportunity_rating }, false);
    }

    await updateAutomationLog(log.id, {
      status: AutomationStatus.COMPLETED,
      products_processed: rated.length,
    });

    return { success: true, processed: rated.length };
  } catch (error) {
    await updateAutomationLog(log.id, {
      status: AutomationStatus.FAILED,
      error_message: error.message,
    });
    return { success: false, error: error.message };
  }
};

/**
 * Run trend stage assignment only
 */
export const runTrendStageTask = async () => {
  const { data: log } = await createAutomationLog({
    job_type: AutomationJobTypes.TREND_STAGE,
    status: AutomationStatus.RUNNING,
  });

  try {
    const { data: products } = await getAllProductsRaw();
    const staged = batchCalculateTrendStages(products);
    
    for (const product of staged) {
      await updateProduct(product.id, { trend_stage: product.trend_stage }, false);
    }

    await updateAutomationLog(log.id, {
      status: AutomationStatus.COMPLETED,
      products_processed: staged.length,
    });

    return { success: true, processed: staged.length };
  } catch (error) {
    await updateAutomationLog(log.id, {
      status: AutomationStatus.FAILED,
      error_message: error.message,
    });
    return { success: false, error: error.message };
  }
};

/**
 * Run AI summary generation only
 */
export const runAISummaryTask = async () => {
  const { data: log } = await createAutomationLog({
    job_type: AutomationJobTypes.AI_SUMMARY,
    status: AutomationStatus.RUNNING,
  });

  try {
    const { data: products } = await getAllProductsRaw();
    const summarized = batchGenerateAISummaries(products);
    
    for (const product of summarized) {
      await updateProduct(product.id, { ai_summary: product.ai_summary }, false);
    }

    await updateAutomationLog(log.id, {
      status: AutomationStatus.COMPLETED,
      products_processed: summarized.length,
    });

    return { success: true, processed: summarized.length };
  } catch (error) {
    await updateAutomationLog(log.id, {
      status: AutomationStatus.FAILED,
      error_message: error.message,
    });
    return { success: false, error: error.message };
  }
};

/**
 * Run alert generation only
 */
export const runAlertGenerationTask = async () => {
  const { data: log } = await createAutomationLog({
    job_type: AutomationJobTypes.ALERT_GENERATION,
    status: AutomationStatus.RUNNING,
  });

  try {
    const { data: products } = await getAllProductsRaw();
    const { count, error } = await createAlertsForProducts(products);
    
    if (error) throw new Error(error);

    await updateAutomationLog(log.id, {
      status: AutomationStatus.COMPLETED,
      products_processed: products.length,
      alerts_generated: count,
    });

    return { success: true, processed: products.length, alertsGenerated: count };
  } catch (error) {
    await updateAutomationLog(log.id, {
      status: AutomationStatus.FAILED,
      error_message: error.message,
    });
    return { success: false, error: error.message };
  }
};

/**
 * CRON JOB ENTRY POINTS
 * 
 * These functions are designed to be called from external schedulers.
 * 
 * Example cron setup (in Supabase Edge Functions or external cron service):
 * 
 * Daily at 2 AM: runDailyAutomation()
 * Every 6 hours: runTrendScoringTask()
 * Every 12 hours: runAlertGenerationTask()
 */
export const CronJobs = {
  // Run full daily automation - recommended: once per day
  daily: runDailyAutomation,
  
  // Run individual tasks - for more granular control
  trendScoring: runTrendScoringTask,
  opportunityRating: runOpportunityRatingTask,
  trendStage: runTrendStageTask,
  aiSummary: runAISummaryTask,
  alertGeneration: runAlertGenerationTask,
};

/**
 * Get automation status/health
 */
export const getAutomationHealth = async () => {
  const { data: logs } = await import('./automationLogService').then(m => m.getAutomationLogs({ limit: 10 }));
  
  const recentLogs = logs || [];
  const lastRun = recentLogs[0];
  const failedRecent = recentLogs.filter(l => l.status === AutomationStatus.FAILED).length;
  
  return {
    healthy: failedRecent < 3,
    lastRunAt: lastRun?.started_at || null,
    lastRunStatus: lastRun?.status || 'unknown',
    recentFailures: failedRecent,
    message: failedRecent >= 3 
      ? 'Multiple recent failures detected' 
      : failedRecent > 0 
        ? 'Some recent failures' 
        : 'All systems operational',
  };
};
