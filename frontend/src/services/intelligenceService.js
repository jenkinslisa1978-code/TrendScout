/**
 * Intelligence Service
 * 
 * Fetches product validation, trend analysis, and success predictions.
 */

import { API_URL } from '@/lib/config';

/**
 * Get complete product analysis (validation + trends + prediction)
 * Primary endpoint for "Should I launch this?" decision
 */
export const getCompleteAnalysis = async (productId) => {
  try {
    const response = await fetch(`${API_URL}/api/intelligence/complete-analysis/${productId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch analysis');
    }
    
    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    console.error('Error fetching complete analysis:', error);
    return { data: null, error: error.message };
  }
};

/**
 * Get product validation only
 */
export const getProductValidation = async (productId) => {
  try {
    const response = await fetch(`${API_URL}/api/intelligence/validate/${productId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch validation');
    }
    
    const result = await response.json();
    return { data: result.validation, error: null };
  } catch (error) {
    console.error('Error fetching validation:', error);
    return { data: null, error: error.message };
  }
};

/**
 * Get success prediction only
 */
export const getSuccessPrediction = async (productId) => {
  try {
    const response = await fetch(`${API_URL}/api/intelligence/success-prediction/${productId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch prediction');
    }
    
    const result = await response.json();
    return { data: result.prediction, error: null };
  } catch (error) {
    console.error('Error fetching prediction:', error);
    return { data: null, error: error.message };
  }
};

/**
 * Get trend analysis only
 */
export const getTrendAnalysis = async (productId) => {
  try {
    const response = await fetch(`${API_URL}/api/intelligence/trend-analysis/${productId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch trend analysis');
    }
    
    const result = await response.json();
    return { data: result.trend_analysis, error: null };
  } catch (error) {
    console.error('Error fetching trend analysis:', error);
    return { data: null, error: error.message };
  }
};

/**
 * Get launch opportunities
 */
export const getLaunchOpportunities = async (minScore = 70, limit = 20) => {
  try {
    const response = await fetch(
      `${API_URL}/api/intelligence/opportunities?min_score=${minScore}&limit=${limit}`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch opportunities');
    }
    
    const data = await response.json();
    return { data: data.opportunities, count: data.count, error: null };
  } catch (error) {
    console.error('Error fetching opportunities:', error);
    return { data: [], count: 0, error: error.message };
  }
};

/**
 * Get early trend opportunities
 */
export const getEarlyOpportunities = async (limit = 20) => {
  try {
    const response = await fetch(
      `${API_URL}/api/intelligence/early-opportunities?limit=${limit}`
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch early opportunities');
    }
    
    const data = await response.json();
    return { data: data.early_opportunities, count: data.count, error: null };
  } catch (error) {
    console.error('Error fetching early opportunities:', error);
    return { data: [], count: 0, error: error.message };
  }
};

export default {
  getCompleteAnalysis,
  getProductValidation,
  getSuccessPrediction,
  getTrendAnalysis,
  getLaunchOpportunities,
  getEarlyOpportunities,
};
