/**
 * Reports Service
 * 
 * API calls for Market Intelligence Reports
 */

import { apiGet } from '@/lib/api';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Get list of all reports
 */
export const getReportsList = async (reportType = null, limit = 20) => {
  try {
    let url = `${API_URL}/api/reports/?limit=${limit}`;
    if (reportType) {
      url += `&report_type=${reportType}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch reports');
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching reports list:', error);
    return { reports: [], count: 0, latest: {} };
  }
};

/**
 * Get the latest weekly winning products report
 */
export const getWeeklyReport = async () => {
  try {
    const response = await apiGet('/api/reports/weekly-winning-products');
    if (!response.ok) throw new Error('Failed to fetch weekly report');
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching weekly report:', error);
    return { report: null, user_plan: 'free', is_authenticated: false };
  }
};

/**
 * Get the latest monthly market trends report
 */
export const getMonthlyReport = async () => {
  try {
    const response = await apiGet('/api/reports/monthly-market-trends');
    if (!response.ok) throw new Error('Failed to fetch monthly report');
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching monthly report:', error);
    return { report: null, user_plan: 'free', is_authenticated: false };
  }
};

/**
 * Get public preview of weekly report (for SEO pages)
 */
export const getPublicWeeklyReport = async () => {
  try {
    const response = await fetch(`${API_URL}/api/reports/public/weekly-winning-products`);
    if (!response.ok) throw new Error('Failed to fetch public weekly report');
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching public weekly report:', error);
    return { report: null, cta: {} };
  }
};

/**
 * Get public preview of monthly report (for SEO pages)
 */
export const getPublicMonthlyReport = async () => {
  try {
    const response = await fetch(`${API_URL}/api/reports/public/monthly-market-trends`);
    if (!response.ok) throw new Error('Failed to fetch public monthly report');
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching public monthly report:', error);
    return { report: null, cta: {} };
  }
};

/**
 * Get report history by type
 */
export const getReportHistory = async (reportType, limit = 20) => {
  try {
    const response = await apiGet(`/api/reports/history/${reportType}?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch report history');
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching report history:', error);
    return { reports: [], count: 0, user_plan: 'free' };
  }
};

/**
 * Get a specific report by slug
 */
export const getReportBySlug = async (slug) => {
  try {
    const response = await apiGet(`/api/reports/by-slug/${slug}`);
    if (!response.ok) throw new Error('Failed to fetch report');
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching report by slug:', error);
    return { report: null, user_plan: 'free', is_authenticated: false };
  }
};

export default {
  getReportsList,
  getWeeklyReport,
  getMonthlyReport,
  getPublicWeeklyReport,
  getPublicMonthlyReport,
  getReportHistory,
  getReportBySlug,
};
