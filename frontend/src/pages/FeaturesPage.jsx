import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import PageMeta from '@/components/PageMeta';
import { RevealSection, RevealStagger } from '@/hooks/useScrollReveal';
import {
  ArrowRight, Search, BarChart3, Shield, Zap, Package,
  ChevronRight, Globe, ShoppingBag, Store, Target,
  PoundSterling, Truck, RefreshCw, Layers, Sparkles, Eye,
} from 'lucide-react';

const ANALYSIS_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/81f208d8f6c269953ffee857229896ade29d1f09335e593295c6b29c43483ceb.png';
const UK_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/62a43b3609a8651b44dec1ecc0b807db6dd12c254625840b3d14f3f69ce97376.png';
const TRENDING_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/ba0394884e89b59c51b94ca102ec8fc11c504f35f64063e9e77fc9a9839c2d60.png';

export default function FeaturesPage() {
  return (
    <LandingLayout>
      <PageMeta
        title="UK Product Validation Features for Ecommerce Sellers | TrendScout"
        description="See how TrendScout helps UK ecommerce sellers validate product ideas with demand signals, competition analysis, margin estimation, and UK Viability Scores."
        canonical="/features"
      />

      {/* ═══ PAGE HEADER ═══ */}
      <section className="relative bg-gradient-to-b from-slate-50 via-white to-white overflow-hidden pt-16 pb-12 lg:pt-24 lg:pb-16" data-testid="features-hero">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(99,102,241,0.06),transparent)]" />
        <div className="relative mx-auto max-w-7xl px-6 lg:px-8 text-center">
          <RevealSection>
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Features</p>
            <h1 className="font-manrope text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-[1.1]" data-testid="features-headline">
              Built for <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">smarter UK product decisions</span>
            </h1>
            <p className="mt-5 text-base sm:text-lg text-slate-500 leading-relaxed max-w-2xl mx-auto">
              TrendScout helps UK ecommerce sellers move from product ideas to clearer go / no-go decisions using demand signals, competition analysis, and UK-specific viability checks.
            </p>
          </RevealSection>
        </div>
      </section>

      {/* ═══ CORE CAPABILITIES ═══ */}
      <section className="py-20 lg:py-24 bg-white" data-testid="core-features-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <RevealSection direction="left" className="relative order-2 lg:order-1">
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
            </RevealSection>
            <RevealSection direction="right" delay={150} className="order-1 lg:order-2">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Core capabilities</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight leading-snug">
                Trend data is easy.<br />Knowing what is worth testing is harder.
              </h2>
              <p className="mt-4 text-base text-slate-500 leading-relaxed">
                Most product research tools stop at what is trending. TrendScout is built to answer the more useful question: is this product commercially worth testing in the UK? That is what our{' '}
                <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-medium">UK Product Viability Score</Link> is for.
              </p>
              <div className="mt-8 space-y-4">
                {[
                  { icon: Search, title: 'Multi-channel demand signals', desc: 'Spot rising products across TikTok, Amazon, Shopify, and Google Trends before they become obvious.' },
                  { icon: Shield, title: 'Competition & saturation analysis', desc: 'See how crowded the niche already is and whether the opportunity is already thinning out.' },
                  { icon: PoundSterling, title: 'UK-first viability insights', desc: 'Estimate landed costs, margins, VAT impact, and shipping practicality before you commit budget.' },
                  { icon: Zap, title: 'Decision support, not just data', desc: 'Use launch scores, reasoning, and supporting tools to decide what is worth testing next.' },
                ].map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.title} className="flex gap-4" data-testid={`feature-detail-${item.title.toLowerCase().replace(/\s/g, '-')}`}>
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
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ UK-SPECIFIC INTELLIGENCE ═══ */}
      <section className="py-20 lg:py-24 bg-slate-50" data-testid="uk-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <RevealSection direction="right">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">UK-focused</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Not every trending product is a good UK business
              </h2>
              <p className="mt-4 text-base text-slate-500 leading-relaxed">
                A product can have millions of TikTok views and still lose money in the UK market. Different VAT rules, higher shipping costs, and saturated ad channels mean UK sellers need UK-specific intelligence.
              </p>
              <p className="mt-3 text-base text-slate-500 leading-relaxed">
                Our <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-semibold">UK Product Viability Score</Link> answers one question: <strong className="text-slate-900">is this product actually worth testing in the UK?</strong>
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
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm" data-testid="uk-viability-cta" onClick={() => trackEvent(EVENTS.UK_LANDING_CTA, { page_type: 'features', cta_label: 'Learn about UK Viability Score' })}>
                    Learn about the UK Viability Score <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </RevealSection>
            <RevealSection direction="left" delay={200} className="relative">
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
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ 7-SIGNAL METHODOLOGY ═══ */}
      <section className="py-20 lg:py-24 bg-white" data-testid="methodology-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-start">
            <RevealSection>
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Scoring model</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Scored on 7 signals. Not vibes.
              </h2>
              <p className="mt-4 text-base text-slate-500 leading-relaxed">
                Every product in TrendScout is evaluated using a multi-signal scoring model. The{' '}
                <Link to="/uk-product-viability-score" className="text-indigo-600 hover:text-indigo-700 font-medium">UK Product Viability Score</Link>{' '}
                combines trend momentum, market saturation, margin potential, ad opportunity, and more.
              </p>
              <div className="mt-6 flex flex-col gap-3">
                <Link to="/how-it-works" className="inline-flex items-center text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors group">
                  Read the full methodology <ArrowRight className="ml-1.5 h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link to="/accuracy" className="inline-flex items-center text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors group">
                  See our accuracy tracking <ArrowRight className="ml-1.5 h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </RevealSection>
            <RevealStagger className="space-y-3" staggerMs={80}>
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
            </RevealStagger>
          </div>
        </div>
      </section>

      {/* ═══ USE CASES ═══ */}
      <section className="py-20 lg:py-24 bg-slate-50" data-testid="use-cases-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="text-center max-w-2xl mx-auto mb-14">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Use cases</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Built for sellers making real product decisions
            </h2>
          </RevealSection>
          <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5" staggerMs={100}>
            {[
              { icon: Store, title: 'Shopify sellers', desc: 'Validate products before you add them to your store or spend money testing them.', link: '/for-shopify' },
              { icon: ShoppingBag, title: 'Amazon UK sellers', desc: 'Check whether demand, competition, and margin potential make a product worth listing.', link: '/for-amazon-uk' },
              { icon: Eye, title: 'TikTok Shop UK sellers', desc: 'See whether a viral-looking product still works once UK margins, audience, and logistics are considered.', link: '/for-tiktok-shop-uk' },
              { icon: Package, title: 'UK dropshippers', desc: 'Research products before committing to suppliers, shipping assumptions, and ad spend.', link: '/dropshipping-product-research-uk' },
              { icon: Sparkles, title: 'Ecommerce founders', desc: 'Use data to prioritise what to test next and reduce bad bets before you invest in stock or ads.', link: '/product-validation-uk' },
              { icon: BarChart3, title: 'Agencies & teams', desc: 'Research and compare opportunities across multiple clients or brands using a more consistent scoring workflow.', link: '/pricing' },
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
          </RevealStagger>
        </div>
      </section>

      {/* ═══ FREE TOOLS ═══ */}
      <section className="py-20 bg-white" data-testid="free-tools-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <RevealSection direction="right">
              <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Free tools</p>
              <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Try before you commit
              </h2>
              <p className="mt-3 text-base text-slate-500 leading-relaxed">
                Use our free calculators and validation tools to get a feel for how TrendScout helps you make clearer product decisions.
              </p>
              <div className="mt-6">
                <Link to="/free-tools">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm" data-testid="free-tools-cta">
                    Explore all free tools <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </RevealSection>
            <RevealSection direction="left" delay={200}>
              <div className="rounded-xl overflow-hidden border border-slate-200/60 shadow-lg">
                <img
                  src={TRENDING_IMG}
                  alt="TrendScout product research interface"
                  className="w-full h-auto"
                  loading="lazy"
                  data-testid="trending-visual"
                />
              </div>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ CTA ═══ */}
      <RevealSection>
        <section className="py-20" data-testid="features-cta-section">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="relative rounded-2xl bg-slate-900 overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,102,241,0.15),transparent_60%)]" />
              <div className="relative p-10 sm:p-16 text-center">
                <h2 className="font-manrope text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight max-w-2xl mx-auto">
                  Ready to validate your next product properly?
                </h2>
                <p className="mt-5 text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
                  Start free. Check UK Viability Scores, compare demand and competition, and make clearer product decisions before you spend.
                </p>
                <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link to="/signup">
                    <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-12 font-semibold rounded-xl shadow-lg" data-testid="features-cta-primary" onClick={() => trackEvent(EVENTS.HOMEPAGE_PRIMARY_CTA, { cta_label: 'Validate Your First Product', source: 'features_cta' })}>
                      Validate Your First Product <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                  <Link to="/pricing">
                    <Button variant="ghost" size="lg" className="text-base px-8 h-12 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl" data-testid="features-cta-secondary">
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
