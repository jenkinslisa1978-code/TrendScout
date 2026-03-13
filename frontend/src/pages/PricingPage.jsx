import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Check, Zap, TrendingUp, Sparkles, Loader2, ArrowRight,
  Rocket, Store, Bell, Eye, FileText, Shield, Star,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { trackEvent, EVENTS } from '@/services/analytics';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 19,
    description: 'Start finding winners',
    features: [
      '10 product views per day',
      'Basic trend insights',
      'Daily product updates',
      'Category filters',
      'Trend score access',
      'Email support',
    ],
    cta: 'Start 7-Day Free Trial',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 39,
    description: 'Full product intelligence',
    features: [
      'Unlimited product discovery',
      'Trend score analytics',
      'AI ad creative generator',
      'Trend alerts & notifications',
      'Supplier intelligence',
      'Product profit calculator',
      'Saved product workspace',
    ],
    cta: 'Start 7-Day Free Trial',
    popular: true,
  },
  {
    id: 'elite',
    name: 'Elite',
    price: 79,
    description: 'Scale with advanced tools',
    features: [
      'Everything in Pro',
      'Competitor store tracking',
      'AI launch simulator',
      'Advanced analytics & reports',
      'TikTok intelligence dashboard',
      'Unlimited insights',
      'Priority support',
    ],
    cta: 'Start 7-Day Free Trial',
    popular: false,
  },
];

export default function PricingPage() {
  const { user, profile } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(null);
  const [currentPlan, setCurrentPlan] = useState('free');

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      toast.success('Subscription updated successfully!');
      window.location.href = '/dashboard';
    }
  }, [searchParams]);

  useEffect(() => {
    if (profile?.plan) setCurrentPlan(profile.plan.toLowerCase());
  }, [profile]);

  const handleSelectPlan = async (planId) => {
    if (!user) {
      trackEvent(EVENTS.SIGNUP_CLICK, { source: 'pricing', plan: planId });
      navigate('/signup');
      return;
    }
    trackEvent(EVENTS.CHECKOUT_START, { plan: planId });
    setLoading(planId);
    try {
      const response = await api.post('/api/stripe/create-checkout-session', {
        plan: planId,
        success_url: `${window.location.origin}/pricing?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${window.location.origin}/pricing`,
      });
      if (response.data.demo_mode) {
        toast.info('Demo mode: Stripe checkout simulated');
        navigate('/dashboard');
        return;
      }
      if (response.data.url) window.location.href = response.data.url;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to start checkout');
    } finally {
      setLoading(null);
    }
  };

  const handleManageBilling = async () => {
    try {
      const response = await api.post('/api/stripe/create-portal-session', {
        return_url: `${window.location.origin}/pricing`,
      });
      if (response.data.demo_mode) {
        toast.info('Demo mode: Billing portal not available');
        return;
      }
      if (response.data.url) window.location.href = response.data.url;
    } catch {
      toast.error('Failed to open billing portal');
    }
  };

  return (
    <LandingLayout>
      <div className="min-h-screen bg-white" data-testid="pricing-page">
        {/* Header */}
        <div className="pt-20 pb-4 text-center max-w-3xl mx-auto px-6">
          <Badge className="bg-indigo-50 text-indigo-600 border-indigo-100 mb-5 text-xs px-3 py-1 rounded-full">
            <Sparkles className="h-3 w-3 mr-1" />
            Simple, Transparent Pricing
          </Badge>
          <h1 className="font-manrope text-4xl font-extrabold text-slate-900 sm:text-5xl" data-testid="pricing-headline">
            Simple pricing. Powerful intelligence.
          </h1>
          <p className="mt-5 text-lg text-slate-500 leading-relaxed">
            One winning product can generate <strong className="text-slate-800">&pound;10,000+ revenue</strong>.<br />
            TrendScout costs less than testing a single TikTok ad campaign.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="max-w-5xl mx-auto px-6 py-16">
          <div className="grid md:grid-cols-3 gap-6">
            {PLANS.map((plan) => {
              const isCurrentPlan = currentPlan === plan.id;
              const planOrder = ['free', 'starter', 'pro', 'elite'];
              const canUpgrade = !isCurrentPlan && planOrder.indexOf(plan.id) > planOrder.indexOf(currentPlan);

              return (
                <div
                  key={plan.id}
                  data-testid={`pricing-card-${plan.id}`}
                  className={`relative rounded-2xl border bg-white p-7 transition-all duration-400 hover:-translate-y-1 ${
                    plan.popular
                      ? 'border-indigo-500 shadow-2xl shadow-indigo-100/70 scale-[1.03]'
                      : 'border-slate-200 hover:border-slate-300 hover:shadow-xl hover:shadow-slate-100/60'
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                      <span className="inline-flex items-center rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-1 text-xs font-semibold text-white shadow-md">
                        Recommended
                      </span>
                    </div>
                  )}
                  <div>
                    <h3 className="font-manrope text-lg font-bold text-slate-900">{plan.name}</h3>
                    <p className="mt-1 text-sm text-slate-500">{plan.description}</p>
                    <div className="mt-5">
                      <span className="font-manrope text-5xl font-extrabold text-slate-900">&pound;{plan.price}</span>
                      <span className="text-slate-400 text-base">/month</span>
                    </div>
                  </div>
                  <ul className="mt-7 space-y-3">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-start gap-2.5">
                        <Check className="h-4 w-4 flex-shrink-0 text-emerald-500 mt-0.5" />
                        <span className="text-sm text-slate-600">{f}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    className={`w-full h-12 mt-8 text-sm font-semibold rounded-xl transition-all duration-300 ${
                      isCurrentPlan
                        ? 'bg-emerald-100 text-emerald-700 hover:bg-emerald-100 cursor-default'
                        : plan.popular
                        ? 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 shadow-md text-white'
                        : 'bg-slate-900 hover:bg-slate-800 text-white'
                    }`}
                    onClick={() => !isCurrentPlan && canUpgrade && handleSelectPlan(plan.id)}
                    disabled={loading === plan.id || isCurrentPlan}
                    data-testid={`pricing-cta-${plan.id}`}
                  >
                    {loading === plan.id ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : isCurrentPlan ? (
                      <><Check className="h-4 w-4 mr-2" /> Current Plan</>
                    ) : (
                      <>{plan.cta} <ArrowRight className="h-4 w-4 ml-2" /></>
                    )}
                  </Button>
                  <p className="text-center text-xs text-slate-400 mt-3">
                    7-day free trial. Cancel anytime.
                  </p>
                </div>
              );
            })}
          </div>

          {/* Free tier mention */}
          <div className="mt-10 text-center">
            <p className="text-slate-500 text-sm">
              Not ready to commit?{' '}
              <Link to="/signup" className="font-semibold text-indigo-600 hover:text-indigo-500">
                Start free
              </Link>{' '}
              — explore trending products before upgrading.
            </p>
          </div>

          {/* Billing Management */}
          {user && currentPlan !== 'free' && (
            <div className="mt-10 text-center">
              <Button variant="outline" onClick={handleManageBilling} data-testid="manage-billing-btn">
                Manage Billing
              </Button>
            </div>
          )}

          {/* Feature Comparison Table */}
          <div className="mt-20">
            <h2 className="font-manrope text-2xl font-bold text-center text-slate-900 mb-8">
              Compare Plans
            </h2>
            <div className="bg-white rounded-xl border shadow-sm overflow-x-auto">
              <table className="w-full" data-testid="feature-comparison-table">
                <thead>
                  <tr className="border-b bg-slate-50">
                    <th className="text-left p-4 font-medium text-slate-700">Feature</th>
                    <th className="text-center p-4 font-medium text-slate-700">Starter <span className="text-xs font-normal">(&pound;19)</span></th>
                    <th className="text-center p-4 font-medium text-indigo-700 bg-indigo-50">Pro <span className="text-xs font-normal">(&pound;39)</span></th>
                    <th className="text-center p-4 font-medium text-slate-700">Elite <span className="text-xs font-normal">(&pound;79)</span></th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { icon: Eye, label: 'Product Views', starter: '10/day', pro: 'Unlimited', elite: 'Unlimited' },
                    { icon: TrendingUp, label: 'Trend Insights', starter: 'Basic', pro: 'Full', elite: 'Advanced' },
                    { icon: Sparkles, label: 'AI Ad Generator', starter: false, pro: true, elite: true },
                    { icon: Bell, label: 'Trend Alerts', starter: false, pro: true, elite: true },
                    { icon: Rocket, label: 'Launch Simulator', starter: false, pro: false, elite: true },
                    { icon: Store, label: 'Competitor Tracking', starter: false, pro: false, elite: true },
                    { icon: FileText, label: 'Analytics & Reports', starter: 'Basic', pro: 'Standard', elite: 'Advanced' },
                    { icon: Shield, label: 'Support', starter: 'Email', pro: 'Priority Email', elite: 'Priority' },
                  ].map((row, idx) => {
                    const Icon = row.icon;
                    const renderCell = (val) => {
                      if (val === true) return <Check className="h-5 w-5 text-emerald-500 mx-auto" />;
                      if (val === false) return <div className="h-5 w-5 rounded-full border-2 border-slate-200 mx-auto" />;
                      return <span className="text-sm text-slate-600">{val}</span>;
                    };
                    return (
                      <tr key={idx} className="border-b last:border-0">
                        <td className="p-4 flex items-center gap-2 text-sm text-slate-700">
                          <Icon className="h-4 w-4 text-slate-400" />
                          {row.label}
                        </td>
                        <td className="p-4 text-center">{renderCell(row.starter)}</td>
                        <td className="p-4 text-center bg-indigo-50/30">{renderCell(row.pro)}</td>
                        <td className="p-4 text-center">{renderCell(row.elite)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Trust Signals */}
          <div className="mt-16 text-center space-y-3">
            <div className="flex items-center justify-center gap-1 text-amber-400">
              {[1,2,3,4,5].map(i => <Star key={i} className="h-4 w-4 fill-amber-400" />)}
            </div>
            <p className="text-slate-600 text-sm font-medium">Trusted by 2,400+ ecommerce sellers</p>
            <p className="text-slate-400 text-xs">Questions? support@trendscout.click</p>
          </div>
        </div>
      </div>
    </LandingLayout>
  );
}
