/**
 * Access Control Service
 * 
 * Centralized access control for plan-based feature gating.
 * Enforces user permissions throughout the application.
 */

import { PLANS, hasFeatureAccess, canAccessCount } from './subscriptionService';

/**
 * Permission Types
 */
export const Permissions = {
  // Product Access
  VIEW_PRODUCTS: 'view_products',
  VIEW_PREMIUM_PRODUCTS: 'view_premium_products',
  SAVE_PRODUCTS: 'save_products',
  
  // Alerts
  VIEW_ALERTS: 'view_alerts',
  
  // Export
  EXPORT_DATA: 'export_data',
  
  // API
  API_ACCESS: 'api_access',
  
  // Admin
  ADMIN_PANEL: 'admin_panel',
  AUTOMATION_CENTER: 'automation_center',
};

/**
 * Plan-based permission mapping
 */
const PERMISSION_MAP = {
  [Permissions.VIEW_PRODUCTS]: {
    free: true,
    starter: true,
    pro: true,
    elite: true,
  },
  [Permissions.VIEW_PREMIUM_PRODUCTS]: {
    free: false,
    starter: false,
    pro: true,
    elite: true,
  },
  [Permissions.SAVE_PRODUCTS]: {
    free: true,
    starter: true,
    pro: true,
    elite: true,
  },
  [Permissions.VIEW_ALERTS]: {
    free: false,
    starter: false,
    pro: true,
    elite: true,
  },
  [Permissions.EXPORT_DATA]: {
    free: false,
    starter: false,
    pro: true,
    elite: true,
  },
  [Permissions.API_ACCESS]: {
    free: false,
    starter: false,
    pro: false,
    elite: true,
  },
  [Permissions.ADMIN_PANEL]: {
    free: 'admin_only',
    starter: 'admin_only',
    pro: 'admin_only',
    elite: 'admin_only',
  },
  [Permissions.AUTOMATION_CENTER]: {
    free: 'admin_only',
    starter: 'admin_only',
    pro: 'admin_only',
    elite: 'admin_only',
  },
};

/**
 * Check if user has permission
 * @param {Object} user - User object with role
 * @param {Object} profile - Profile object with plan
 * @param {string} permission - Permission to check
 * @param {boolean} isDemoMode - Whether in demo mode
 * @returns {boolean}
 */
export const hasPermission = (user, profile, permission, isDemoMode = false) => {
  // Demo mode grants full access
  if (isDemoMode) return true;
  
  // No user = no access
  if (!user) return false;
  
  const plan = profile?.plan || 'free';
  const role = profile?.role || 'user';
  
  const permissionRule = PERMISSION_MAP[permission];
  if (!permissionRule) return false;
  
  const planPermission = permissionRule[plan];
  
  // Admin-only permissions
  if (planPermission === 'admin_only') {
    return role === 'admin';
  }
  
  return planPermission === true;
};

/**
 * Check if user can view a specific product
 */
export const canViewProduct = (user, profile, product, isDemoMode = false) => {
  if (isDemoMode) return true;
  if (!user) return false;
  
  // Non-premium products are viewable by all
  if (!product.is_premium) return true;
  
  // Premium products require pro or elite
  return hasPermission(user, profile, Permissions.VIEW_PREMIUM_PRODUCTS, isDemoMode);
};

/**
 * Check if user can save more products
 */
export const canSaveMoreProducts = (user, profile, currentSavedCount, isDemoMode = false) => {
  if (isDemoMode) return true;
  if (!user) return false;
  
  const plan = PLANS[profile?.plan || 'free'];
  const limit = plan.features.maxSavedProducts;
  
  // -1 means unlimited
  if (limit === -1) return true;
  
  return currentSavedCount < limit;
};

/**
 * Get user's product view limit
 */
export const getProductViewLimit = (profile, isDemoMode = false) => {
  if (isDemoMode) return -1; // Unlimited
  
  const plan = PLANS[profile?.plan || 'free'];
  return plan.features.maxProducts;
};

/**
 * Get user's saved product limit
 */
export const getSavedProductLimit = (profile, isDemoMode = false) => {
  if (isDemoMode) return -1; // Unlimited
  
  const plan = PLANS[profile?.plan || 'free'];
  return plan.features.maxSavedProducts;
};

/**
 * Check if user is admin
 */
export const isAdmin = (profile, isDemoMode = false) => {
  if (isDemoMode) return true;
  return profile?.role === 'admin';
};

/**
 * Check if user is elite
 */
export const isElitePlan = (profile, isDemoMode = false) => {
  if (isDemoMode) return true;
  return profile?.plan === 'elite';
};

/**
 * Get restricted features for current plan
 */
export const getRestrictedFeatures = (profile, isDemoMode = false) => {
  if (isDemoMode) return [];
  
  const plan = profile?.plan || 'free';
  const restricted = [];
  
  if (plan === 'free') {
    restricted.push('Premium Products', 'Trend Alerts', 'Export Data', 'API Access', 'Advanced Filters');
  } else if (plan === 'starter') {
    restricted.push('Premium Products', 'Trend Alerts', 'Export Data', 'API Access', 'Advanced Filters');
  } else if (plan === 'pro') {
    restricted.push('Trend Alerts', 'API Access');
  }
  
  return restricted;
};

/**
 * Get upgrade path for a feature
 */
export const getUpgradePathForFeature = (feature, currentPlan = 'free') => {
  const featureRequirements = {
    [Permissions.VIEW_PREMIUM_PRODUCTS]: 'pro',
    [Permissions.VIEW_ALERTS]: 'elite',
    [Permissions.EXPORT_DATA]: 'pro',
    [Permissions.API_ACCESS]: 'elite',
  };
  
  const requiredPlan = featureRequirements[feature];
  
  if (!requiredPlan) return null;
  
  const planOrder = ['free', 'starter', 'pro', 'elite'];
  const currentIndex = planOrder.indexOf(currentPlan);
  const requiredIndex = planOrder.indexOf(requiredPlan);
  
  if (requiredIndex <= currentIndex) return null;
  
  return {
    requiredPlan,
    upgradeTo: requiredPlan,
    price: PLANS[requiredPlan].price,
  };
};

/**
 * Access Control HOC helper
 * Use this in components to conditionally render based on permissions
 */
export const withAccessControl = (WrappedComponent, requiredPermission) => {
  return function AccessControlledComponent(props) {
    const { user, profile, isDemoMode } = props;
    
    if (!hasPermission(user, profile, requiredPermission, isDemoMode)) {
      return null; // Or return an upgrade prompt
    }
    
    return <WrappedComponent {...props} />;
  };
};
