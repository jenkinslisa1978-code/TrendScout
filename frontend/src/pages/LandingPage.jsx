import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import {
  TrendingUp, ArrowRight, Check, Search, BarChart3, Shield,
  Zap, Package, ChevronRight, Globe, ShoppingBag, Store,
  Target, PoundSterling, Truck, RefreshCw, Layers, Sparkles,
  Eye, LineChart,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

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
      {/* ═══ A. HERO ═══ */}
      <section className="relative bg-white overflow-hidden" data-testid="hero-section">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(79,70,229,0.04),transparent_50%)]" />
        <div className="relative mx-auto max-w-7xl px-6 pt-20 pb-16 lg:px-8 lg:pt-28 lg:pb-24">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 border border-indigo-100 px-3 py-1 mb-6 animate-fade-in">
              <span className="flex h-1.5 w-1.5 rounded-full bg-indigo-500" />
              <span className="text-xs font-medium text-indigo-700">Built for UK ecommerce sellers</span>
            </div>
            <h1
              className="font-manrope text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold tracking-tight text-slate-900 leading-[1.1]"
              data-testid="hero-headline"
            >
              Find products that can actually{' '}
              <span className="text-indigo-600">sell in the UK</span>
            </h1>
            <p className="mt-5 text-lg text-slate-600 leading-relaxed max-w-2xl" data-testid="hero-subheadline">
              TrendScout helps UK ecommerce sellers discover trending products, analyse competition, estimate profit potential, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-start gap-3">
              <Link to="/signup">
                <Button
                  size="lg"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white text-base px-7 h-12 font-semibold rounded-lg shadow-sm"
                  data-testid="hero-cta-primary"
                  onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'hero' })}
                >
                  Start Free
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/trending-products">
                <Button
                  variant="outline"
                  size="lg"
                  className="text-base px-7 h-12 text-slate-700 border-slate-300 hover:bg-slate-50 rounded-lg font-medium"
                  data-testid="hero-cta-secondary"
                  onClick={() => trackEvent(EVENTS.TRENDING_VIEW, { source: 'hero' })}
                >
                  See Trending Products
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ B. TRUST BAR ═══ */}
      <section className="border-y border-slate-100 bg-slate-50/50" data-testid="trust-bar">
        <div className="mx-auto max-w-7xl px-6 py-5 lg:px-8">
          <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-3 text-sm text-slate-500">
            <span className="flex items-center gap-2"><Globe className="h-4 w-4 text-indigo-500" /> Built for UK ecommerce sellers</span>
            <span className="flex items-center gap-2"><Package className="h-4 w-4 text-indigo-500" /> <span className="font-mono font-semibold text-slate-700">150+</span> products tracked</span>
            <span className="flex items-center gap-2"><BarChart3 className="h-4 w-4 text-indigo-500" /> <span className="font-mono font-semibold text-slate-700">7</span> trend signals per product</span>
            <span className="flex items-center gap-2"><RefreshCw className="h-4 w-4 text-indigo-500" /> Updated daily</span>
          </div>
        </div>
      </section>

      {/* ═══ C. WHY TRENDSCOUT IS DIFFERENT ═══ */}
      <section className="py-20 bg-white" data-testid="why-different-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-2xl mb-12">
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Trend data is easy. Profitable decisions are harder.
            </h2>
            <p className="mt-3 text-base text-slate-500">
              Most product research tools show you what is trending. TrendScout tells you whether it is commercially viable in the UK.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { icon: Search, title: 'Multi-channel trend detection', desc: 'Spot rising products across TikTok, Amazon, Shopify, and Google Trends before they peak.' },
              { icon: Shield, title: 'Saturation & competition analysis', desc: 'See how many sellers are already active, how crowded the ad space is, and where gaps exist.' },
              { icon: PoundSterling, title: 'UK-first viability insights', desc: 'Estimate landed costs, margins, VAT impact, and shipping practicality for UK customers.' },
              { icon: Zap, title: 'AI-assisted launch decisions', desc: 'Get launch scores, ad angle suggestions, and profit projections — not just raw data.' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.title}
                  className="rounded-xl border border-slate-200 bg-white p-6 hover:border-indigo-200 hover:shadow-md transition-all duration-200"
                  data-testid={`feature-card-${item.title.toLowerCase().replace(/\s/g, '-')}`}
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 mb-4">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-manrope text-base font-semibold text-slate-900">{item.title}</h3>
                  <p className="mt-2 text-sm text-slate-500 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ D. HOW IT WORKS ═══ */}
      <section className="py-20 bg-slate-50" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-2xl mb-12">
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              From trend signal to launch decision in four steps
            </h2>
          </div>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: '01', title: 'Discover rising products', desc: 'Browse products gaining traction across TikTok, Amazon, and ecommerce stores. Filtered and scored daily.' },
              { step: '02', title: 'Analyse saturation and demand', desc: 'Check how many sellers are already active, ad competition levels, and real demand signals.' },
              { step: '03', title: 'Check UK viability', desc: 'Estimate profit margins, landed costs, VAT implications, and shipping practicality for UK buyers.' },
              { step: '04', title: 'Launch with more confidence', desc: 'Use AI launch scores, ad angle suggestions, and competitor insights to make faster decisions.' },
            ].map((item) => (
              <div key={item.step} className="relative" data-testid={`step-${item.step}`}>
                <span className="font-mono text-xs font-semibold text-indigo-500 mb-3 block">{item.step}</span>
                <h3 className="font-manrope text-base font-semibold text-slate-900 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-10">
            <Link to="/how-it-works">
              <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-white rounded-lg font-medium" data-testid="learn-more-hiw">
                Learn more about our methodology <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ E. FEATURE SHOWCASE — Live Trending Products ═══ */}
      <section className="py-20 bg-white" data-testid="product-showcase-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
            <div>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Products trending right now
              </h2>
              <p className="mt-2 text-base text-slate-500">
                Real products scored and updated daily. See the data before you sign up.
              </p>
            </div>
            <Link to="/trending-products">
              <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg font-medium text-sm" data-testid="view-all-products-btn">
                View all products <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>

          {products.length > 0 ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {products.slice(0, 6).map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {[1,2,3].map(i => (
                <div key={i} className="rounded-xl border border-slate-200 bg-slate-50 p-6 h-52 animate-pulse" />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ═══ F. UK-SPECIFIC SECTION ═══ */}
      <section className="py-20 bg-slate-50" data-testid="uk-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Not every viral product works in the UK
              </h2>
              <p className="mt-4 text-base text-slate-600 leading-relaxed">
                A product can have millions of TikTok views and still lose money in the UK market. Different VAT rules, higher shipping costs, local returns expectations, and saturated ad channels mean UK sellers need UK-specific intelligence.
              </p>
              <p className="mt-3 text-base text-slate-600 leading-relaxed">
                TrendScout is built to answer one question: <strong className="text-slate-900">can this product actually sell profitably in the UK?</strong>
              </p>
              <div className="mt-8">
                <Link to="/uk-product-research">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold" data-testid="uk-research-cta">
                    Learn about UK product research <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { icon: PoundSterling, label: 'VAT & landed cost', desc: 'Factor in 20% VAT and actual import costs' },
                { icon: Truck, label: 'Shipping practicality', desc: 'UK delivery times and carrier feasibility' },
                { icon: Target, label: 'Margin potential', desc: 'Realistic profit after all UK-specific costs' },
                { icon: Layers, label: 'Saturation levels', desc: 'How many UK sellers are already active' },
                { icon: RefreshCw, label: 'Returns friction', desc: 'Product categories with high UK return rates' },
                { icon: Globe, label: 'Channel fit', desc: 'Which UK sales channel suits this product' },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.label} className="rounded-lg border border-slate-200 bg-white p-4">
                    <Icon className="h-5 w-5 text-indigo-600 mb-2" />
                    <p className="text-sm font-semibold text-slate-900">{item.label}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ G. USE CASES ═══ */}
      <section className="py-20 bg-white" data-testid="use-cases-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="max-w-2xl mb-12">
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Built for how UK sellers actually work
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: Store, title: 'Shopify sellers', desc: 'Find products to test on your Shopify store. Push products directly from TrendScout to your store as drafts.', link: '/for-shopify' },
              { icon: ShoppingBag, title: 'Amazon UK sellers', desc: 'Spot products gaining demand on Amazon.co.uk before the category gets crowded. Check saturation and margin potential.', link: '/for-amazon-uk' },
              { icon: Eye, title: 'TikTok Shop UK sellers', desc: 'Find products going viral on TikTok and check whether the UK audience, margins, and logistics work.', link: '/for-tiktok-shop-uk' },
              { icon: Package, title: 'UK dropshippers', desc: 'Research products before committing to suppliers. See estimated margins, shipping times, and competition levels.', link: '/uk-product-research' },
              { icon: Sparkles, title: 'Ecommerce founders', desc: 'Validate product ideas with data instead of guesswork. Reduce risk before investing in inventory or ads.', link: '/how-it-works' },
              { icon: BarChart3, title: 'Agencies & power users', desc: 'Research products for multiple clients. Use the API for custom integrations and automated product screening.', link: '/pricing' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.title}
                  to={item.link}
                  className="group rounded-xl border border-slate-200 bg-white p-6 hover:border-indigo-200 hover:shadow-md transition-all duration-200"
                  data-testid={`usecase-${item.title.toLowerCase().replace(/\s/g, '-')}`}
                >
                  <Icon className="h-5 w-5 text-slate-400 group-hover:text-indigo-600 transition-colors mb-3" />
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

      {/* ═══ H. PROOF OF VALUE — Platform Methodology ═══ */}
      <section className="py-20 bg-slate-50" data-testid="methodology-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            <div>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Scored on 7 signals. Not vibes.
              </h2>
              <p className="mt-4 text-base text-slate-600 leading-relaxed">
                Every product in TrendScout is evaluated using a multi-signal scoring model. The launch score combines trend momentum, market saturation, margin potential, ad opportunity, and more — giving you a single number to help prioritise what is worth testing.
              </p>
              <Link to="/how-it-works" className="inline-flex items-center mt-6 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
                Read the full methodology <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Link>
            </div>
            <div className="space-y-3">
              {[
                { label: 'Trend momentum', desc: 'Is demand growing, peaking, or declining?', pct: 82 },
                { label: 'Market saturation', desc: 'How many sellers are already active in this space?', pct: 45 },
                { label: 'Margin potential', desc: 'Can you make money after costs, VAT, and shipping?', pct: 68 },
                { label: 'Ad opportunity', desc: 'Is there space to advertise profitably?', pct: 55 },
                { label: 'Search growth', desc: 'Are people actively searching for this product?', pct: 72 },
                { label: 'Social buzz', desc: 'How much organic social engagement does it have?', pct: 90 },
                { label: 'Supplier availability', desc: 'Are there reliable suppliers with reasonable lead times?', pct: 60 },
              ].map((signal) => (
                <div key={signal.label} className="rounded-lg border border-slate-200 bg-white p-4">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm font-medium text-slate-900">{signal.label}</span>
                    <span className="font-mono text-xs font-semibold text-indigo-600">{signal.pct}%</span>
                  </div>
                  <p className="text-xs text-slate-500 mb-2">{signal.desc}</p>
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full transition-all duration-500" style={{ width: `${signal.pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ I. FINAL CTA ═══ */}
      <section className="py-20 bg-white" data-testid="final-cta-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="rounded-2xl bg-slate-900 p-10 sm:p-14 text-center">
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-white tracking-tight">
              Validate your next product before you waste money on ads or stock
            </h2>
            <p className="mt-4 text-base text-slate-400 max-w-xl mx-auto">
              Start free. Browse trending products, check scores, and explore UK viability insights — no credit card needed.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link to="/signup">
                <Button
                  size="lg"
                  className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-12 font-semibold rounded-lg"
                  data-testid="final-cta-primary"
                  onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'final_cta' })}
                >
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/trending-products">
                <Button
                  variant="ghost"
                  size="lg"
                  className="text-base px-8 h-12 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg"
                  data-testid="final-cta-secondary"
                >
                  See Trending Products
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </LandingLayout>
  );
}

/* ── Product Card ── */
function ProductCard({ product }) {
  const score = product.launch_score || 0;
  const scoreColor = score >= 65 ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
    : score >= 45 ? 'text-amber-700 bg-amber-50 border-amber-200'
    : 'text-slate-600 bg-slate-50 border-slate-200';

  return (
    <Link
      to={`/trending/${product.slug}`}
      className="group block rounded-xl border border-slate-200 bg-white overflow-hidden hover:border-indigo-200 hover:shadow-md transition-all duration-200"
      data-testid={`product-card-${product.id}`}
    >
      <div className="relative h-40 bg-slate-100 overflow-hidden">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy" />
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
          {product.margin_percent ? (
            <span className="text-xs text-slate-500">
              Est. margin: <span className="font-mono font-semibold text-slate-700">{Math.round(product.margin_percent)}%</span>
            </span>
          ) : (
            <span className="text-xs text-slate-400">View details</span>
          )}
          <span className="text-xs font-medium text-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity flex items-center">
            View <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </div>
    </Link>
  );
}
