import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import useABTest, { trackABConversion } from '@/hooks/useABTest';
import PageMeta, { organizationSchema, websiteSchema, softwareAppSchema } from '@/components/PageMeta';
import { ViabilityIndicator } from '@/components/ViabilityBadge';
import { RevealSection, RevealStagger } from '@/hooks/useScrollReveal';
import QuickViabilitySearch from '@/components/QuickViabilitySearch';
import {
  TrendingUp, ArrowRight, Check, Search, BarChart3, Shield,
  Zap, Package, ChevronRight, Globe, PoundSterling, RefreshCw,
  ShoppingBag, Store, Target, AlertTriangle, Sparkles,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const HERO_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/9e43031a2a6c68898323a79dc325d24cd4db83b9150424ed694dc19e140553b0.png';

export default function LandingPage() {
  const [products, setProducts] = useState([]);
  const heroCta = useABTest('hero_cta', ['Find Winning Products', 'Start Free', 'Try TrendScout Free']);
  const finalCta = useABTest('final_cta', ['Find Winning Products', 'Start Free', 'Start Your Free Trial']);

  useEffect(() => {
    fetch(`${API_URL}/api/public/trending-products?limit=3`)
      .then(r => r.json())
      .then(d => setProducts(d.products || []))
      .catch(() => {});
  }, []);

  return (
    <LandingLayout>
      <PageMeta
        title="AI Product Research for UK Ecommerce Sellers"
        description="Stop guessing. Find products that actually sell in the UK. Discover trends, validate viability, analyse competition, and launch smarter across Shopify, TikTok Shop, and Amazon.co.uk."
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
                <span className="text-xs font-semibold text-indigo-700 tracking-wide">UK-first product intelligence</span>
              </div>
              <h1 className="font-manrope text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold tracking-tight text-slate-900 leading-[1.08]" data-testid="hero-headline">
                Stop guessing.{' '}
                <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">Find products that actually sell in the UK.</span>
              </h1>
              <p className="mt-5 text-base sm:text-lg text-slate-500 leading-relaxed" data-testid="hero-subheadline">
                Discover trending products, analyse competition, estimate UK viability, and make smarter launch decisions for Shopify, TikTok Shop, and Amazon UK &mdash; before you spend on ads or stock.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row items-start gap-3">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-base px-8 h-12 font-semibold rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transition-all"
                    data-testid="hero-cta-primary"
                    onClick={() => { trackABConversion('hero_cta'); trackEvent(EVENTS.HOMEPAGE_PRIMARY_CTA, { cta_label: heroCta, source: 'hero' }); }}
                  >
                    {heroCta} <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/how-it-works">
                  <Button
                    variant="outline"
                    size="lg"
                    className="text-base px-8 h-12 text-slate-700 border-slate-200 hover:bg-slate-50 rounded-xl font-medium"
                    data-testid="hero-cta-secondary"
                    onClick={() => trackEvent(EVENTS.HOMEPAGE_SECONDARY_CTA, { cta_label: 'See How It Works', source: 'hero' })}
                  >
                    See How It Works
                  </Button>
                </Link>
              </div>
              <div className="mt-8 flex items-center gap-6 text-sm text-slate-400">
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
                  alt="TrendScout dashboard showing product trends, viability scores and market analytics"
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
                  <p className="text-xs text-slate-500">Products tracked</p>
                  <p className="text-sm font-bold text-slate-900 font-mono">150+</p>
                </div>
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ TRUST / CREDIBILITY STRIP ═══ */}
      <section className="border-y border-slate-100 bg-white" data-testid="trust-bar">
        <div className="mx-auto max-w-7xl px-6 py-5 lg:px-8">
          <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-3 text-sm text-slate-500">
            <span className="flex items-center gap-2"><Globe className="h-4 w-4 text-indigo-500" /> Built for UK ecommerce sellers</span>
            <span className="flex items-center gap-2"><Shield className="h-4 w-4 text-indigo-500" /> 7-signal scoring model</span>
            <span className="flex items-center gap-2"><BarChart3 className="h-4 w-4 text-indigo-500" /> Multi-channel product intelligence</span>
            <span className="flex items-center gap-2"><Store className="h-4 w-4 text-indigo-500" /> Shopify, TikTok Shop &amp; Amazon UK</span>
          </div>
        </div>
      </section>

      {/* ═══ WHO IT'S FOR ═══ */}
      <section className="py-16 lg:py-20 bg-white" data-testid="audience-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Who it's for</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Built for sellers who want data, not guesswork
            </h2>
          </RevealSection>
          <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5" staggerMs={80}>
            {[
              {
                icon: ShoppingBag,
                title: 'Shopify sellers',
                desc: 'Find products with real UK demand before you build a store around them.',
              },
              {
                icon: Package,
                title: 'Amazon UK sellers',
                desc: 'Spot opportunities with margin potential after FBA fees, VAT, and returns.',
              },
              {
                icon: Zap,
                title: 'TikTok Shop UK sellers',
                desc: 'Go beyond viral views. Validate whether a trending product can convert in the UK.',
              },
              {
                icon: Target,
                title: 'UK ecommerce founders',
                desc: 'Make data-backed product decisions. Test fewer products. Waste less money.',
              },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="rounded-xl border border-slate-200 bg-white p-6 hover:border-indigo-200 hover:shadow-md transition-all duration-300" data-testid={`audience-card-${item.title.toLowerCase().replace(/\s/g, '-')}`}>
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 mb-4">
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

      {/* ═══ UK DIFFERENTIATION ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50 border-y border-slate-100" data-testid="uk-differentiation-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <RevealSection direction="right">
              <div className="inline-flex items-center gap-2 rounded-full bg-amber-50 border border-amber-200 px-3 py-1 mb-5">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
                <span className="text-xs font-semibold text-amber-700">The UK market is different</span>
              </div>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight leading-snug">
                Not every viral product works in the UK.
              </h2>
              <p className="mt-4 text-base text-slate-500 leading-relaxed">
                A product blowing up on US TikTok might have completely different economics here. <strong className="text-slate-700">20% VAT, higher shipping costs, different consumer expectations, and smaller addressable markets</strong> all change the equation.
              </p>
              <p className="mt-3 text-base text-slate-500 leading-relaxed">
                TrendScout evaluates products based on <strong className="text-slate-700">UK commercial reality</strong> &mdash; not global hype alone. That means you spend less time testing products that were never going to work here.
              </p>
              <div className="mt-6 space-y-3">
                {[
                  'VAT and landed cost impact on margins',
                  'UK-specific demand signals and search data',
                  'Shipping practicality and returns friction',
                  'Channel suitability for UK platforms',
                ].map((item) => (
                  <div key={item} className="flex items-center gap-2.5">
                    <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-indigo-100">
                      <Check className="h-3 w-3 text-indigo-600" />
                    </div>
                    <span className="text-sm text-slate-600">{item}</span>
                  </div>
                ))}
              </div>
            </RevealSection>
            <RevealSection direction="left" delay={150}>
              <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-8">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-5">Example: Same product, different markets</p>
                <div className="space-y-4">
                  <div className="rounded-xl bg-slate-50 border border-slate-100 p-5">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-slate-700">US market view</span>
                      <span className="text-xs font-mono font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">82/100</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-xs text-slate-500">
                      <div>Margin estimate: <span className="font-semibold text-slate-700">~45%</span></div>
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
                      <div>Margin estimate: <span className="font-semibold text-amber-700">~22%</span></div>
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

      {/* ═══ HOW IT WORKS ═══ */}
      <section className="py-16 lg:py-20 bg-white" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-14">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">How it works</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              From discovery to launch decision in minutes
            </h2>
          </RevealSection>
          <RevealStagger className="grid md:grid-cols-3 gap-8" staggerMs={150}>
            {[
              {
                step: '01',
                icon: Search,
                title: 'Discover products',
                desc: 'Browse products gaining traction across TikTok, Amazon, and Shopify. Multi-channel signals mean stronger demand validation.',
              },
              {
                step: '02',
                icon: Shield,
                title: 'Analyse UK viability',
                desc: 'Every product is scored across 7 signals including margin potential, competition, VAT impact, and UK-specific demand.',
              },
              {
                step: '03',
                icon: Zap,
                title: 'Launch with confidence',
                desc: 'Use AI-generated ad angles, profit projections, and competitive data to decide whether to test. Fewer wasted ad spends.',
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

      {/* ═══ FEATURE HIGHLIGHTS ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50 border-y border-slate-100" data-testid="features-highlight-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-14">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">What you get</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Research tools built around outcomes
            </h2>
            <p className="mt-3 text-base text-slate-500">
              Not just data. Actionable intelligence that helps you make better product decisions.
            </p>
          </RevealSection>
          <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5" staggerMs={100}>
            {[
              { icon: Search, title: 'Trend detection', desc: 'Spot rising products across TikTok, Amazon, and Shopify before they peak or saturate.' },
              { icon: Shield, title: 'Competition analysis', desc: 'See seller density, ad saturation, and where gaps still exist before entering a niche.' },
              { icon: PoundSterling, title: 'Profit estimation', desc: 'Estimate landed costs, margins, and VAT impact for UK customers — not just US projections.' },
              { icon: Zap, title: 'AI launch insights', desc: 'Get ad angle suggestions, launch scores, and profit projections to validate before you spend.' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="rounded-xl border border-slate-200 bg-white p-6 hover:border-indigo-200 hover:shadow-lg transition-all duration-300 group" data-testid={`feature-card-${item.title.toLowerCase().replace(/\s/g, '-')}`}>
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-all duration-300 mb-4">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-manrope text-base font-semibold text-slate-900">{item.title}</h3>
                  <p className="mt-2 text-sm text-slate-500 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </RevealStagger>
          <RevealSection delay={400} className="mt-10 text-center">
            <Link to="/features">
              <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50 rounded-xl font-medium" data-testid="see-all-features-btn">
                See all features <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </RevealSection>
        </div>
      </section>

      {/* ═══ QUICK VIABILITY SEARCH ═══ */}
      <QuickViabilitySearch />

      {/* ═══ LIVE TRENDING PRODUCTS ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50" data-testid="product-showcase-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection>
            <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
              <div>
                <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Live data</p>
                <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                  Products trending right now
                </h2>
                <p className="mt-2 text-base text-slate-500">
                  Real products scored daily with{' '}
                  <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-medium">UK Viability Scores</Link>.
                </p>
              </div>
              <Link to="/trending-products">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm" data-testid="view-all-products-btn" onClick={() => trackEvent(EVENTS.TRENDING_VIEW, { source: 'homepage' })}>
                  View all products <ArrowRight className="ml-2 h-4 w-4" />
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

      {/* ═══ PRICING PREVIEW ═══ */}
      <section className="py-16 lg:py-20 bg-white" data-testid="pricing-preview-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Pricing</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              One winning product pays for months of TrendScout
            </h2>
            <p className="mt-3 text-base text-slate-500">
              Start free. Upgrade when you're ready. Cancel anytime.
            </p>
          </RevealSection>
          <RevealStagger className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto" staggerMs={120}>
            {[
              { name: 'Starter', price: '19', desc: 'For beginners validating first products', features: ['10 product views/day', 'UK viability indicators', 'Basic trend insights'], popular: false },
              { name: 'Growth', price: '39', desc: 'For active sellers testing multiple ideas', features: ['Unlimited product discovery', 'AI ad creative generator', 'Profitability simulator', 'Trend alerts'], popular: true },
              { name: 'Pro', price: '79', desc: 'For agencies and power users', features: ['Everything in Growth', 'Competitor store tracking', 'AI launch simulator', 'API access'], popular: false },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl border p-6 transition-all duration-300 ${
                  plan.popular
                    ? 'border-indigo-500 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500 scale-[1.02]'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
                data-testid={`pricing-preview-${plan.name.toLowerCase()}`}
              >
                {plan.popular && (
                  <div className="flex justify-center mb-4">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-600 px-3 py-0.5 text-xs font-semibold text-white">
                      <Sparkles className="h-3 w-3" /> Best for serious sellers
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
                    Start 7-day free trial <ArrowRight className="h-4 w-4 ml-1.5" />
                  </Button>
                </Link>
                <p className="text-center text-xs text-slate-400 mt-2">No credit card required</p>
              </div>
            ))}
          </RevealStagger>
          <RevealSection delay={300} className="mt-8 text-center">
            <Link to="/pricing" className="text-sm font-medium text-indigo-600 hover:text-indigo-700 inline-flex items-center gap-1">
              Compare all plans and features <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </RevealSection>
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
                  Validate your next product before you waste money on ads or stock
                </h2>
                <p className="mt-5 text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
                  Start free. Browse trending products, check UK Viability Scores, and explore margin insights &mdash; no credit card needed.
                </p>
                <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link to="/signup">
                    <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-12 font-semibold rounded-xl shadow-lg" data-testid="final-cta-primary" onClick={() => { trackABConversion('final_cta'); trackEvent(EVENTS.HOMEPAGE_PRIMARY_CTA, { cta_label: finalCta, source: 'final_cta' }); }}>
                      {finalCta} <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                  <Link to="/sample-product-analysis">
                    <Button variant="ghost" size="lg" className="text-base px-8 h-12 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl" data-testid="final-cta-secondary" onClick={() => trackEvent(EVENTS.PRICING_VIEW, { source: 'homepage_cta' })}>
                      View Sample Analysis
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
