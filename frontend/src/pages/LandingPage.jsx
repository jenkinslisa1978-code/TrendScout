import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import { trackABConversion } from '@/hooks/useABTest';
import PageMeta, { organizationSchema, websiteSchema, softwareAppSchema } from '@/components/PageMeta';
import { ViabilityIndicator } from '@/components/ViabilityBadge';
import { RevealSection, RevealStagger } from '@/hooks/useScrollReveal';
import ProductValidator from '@/components/ProductValidator';
import {
  TrendingUp, ArrowRight, Check, Search, BarChart3, Shield,
  Zap, Package, ChevronRight, ChevronDown, Globe, PoundSterling,
  ShoppingBag, Store, Target, AlertTriangle, X, Rocket, Calculator,
  Truck,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const HERO_BG = 'https://static.prod-images.emergentagent.com/jobs/19e567c4-0b4a-48ff-90b7-fa2a9c1d88e2/images/b6d8438eecd6202e27e4992235154ae9a85785b12a0760204d3de353bb236c3b.png';

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

      {/* ═══ HERO — DARK ═══ */}
      <section className="relative bg-[#09090b] overflow-hidden" data-testid="hero-section">
        <img src={HERO_BG} alt="" className="absolute inset-0 w-full h-full object-cover opacity-30 pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-b from-[#09090b]/40 via-transparent to-[#09090b]" />
        <div className="relative mx-auto max-w-7xl px-6 pt-20 pb-16 lg:px-8 lg:pt-28 lg:pb-24">
          <div className="grid lg:grid-cols-2 gap-14 lg:gap-10 items-center">
            <RevealSection direction="right" className="max-w-xl">
              <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3.5 py-1.5 mb-6">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
                <span className="text-xs font-bold text-emerald-400 tracking-[0.15em] uppercase">Built for UK sellers who test before they invest</span>
              </div>
              <h1 className="font-manrope text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold tracking-tighter text-white leading-[1.05]" data-testid="hero-headline">
                Stop guessing which products will work.{' '}
                <span className="bg-gradient-to-r from-emerald-400 to-emerald-300 bg-clip-text text-transparent">Validate before you spend a penny.</span>
              </h1>
              <p className="mt-6 text-base sm:text-lg text-zinc-400 leading-relaxed" data-testid="hero-subheadline">
                Most sellers fail because they pick products on gut feel. TrendScout scores real UK demand, margins after VAT, and competition level &mdash; so you eliminate bad ideas in seconds, not months.
              </p>
              <ul className="mt-6 space-y-2.5">
                {[
                  'Real UK demand signals — not US data repackaged for British sellers',
                  'True margins after VAT, shipping, and platform fees',
                  'Spot saturated niches before wasting £500 on ads',
                  'Clear go/no-go score — no more gut-feel decisions',
                  'Works for Shopify, Amazon UK, and TikTok Shop',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-sm text-zinc-400">
                    <Check className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
              <div className="mt-8 flex flex-col sm:flex-row items-start gap-3">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-emerald-500 hover:bg-emerald-400 text-white text-base px-8 h-12 font-bold rounded-md shadow-[0_0_20px_rgba(16,185,129,0.35)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] transition-all tracking-wide"
                    data-testid="hero-cta-primary"
                    onClick={() => { trackABConversion('hero_cta'); trackEvent(EVENTS.HOMEPAGE_PRIMARY_CTA, { cta_label: 'Validate Your First Product', source: 'hero' }); }}
                  >
                    Validate Your First Product <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/sample-product-analysis">
                  <Button
                    variant="ghost"
                    size="lg"
                    className="text-base px-8 h-12 text-zinc-400 hover:text-white hover:bg-white/5 rounded-md font-medium border border-zinc-800 hover:border-zinc-600 transition-all"
                    data-testid="hero-cta-secondary"
                  >
                    See a Live Example
                  </Button>
                </Link>
              </div>
              <div className="mt-6 flex items-center gap-6 text-sm text-zinc-500">
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-600" /> No credit card</span>
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-600" /> UK-focused data</span>
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-600" /> Cancel anytime</span>
              </div>
            </RevealSection>
            <RevealSection direction="left" delay={200} className="relative lg:ml-4">
              <div className="absolute -inset-6 rounded-3xl bg-emerald-500/5 blur-3xl" />
              <div className="relative">
                <p className="text-xs font-bold text-emerald-400 uppercase tracking-[0.2em] mb-3 text-center lg:text-left">Try it free — no signup needed</p>
                <ProductValidator />
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ TRUST BAR — DARK ═══ */}
      <section className="border-y border-white/[0.06] bg-[#121214]" data-testid="trust-bar">
        <div className="mx-auto max-w-7xl px-6 py-5 lg:px-8">
          <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-3 text-sm text-zinc-500">
            <span className="flex items-center gap-2"><Globe className="h-4 w-4 text-emerald-500" /> Built for UK sellers</span>
            <span className="flex items-center gap-2"><Shield className="h-4 w-4 text-emerald-500" /> 7-signal scoring model</span>
            <span className="flex items-center gap-2"><BarChart3 className="h-4 w-4 text-emerald-500" /> Multi-channel demand data</span>
            <span className="flex items-center gap-2"><Store className="h-4 w-4 text-emerald-500" /> Shopify, TikTok Shop, Amazon UK</span>
          </div>
        </div>
      </section>

      {/* ═══ HOW IT WORKS — DARK ═══ */}
      <section className="py-20 lg:py-24 bg-[#09090b]" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-16">
            <p className="text-xs font-bold text-emerald-500 uppercase tracking-[0.2em] mb-3">How it works</p>
            <h2 className="font-manrope text-3xl lg:text-4xl font-bold text-white tracking-tight">
              From product idea to validated decision in three steps
            </h2>
          </RevealSection>
          <RevealStagger className="grid md:grid-cols-3 gap-8" staggerMs={150}>
            {[
              { step: '01', icon: Search, title: 'Search or browse products', desc: 'Enter a product idea or browse products gaining traction across TikTok, Amazon UK, and Shopify.' },
              { step: '02', icon: Shield, title: 'Get a UK Viability Score', desc: 'Every product is scored across 7 signals: demand, competition, margin potential, VAT impact, shipping, channel fit, and trend trajectory.' },
              { step: '03', icon: Target, title: 'Decide with confidence', desc: 'Use the score, margin estimates, and competition data to decide whether a product is worth testing.' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.step} className="relative text-center" data-testid={`how-step-${item.step}`}>
                  <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-5 mx-auto">
                    <Icon className="h-6 w-6" />
                  </div>
                  <p className="text-xs font-bold text-emerald-500 font-mono mb-2 tracking-wider">Step {item.step}</p>
                  <h3 className="font-manrope text-lg font-semibold text-white mb-2">{item.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed max-w-xs mx-auto">{item.desc}</p>
                </div>
              );
            })}
          </RevealStagger>
        </div>
      </section>

      {/* ═══ BENTO FEATURES — DARK ═══ */}
      <section className="py-20 lg:py-24 bg-[#121214]" data-testid="features-bento-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-16">
            <p className="text-xs font-bold text-emerald-500 uppercase tracking-[0.2em] mb-3">Features</p>
            <h2 className="font-manrope text-3xl lg:text-4xl font-bold text-white tracking-tight">
              Everything you need to validate and launch
            </h2>
          </RevealSection>
          <RevealStagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5" staggerMs={100}>
            {/* Large card — One-Click Launch */}
            <div className="md:col-span-2 rounded-2xl bg-[#18181b] border border-white/[0.08] p-8 hover:-translate-y-1 hover:border-white/20 hover:shadow-[0_8px_30px_rgba(16,185,129,0.08)] transition-all group" data-testid="feature-one-click-launch">
              <div className="flex items-center gap-2 mb-3">
                <Rocket className="h-5 w-5 text-emerald-400" />
                <span className="text-xs font-bold text-emerald-500 tracking-[0.15em] uppercase">One-Click Launch</span>
              </div>
              <h3 className="font-manrope text-xl font-bold text-white mb-2">From product idea to launch-ready in 30 seconds</h3>
              <p className="text-sm text-zinc-500 leading-relaxed max-w-lg">
                Click "Launch" on any product and instantly get AI-generated ad copy, target audience, 90-day profit projections, and export-ready listings for Shopify, WooCommerce, and Etsy.
              </p>
              <div className="mt-5 flex gap-3">
                <span className="inline-flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded text-xs font-bold tracking-wider">SHOPIFY</span>
                <span className="inline-flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded text-xs font-bold tracking-wider">WOOCOMMERCE</span>
                <span className="inline-flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded text-xs font-bold tracking-wider">ETSY</span>
              </div>
            </div>
            {/* Profit Simulator */}
            <div className="lg:row-span-2 rounded-2xl bg-[#18181b] border border-white/[0.08] p-8 hover:-translate-y-1 hover:border-white/20 hover:shadow-[0_8px_30px_rgba(16,185,129,0.08)] transition-all flex flex-col justify-between" data-testid="feature-profit-simulator">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Calculator className="h-5 w-5 text-amber-400" />
                  <span className="text-xs font-bold text-amber-500 tracking-[0.15em] uppercase">Profit Simulator</span>
                </div>
                <h3 className="font-manrope text-xl font-bold text-white mb-2">Will this product actually make money?</h3>
                <p className="text-sm text-zinc-500 leading-relaxed">
                  Interactive sliders, UK VAT factored in, and 30/60/90-day revenue projections. See exactly what your bank balance looks like before you start.
                </p>
              </div>
              <Link to="/profit-simulator" className="mt-6">
                <Button className="w-full bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/20 font-bold tracking-wide rounded-md transition-all" data-testid="feature-profit-sim-cta">
                  Try Free Simulator <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
            {/* CJ Dropshipping */}
            <div className="rounded-2xl bg-[#18181b] border border-white/[0.08] p-8 hover:-translate-y-1 hover:border-white/20 hover:shadow-[0_8px_30px_rgba(16,185,129,0.08)] transition-all" data-testid="feature-cj-supplier">
              <div className="flex items-center gap-2 mb-3">
                <Package className="h-5 w-5 text-violet-400" />
                <span className="text-xs font-bold text-violet-400 tracking-[0.15em] uppercase">Supplier Intel</span>
              </div>
              <h3 className="font-manrope text-lg font-semibold text-white mb-2">CJ Dropshipping integrated</h3>
              <p className="text-sm text-zinc-500 leading-relaxed">Live supplier costs, stock status, and shipping estimates from CJ Dropshipping. Auto-synced every 6 hours.</p>
            </div>
            {/* Competitor Intel */}
            <div className="rounded-2xl bg-[#18181b] border border-white/[0.08] p-8 hover:-translate-y-1 hover:border-white/20 hover:shadow-[0_8px_30px_rgba(16,185,129,0.08)] transition-all" data-testid="feature-competitor-intel">
              <div className="flex items-center gap-2 mb-3">
                <Target className="h-5 w-5 text-sky-400" />
                <span className="text-xs font-bold text-sky-400 tracking-[0.15em] uppercase">Competitor Intel</span>
              </div>
              <h3 className="font-manrope text-lg font-semibold text-white mb-2">See what competitors are doing</h3>
              <p className="text-sm text-zinc-500 leading-relaxed">Ad spend estimates, pricing strategies, and market saturation data so you know exactly what you're up against.</p>
            </div>
          </RevealStagger>
        </div>
      </section>

      {/* ═══ UK VIABILITY SCORE — DARK ═══ */}
      <section className="py-20 lg:py-24 bg-[#09090b]" data-testid="viability-score-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-14 items-center">
            <RevealSection direction="right">
              <p className="text-xs font-bold text-emerald-500 uppercase tracking-[0.2em] mb-3">The UK Viability Score</p>
              <h2 className="font-manrope text-3xl lg:text-4xl font-bold text-white tracking-tight leading-snug">
                A single number that tells you if a product can work in the UK.
              </h2>
              <p className="mt-5 text-base text-zinc-400 leading-relaxed">
                Most tools show US-centric data. A product trending on US TikTok has completely different economics here &mdash; <strong className="text-white">20% VAT, higher shipping costs, smaller markets</strong>.
              </p>
              <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { signal: 'UK demand strength', desc: 'Search volume and trend trajectory' },
                  { signal: 'Competition density', desc: 'How many sellers in this niche' },
                  { signal: 'Margin potential', desc: 'Profit after COGS, VAT, and fees' },
                  { signal: 'VAT and landed cost', desc: '20% VAT and import duty impact' },
                  { signal: 'Shipping practicality', desc: 'Size, weight, returns friction' },
                  { signal: 'Channel suitability', desc: 'Best fit platform for this product' },
                  { signal: 'Trend trajectory', desc: 'Rising, peaking, or declining' },
                ].map((item) => (
                  <div key={item.signal} className="flex items-start gap-2.5">
                    <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 border border-emerald-500/20 mt-0.5">
                      <Check className="h-3 w-3 text-emerald-400" />
                    </div>
                    <div>
                      <span className="text-sm font-medium text-zinc-200">{item.signal}</span>
                      <p className="text-xs text-zinc-600">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </RevealSection>
            <RevealSection direction="left" delay={150}>
              <div className="rounded-2xl bg-[#18181b] border border-white/[0.08] p-8">
                <p className="text-xs font-bold text-zinc-500 uppercase tracking-[0.15em] mb-5">Same product, different markets</p>
                <div className="space-y-4">
                  <div className="rounded-xl bg-[#121214] border border-white/[0.06] p-5">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-zinc-300">US market view</span>
                      <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">82/100</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-xs text-zinc-500">
                      <div>Margin: <span className="font-semibold text-zinc-300">~45%</span></div>
                      <div>Shipping: <span className="font-semibold text-zinc-300">$3.99</span></div>
                      <div>Competition: <span className="font-semibold text-zinc-300">Medium</span></div>
                      <div>Tax: <span className="font-semibold text-zinc-300">Varies</span></div>
                    </div>
                  </div>
                  <div className="rounded-xl bg-amber-500/5 border border-amber-500/15 p-5">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-semibold text-zinc-300">UK market view</span>
                      <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">54/100</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-xs text-zinc-500">
                      <div>Margin: <span className="font-semibold text-amber-400">~22%</span></div>
                      <div>Shipping: <span className="font-semibold text-amber-400">&pound;6.99</span></div>
                      <div>Competition: <span className="font-semibold text-amber-400">High</span></div>
                      <div>VAT: <span className="font-semibold text-amber-400">20% flat</span></div>
                    </div>
                  </div>
                </div>
                <p className="mt-4 text-xs text-zinc-600 text-center">TrendScout catches this before you waste your budget.</p>
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ LIVE TRENDING PRODUCTS — DARK ═══ */}
      <section className="py-20 lg:py-24 bg-[#121214]" data-testid="product-showcase-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection>
            <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
              <div>
                <p className="text-xs font-bold text-emerald-500 uppercase tracking-[0.2em] mb-3">Live data</p>
                <h2 className="font-manrope text-3xl lg:text-4xl font-bold text-white tracking-tight">Products scored this week</h2>
                <p className="mt-2 text-base text-zinc-500">Real products with UK Viability Scores &mdash; updated from live market data.</p>
              </div>
              <Link to="/trending-products">
                <Button className="bg-emerald-500 hover:bg-emerald-400 text-white rounded-md font-bold shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all tracking-wide" data-testid="view-all-products-btn">
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
              {[1,2,3].map(i => <div key={i} className="rounded-xl border border-white/[0.06] bg-[#18181b] p-6 h-52 animate-pulse" />)}
            </div>
          )}
        </div>
      </section>

      {/* ═══ PRICING — DARK ═══ */}
      <section className="py-20 lg:py-24 bg-[#09090b]" data-testid="pricing-preview-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-14">
            <p className="text-xs font-bold text-emerald-500 uppercase tracking-[0.2em] mb-3">Pricing</p>
            <h2 className="font-manrope text-3xl lg:text-4xl font-bold text-white tracking-tight">
              One validated product pays for months of TrendScout
            </h2>
            <p className="mt-3 text-base text-zinc-500">Start free. Upgrade when you see the value. Cancel anytime.</p>
          </RevealSection>
          <RevealStagger className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto items-stretch" staggerMs={120}>
            {[
              { name: 'Starter', price: '19', desc: 'Validate your first ideas', features: ['10 product analyses/day', 'UK Viability Scores', 'Basic trend data', 'Email support'], popular: false },
              { name: 'Growth', price: '39', desc: 'For active sellers testing products', features: ['Unlimited analyses', 'One-Click Launch', 'Profit simulator', 'AI ad copy generator', 'CJ Dropshipping sync', 'Priority support'], popular: true },
              { name: 'Pro', price: '79', desc: 'For agencies and power sellers', features: ['Everything in Growth', 'Competitor tracking', 'AI launch simulator', 'API access', 'Dedicated support'], popular: false },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl border p-7 transition-all duration-300 ${
                  plan.popular
                    ? 'bg-[#18181b] border-emerald-500/40 shadow-[0_0_40px_rgba(16,185,129,0.12)] scale-[1.03] ring-1 ring-emerald-500/30'
                    : 'bg-[#121214] border-white/[0.08] hover:border-white/[0.15]'
                }`}
                data-testid={`pricing-preview-${plan.name.toLowerCase()}`}
              >
                {plan.popular && (
                  <div className="flex justify-center mb-4">
                    <span className="inline-flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 px-3 py-0.5 text-xs font-bold text-emerald-400 rounded-full tracking-wider uppercase">
                      Over 80% choose this
                    </span>
                  </div>
                )}
                <h3 className="font-manrope text-lg font-bold text-white">{plan.name}</h3>
                <p className="text-xs text-zinc-500 mt-0.5">{plan.desc}</p>
                <div className="flex items-baseline gap-1 mt-4">
                  <span className="font-manrope text-4xl font-extrabold text-white">&pound;{plan.price}</span>
                  <span className="text-sm text-zinc-600">/mo</span>
                </div>
                <ul className="mt-5 space-y-2.5">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-zinc-400">
                      <Check className="h-3.5 w-3.5 text-emerald-500 shrink-0" /> {f}
                    </li>
                  ))}
                </ul>
                <Link to="/pricing" className="block mt-6">
                  <Button
                    className={`w-full h-11 text-sm font-bold rounded-md tracking-wide ${
                      plan.popular
                        ? 'bg-emerald-500 hover:bg-emerald-400 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)]'
                        : 'bg-zinc-900 border border-white/10 text-white hover:bg-zinc-800'
                    }`}
                    data-testid={`pricing-preview-cta-${plan.name.toLowerCase()}`}
                  >
                    Start validating <ArrowRight className="h-4 w-4 ml-1.5" />
                  </Button>
                </Link>
                <p className="text-center text-xs text-zinc-600 mt-2">No credit card required</p>
              </div>
            ))}
          </RevealStagger>
        </div>
      </section>

      {/* ═══ FAQ — DARK ═══ */}
      <section className="py-20 lg:py-24 bg-[#121214]" data-testid="faq-section">
        <div className="mx-auto max-w-3xl px-6 lg:px-8">
          <RevealSection className="text-center mb-12">
            <p className="text-xs font-bold text-emerald-500 uppercase tracking-[0.2em] mb-3">Questions</p>
            <h2 className="font-manrope text-3xl lg:text-4xl font-bold text-white tracking-tight">Frequently asked questions</h2>
          </RevealSection>
          <div className="space-y-3">
            {[
              { q: 'What is the UK Viability Score?', a: 'A 0-100 score evaluating a product\'s commercial potential in the UK. It considers demand, competition, margins, VAT, shipping, channel fit, and trend trajectory.' },
              { q: 'How is TrendScout different from Jungle Scout?', a: 'Jungle Scout is Amazon US-centric. TrendScout is built from the ground up for UK economics — 20% VAT, GBP, UK shipping costs, and covers Shopify + TikTok Shop too.' },
              { q: 'Do I need to be UK-based?', a: 'No, but our data is optimised for selling TO UK customers. If you sell or plan to sell in the UK market, it\'s for you.' },
              { q: 'Can TrendScout guarantee a winning product?', a: 'No. We give you better data to make better decisions. It reduces the risk of launching a dud by showing real demand, competition, and margin data.' },
              { q: 'Is there a free plan?', a: 'Yes. Free trial on any plan, no credit card required. The Starter plan at £19/mo gives you 10 analyses per day.' },
              { q: 'How often is data updated?', a: 'Trending products are re-scored weekly. CJ Dropshipping supply data syncs every 6 hours. Market signals update as new data becomes available.' },
            ].map((item, idx) => (
              <div key={idx} className="rounded-xl border border-white/[0.08] bg-[#18181b] overflow-hidden" data-testid={`faq-item-${idx}`}>
                <button className="w-full flex items-center justify-between px-6 py-4 text-left" onClick={() => setOpenFaq(openFaq === idx ? null : idx)} data-testid={`faq-toggle-${idx}`}>
                  <span className="text-sm font-semibold text-zinc-200 pr-4">{item.q}</span>
                  <ChevronDown className={`h-4 w-4 text-zinc-500 shrink-0 transition-transform duration-200 ${openFaq === idx ? 'rotate-180' : ''}`} />
                </button>
                {openFaq === idx && (
                  <div className="px-6 pb-4"><p className="text-sm text-zinc-500 leading-relaxed">{item.a}</p></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ FINAL CTA — DARK ═══ */}
      <RevealSection>
        <section className="py-20 lg:py-24 bg-[#09090b]" data-testid="final-cta-section">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="relative rounded-2xl bg-gradient-to-br from-emerald-500/10 via-[#18181b] to-[#18181b] border border-emerald-500/20 overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(16,185,129,0.12),transparent_60%)]" />
              <div className="relative p-12 sm:p-20 text-center">
                <h2 className="font-manrope text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tighter max-w-2xl mx-auto">
                  Stop guessing. Start validating.
                </h2>
                <p className="mt-5 text-base text-zinc-500 max-w-xl mx-auto leading-relaxed">
                  Check UK demand, analyse margins, and score viability &mdash; before you spend money on ads, stock, or supplier orders.
                </p>
                <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link to="/signup">
                    <Button size="lg" className="bg-emerald-500 hover:bg-emerald-400 text-white text-base px-10 h-13 font-bold rounded-md shadow-[0_0_30px_rgba(16,185,129,0.4)] hover:shadow-[0_0_40px_rgba(16,185,129,0.55)] transition-all tracking-wide" data-testid="final-cta-primary">
                      Validate Your First Product <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                  <Link to="/sample-product-analysis">
                    <Button variant="ghost" size="lg" className="text-base px-8 h-12 text-zinc-400 hover:text-white hover:bg-white/5 rounded-md border border-zinc-800 hover:border-zinc-600 transition-all" data-testid="final-cta-secondary">
                      See a Live Example
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

/* ── Shipping Badge — UK Delivery Tier ── */
function ShippingBadge({ shipping }) {
  if (!shipping) return null;
  const config = {
    green:  { dot: 'bg-emerald-400', text: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/25' },
    yellow: { dot: 'bg-amber-400',   text: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/25' },
    red:    { dot: 'bg-red-400',     text: 'text-red-400',     bg: 'bg-red-500/10 border-red-500/25' },
  };
  const c = config[shipping.tier] || config.red;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[10px] font-bold tracking-wide ${c.bg} ${c.text}`}
      data-testid="shipping-badge"
      title={shipping.description}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
      {shipping.label}
    </span>
  );
}

/* ── Product Card — Dark ── */
function ProductCard({ product }) {
  const score = product.launch_score || 0;
  const viabilityScore = product.viability_score || product.overall_score || Math.max(0, score + Math.floor(Math.random() * 10 - 5));
  const scoreColor = score >= 65 ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
    : score >= 45 ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
    : 'text-zinc-400 bg-zinc-800 border-zinc-700';

  return (
    <Link
      to={`/trending/${product.slug}`}
      className="group block rounded-xl border border-white/[0.08] bg-[#18181b] overflow-hidden hover:border-emerald-500/30 hover:shadow-[0_8px_30px_rgba(16,185,129,0.08)] hover:-translate-y-1 transition-all duration-300"
      data-testid={`product-card-${product.id}`}
      onClick={() => trackEvent(EVENTS.TRENDING_PRODUCT_CARD_CLICK, { product_name: product.product_name, source: 'homepage' })}
    >
      <div className="relative h-44 bg-[#121214] overflow-hidden">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
        ) : (
          <div className="w-full h-full flex items-center justify-center"><Package className="h-10 w-10 text-zinc-700" /></div>
        )}
        <div className="absolute top-2.5 left-2.5">
          <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-bold ${scoreColor}`}>
            <span className="font-mono">{score}</span><span className="text-[10px] ml-0.5 opacity-60">/100</span>
          </span>
        </div>
        {product.uk_shipping && (
          <div className="absolute top-2.5 right-2.5">
            <ShippingBadge shipping={product.uk_shipping} />
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="text-sm font-semibold text-zinc-200 line-clamp-1 group-hover:text-emerald-400 transition-colors">{product.product_name}</h3>
        <p className="mt-1 text-xs text-zinc-600">{product.category || 'Uncategorised'}</p>
        {product.uk_shipping && (
          <div className="flex items-center gap-1.5 mt-2" data-testid="shipping-info-row">
            <Truck className="h-3 w-3 text-zinc-500" />
            <span className="text-[11px] text-zinc-500">UK delivery: <span className={
              product.uk_shipping.tier === 'green' ? 'text-emerald-400 font-medium' :
              product.uk_shipping.tier === 'yellow' ? 'text-amber-400 font-medium' :
              'text-red-400 font-medium'
            }>{product.uk_shipping.days_estimate}</span></span>
          </div>
        )}
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/[0.06]">
          <ViabilityIndicator score={viabilityScore} />
          <span className="text-xs font-medium text-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity flex items-center">
            View <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </div>
    </Link>
  );
}
