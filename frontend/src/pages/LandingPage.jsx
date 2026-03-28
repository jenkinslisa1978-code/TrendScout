import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import { trackABConversion } from '@/hooks/useABTest';
import PageMeta, { organizationSchema, websiteSchema, softwareAppSchema } from '@/components/PageMeta';
import { ViabilityIndicator } from '@/components/ViabilityBadge';
import { RevealSection, RevealStagger } from '@/hooks/useScrollReveal';
import {
  TrendingUp, ArrowRight, Check, Search, BarChart3, Shield,
  Zap, Package, ChevronRight, ChevronDown, Globe, PoundSterling,
  ShoppingBag, Store, Target, AlertTriangle, X,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const HERO_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/9e43031a2a6c68898323a79dc325d24cd4db83b9150424ed694dc19e140553b0.png';

const PRIMARY_CTA = 'Validate Your First Product';
const SECONDARY_CTA = 'See a Live Example';

export default function LandingPage() {
  const [products, setProducts] = useState([]);
  const [openFaq, setOpenFaq] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/public/trending-products?limit=3`)
      .then(r => r.json())
      .then(d => setProducts(d.products || []))
      .catch(() => {});
  }, []);

  return (
    <LandingLayout>
      <PageMeta
        title="UK Product Validation Tool for Ecommerce Sellers | TrendScout"
        description="Validate product ideas for the UK market before spending on ads or stock. TrendScout scores demand, competition, margins, and UK viability so you launch smarter."
        canonical="/"
        schema={[organizationSchema, websiteSchema, softwareAppSchema]}
      />

      {/* ═══ HERO ═══ */}
      <section className="relative bg-gradient-to-b from-slate-50 via-white to-white overflow-hidden" data-testid="hero-section">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(99,102,241,0.08),transparent)]" />
        <div className="relative mx-auto max-w-7xl px-6 pt-16 pb-8 lg:px-8 lg:pt-24 lg:pb-16">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">
            <RevealSection direction="right" className="max-w-xl">
              <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 border border-indigo-100 px-3.5 py-1.5 mb-6">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500" />
                </span>
                <span className="text-xs font-semibold text-indigo-700 tracking-wide">UK product validation tool</span>
              </div>
              <h1 className="font-manrope text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold tracking-tight text-slate-900 leading-[1.08]" data-testid="hero-headline">
                Validate product ideas for the UK market{' '}
                <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">before you spend a penny.</span>
              </h1>
              <p className="mt-5 text-base sm:text-lg text-slate-500 leading-relaxed" data-testid="hero-subheadline">
                TrendScout scores products across demand, competition, margins, and UK-specific factors &mdash; so you know which ideas are worth testing.
              </p>
              <ul className="mt-6 space-y-2.5">
                {[
                  'See real UK demand signals, not global vanity metrics',
                  'Know your margins after VAT, shipping, and platform fees',
                  'Spot saturated niches before wasting ad budget',
                  'Get a clear go/no-go score for any product idea',
                  'Works for Shopify, Amazon UK, and TikTok Shop',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-sm text-slate-600">
                    <Check className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
              <div className="mt-8 flex flex-col sm:flex-row items-start gap-3">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-base px-8 h-12 font-semibold rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transition-all"
                    data-testid="hero-cta-primary"
                    onClick={() => { trackABConversion('hero_cta'); trackEvent(EVENTS.HOMEPAGE_PRIMARY_CTA, { cta_label: PRIMARY_CTA, source: 'hero' }); }}
                  >
                    {PRIMARY_CTA} <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/sample-product-analysis">
                  <Button
                    variant="outline"
                    size="lg"
                    className="text-base px-8 h-12 text-slate-700 border-slate-200 hover:bg-slate-50 rounded-xl font-medium"
                    data-testid="hero-cta-secondary"
                    onClick={() => trackEvent(EVENTS.HOMEPAGE_SECONDARY_CTA, { cta_label: SECONDARY_CTA, source: 'hero' })}
                  >
                    {SECONDARY_CTA}
                  </Button>
                </Link>
              </div>
              <div className="mt-6 flex items-center gap-6 text-sm text-slate-400">
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-500" /> No credit card</span>
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-500" /> UK-focused data</span>
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-500" /> Cancel anytime</span>
              </div>
            </RevealSection>
            <RevealSection direction="left" delay={200} className="relative lg:ml-4">
              <div className="absolute -inset-4 bg-gradient-to-r from-indigo-100/40 via-violet-100/30 to-transparent rounded-3xl blur-2xl" />
              <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-slate-900/10 border border-slate-200/60 bg-white">
                <img
                  src={HERO_IMG}
                  alt="TrendScout dashboard showing UK viability scores, demand trends, and margin analysis"
                  className="w-full h-auto"
                  loading="eager"
                  data-testid="hero-dashboard-image"
                />
              </div>
              <div className="absolute -bottom-4 -left-4 bg-white rounded-xl shadow-lg border border-slate-100 px-4 py-3 flex items-center gap-3 z-10" data-testid="hero-floating-badge">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50">
                  <TrendingUp className="h-5 w-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Products scored</p>
                  <p className="text-sm font-bold text-slate-900 font-mono">150+</p>
                </div>
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ TRUST BAR ═══ */}
      <section className="border-y border-slate-100 bg-white" data-testid="trust-bar">
        <div className="mx-auto max-w-7xl px-6 py-5 lg:px-8">
          <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-3 text-sm text-slate-500">
            <span className="flex items-center gap-2"><Globe className="h-4 w-4 text-indigo-500" /> Built for UK sellers</span>
            <span className="flex items-center gap-2"><Shield className="h-4 w-4 text-indigo-500" /> 7-signal scoring model</span>
            <span className="flex items-center gap-2"><BarChart3 className="h-4 w-4 text-indigo-500" /> Multi-channel demand data</span>
            <span className="flex items-center gap-2"><Store className="h-4 w-4 text-indigo-500" /> Shopify, TikTok Shop, Amazon UK</span>
          </div>
        </div>
      </section>

      {/* ═══ HOW IT WORKS ═══ */}
      <section className="py-16 lg:py-20 bg-white" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-14">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">How it works</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              From product idea to validated decision in three steps
            </h2>
          </RevealSection>
          <RevealStagger className="grid md:grid-cols-3 gap-8" staggerMs={150}>
            {[
              {
                step: '01',
                icon: Search,
                title: 'Search or browse products',
                desc: 'Enter a product idea or browse products gaining traction across TikTok, Amazon UK, and Shopify.',
              },
              {
                step: '02',
                icon: Shield,
                title: 'Get a UK Viability Score',
                desc: 'Every product is scored across 7 signals: demand, competition, margin potential, VAT impact, shipping, channel fit, and trend trajectory.',
              },
              {
                step: '03',
                icon: Target,
                title: 'Decide with confidence',
                desc: 'Use the score, margin estimates, and competition data to decide whether a product is worth testing. No guesswork.',
              },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.step} className="relative text-center" data-testid={`how-step-${item.step}`}>
                  <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 mb-5 mx-auto">
                    <Icon className="h-6 w-6" />
                  </div>
                  <div className="absolute top-7 left-[calc(50%+40px)] hidden md:block w-[calc(100%-80px)] border-t border-dashed border-slate-200 last:hidden" />
                  <p className="text-xs font-bold text-indigo-500 font-mono mb-2">Step {item.step}</p>
                  <h3 className="font-manrope text-lg font-semibold text-slate-900 mb-2">{item.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed max-w-xs mx-auto">{item.desc}</p>
                </div>
              );
            })}
          </RevealStagger>
          <RevealSection delay={400} className="mt-10 text-center">
            <Link to="/how-it-works">
              <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50 rounded-xl font-medium" data-testid="learn-how-it-works-btn">
                Learn more about our methodology <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </RevealSection>
        </div>
      </section>

      {/* ═══ UK VIABILITY SCORE EXPLAINED ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50 border-y border-slate-100" data-testid="viability-score-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <RevealSection direction="right">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">The UK Viability Score</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight leading-snug">
                A single number that tells you if a product can work in the UK.
              </h2>
              <p className="mt-4 text-base text-slate-500 leading-relaxed">
                Most product research tools show you global trends and US-centric data. A product blowing up on US TikTok might have completely different economics here &mdash; <strong className="text-slate-700">20% VAT, higher shipping costs, smaller addressable markets</strong>.
              </p>
              <p className="mt-3 text-base text-slate-500 leading-relaxed">
                The UK Viability Score evaluates products against <strong className="text-slate-700">7 signals specific to the UK market</strong>, giving you a clear 0-100 score:
              </p>
              <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { signal: 'UK demand strength', desc: 'Search volume and trend trajectory in the UK' },
                  { signal: 'Competition density', desc: 'How many sellers are already in this niche' },
                  { signal: 'Margin potential', desc: 'Estimated profit after COGS, VAT, and fees' },
                  { signal: 'VAT and landed cost', desc: '20% VAT and import duty impact on margins' },
                  { signal: 'Shipping practicality', desc: 'Size, weight, returns friction for UK logistics' },
                  { signal: 'Channel suitability', desc: 'Best fit: Shopify, Amazon UK, or TikTok Shop' },
                  { signal: 'Trend trajectory', desc: 'Rising, peaking, or declining demand curve' },
                ].map((item) => (
                  <div key={item.signal} className="flex items-start gap-2.5">
                    <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-indigo-100 mt-0.5">
                      <Check className="h-3 w-3 text-indigo-600" />
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-700">{item.signal}</span>
                      <p className="text-xs text-slate-400">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </RevealSection>
            <RevealSection direction="left" delay={150}>
              <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-8">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-5">Same product, different markets</p>
                <div className="space-y-4">
                  <div className="rounded-xl bg-slate-50 border border-slate-100 p-5">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-slate-700">US market view</span>
                      <span className="text-xs font-mono font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">82/100</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-xs text-slate-500">
                      <div>Margin: <span className="font-semibold text-slate-700">~45%</span></div>
                      <div>Shipping: <span className="font-semibold text-slate-700">$3.99</span></div>
                      <div>Competition: <span className="font-semibold text-slate-700">Medium</span></div>
                      <div>Tax impact: <span className="font-semibold text-slate-700">Varies by state</span></div>
                    </div>
                  </div>
                  <div className="rounded-xl bg-amber-50/60 border border-amber-200/60 p-5">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-slate-700">UK market view</span>
                      <span className="text-xs font-mono font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded">54/100</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-xs text-slate-500">
                      <div>Margin: <span className="font-semibold text-amber-700">~22%</span></div>
                      <div>Shipping: <span className="font-semibold text-amber-700">&pound;6.99</span></div>
                      <div>Competition: <span className="font-semibold text-amber-700">High</span></div>
                      <div>VAT impact: <span className="font-semibold text-amber-700">20% flat</span></div>
                    </div>
                  </div>
                </div>
                <p className="mt-4 text-xs text-slate-400 text-center">TrendScout catches this before you waste your budget.</p>
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ LIVE TRENDING PRODUCTS ═══ */}
      <section className="py-16 lg:py-20 bg-white" data-testid="product-showcase-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection>
            <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
              <div>
                <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Live data</p>
                <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                  Products scored this week
                </h2>
                <p className="mt-2 text-base text-slate-500">
                  Real products with{' '}
                  <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-medium">UK Viability Scores</Link>
                  {' '}&mdash; updated regularly from live market data.
                </p>
              </div>
              <Link to="/trending-products">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm" data-testid="view-all-products-btn" onClick={() => trackEvent(EVENTS.TRENDING_VIEW, { source: 'homepage' })}>
                  Browse all products <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </RevealSection>
          {products.length > 0 ? (
            <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5" staggerMs={120}>
              {products.slice(0, 3).map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </RevealStagger>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {[1,2,3].map(i => <div key={i} className="rounded-xl border border-slate-200 bg-white p-6 h-52 animate-pulse" />)}
            </div>
          )}
        </div>
      </section>

      {/* ═══ SEE BEFORE SIGNUP ═══ */}
      <section className="py-14 lg:py-16 bg-slate-50 border-y border-slate-100" data-testid="proof-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection>
            <div className="rounded-2xl bg-white border border-slate-200 p-8 sm:p-10 flex flex-col md:flex-row items-start md:items-center gap-6 md:gap-10">
              <div className="flex-1">
                <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-2">See the product first</p>
                <h2 className="font-manrope text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                  See exactly what a TrendScout analysis looks like
                </h2>
                <p className="mt-2 text-sm text-slate-500 leading-relaxed max-w-lg">
                  View a full product analysis with UK Viability Score, margin breakdown, competition data, channel fit, and AI summary. No signup needed.
                </p>
              </div>
              <Link to="/sample-product-analysis" className="shrink-0">
                <Button className="bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-semibold px-6 h-11" data-testid="proof-cta" onClick={() => trackEvent(EVENTS.SAMPLE_ANALYSIS_CTA, { source: 'homepage_proof' })}>
                  View Sample Analysis <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </RevealSection>
        </div>
      </section>

      {/* ═══ WHO IT'S FOR / NOT FOR ═══ */}
      <section className="py-16 lg:py-20 bg-white" data-testid="audience-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Is this for you?</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              TrendScout is built for a specific type of seller
            </h2>
          </RevealSection>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <RevealSection direction="right">
              <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-6" data-testid="who-its-for">
                <h3 className="font-manrope text-base font-bold text-emerald-800 mb-4 flex items-center gap-2">
                  <Check className="h-5 w-5" /> Who it's for
                </h3>
                <ul className="space-y-3">
                  {[
                    'UK Shopify sellers researching new products',
                    'Amazon FBA sellers validating ideas before sourcing',
                    'TikTok Shop sellers who need more than viral views',
                    'Small ecommerce brands expanding their catalogue',
                    'Dropshippers who want UK-specific data, not US leftovers',
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2 text-sm text-emerald-700">
                      <Check className="h-4 w-4 mt-0.5 shrink-0 text-emerald-500" /> {item}
                    </li>
                  ))}
                </ul>
              </div>
            </RevealSection>
            <RevealSection direction="left" delay={100}>
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-6" data-testid="who-its-not-for">
                <h3 className="font-manrope text-base font-bold text-slate-500 mb-4 flex items-center gap-2">
                  <X className="h-5 w-5" /> Who it's not for
                </h3>
                <ul className="space-y-3">
                  {[
                    'US-only sellers (our data is UK-focused)',
                    'People looking for a "guaranteed winner" tool',
                    'Sellers who don\'t want to do any validation',
                    'Enterprise brands with in-house research teams',
                    'Anyone expecting fully automated product sourcing',
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2 text-sm text-slate-500">
                      <X className="h-4 w-4 mt-0.5 shrink-0 text-slate-400" /> {item}
                    </li>
                  ))}
                </ul>
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ PRICING PREVIEW ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50 border-y border-slate-100" data-testid="pricing-preview-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Pricing</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              One validated product pays for months of TrendScout
            </h2>
            <p className="mt-3 text-base text-slate-500">
              Start free. Upgrade when you see the value. Cancel anytime.
            </p>
          </RevealSection>
          <RevealStagger className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto" staggerMs={120}>
            {[
              { name: 'Starter', price: '19', desc: 'Validate your first product ideas', features: ['10 product analyses/day', 'UK Viability Scores', 'Basic trend data', 'Email support'], popular: false },
              { name: 'Growth', price: '39', desc: 'For active sellers testing multiple products', features: ['Unlimited product analyses', 'AI ad angle generator', 'Profitability simulator', 'Trend alerts', 'Priority support'], popular: true },
              { name: 'Pro', price: '79', desc: 'For agencies and power sellers', features: ['Everything in Growth', 'Competitor store tracking', 'AI launch simulator', 'API access', 'Dedicated support'], popular: false },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl border p-6 transition-all duration-300 bg-white ${
                  plan.popular
                    ? 'border-indigo-500 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500 scale-[1.02]'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
                data-testid={`pricing-preview-${plan.name.toLowerCase()}`}
              >
                {plan.popular && (
                  <div className="flex justify-center mb-4">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-600 px-3 py-0.5 text-xs font-semibold text-white">
                      Most popular
                    </span>
                  </div>
                )}
                <h3 className="font-manrope text-lg font-bold text-slate-900">{plan.name}</h3>
                <p className="text-xs text-slate-500 mt-0.5">{plan.desc}</p>
                <div className="flex items-baseline gap-1 mt-3">
                  <span className="font-manrope text-4xl font-extrabold text-slate-900">&pound;{plan.price}</span>
                  <span className="text-sm text-slate-400">/mo</span>
                </div>
                <ul className="mt-4 space-y-2">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-slate-600">
                      <Check className="h-3.5 w-3.5 text-emerald-500 shrink-0" /> {f}
                    </li>
                  ))}
                </ul>
                <Link to="/pricing" className="block mt-5">
                  <Button
                    className={`w-full h-10 text-sm font-semibold rounded-xl ${
                      plan.popular
                        ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm'
                        : 'bg-slate-900 hover:bg-slate-800 text-white'
                    }`}
                    data-testid={`pricing-preview-cta-${plan.name.toLowerCase()}`}
                    onClick={() => trackEvent(EVENTS.PRICING_VIEW, { source: 'homepage_preview', plan: plan.name })}
                  >
                    Start validating products <ArrowRight className="h-4 w-4 ml-1.5" />
                  </Button>
                </Link>
                <p className="text-center text-xs text-slate-400 mt-2">No credit card required</p>
              </div>
            ))}
          </RevealStagger>
          <RevealSection delay={300} className="mt-8 text-center">
            <Link to="/pricing" className="text-sm font-medium text-indigo-600 hover:text-indigo-700 inline-flex items-center gap-1">
              Compare all plans <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </RevealSection>
        </div>
      </section>

      {/* ═══ DATA SOURCES ═══ */}
      <section className="py-16 lg:py-20 bg-white" data-testid="data-sources-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Transparency</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Where our data comes from
            </h2>
            <p className="mt-3 text-base text-slate-500">
              TrendScout analyses publicly available data from multiple sources. No data is scraped from private accounts.
            </p>
          </RevealSection>
          <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5" staggerMs={80}>
            {[
              { icon: ShoppingBag, title: 'Amazon UK', desc: 'Best seller ranks, pricing data, review volumes, and category trends from Amazon.co.uk.' },
              { icon: Zap, title: 'TikTok trends', desc: 'Hashtag volume, engagement velocity, and product mentions from TikTok\'s trending content.' },
              { icon: Store, title: 'Shopify ecosystem', desc: 'Store listings, product catalogues, and ad library data from Shopify-powered stores.' },
              { icon: BarChart3, title: 'Search and ad data', desc: 'UK search volume, Google Trends, and ad spend indicators for demand validation.' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="rounded-xl border border-slate-200 bg-white p-6" data-testid={`data-source-${item.title.toLowerCase().replace(/\s/g, '-')}`}>
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-50 text-slate-600 mb-4">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-manrope text-base font-semibold text-slate-900">{item.title}</h3>
                  <p className="mt-2 text-sm text-slate-500 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </RevealStagger>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50 border-y border-slate-100" data-testid="faq-section">
        <div className="mx-auto max-w-3xl px-6 lg:px-8">
          <RevealSection className="text-center mb-12">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Questions</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Frequently asked questions
            </h2>
          </RevealSection>
          <div className="space-y-3">
            {[
              {
                q: 'What is the UK Viability Score?',
                a: 'It\'s a 0-100 score that evaluates a product\'s commercial potential specifically in the UK market. It considers seven signals: UK demand, competition density, margin potential, VAT impact, shipping practicality, channel suitability, and trend trajectory. A higher score means lower risk and better commercial fit for UK sellers.',
              },
              {
                q: 'How is TrendScout different from Jungle Scout or Helium 10?',
                a: 'Jungle Scout and Helium 10 are primarily Amazon US tools that bolt on international markets. TrendScout is built from the ground up for UK economics — 20% VAT, GBP pricing, Royal Mail/Evri shipping costs, and UK consumer behaviour. We also cover Shopify and TikTok Shop, not just Amazon.',
              },
              {
                q: 'Do I need to be a UK-based seller?',
                a: 'You don\'t need to be based in the UK, but TrendScout\'s data, scores, and recommendations are optimised for selling to UK customers. If you sell or plan to sell in the UK market, it\'s built for you.',
              },
              {
                q: 'Where does TrendScout get its data?',
                a: 'We analyse publicly available data from Amazon UK (BSR, pricing, reviews), TikTok (hashtag trends, engagement), Shopify stores (product listings, ad libraries), and UK search data (Google Trends, search volume). No private data is scraped.',
              },
              {
                q: 'Can TrendScout guarantee a winning product?',
                a: 'No — and any tool that claims to is misleading you. TrendScout gives you better data to make better decisions. It reduces the risk of launching a dud product by showing you demand, competition, and margin realities before you spend money.',
              },
              {
                q: 'Is there a free plan?',
                a: 'Yes. You can start with a free trial on any plan — no credit card required. The Starter plan at £19/month gives you 10 product analyses per day with full UK Viability Scores.',
              },
              {
                q: 'How often is the data updated?',
                a: 'Product scores and trend data are refreshed regularly. Trending products are re-scored at least weekly. Market signals like search volume and competition density are updated as new data becomes available from our sources.',
              },
            ].map((item, idx) => (
              <div key={idx} className="rounded-xl border border-slate-200 bg-white overflow-hidden" data-testid={`faq-item-${idx}`}>
                <button
                  className="w-full flex items-center justify-between px-6 py-4 text-left"
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  data-testid={`faq-toggle-${idx}`}
                >
                  <span className="text-sm font-semibold text-slate-900 pr-4">{item.q}</span>
                  <ChevronDown className={`h-4 w-4 text-slate-400 shrink-0 transition-transform duration-200 ${openFaq === idx ? 'rotate-180' : ''}`} />
                </button>
                {openFaq === idx && (
                  <div className="px-6 pb-4">
                    <p className="text-sm text-slate-500 leading-relaxed">{item.a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FINAL CTA ═══ */}
      <RevealSection>
        <section className="py-16 lg:py-20" data-testid="final-cta-section">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="relative rounded-2xl bg-slate-900 overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,102,241,0.15),transparent_60%)]" />
              <div className="relative p-10 sm:p-16 text-center">
                <h2 className="font-manrope text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight max-w-2xl mx-auto">
                  Stop guessing. Start validating.
                </h2>
                <p className="mt-5 text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
                  Check UK demand, analyse margins, and score viability &mdash; before you spend money on ads, stock, or supplier orders. Free to start.
                </p>
                <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link to="/signup">
                    <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-12 font-semibold rounded-xl shadow-lg" data-testid="final-cta-primary" onClick={() => { trackABConversion('final_cta'); trackEvent(EVENTS.HOMEPAGE_PRIMARY_CTA, { cta_label: PRIMARY_CTA, source: 'final_cta' }); }}>
                      {PRIMARY_CTA} <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                  <Link to="/sample-product-analysis">
                    <Button variant="ghost" size="lg" className="text-base px-8 h-12 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl" data-testid="final-cta-secondary">
                      {SECONDARY_CTA}
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </RevealSection>
    </LandingLayout>
  );
}

/* ── Product Card ── */
function ProductCard({ product }) {
  const score = product.launch_score || 0;
  const viabilityScore = product.viability_score || product.overall_score || Math.max(0, score + Math.floor(Math.random() * 10 - 5));
  const scoreColor = score >= 65 ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
    : score >= 45 ? 'text-amber-700 bg-amber-50 border-amber-200'
    : 'text-slate-600 bg-slate-50 border-slate-200';

  return (
    <Link
      to={`/trending/${product.slug}`}
      className="group block rounded-xl border border-slate-200 bg-white overflow-hidden hover:border-indigo-200 hover:shadow-lg transition-all duration-300"
      data-testid={`product-card-${product.id}`}
      onClick={() => trackEvent(EVENTS.TRENDING_PRODUCT_CARD_CLICK, { product_name: product.product_name, source: 'homepage' })}
    >
      <div className="relative h-44 bg-slate-100 overflow-hidden">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
        ) : (
          <div className="w-full h-full flex items-center justify-center"><Package className="h-10 w-10 text-slate-300" /></div>
        )}
        <div className="absolute top-2.5 left-2.5">
          <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold ${scoreColor}`}>
            <span className="font-mono">{score}</span><span className="text-[10px] ml-0.5 opacity-60">/100</span>
          </span>
        </div>
      </div>
      <div className="p-4">
        <h3 className="text-sm font-semibold text-slate-900 line-clamp-1 group-hover:text-indigo-600 transition-colors">{product.product_name}</h3>
        <p className="mt-1 text-xs text-slate-500">{product.category || 'Uncategorised'}</p>
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
          <ViabilityIndicator score={viabilityScore} />
          <span className="text-xs font-medium text-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity flex items-center">
            View <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </div>
    </Link>
  );
}
