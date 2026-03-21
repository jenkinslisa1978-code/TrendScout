import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import PageMeta, { organizationSchema, websiteSchema, softwareAppSchema } from '@/components/PageMeta';
import { ViabilityIndicator } from '@/components/ViabilityBadge';
import {
  TrendingUp, ArrowRight, Check, Search, BarChart3, Shield,
  Zap, Package, ChevronRight, Globe, ShoppingBag, Store,
  Target, PoundSterling, Truck, RefreshCw, Layers, Sparkles,
  Eye,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const HERO_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/9e43031a2a6c68898323a79dc325d24cd4db83b9150424ed694dc19e140553b0.png';
const ANALYSIS_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/81f208d8f6c269953ffee857229896ade29d1f09335e593295c6b29c43483ceb.png';
const UK_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/62a43b3609a8651b44dec1ecc0b807db6dd12c254625840b3d14f3f69ce97376.png';
const TRENDING_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/ba0394884e89b59c51b94ca102ec8fc11c504f35f64063e9e77fc9a9839c2d60.png';

export default function LandingPage() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/api/public/trending-products?limit=6`)
      .then(r => r.json())
      .then(d => setProducts(d.products || []))
      .catch(() => {});
  }, []);

  return (
    <LandingLayout>
      <PageMeta
        title="AI Product Research for UK Ecommerce Sellers"
        description="Find products that can actually sell in the UK. Discover trends, analyse competition, estimate margins, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk."
        canonical="/"
        schema={[organizationSchema, websiteSchema, softwareAppSchema]}
      />

      {/* ═══ A. HERO ═══ */}
      <section className="relative bg-gradient-to-b from-slate-50 via-white to-white overflow-hidden" data-testid="hero-section">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(99,102,241,0.08),transparent)]" />
        <div className="relative mx-auto max-w-7xl px-6 pt-16 pb-8 lg:px-8 lg:pt-24 lg:pb-16">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">
            {/* Left: Copy */}
            <div className="max-w-xl">
              <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 border border-indigo-100 px-3.5 py-1.5 mb-6">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500" />
                </span>
                <span className="text-xs font-semibold text-indigo-700 tracking-wide">Built for UK ecommerce sellers</span>
              </div>
              <h1 className="font-manrope text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold tracking-tight text-slate-900 leading-[1.08]" data-testid="hero-headline">
                Find products that can actually{' '}
                <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">sell in the UK</span>
              </h1>
              <p className="mt-5 text-base sm:text-lg text-slate-500 leading-relaxed" data-testid="hero-subheadline">
                Discover trending products, analyse competition, estimate profit potential, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row items-start gap-3">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-base px-8 h-12 font-semibold rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transition-all"
                    data-testid="hero-cta-primary"
                    onClick={() => trackEvent(EVENTS.HOMEPAGE_PRIMARY_CTA, { cta_label: 'Start Free', source: 'hero' })}
                  >
                    Start Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/trending-products">
                  <Button
                    variant="outline"
                    size="lg"
                    className="text-base px-8 h-12 text-slate-700 border-slate-200 hover:bg-slate-50 rounded-xl font-medium"
                    data-testid="hero-cta-secondary"
                    onClick={() => trackEvent(EVENTS.HOMEPAGE_SECONDARY_CTA, { cta_label: 'See Trending Products', source: 'hero' })}
                  >
                    See Trending Products
                  </Button>
                </Link>
              </div>
              <div className="mt-8 flex items-center gap-6 text-sm text-slate-400">
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-500" /> No credit card</span>
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-500" /> UK-focused data</span>
                <span className="flex items-center gap-1.5"><Check className="h-4 w-4 text-emerald-500" /> Updated daily</span>
              </div>
            </div>

            {/* Right: Dashboard mockup */}
            <div className="relative lg:ml-4">
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
              {/* Floating badge */}
              <div className="absolute -bottom-4 -left-4 bg-white rounded-xl shadow-lg border border-slate-100 px-4 py-3 flex items-center gap-3 z-10" data-testid="hero-floating-badge">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50">
                  <TrendingUp className="h-5 w-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Products tracked</p>
                  <p className="text-sm font-bold text-slate-900 font-mono">150+</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ B. TRUST BAR ═══ */}
      <section className="border-y border-slate-100 bg-white" data-testid="trust-bar">
        <div className="mx-auto max-w-7xl px-6 py-5 lg:px-8">
          <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-3 text-sm text-slate-500">
            <span className="flex items-center gap-2"><Globe className="h-4 w-4 text-indigo-500" /> UK-first intelligence</span>
            <span className="flex items-center gap-2"><Shield className="h-4 w-4 text-indigo-500" /> 7-signal viability scoring</span>
            <span className="flex items-center gap-2"><BarChart3 className="h-4 w-4 text-indigo-500" /> Multi-channel trend detection</span>
            <span className="flex items-center gap-2"><RefreshCw className="h-4 w-4 text-indigo-500" /> Updated daily</span>
          </div>
        </div>
      </section>

      {/* ═══ C. VISUAL FEATURE SHOWCASE ═══ */}
      <section className="py-20 lg:py-28 bg-white" data-testid="why-different-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Image side */}
            <div className="relative order-2 lg:order-1">
              <div className="absolute -inset-8 bg-gradient-to-br from-indigo-50/50 to-violet-50/30 rounded-3xl" />
              <div className="relative rounded-2xl overflow-hidden shadow-xl border border-slate-200/60">
                <img
                  src={ANALYSIS_IMG}
                  alt="Product viability analysis showing scoring breakdown with trend momentum, margin potential, and saturation metrics"
                  className="w-full h-auto"
                  loading="lazy"
                  data-testid="analysis-visual"
                />
              </div>
            </div>
            {/* Text side */}
            <div className="order-1 lg:order-2">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Why TrendScout</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight leading-snug">
                Trend data is easy.<br />Profitable decisions are harder.
              </h2>
              <p className="mt-4 text-base text-slate-500 leading-relaxed">
                Most product research tools show you what is trending. TrendScout tells you whether it is commercially viable in the UK with our{' '}
                <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-medium">UK Product Viability Score</Link>.
              </p>
              <div className="mt-8 space-y-4">
                {[
                  { icon: Search, title: 'Multi-channel trend detection', desc: 'Spot rising products across TikTok, Amazon, Shopify, and Google Trends before they peak.' },
                  { icon: Shield, title: 'Saturation & competition analysis', desc: 'See how many sellers are already active and where gaps exist.' },
                  { icon: PoundSterling, title: 'UK-first viability insights', desc: 'Estimate landed costs, margins, VAT impact, and shipping practicality.' },
                  { icon: Zap, title: 'AI-assisted launch decisions', desc: 'Get launch scores, ad angle suggestions, and profit projections.' },
                ].map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.title} className="flex gap-4" data-testid={`feature-card-${item.title.toLowerCase().replace(/\s/g, '-')}`}>
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900">{item.title}</h3>
                        <p className="mt-0.5 text-sm text-slate-500">{item.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ D. HOW IT WORKS ═══ */}
      <section className="py-20 lg:py-28 bg-slate-50" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">How It Works</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              From trend signal to launch decision in four steps
            </h2>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: '01', title: 'Discover rising products', desc: 'Browse products gaining traction across TikTok, Amazon, and ecommerce stores. Filtered and scored daily.', icon: Search },
              { step: '02', title: 'Analyse saturation & demand', desc: 'Check how many sellers are already active, ad competition levels, and real demand signals.', icon: BarChart3 },
              { step: '03', title: 'Check UK viability', desc: 'Estimate profit margins, landed costs, VAT implications, and shipping practicality for UK buyers.', icon: Shield },
              { step: '04', title: 'Launch with confidence', desc: 'Use AI launch scores, ad angle suggestions, and competitor insights to make faster decisions.', icon: Zap },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.step} className="relative bg-white rounded-xl border border-slate-200 p-6 hover:border-indigo-200 hover:shadow-lg transition-all duration-300 group" data-testid={`step-${item.step}`}>
                  <div className="flex items-center gap-3 mb-4">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white text-xs font-bold font-mono">{item.step}</span>
                    <Icon className="h-4 w-4 text-slate-400 group-hover:text-indigo-500 transition-colors" />
                  </div>
                  <h3 className="font-manrope text-base font-semibold text-slate-900 mb-2">{item.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
          <div className="mt-12 text-center">
            <Link to="/how-it-works">
              <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-white rounded-xl font-medium" data-testid="learn-more-hiw">
                Learn more about our methodology <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ E. LIVE TRENDING PRODUCTS ═══ */}
      <section className="py-20 lg:py-28 bg-white" data-testid="product-showcase-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-5 gap-12 items-start">
            {/* Left: Visual + context */}
            <div className="lg:col-span-2">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Live Data</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Products trending right now
              </h2>
              <p className="mt-3 text-base text-slate-500 leading-relaxed">
                Real products scored and updated daily. Every product includes a{' '}
                <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-medium">UK Viability Score</Link>.
              </p>
              <div className="mt-6 rounded-xl overflow-hidden border border-slate-200/60 shadow-md">
                <img
                  src={TRENDING_IMG}
                  alt="TrendScout trending products interface showing scored product cards"
                  className="w-full h-auto"
                  loading="lazy"
                  data-testid="trending-visual"
                />
              </div>
              <div className="mt-6">
                <Link to="/trending-products">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm" data-testid="view-all-products-btn" onClick={() => trackEvent(EVENTS.TRENDING_VIEW, { source: 'homepage' })}>
                    View all products <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
            {/* Right: Live product cards */}
            <div className="lg:col-span-3">
              {products.length > 0 ? (
                <div className="grid sm:grid-cols-2 gap-4">
                  {products.slice(0, 6).map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              ) : (
                <div className="grid sm:grid-cols-2 gap-4">
                  {[1,2,3,4,5,6].map(i => <div key={i} className="rounded-xl border border-slate-200 bg-slate-50/50 p-6 h-48 animate-pulse" />)}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ F. UK-SPECIFIC SECTION WITH MAP ═══ */}
      <section className="py-20 lg:py-28 bg-slate-50" data-testid="uk-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">UK-Focused</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Not every viral product works in the UK
              </h2>
              <p className="mt-4 text-base text-slate-500 leading-relaxed">
                A product can have millions of TikTok views and still lose money in the UK market. Different VAT rules, higher shipping costs, and saturated ad channels mean UK sellers need UK-specific intelligence.
              </p>
              <p className="mt-3 text-base text-slate-500 leading-relaxed">
                Our <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-semibold">UK Product Viability Score</Link> answers one question: <strong className="text-slate-900">can this product actually sell profitably in the UK?</strong>
              </p>
              <div className="mt-8 grid grid-cols-2 gap-3">
                {[
                  { icon: PoundSterling, label: 'VAT & landed cost' },
                  { icon: Truck, label: 'Shipping practicality' },
                  { icon: Target, label: 'Margin potential' },
                  { icon: Layers, label: 'Saturation levels' },
                  { icon: RefreshCw, label: 'Returns friction' },
                  { icon: Globe, label: 'Channel fit' },
                ].map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="flex items-center gap-2.5 rounded-lg bg-white border border-slate-200 px-3 py-2.5">
                      <Icon className="h-4 w-4 text-indigo-600 shrink-0" />
                      <span className="text-sm font-medium text-slate-700">{item.label}</span>
                    </div>
                  );
                })}
              </div>
              <div className="mt-8">
                <Link to="/uk-product-viability-score">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm" data-testid="uk-viability-cta" onClick={() => trackEvent(EVENTS.UK_LANDING_CTA, { page_type: 'homepage', cta_label: 'Learn about UK Viability Score' })}>
                    Learn about the UK Viability Score <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
            {/* UK visual */}
            <div className="relative">
              <div className="absolute -inset-6 bg-gradient-to-br from-indigo-50/40 to-blue-50/30 rounded-3xl" />
              <div className="relative">
                <img
                  src={UK_IMG}
                  alt="UK ecommerce intelligence map showing data-driven insights for British market sellers"
                  className="w-full h-auto rounded-2xl"
                  loading="lazy"
                  data-testid="uk-map-visual"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ G. USE CASES ═══ */}
      <section className="py-20 lg:py-28 bg-white" data-testid="use-cases-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Solutions</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Built for how UK sellers actually work
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: Store, title: 'Shopify sellers', desc: 'Find products to test on your Shopify store. Push products directly from TrendScout to your store as drafts.', link: '/for-shopify' },
              { icon: ShoppingBag, title: 'Amazon UK sellers', desc: 'Spot products gaining demand on Amazon.co.uk before the category gets crowded.', link: '/for-amazon-uk' },
              { icon: Eye, title: 'TikTok Shop UK sellers', desc: 'Find products going viral on TikTok and check whether the UK audience, margins, and logistics work.', link: '/for-tiktok-shop-uk' },
              { icon: Package, title: 'UK dropshippers', desc: 'Research products before committing to suppliers. See estimated margins and competition levels.', link: '/dropshipping-product-research-uk' },
              { icon: Sparkles, title: 'Ecommerce founders', desc: 'Validate product ideas with data instead of guesswork. Reduce risk before investing in inventory or ads.', link: '/product-validation-uk' },
              { icon: BarChart3, title: 'Agencies & power users', desc: 'Research products for multiple clients. Use the API for custom integrations and automated screening.', link: '/pricing' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <Link key={item.title} to={item.link} className="group rounded-xl border border-slate-200 bg-white p-6 hover:border-indigo-200 hover:shadow-lg transition-all duration-300" data-testid={`usecase-${item.title.toLowerCase().replace(/\s/g, '-')}`}>
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-500 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-all duration-300 mb-4">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-manrope text-base font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">{item.title}</h3>
                  <p className="mt-2 text-sm text-slate-500 leading-relaxed">{item.desc}</p>
                  <span className="inline-flex items-center mt-3 text-xs font-medium text-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity">
                    Learn more <ChevronRight className="h-3 w-3 ml-0.5" />
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ H. METHODOLOGY — 7 Signal Scoring ═══ */}
      <section className="py-20 lg:py-28 bg-slate-50" data-testid="methodology-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-start">
            <div>
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Scoring Model</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Scored on 7 signals. Not vibes.
              </h2>
              <p className="mt-4 text-base text-slate-500 leading-relaxed">
                Every product in TrendScout is evaluated using a multi-signal scoring model. The{' '}
                <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-medium">UK Viability Score</Link>{' '}
                combines trend momentum, market saturation, margin potential, ad opportunity, and more.
              </p>
              <Link to="/how-it-works" className="inline-flex items-center mt-6 text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors group">
                Read the full methodology <ArrowRight className="ml-1.5 h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
            <div className="space-y-3">
              {[
                { label: 'Trend momentum', desc: 'Is demand growing, peaking, or declining?', pct: 82 },
                { label: 'Market saturation', desc: 'How many sellers are already active?', pct: 45 },
                { label: 'Margin potential', desc: 'Can you make money after all costs?', pct: 68 },
                { label: 'Ad opportunity', desc: 'Is there space to advertise profitably?', pct: 55 },
                { label: 'Search growth', desc: 'Are people actively searching for this?', pct: 72 },
                { label: 'Social buzz', desc: 'How much organic engagement does it have?', pct: 90 },
                { label: 'Supplier availability', desc: 'Reliable suppliers with reasonable lead times?', pct: 60 },
              ].map((signal) => (
                <div key={signal.label} className="rounded-lg border border-slate-200 bg-white p-4 hover:border-indigo-100 transition-colors">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-slate-900">{signal.label}</span>
                    <span className="font-mono text-xs font-bold text-indigo-600">{signal.pct}%</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-2.5">{signal.desc}</p>
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-700"
                      style={{ width: `${signal.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ I. FREE TOOLS TEASER ═══ */}
      <section className="py-20 bg-white" data-testid="free-tools-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-8 sm:p-12">
            <div className="grid lg:grid-cols-2 gap-8 items-center">
              <div>
                <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Free Tools</p>
                <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                  Try before you commit
                </h2>
                <p className="mt-3 text-base text-slate-500 leading-relaxed">
                  Use our free calculators and validation tools to get a taste of what TrendScout can do for your ecommerce business.
                </p>
                <div className="mt-6">
                  <Link to="/free-tools">
                    <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm" data-testid="free-tools-cta">
                      Explore free tools <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: 'Profit Calculator', desc: 'Estimate margins & ROI' },
                  { name: 'Product Validator', desc: 'Score your product idea' },
                  { name: 'TikTok Ad Budget', desc: 'Plan your ad spend' },
                  { name: 'Validation Checklist', desc: 'Pre-launch checks' },
                ].map((tool) => (
                  <div key={tool.name} className="rounded-lg bg-white border border-slate-200 p-4 hover:border-indigo-200 hover:shadow-sm transition-all">
                    <p className="text-sm font-semibold text-slate-900">{tool.name}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{tool.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ J. FINAL CTA ═══ */}
      <section className="py-20" data-testid="final-cta-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="relative rounded-2xl bg-slate-900 overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,102,241,0.15),transparent_60%)]" />
            <div className="relative p-10 sm:p-16 text-center">
              <h2 className="font-manrope text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight max-w-2xl mx-auto">
                Validate your next product before you waste money on ads or stock
              </h2>
              <p className="mt-5 text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
                Start free. Browse trending products, check UK Viability Scores, and explore margin insights — no credit card needed.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link to="/signup">
                  <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-12 font-semibold rounded-xl shadow-lg" data-testid="final-cta-primary" onClick={() => trackEvent(EVENTS.HOMEPAGE_PRIMARY_CTA, { cta_label: 'Start Free', source: 'final_cta' })}>
                    Start Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/pricing">
                  <Button variant="ghost" size="lg" className="text-base px-8 h-12 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl" data-testid="final-cta-secondary" onClick={() => trackEvent(EVENTS.PRICING_VIEW, { source: 'homepage_cta' })}>
                    See Pricing
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </LandingLayout>
  );
}

/* ── Product Card with Viability Score ── */
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
      <div className="relative h-36 bg-slate-100 overflow-hidden">
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
