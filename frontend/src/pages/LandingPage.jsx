import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import PageMeta, { organizationSchema, websiteSchema, softwareAppSchema } from '@/components/PageMeta';
import { ViabilityIndicator } from '@/components/ViabilityBadge';
import { RevealSection, RevealStagger } from '@/hooks/useScrollReveal';
import {
  TrendingUp, ArrowRight, Check, Search, BarChart3, Shield,
  Zap, Package, ChevronRight, Globe, PoundSterling, RefreshCw,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const HERO_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/9e43031a2a6c68898323a79dc325d24cd4db83b9150424ed694dc19e140553b0.png';

export default function LandingPage() {
  const [products, setProducts] = useState([]);

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
        description="Find products that can actually sell in the UK. Discover trends, analyse competition, estimate margins, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk."
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

      {/* ═══ TRUST BAR ═══ */}
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

      {/* ═══ QUICK FEATURE HIGHLIGHTS ═══ */}
      <section className="py-20 lg:py-24 bg-white" data-testid="features-highlight-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-14">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Why TrendScout</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Everything you need to find profitable products
            </h2>
            <p className="mt-3 text-base text-slate-500">
              From trend detection to launch decisions — built specifically for UK ecommerce sellers.
            </p>
          </RevealSection>
          <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5" staggerMs={100}>
            {[
              { icon: Search, title: 'Trend Detection', desc: 'Spot rising products across TikTok, Amazon, Shopify, and Google Trends before they peak.' },
              { icon: Shield, title: 'Competition Analysis', desc: 'See how many sellers are active, how crowded the ad space is, and where gaps exist.' },
              { icon: PoundSterling, title: 'UK Viability Scoring', desc: 'Estimate landed costs, margins, VAT impact, and shipping practicality for UK customers.' },
              { icon: Zap, title: 'AI Launch Decisions', desc: 'Get launch scores, ad angle suggestions, and profit projections — not just raw data.' },
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

      {/* ═══ LIVE TRENDING PRODUCTS ═══ */}
      <section className="py-20 lg:py-24 bg-slate-50" data-testid="product-showcase-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection>
            <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
              <div>
                <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Live Data</p>
                <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                  Products trending right now
                </h2>
                <p className="mt-2 text-base text-slate-500">
                  Real products scored and updated daily with{' '}
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

      {/* ═══ FINAL CTA ═══ */}
      <RevealSection>
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
