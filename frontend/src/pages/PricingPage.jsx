/**
 * Pricing Page
 * 
 * Displays subscription plans with GBP pricing.
 * Handles Stripe checkout for Pro and Elite plans.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Check,
  Zap,
  Crown,
  Rocket,
  TrendingUp,
  Store,
  Bell,
  FileText,
  Eye,
  Sparkles,
  Loader2,
  ArrowRight
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { toast } from 'sonner';

// Plan configurations matching backend
const PLANS = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    description: 'Get started with basic product research',
    icon: Zap,
    color: 'slate',
    features: [
      { text: 'Limited product insights', included: true },
      { text: 'Report previews only', included: true },
      { text: '1 store', included: true },
      { text: 'Limited watchlist access', included: true },
      { text: 'Limited alerts', included: true },
      { text: 'Early trend detection', included: false },
      { text: 'Advanced opportunity insights', included: false },
      { text: 'Automation insights', included: false },
    ],
    cta: 'Current Plan',
    popular: false
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 39,
    description: 'Full access for serious sellers',
    icon: Rocket,
    color: 'indigo',
    features: [
      { text: 'Full product insights', included: true },
      { text: 'Complete reports access', included: true },
      { text: 'Up to 5 stores', included: true },
      { text: 'Full watchlist access', included: true },
      { text: 'Full alerts access', included: true },
      { text: 'Early trend detection', included: false },
      { text: 'Advanced opportunity insights', included: false },
      { text: 'Automation insights', included: false },
    ],
    cta: 'Upgrade to Pro',
    popular: true
  },
  {
    id: 'elite',
    name: 'Elite',
    price: 99,
    description: 'Everything you need to scale',
    icon: Crown,
    color: 'amber',
    features: [
      { text: 'Everything in Pro', included: true },
      { text: 'Early trend detection', included: true },
      { text: 'Advanced opportunity insights', included: true },
      { text: 'Automation insights', included: true },
      { text: 'Unlimited stores', included: true },
      { text: 'Priority opportunity alerts', included: true },
      { text: 'Premium market analysis', included: true },
      { text: 'Full Live Feed access', included: true },
    ],
    cta: 'Go Elite',
    popular: false
  }
];

function PlanCard({ plan, currentPlan, onSelect, loading }) {
  const isCurrentPlan = currentPlan === plan.id;
  const canUpgrade = !isCurrentPlan && (
    (currentPlan === 'free' && (plan.id === 'pro' || plan.id === 'elite')) ||
    (currentPlan === 'pro' && plan.id === 'elite')
  );
  const isDowngrade = (currentPlan === 'elite' && (plan.id === 'pro' || plan.id === 'free')) ||
                      (currentPlan === 'pro' && plan.id === 'free');
  
  const Icon = plan.icon;
  
  const colorClasses = {
    slate: {
      border: 'border-slate-200',
      bg: 'bg-slate-50',
      badge: 'bg-slate-100 text-slate-700',
      button: 'bg-slate-200 text-slate-700 hover:bg-slate-300',
      icon: 'text-slate-500'
    },
    indigo: {
      border: 'border-indigo-200 ring-2 ring-indigo-500',
      bg: 'bg-indigo-50',
      badge: 'bg-indigo-100 text-indigo-700',
      button: 'bg-indigo-600 text-white hover:bg-indigo-700',
      icon: 'text-indigo-500'
    },
    amber: {
      border: 'border-amber-200',
      bg: 'bg-amber-50',
      badge: 'bg-amber-100 text-amber-700',
      button: 'bg-amber-500 text-white hover:bg-amber-600',
      icon: 'text-amber-500'
    }
  };
  
  const colors = colorClasses[plan.color];
  
  return (
    <Card className={`relative overflow-hidden transition-all duration-300 hover:shadow-lg ${colors.border}`}>
      {plan.popular && (
        <div className="absolute top-0 right-0">
          <Badge className="rounded-none rounded-bl-lg bg-indigo-600 text-white px-3 py-1">
            Most Popular
          </Badge>
        </div>
      )}
      
      <CardHeader className={`${colors.bg} pb-4`}>
        <div className="flex items-center gap-3 mb-2">
          <div className={`p-2 rounded-lg bg-white shadow-sm`}>
            <Icon className={`h-6 w-6 ${colors.icon}`} />
          </div>
          <CardTitle className="text-xl">{plan.name}</CardTitle>
        </div>
        <CardDescription>{plan.description}</CardDescription>
        
        <div className="mt-4">
          <span className="text-4xl font-bold text-slate-900">£{plan.price}</span>
          <span className="text-slate-500">/month</span>
        </div>
      </CardHeader>
      
      <CardContent className="pt-6">
        <ul className="space-y-3 mb-6">
          {plan.features.map((feature, idx) => (
            <li key={idx} className="flex items-start gap-3">
              {feature.included ? (
                <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-slate-200 flex-shrink-0 mt-0.5" />
              )}
              <span className={feature.included ? 'text-slate-700' : 'text-slate-400'}>
                {feature.text}
              </span>
            </li>
          ))}
        </ul>
        
        <Button
          className={`w-full ${isCurrentPlan ? 'bg-green-100 text-green-700 hover:bg-green-100 cursor-default' : colors.button}`}
          onClick={() => !isCurrentPlan && canUpgrade && onSelect(plan.id)}
          disabled={loading || isCurrentPlan || isDowngrade}
        >
          {loading === plan.id ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : isCurrentPlan ? (
            <>
              <Check className="h-4 w-4 mr-2" />
              Current Plan
            </>
          ) : isDowngrade ? (
            'Manage in Billing'
          ) : (
            <>
              {plan.cta}
              <ArrowRight className="h-4 w-4 ml-2" />
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

export default function PricingPage() {
  const { user, profile } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(null);
  const [currentPlan, setCurrentPlan] = useState('free');
  
  // Check for success/cancel from Stripe
  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      toast.success('Subscription updated successfully!');
      // Refresh profile data
      window.location.href = '/dashboard';
    }
  }, [searchParams]);
  
  // Get current plan from profile
  useEffect(() => {
    if (profile?.plan) {
      setCurrentPlan(profile.plan.toLowerCase());
    }
  }, [profile]);
  
  const handleSelectPlan = async (planId) => {
    if (!user) {
      toast.error('Please sign in to upgrade');
      navigate('/login');
      return;
    }
    
    if (planId === 'free') {
      return; // Can't upgrade to free
    }
    
    setLoading(planId);
    
    try {
      const response = await api.post('/api/stripe/create-checkout-session', {
        plan: planId,
        success_url: `${window.location.origin}/pricing?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${window.location.origin}/pricing`
      });
      
      if (response.data.demo_mode) {
        toast.info('Demo mode: Stripe checkout simulated');
        // Simulate upgrade in demo mode
        navigate('/dashboard');
        return;
      }
      
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Checkout error:', error);
      toast.error(error.response?.data?.detail || 'Failed to start checkout');
    } finally {
      setLoading(null);
    }
  };
  
  const handleManageBilling = async () => {
    try {
      const response = await api.post('/api/stripe/create-portal-session', {
        return_url: `${window.location.origin}/pricing`
      });
      
      if (response.data.demo_mode) {
        toast.info('Demo mode: Billing portal not available');
        return;
      }
      
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Portal error:', error);
      toast.error('Failed to open billing portal');
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white" data-testid="pricing-page">
      {/* Header */}
      <div className="pt-16 pb-12 text-center">
        <Badge className="bg-indigo-100 text-indigo-700 mb-4">
          <Sparkles className="h-3 w-3 mr-1" />
          Simple, transparent pricing
        </Badge>
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Choose your plan
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Start free and upgrade as you grow. All prices in GBP.
          Cancel anytime.
        </p>
      </div>
      
      {/* Pricing Cards */}
      <div className="max-w-6xl mx-auto px-4 pb-16">
        <div className="grid md:grid-cols-3 gap-8">
          {PLANS.map(plan => (
            <PlanCard
              key={plan.id}
              plan={plan}
              currentPlan={currentPlan}
              onSelect={handleSelectPlan}
              loading={loading}
            />
          ))}
        </div>
        
        {/* Billing Management */}
        {user && currentPlan !== 'free' && (
          <div className="mt-12 text-center">
            <p className="text-slate-600 mb-4">
              Need to update your payment method or cancel your subscription?
            </p>
            <Button
              variant="outline"
              onClick={handleManageBilling}
              data-testid="manage-billing-btn"
            >
              Manage Billing
            </Button>
          </div>
        )}
        
        {/* Features Comparison */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-center text-slate-900 mb-8">
            Compare Features
          </h2>
          
          <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-slate-50">
                  <th className="text-left p-4 font-medium text-slate-700">Feature</th>
                  <th className="text-center p-4 font-medium text-slate-700">Free</th>
                  <th className="text-center p-4 font-medium text-indigo-700 bg-indigo-50">Pro</th>
                  <th className="text-center p-4 font-medium text-amber-700">Elite</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-4 flex items-center gap-2">
                    <Eye className="h-4 w-4 text-slate-400" />
                    Product Insights
                  </td>
                  <td className="p-4 text-center text-slate-500">Limited</td>
                  <td className="p-4 text-center bg-indigo-50/50"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                  <td className="p-4 text-center"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 flex items-center gap-2">
                    <FileText className="h-4 w-4 text-slate-400" />
                    Market Reports
                  </td>
                  <td className="p-4 text-center text-slate-500">Preview</td>
                  <td className="p-4 text-center bg-indigo-50/50"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                  <td className="p-4 text-center"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 flex items-center gap-2">
                    <Store className="h-4 w-4 text-slate-400" />
                    Stores
                  </td>
                  <td className="p-4 text-center">1</td>
                  <td className="p-4 text-center bg-indigo-50/50">5</td>
                  <td className="p-4 text-center">Unlimited</td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 flex items-center gap-2">
                    <Bell className="h-4 w-4 text-slate-400" />
                    Watchlist & Alerts
                  </td>
                  <td className="p-4 text-center text-slate-500">Limited</td>
                  <td className="p-4 text-center bg-indigo-50/50"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                  <td className="p-4 text-center"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-slate-400" />
                    Early Trend Detection
                  </td>
                  <td className="p-4 text-center"><div className="h-5 w-5 rounded-full border-2 border-slate-200 mx-auto" /></td>
                  <td className="p-4 text-center bg-indigo-50/50"><div className="h-5 w-5 rounded-full border-2 border-slate-200 mx-auto" /></td>
                  <td className="p-4 text-center"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                </tr>
                <tr className="border-b">
                  <td className="p-4 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-slate-400" />
                    Advanced Opportunities
                  </td>
                  <td className="p-4 text-center"><div className="h-5 w-5 rounded-full border-2 border-slate-200 mx-auto" /></td>
                  <td className="p-4 text-center bg-indigo-50/50"><div className="h-5 w-5 rounded-full border-2 border-slate-200 mx-auto" /></td>
                  <td className="p-4 text-center"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="p-4 flex items-center gap-2">
                    <Zap className="h-4 w-4 text-slate-400" />
                    Automation Insights
                  </td>
                  <td className="p-4 text-center"><div className="h-5 w-5 rounded-full border-2 border-slate-200 mx-auto" /></td>
                  <td className="p-4 text-center bg-indigo-50/50"><div className="h-5 w-5 rounded-full border-2 border-slate-200 mx-auto" /></td>
                  <td className="p-4 text-center"><Check className="h-5 w-5 text-green-500 mx-auto" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        {/* FAQ or Trust Signals */}
        <div className="mt-16 text-center">
          <p className="text-slate-500">
            Questions? Contact us at support@viralscout.com
          </p>
        </div>
      </div>
    </div>
  );
}
