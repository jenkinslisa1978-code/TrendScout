import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import {
  Check, X, Loader2, ArrowRight, ChevronDown, ChevronUp,
  Sparkles, Eye, TrendingUp, Zap, Shield, BarChart3, Store, Bell, FileText, Rocket,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { trackEvent, EVENTS } from '@/services/analytics';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    monthlyPrice: 19,
    annualPrice: 15,
    tagline: 'For beginners validating first products',
    features: [
      '10 product views per day',
      'Basic trend insights',
      'Daily product updates',
      'Category filters',
      'Trend score access',
      'UK viability indicators',
      'Email support',
    ],
    cta: 'Start 7-day free trial',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Growth',
    monthlyPrice: 39,
    annualPrice: 31,
    tagline: 'For active sellers testing multiple ideas',
    features: [
      'Unlimited product discovery',
      'Full trend score analytics',
      'AI ad creative generator',
      'Trend alerts and notifications',
      'Supplier intelligence',
      'Profitability simulator',
      'Saturation analysis',
      'Saved product workspace',
      'Priority email support',
    ],
    cta: 'Start 7-day free trial',
    popular: true,
  },
  {
    id: 'elite',
    name: 'Pro',
    monthlyPrice: 79,
    annualPrice: 63,
    tagline: 'For agencies, power users, and serious sellers',
    features: [
      'Everything in Growth',
      'Competitor store tracking',
      'AI launch simulator',
      'Advanced analytics and reports',
      'TikTok intelligence dashboard',
      'API access (100 req/min)',
      'Shopify push-to-store',
      'Unlimited insights',
      'Priority support',
    ],
    cta: 'Start 7-day free trial',
    popular: false,
  },
];

const COMPARISON_ROWS = [
  { label: 'Product views', starter: '10/day', growth: 'Unlimited', pro: 'Unlimited', icon: Eye },
  { label: 'Trend insights', starter: 'Basic', growth: 'Full', pro: 'Advanced', icon: TrendingUp },
  { label: 'UK viability score', starter: true, growth: true, pro: true, icon: Shield },
  { label: 'AI ad generator', starter: false, growth: true, pro: true, icon: Sparkles },
  { label: 'Trend alerts', starter: false, growth: true, pro: true, icon: Bell },
  { label: 'Profitability simulator', starter: false, growth: true, pro: true, icon: BarChart3 },
  { label: 'Saturation analysis', starter: false, growth: true, pro: true, icon: Shield },
  { label: 'Saved products', starter: '5', growth: 'Unlimited', pro: 'Unlimited', icon: FileText },
  { label: 'Launch simulator', starter: false, growth: false, pro: true, icon: Rocket },
  { label: 'Competitor tracking', starter: false, growth: false, pro: true, icon: Store },
  { label: 'API access', starter: false, growth: false, pro: true, icon: Zap },
  { label: 'Shopify push-to-store', starter: false, growth: false, pro: true, icon: Store },
  { label: 'Support', starter: 'Email', growth: 'Priority email', pro: 'Priority', icon: FileText },
];

const FAQS = [
  { q: 'Is there a free plan?', a: 'Yes. You can browse trending products and access basic trend scores without paying. The free plan gives you a taste of TrendScout so you can decide if it is worth upgrading.' },
  { q: 'Can I cancel anytime?', a: 'Yes. No lock-in contracts. Cancel your subscription at any time from your account settings. You keep access until the end of your billing period.' },
  { q: 'Do you offer refunds?', a: 'If you are not happy within the first 7 days of a paid plan, contact us and we will sort it out. After that, cancellations take effect at the end of the billing period.' },
  { q: 'Is pricing in GBP?', a: 'Yes. All prices shown are in British pounds (GBP). VAT may apply depending on your billing address.' },
  { q: 'What happens after my free trial?', a: 'Your trial converts to a paid subscription after 7 days. You will be notified before any charge. Cancel before the trial ends and you will not be billed.' },
  { q: 'Why should I use TrendScout instead of Jungle Scout or Sell The Trend?', a: 'TrendScout is built specifically for UK ecommerce sellers. It factors in VAT, UK shipping costs, local demand signals, and UK market saturation — things generic US-focused tools do not cover.' },
];

export default function PricingPage() {
  const { user, profile } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(null);
  const [currentPlan, setCurrentPlan] = useState('free');
  const [annual, setAnnual] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);

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
    trackEvent(EVENTS.CHECKOUT_START, { plan: planId, billing: annual ? 'annual' : 'monthly' });
    setLoading(planId);
    try {
      const response = await api.post('/api/stripe/create-checkout-session', {
        plan: planId,
        billing_period: annual ? 'annual' : 'monthly',
        success_url: `${window.location.origin}/pricing?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${window.location.origin}/pricing`,
      });
      if (!response.ok) {
        toast.error(response.data?.error?.message || response.data?.detail || 'Failed to start checkout');
        return;
      }
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

  const renderCell = (val) => {
    if (val === true) return <Check className="h-4 w-4 text-emerald-600 mx-auto" />;
    if (val === false) return <X className="h-4 w-4 text-slate-300 mx-auto" />;
    return <span className="text-sm text-slate-700">{val}</span>;
  };

  return (
    <LandingLayout>
      <div className="bg-white" data-testid="pricing-page">
        {/* Header */}
        <div className="pt-16 pb-2 text-center max-w-3xl mx-auto px-6">
          <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight" data-testid="pricing-headline">
            Simple pricing. Built for UK sellers.
          </h1>
          <p className="mt-4 text-base text-slate-500 leading-relaxed max-w-xl mx-auto">
            One winning product can generate thousands in revenue. TrendScout costs less than testing a single ad campaign.
          </p>

          {/* Billing toggle */}
          <div className="mt-8 inline-flex items-center gap-3 rounded-full bg-slate-100 p-1" data-testid="billing-toggle">
            <button
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${!annual ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              onClick={() => setAnnual(false)}
              data-testid="toggle-monthly"
            >
              Monthly
            </button>
            <button
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${annual ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              onClick={() => setAnnual(true)}
              data-testid="toggle-annual"
            >
              Annual <span className="text-emerald-600 font-semibold ml-1">Save 20%</span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="max-w-5xl mx-auto px-6 py-12">
          <div className="grid md:grid-cols-3 gap-5">
            {PLANS.map((plan) => {
              const price = annual ? plan.annualPrice : plan.monthlyPrice;
              const isCurrentPlan = currentPlan === plan.id;
              const planOrder = ['free', 'starter', 'pro', 'elite'];
              const canUpgrade = !isCurrentPlan && planOrder.indexOf(plan.id) > planOrder.indexOf(currentPlan);

              return (
                <div
                  key={plan.id}
                  data-testid={`pricing-card-${plan.id}`}
                  className={`relative rounded-xl border p-6 transition-all duration-200 ${
                    plan.popular ? 'border-indigo-500 shadow-lg ring-1 ring-indigo-500' : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-4">
                      <span className="inline-flex items-center rounded-md bg-indigo-600 px-2.5 py-0.5 text-xs font-semibold text-white">
                        Most popular
                      </span>
                    </div>
                  )}
                  <div>
                    <h3 className="font-manrope text-lg font-bold text-slate-900">{plan.name}</h3>
                    <p className="mt-1 text-sm text-slate-500">{plan.tagline}</p>
                    <div className="mt-4 flex items-baseline gap-1">
                      <span className="font-manrope text-4xl font-extrabold text-slate-900">&pound;{price}</span>
                      <span className="text-sm text-slate-400">/month</span>
                    </div>
                    {annual && (
                      <p className="text-xs text-emerald-600 font-medium mt-1">
                        &pound;{price * 12}/year &middot; Save &pound;{(plan.monthlyPrice - plan.annualPrice) * 12}/year
                      </p>
                    )}
                  </div>
                  <ul className="mt-6 space-y-2.5">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-start gap-2">
                        <Check className="h-4 w-4 flex-shrink-0 text-emerald-500 mt-0.5" />
                        <span className="text-sm text-slate-600">{f}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    className={`w-full h-11 mt-6 text-sm font-semibold rounded-lg transition-all ${
                      isCurrentPlan
                        ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-50 cursor-default border border-emerald-200'
                        : plan.popular
                        ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm'
                        : 'bg-slate-900 hover:bg-slate-800 text-white'
                    }`}
                    onClick={() => !isCurrentPlan && canUpgrade && handleSelectPlan(plan.id)}
                    disabled={loading === plan.id || isCurrentPlan}
                    data-testid={`pricing-cta-${plan.id}`}
                  >
                    {loading === plan.id ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : isCurrentPlan ? (
                      <><Check className="h-4 w-4 mr-1" /> Current plan</>
                    ) : (
                      <>{plan.cta} <ArrowRight className="h-4 w-4 ml-1" /></>
                    )}
                  </Button>
                  <p className="text-center text-xs text-slate-400 mt-2.5">7-day free trial. Cancel anytime.</p>
                </div>
              );
            })}
          </div>

          {/* Free tier */}
          <div className="mt-8 text-center">
            <p className="text-sm text-slate-500">
              Not ready to commit?{' '}
              <Link to="/signup" className="font-semibold text-indigo-600 hover:text-indigo-700">Start free</Link>
              {' '}&mdash; browse trending products and basic scores before upgrading.
            </p>
          </div>

          {user && currentPlan !== 'free' && (
            <div className="mt-6 text-center">
              <Button variant="outline" onClick={handleManageBilling} data-testid="manage-billing-btn" className="rounded-lg">
                Manage Billing
              </Button>
            </div>
          )}
        </div>

        {/* Feature Comparison */}
        <div className="max-w-5xl mx-auto px-6 pb-16">
          <h2 className="font-manrope text-2xl font-bold text-center text-slate-900 mb-8">Compare plans</h2>
          <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">
            <table className="w-full text-sm" data-testid="feature-comparison-table">
              <thead>
                <tr className="border-b bg-slate-50">
                  <th className="text-left p-4 font-medium text-slate-700 w-[40%]">Feature</th>
                  <th className="text-center p-4 font-medium text-slate-700 w-[20%]">Starter<br/><span className="text-xs font-normal text-slate-400">&pound;{annual ? '15' : '19'}/mo</span></th>
                  <th className="text-center p-4 font-medium text-indigo-700 bg-indigo-50/50 w-[20%]">Growth<br/><span className="text-xs font-normal text-indigo-400">&pound;{annual ? '31' : '39'}/mo</span></th>
                  <th className="text-center p-4 font-medium text-slate-700 w-[20%]">Pro<br/><span className="text-xs font-normal text-slate-400">&pound;{annual ? '63' : '79'}/mo</span></th>
                </tr>
              </thead>
              <tbody>
                {COMPARISON_ROWS.map((row, idx) => {
                  const Icon = row.icon;
                  return (
                    <tr key={idx} className="border-b last:border-0 hover:bg-slate-50/50 transition-colors">
                      <td className="p-3.5 flex items-center gap-2 text-slate-700">
                        <Icon className="h-4 w-4 text-slate-400 flex-shrink-0" />
                        {row.label}
                      </td>
                      <td className="p-3.5 text-center">{renderCell(row.starter)}</td>
                      <td className="p-3.5 text-center bg-indigo-50/20">{renderCell(row.growth)}</td>
                      <td className="p-3.5 text-center">{renderCell(row.pro)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-2xl mx-auto px-6 pb-20">
          <h2 className="font-manrope text-2xl font-bold text-center text-slate-900 mb-8">Frequently asked questions</h2>
          <div className="space-y-2" data-testid="pricing-faq">
            {FAQS.map((faq, idx) => (
              <div key={idx} className="border border-slate-200 rounded-lg overflow-hidden">
                <button
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors"
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  data-testid={`faq-${idx}`}
                >
                  <span className="text-sm font-medium text-slate-900">{faq.q}</span>
                  {openFaq === idx ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
                </button>
                {openFaq === idx && (
                  <div className="px-4 pb-4">
                    <p className="text-sm text-slate-600 leading-relaxed">{faq.a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </LandingLayout>
  );
}
