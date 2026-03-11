import { apiPost } from '@/lib/api';

/**
 * Stripe Subscription Service
 * 
 * Handles subscription management, plan changes, and billing integration.
 * 
 * STRIPE-READY: All endpoints structured for Stripe webhook integration.
 */

// LocalStorage key for demo mode
const SUBSCRIPTION_STORAGE_KEY = 'trendscout_subscription';

// Plan definitions
export const PLANS = {
  free: {
    id: 'free',
    name: 'Free',
    price: 0,
    priceId: '', // No Stripe for free tier
    features: {
      maxProducts: 10,
      maxSavedProducts: 5,
      trendAlerts: false,
      apiAccess: false,
      prioritySupport: false,
      advancedFilters: false,
      exportData: false,
    },
    description: 'Get started with product research',
  },
  pro: {
    id: 'pro',
    name: 'Pro',
    price: 39,
    priceId: process.env.REACT_APP_STRIPE_PRO_PRICE_ID || '',
    features: {
      maxProducts: 100,
      maxSavedProducts: 50,
      trendAlerts: false,
      apiAccess: false,
      prioritySupport: true,
      advancedFilters: true,
      exportData: true,
    },
    description: 'Full access for serious sellers',
  },
  elite: {
    id: 'elite',
    name: 'Elite',
    price: 99,
    priceId: process.env.REACT_APP_STRIPE_ELITE_PRICE_ID || '',
    features: {
      maxProducts: -1, // Unlimited
      maxSavedProducts: -1, // Unlimited
      trendAlerts: true,
      apiAccess: true,
      prioritySupport: true,
      advancedFilters: true,
      exportData: true,
    },
    description: 'Full access with trend alerts',
  },
};

/**
 * Get demo subscription from localStorage
 */
const getDemoSubscription = () => {
  try {
    const sub = localStorage.getItem(SUBSCRIPTION_STORAGE_KEY);
    return sub ? JSON.parse(sub) : null;
  } catch {
    return null;
  }
};

/**
 * Set demo subscription in localStorage
 */
const setDemoSubscription = (subscription) => {
  try {
    localStorage.setItem(SUBSCRIPTION_STORAGE_KEY, JSON.stringify(subscription));
  } catch {
    // Ignore localStorage errors
  }
};

/**
 * Get current user's subscription
 */
export const getSubscription = async (userId) => {
  const subscription = getDemoSubscription();
  if (subscription) {
    return { data: subscription, error: null };
  }
  
  // Default to elite in demo mode
  const defaultSub = {
    id: 'demo-sub-id',
    user_id: userId,
    plan_name: 'elite',
    status: 'active',
    stripe_subscription_id: null,
    stripe_customer_id: null,
    current_period_start: new Date().toISOString(),
    current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    cancel_at_period_end: false,
    created_at: new Date().toISOString(),
  };
  setDemoSubscription(defaultSub);
  return { data: defaultSub, error: null };
};

/**
 * Get plan details
 */
export const getPlanDetails = (planId) => {
  return PLANS[planId] || PLANS.free;
};

/**
 * Check if user has access to a feature
 */
export const hasFeatureAccess = (subscription, feature) => {
  if (!subscription) return false;
  
  const plan = PLANS[subscription.plan_name];
  if (!plan) return false;

  // Check if subscription is active
  if (subscription.status !== 'active' && subscription.status !== 'trialing') {
    return false;
  }

  return plan.features[feature] === true || 
         (typeof plan.features[feature] === 'number' && plan.features[feature] !== 0);
};

/**
 * Check if user can access a specific number of items
 */
export const canAccessCount = (subscription, feature, currentCount) => {
  if (!subscription) return false;
  
  const plan = PLANS[subscription.plan_name];
  if (!plan) return false;

  const limit = plan.features[feature];
  
  // -1 means unlimited
  if (limit === -1) return true;
  
  return currentCount < limit;
};

/**
 * Create Stripe checkout session
 * STRIPE-READY: Call this to redirect user to Stripe Checkout
 */
export const createCheckoutSession = async (userId, planId, successUrl, cancelUrl) => {
  const plan = PLANS[planId];
  if (!plan || !plan.priceId) {
    return { error: 'Invalid plan or missing Stripe price ID' };
  }

  try {
    const response = await apiPost('/api/stripe/create-checkout-session', {
      price_id: plan.priceId,
      success_url: successUrl,
      cancel_url: cancelUrl,
    });

    const data = await response.json();
    
    if (!response.ok) {
      return { error: data.detail || data.message || 'Failed to create checkout session' };
    }

    return { data, error: null };
  } catch (error) {
    return { error: error.message };
  }
};

/**
 * Create Stripe customer portal session
 * STRIPE-READY: For managing existing subscriptions
 */
export const createPortalSession = async (userId, returnUrl) => {
  try {
    const response = await apiPost('/api/stripe/create-portal-session', {
      return_url: returnUrl,
    });

    const data = await response.json();
    
    if (!response.ok) {
      return { error: data.detail || data.message || 'Failed to create portal session' };
    }

    return { data, error: null };
  } catch (error) {
    return { error: error.message };
  }
};

/**
 * Cancel subscription
 */
export const cancelSubscription = async (userId, cancelAtPeriodEnd = true) => {
  try {
    const response = await apiPost('/api/stripe/cancel-subscription', {
      cancel_at_period_end: cancelAtPeriodEnd,
    });

    const data = await response.json();
    
    if (!response.ok) {
      return { error: data.detail || data.message || 'Failed to cancel subscription' };
    }

    return { error: null };
  } catch (error) {
    return { error: error.message };
  }
};

/**
 * Update subscription (change plan)
 */
export const updateSubscription = async (userId, newPlanId) => {
  try {
    const response = await apiPost('/api/stripe/update-subscription', {
      new_plan_id: newPlanId,
      new_price_id: PLANS[newPlanId]?.priceId,
    });

    const data = await response.json();
    
    if (!response.ok) {
      return { error: data.detail || data.message || 'Failed to update subscription' };
    }

    return { error: null };
  } catch (error) {
    return { error: error.message };
  }
};

/**
 * WEBHOOK HANDLER STRUCTURE
 * 
 * This is the structure for handling Stripe webhooks.
 * Implement in backend/server.py:
 * 
 * Webhook Events to Handle:
 * - checkout.session.completed -> Create/update subscription
 * - customer.subscription.updated -> Update subscription status
 * - customer.subscription.deleted -> Mark subscription as canceled
 * - invoice.payment_succeeded -> Record successful payment
 * - invoice.payment_failed -> Handle failed payment
 */
export const WebhookEvents = {
  CHECKOUT_COMPLETED: 'checkout.session.completed',
  SUBSCRIPTION_UPDATED: 'customer.subscription.updated',
  SUBSCRIPTION_DELETED: 'customer.subscription.deleted',
  PAYMENT_SUCCEEDED: 'invoice.payment_succeeded',
  PAYMENT_FAILED: 'invoice.payment_failed',
};

/**
 * Process webhook event (called from backend)
 * This is a reference for backend implementation
 */
export const processWebhookEvent = async (event) => {
  const eventType = event.type;
  const eventData = event.data.object;

  switch (eventType) {
    case WebhookEvents.CHECKOUT_COMPLETED:
      // Extract customer and subscription info
      // Update database with new subscription
      break;
    
    case WebhookEvents.SUBSCRIPTION_UPDATED:
      // Update subscription status in database
      break;
    
    case WebhookEvents.SUBSCRIPTION_DELETED:
      // Mark subscription as canceled
      // Downgrade user to starter plan
      break;
    
    case WebhookEvents.PAYMENT_FAILED:
      // Send notification to user
      // Consider grace period
      break;
    
    default:
      console.log(`Unhandled webhook event: ${eventType}`);
  }
};
