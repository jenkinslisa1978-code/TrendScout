import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { faqSchema, breadcrumbSchema, softwareAppSchema } from '@/components/PageMeta';
import { RevealSection, RevealStagger } from '@/hooks/useScrollReveal';
import {
  Check, X, Loader2, ArrowRight, ChevronDown,
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
    tagline: 'Start validating product ideas',
    icon: Eye,
    features: [
      '10 product views per day',
      'Basic trend insights',
      'Daily product updates',
      'Category filters',
      'Trend score access',
      'UK viability indicators',
      'Email support',
    ],
    cta: 'Try free for 7 days',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Growth',
    monthlyPrice: 39,
    annualPrice: 31,
    tagline: 'Best for serious sellers',
    icon: TrendingUp,
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
    cta: 'Start validating products',
    popular: true,
  },
  {
    id: 'elite',
    name: 'Pro',
    monthlyPrice: 79,
    annualPrice: 63,
    tagline: 'For agencies and power users',
    icon: Rocket,
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
    cta: 'Start validating products',
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
    return <span className="text-sm font-medium text-slate-700">{val}</span>;
  };

  return (
    <LandingLayout>
      <PageMeta
        title="Plans and Pricing — Start from £19/mo | TrendScout"
        description="Simple pricing for UK product validation. Starter £19/mo, Growth £39/mo, Pro £79/mo. Start free, no credit card required. Cancel anytime."
        canonical="/pricing"
        schema={[
          softwareAppSchema,
          faqSchema(FAQS),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Pricing' }]),
        ]}
      />
      <div className="bg-white" data-testid="pricing-page">

        {/* ═══ HERO ═══ */}
        <section className="relative bg-gradient-to-b from-slate-50 via-white to-white overflow-hidden pt-16 pb-4 lg:pt-24 lg:pb-8">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(99,102,241,0.06),transparent)]" />
          <div className="relative mx-auto max-w-7xl px-6 lg:px-8 text-center">
            <RevealSection>
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Pricing</p>
              <h1 className="font-manrope text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-[1.1]" data-testid="pricing-headline">
                Pick a plan.{' '}
                <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">Built for UK sellers.</span>
              </h1>
              <p className="mt-5 text-base sm:text-lg text-slate-500 leading-relaxed max-w-xl mx-auto">
                One winning product can generate thousands in revenue. TrendScout costs less than testing a single ad campaign.
              </p>

              {/* Billing toggle */}
              <div className="mt-8 inline-flex items-center gap-1 rounded-full bg-slate-100 p-1" data-testid="billing-toggle">
                <button
                  className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 ${!annual ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                  onClick={() => { setAnnual(false); trackEvent(EVENTS.PRICING_TOGGLE, { billing: 'monthly' }); }}
                  data-testid="toggle-monthly"
                >
                  Monthly
                </button>
                <button
                  className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 ${annual ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                  onClick={() => { setAnnual(true); trackEvent(EVENTS.PRICING_TOGGLE, { billing: 'annual' }); }}
                  data-testid="toggle-annual"
                >
                  Annual <span className="text-emerald-600 font-semibold ml-1">Save 20%</span>
                </button>
              </div>
            </RevealSection>
          </div>
        </section>

        {/* ═══ PRICING CARDS ═══ */}
        <section className="py-12 lg:py-16">
          <div className="mx-auto max-w-6xl px-6 lg:px-8">
            <RevealStagger className="grid md:grid-cols-3 gap-6" staggerMs={120}>
              {PLANS.map((plan) => {
                const price = annual ? plan.annualPrice : plan.monthlyPrice;
                const isCurrentPlan = currentPlan === plan.id;
                const planOrder = ['free', 'starter', 'pro', 'elite'];
                const canUpgrade = !isCurrentPlan && planOrder.indexOf(plan.id) > planOrder.indexOf(currentPlan);
                const Icon = plan.icon;

                return (
                  <div
                    key={plan.id}
                    data-testid={`pricing-card-${plan.id}`}
                    className={`relative rounded-2xl border p-7 transition-all duration-300 hover:shadow-xl ${
                      plan.popular
                        ? 'border-indigo-500 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500 scale-[1.02]'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-600 px-4 py-1 text-xs font-semibold text-white shadow-sm">
                          <Sparkles className="h-3 w-3" /> Most popular
                        </span>
                      </div>
                    )}

                    <div className="flex items-center gap-3 mb-4">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${plan.popular ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-500'}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="font-manrope text-lg font-bold text-slate-900">{plan.name}</h3>
                        <p className="text-xs text-slate-500">{plan.tagline}</p>
                      </div>
                    </div>

                    <div className="flex items-baseline gap-1 mt-2">
                      <span className="font-manrope text-5xl font-extrabold text-slate-900">&pound;{price}</span>
                      <span className="text-sm text-slate-400">/month</span>
                    </div>
                    {annual && (
                      <p className="text-xs text-emerald-600 font-medium mt-1.5">
                        &pound;{price * 12}/year &middot; Save &pound;{(plan.monthlyPrice - plan.annualPrice) * 12}/year
                      </p>
                    )}

                    <div className="my-6 h-px bg-slate-100" />

                    <ul className="space-y-3">
                      {plan.features.map((f) => (
                        <li key={f} className="flex items-start gap-2.5">
                          <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-50 mt-0.5">
                            <Check className="h-3 w-3 text-emerald-600" />
                          </div>
                          <span className="text-sm text-slate-600">{f}</span>
                        </li>
                      ))}
                    </ul>

                    <Button
                      className={`w-full h-12 mt-7 text-sm font-semibold rounded-xl transition-all duration-200 ${
                        isCurrentPlan
                          ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-50 cursor-default border border-emerald-200'
                          : plan.popular
                          ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20 hover:shadow-indigo-500/30'
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
                        <>{plan.cta} <ArrowRight className="h-4 w-4 ml-1.5" /></>
                      )}
                    </Button>
                    <p className="text-center text-xs text-slate-400 mt-3">Try before you commit. Cancel anytime.</p>
                  </div>
                );
              })}
            </RevealStagger>

            {/* Free tier callout */}
            <RevealSection delay={400} className="mt-10 text-center">
              <p className="text-sm text-slate-500">
                Not ready to commit?{' '}
                <Link to="/signup" className="font-semibold text-indigo-600 hover:text-indigo-700">Start free</Link>
                {' '}&mdash; browse trending products and basic scores before upgrading.
              </p>
            </RevealSection>

            {user && currentPlan !== 'free' && (
              <div className="mt-6 text-center">
                <Button variant="outline" onClick={handleManageBilling} data-testid="manage-billing-btn" className="rounded-xl">
                  Manage Billing
                </Button>
              </div>
            )}
          </div>
        </section>

        {/* ═══ TRUST STRIP ═══ */}
        <section className="py-10 bg-slate-50 border-y border-slate-100" data-testid="pricing-trust-strip">
          <div className="mx-auto max-w-5xl px-6 lg:px-8">
            <RevealStagger className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center" staggerMs={100}>
              {[
                { val: '7 days', label: 'Free trial on every plan' },
                { val: '0', label: 'Lock-in contracts' },
                { val: 'GBP', label: 'All prices in pounds' },
                { val: '< 2 min', label: 'To start researching' },
              ].map((item) => (
                <div key={item.label}>
                  <p className="font-manrope text-2xl font-extrabold text-indigo-600">{item.val}</p>
                  <p className="text-xs text-slate-500 mt-1">{item.label}</p>
                </div>
              ))}
            </RevealStagger>
          </div>
        </section>

        {/* ═══ FEATURE COMPARISON TABLE ═══ */}
        <section className="py-16 lg:py-20" data-testid="comparison-section">
          <div className="mx-auto max-w-6xl px-6 lg:px-8">
            <RevealSection className="text-center mb-10">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Compare</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Detailed feature comparison
              </h2>
            </RevealSection>
            <RevealSection delay={100}>
              <div className="rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm" data-testid="feature-comparison-table">
                    <thead>
                      <tr className="border-b bg-slate-50">
                        <th className="text-left p-4 pl-5 font-medium text-slate-700 w-[40%]">Feature</th>
                        <th className="text-center p-4 font-medium text-slate-700 w-[20%]">
                          <span className="block font-semibold">Starter</span>
                          <span className="text-xs font-normal text-slate-400">&pound;{annual ? '15' : '19'}/mo</span>
                        </th>
                        <th className="text-center p-4 font-medium text-indigo-700 bg-indigo-50/50 w-[20%]">
                          <span className="block font-semibold">Growth</span>
                          <span className="text-xs font-normal text-indigo-400">&pound;{annual ? '31' : '39'}/mo</span>
                        </th>
                        <th className="text-center p-4 font-medium text-slate-700 w-[20%]">
                          <span className="block font-semibold">Pro</span>
                          <span className="text-xs font-normal text-slate-400">&pound;{annual ? '63' : '79'}/mo</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {COMPARISON_ROWS.map((row, idx) => {
                        const Icon = row.icon;
                        return (
                          <tr key={idx} className="border-b last:border-0 hover:bg-slate-50/50 transition-colors">
                            <td className="p-3.5 pl-5 flex items-center gap-2.5 text-slate-700">
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
            </RevealSection>
          </div>
        </section>

        {/* ═══ FAQ ═══ */}
        <section className="py-16 lg:py-20 bg-slate-50">
          <div className="mx-auto max-w-3xl px-6 lg:px-8">
            <RevealSection className="text-center mb-10">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">FAQ</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Frequently asked questions
              </h2>
            </RevealSection>
            <RevealSection delay={100}>
              <div className="space-y-3" data-testid="pricing-faq">
                {FAQS.map((faq, idx) => (
                  <div
                    key={idx}
                    className="rounded-xl border border-slate-200 bg-white overflow-hidden transition-all duration-300 hover:border-slate-300"
                  >
                    <button
                      className="w-full flex items-center justify-between p-5 text-left"
                      onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                      data-testid={`faq-${idx}`}
                    >
                      <span className="text-sm font-semibold text-slate-900 pr-4">{faq.q}</span>
                      <ChevronDown className={`h-4 w-4 text-slate-400 shrink-0 transition-transform duration-300 ${openFaq === idx ? 'rotate-180' : ''}`} />
                    </button>
                    <div className={`overflow-hidden transition-all duration-300 ${openFaq === idx ? 'max-h-48 pb-5' : 'max-h-0'}`}>
                      <p className="text-sm text-slate-500 leading-relaxed px-5">{faq.a}</p>
                    </div>
                  </div>
                ))}
              </div>
            </RevealSection>
          </div>
        </section>

        {/* ═══ FINAL CTA ═══ */}
        <RevealSection>
          <section className="py-16 lg:py-20">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
              <div className="relative rounded-2xl bg-slate-900 overflow-hidden">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,102,241,0.15),transparent_60%)]" />
                <div className="relative p-10 sm:p-16 text-center">
                  <h2 className="font-manrope text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight max-w-2xl mx-auto">
                    Find your next winning product today
                  </h2>
                  <p className="mt-5 text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
                    Join UK ecommerce sellers who use data — not guesswork — to choose what to sell next.
                  </p>
                  <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Link to="/signup">
                      <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-12 font-semibold rounded-xl shadow-lg" data-testid="pricing-final-cta">
                        Start Free <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                    <Link to="/trending-products">
                      <Button variant="ghost" size="lg" className="text-base px-8 h-12 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl">
                        Browse Products First
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </RevealSection>
      </div>
    </LandingLayout>
  );
}
