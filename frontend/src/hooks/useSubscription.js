/**
 * useSubscription Hook
 * 
 * Provides subscription status and feature access checks throughout the app.
 */

import { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

// Default features for unauthenticated users
const DEFAULT_FEATURES = {
  full_reports: false,
  full_insights: false,
  pdf_export: false,
  watchlist: false,
  alerts: false,
  early_trends: false,
  automation_insights: false,
  advanced_opportunities: false,
  direct_publish: false,
  automated_reports: false,
  priority_alerts: false,
  max_stores: 1,
  can_create_store: true,
  current_store_count: 0
};

// Subscription context
const SubscriptionContext = createContext(null);

/**
 * Subscription Provider - wraps app to provide subscription data
 */
export function SubscriptionProvider({ children }) {
  const { user, profile, isDemoMode } = useAuth();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState({
    plan: 'free',
    status: 'active',
    features: DEFAULT_FEATURES
  });
  
  // Fetch subscription data
  const refreshSubscription = useCallback(async () => {
    if (!user) {
      setSubscription({
        plan: 'free',
        status: 'active',
        features: DEFAULT_FEATURES
      });
      setLoading(false);
      return;
    }
    
    // In demo mode, grant elite access for testing
    if (isDemoMode) {
      setSubscription({
        plan: 'elite',
        status: 'active',
        features: {
          full_reports: true,
          full_insights: true,
          pdf_export: true,
          watchlist: true,
          alerts: true,
          early_trends: true,
          automation_insights: true,
          advanced_opportunities: true,
          direct_publish: true,
          automated_reports: true,
          priority_alerts: true,
          max_stores: -1,
          can_create_store: true,
          current_store_count: 0
        }
      });
      setLoading(false);
      return;
    }
    
    try {
      const response = await api.get('/api/stripe/feature-access');
      if (response.data) {
        setSubscription({
          plan: response.data.plan || 'free',
          status: 'active',
          features: response.data.features || DEFAULT_FEATURES,
          isAdmin: response.data.is_admin || false,
          adminBypass: response.data.admin_bypass || false
        });
      }
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
      // Fall back to profile data
      const plan = profile?.plan || 'free';
      setSubscription({
        plan,
        status: 'active',
        features: getDefaultFeaturesForPlan(plan)
      });
    } finally {
      setLoading(false);
    }
  }, [user, profile, isDemoMode]);
  
  // Refresh on user change
  useEffect(() => {
    refreshSubscription();
  }, [refreshSubscription]);
  
  const value = {
    ...subscription,
    loading,
    refresh: refreshSubscription,
    
    // Admin status
    isAdmin: subscription.isAdmin || false,
    adminBypass: subscription.adminBypass || false,
    
    // Convenience methods
    isPro: subscription.plan === 'pro' || subscription.plan === 'elite',
    isElite: subscription.plan === 'elite',
    isFree: subscription.plan === 'free',
    isStarter: subscription.plan === 'starter',
    isStarterOrAbove: ['starter', 'pro', 'elite'].includes(subscription.plan),
    isProOrAbove: ['pro', 'elite'].includes(subscription.plan),

    // Plan limits
    maxAnalysesDaily: subscription.features.max_analyses_daily ?? 2,
    maxSimulationsDaily: subscription.features.max_simulations_daily ?? 0,
    opportunityFeedLimit: subscription.features.opportunity_feed_limit ?? 3,
    canUseBudgetOptimizer: subscription.features.budget_optimizer ?? false,
    canUseRadarAlerts: subscription.features.radar_alerts ?? false,
    canUseLaunchpad: subscription.features.launchpad ?? false,
    canUseAdTesting: subscription.features.ad_testing ?? false,
    canUseLaunchSimulator: subscription.features.launch_simulator ?? false,
    canUseAdGenerator: subscription.features.ad_generator ?? false,
    
    // Feature checks
    canAccessFullReports: subscription.features.full_reports,
    canAccessFullInsights: subscription.features.full_insights,
    canExportPdf: subscription.features.pdf_export,
    canAccessWatchlist: subscription.features.watchlist,
    canAccessAlerts: subscription.features.alerts,
    canAccessEarlyTrends: subscription.features.early_trends,
    canAccessAutomation: subscription.features.automation_insights,
    canAccessAdvancedOpportunities: subscription.features.advanced_opportunities,
    canDirectPublish: subscription.features.direct_publish,
    canAccessAutomatedReports: subscription.features.automated_reports,
    canAccessPriorityAlerts: subscription.features.priority_alerts,
    canCreateStore: subscription.features.can_create_store,
    maxStores: subscription.features.max_stores,
    storeCount: subscription.features.current_store_count
  };
  
  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
}

/**
 * useSubscription hook - access subscription data
 */
export function useSubscription() {
  const context = useContext(SubscriptionContext);
  
  if (!context) {
    // Return safe defaults if used outside provider
    return {
      plan: 'free',
      status: 'active',
      features: DEFAULT_FEATURES,
      loading: false,
      refresh: () => {},
      isPro: false,
      isElite: false,
      isFree: true,
      canAccessFullReports: false,
      canAccessFullInsights: false,
      canExportPdf: false,
      canAccessWatchlist: false,
      canAccessAlerts: false,
      canAccessEarlyTrends: false,
      canAccessAutomation: false,
      canAccessAdvancedOpportunities: false,
      canDirectPublish: false,
      canAccessAutomatedReports: false,
      canAccessPriorityAlerts: false,
      canCreateStore: true,
      maxStores: 1,
      storeCount: 0
    };
  }
  
  return context;
}

/**
 * Get default features for a plan
 */
function getDefaultFeaturesForPlan(plan) {
  switch (plan?.toLowerCase()) {
    case 'elite':
      return {
        full_reports: true,
        full_insights: true,
        pdf_export: true,
        watchlist: true,
        alerts: true,
        early_trends: true,
        automation_insights: true,
        advanced_opportunities: true,
        direct_publish: true,
        automated_reports: true,
        priority_alerts: true,
        max_stores: -1,
        can_create_store: true,
        current_store_count: 0
      };
    case 'pro':
      return {
        full_reports: true,
        full_insights: true,
        pdf_export: true,
        watchlist: true,
        alerts: true,
        early_trends: false,
        automation_insights: false,
        advanced_opportunities: false,
        direct_publish: false,
        automated_reports: false,
        priority_alerts: false,
        max_stores: 5,
        can_create_store: true,
        current_store_count: 0,
        ad_generator: true,
        ad_testing: true,
        launch_simulator: true,
        budget_optimizer: false,
        radar_alerts: false,
        launchpad: false,
        max_analyses_daily: -1,
        max_simulations_daily: -1,
        opportunity_feed_limit: -1,
      };
    case 'starter':
      return {
        full_reports: false,
        full_insights: false,
        pdf_export: false,
        watchlist: false,
        alerts: false,
        early_trends: false,
        automation_insights: false,
        advanced_opportunities: false,
        direct_publish: false,
        automated_reports: false,
        priority_alerts: false,
        max_stores: 2,
        can_create_store: true,
        current_store_count: 0,
        ad_generator: true,
        ad_testing: false,
        launch_simulator: true,
        budget_optimizer: false,
        radar_alerts: false,
        launchpad: false,
        max_analyses_daily: 5,
        max_simulations_daily: 3,
        opportunity_feed_limit: 10,
      };
    default:
      return DEFAULT_FEATURES;
  }
}

/**
 * Higher-order component for feature gating
 */
export function withFeatureAccess(WrappedComponent, requiredFeature, FallbackComponent = null) {
  return function FeatureGatedComponent(props) {
    const subscription = useSubscription();
    
    const hasAccess = () => {
      switch (requiredFeature) {
        case 'full_reports':
          return subscription.canAccessFullReports;
        case 'full_insights':
          return subscription.canAccessFullInsights;
        case 'watchlist':
          return subscription.canAccessWatchlist;
        case 'alerts':
          return subscription.canAccessAlerts;
        case 'early_trends':
          return subscription.canAccessEarlyTrends;
        case 'automation':
          return subscription.canAccessAutomation;
        case 'advanced_opportunities':
          return subscription.canAccessAdvancedOpportunities;
        default:
          return false;
      }
    };
    
    if (subscription.loading) {
      return null; // Or loading spinner
    }
    
    if (!hasAccess()) {
      return FallbackComponent ? <FallbackComponent {...props} /> : null;
    }
    
    return <WrappedComponent {...props} />;
  };
}

export default useSubscription;
