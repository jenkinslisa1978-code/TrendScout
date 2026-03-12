import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  Rocket,
  Store,
  Zap,
  Check,
  ArrowRight,
  Sparkles,
  Package,
  Star,
  Eye,
  BarChart3,
  Search,
  Video,
  DollarSign,
  Truck,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// ── Pricing ─────────────────────────────────────────

const pricingPlans = [
  {
    id: 'free',
    name: 'Free',
    price: '0',
    description: 'Get started with product research',
    features: [
      'Limited product insights',
      'Report previews',
      '1 store',
      'Limited watchlist & alerts',
      'Community support',
    ],
    cta: 'Get Started Free',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '39',
    description: 'Full insights & multiple stores',
    features: [
      'Full product insights',
      'Complete reports + PDF export',
      'Up to 5 stores',
      'Full watchlist & alerts',
      'Ad discovery',
      'Priority support',
    ],
    cta: 'Upgrade to Pro',
    popular: true,
  },
  {
    id: 'elite',
    name: 'Elite',
    price: '99',
    description: 'Everything you need to dominate',
    features: [
      'Everything in Pro',
      'Unlimited stores',
      'Early trend detection',
      'Automated reports & priority alerts',
      'Direct Shopify publish',
      'Dedicated support',
    ],
    cta: 'Go Elite',
    popular: false,
  },
];

// ── Trend stage styling ──────────────────────────────

const TREND_BADGE = {
  Exploding: 'bg-red-100 text-red-700 border-red-200',
  Emerging: 'bg-orange-100 text-orange-700 border-orange-200',
  Rising: 'bg-amber-100 text-amber-700 border-amber-200',
  Stable: 'bg-blue-100 text-blue-700 border-blue-200',
  Declining: 'bg-slate-100 text-slate-500 border-slate-200',
};

// ── Component ────────────────────────────────────────

export default function LandingPage() {
  const [featured, setFeatured] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API_URL}/api/public/featured-product`)
      .then((r) => r.json())
      .then((d) => d.product && setFeatured(d.product))
      .catch(() => {});
  }, []);

  return (
    <LandingLayout>
      {/* ───── HERO ───── */}
      <section className="relative overflow-hidden" data-testid="hero-section">
        {/* Ambient background */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-[-20%] left-[10%] w-[600px] h-[600px] rounded-full bg-indigo-100/60 blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[5%] w-[500px] h-[500px] rounded-full bg-purple-100/40 blur-[100px]" />
        </div>

        <div className="mx-auto max-w-7xl px-6 pt-20 pb-16 lg:px-8 lg:pt-28">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Copy */}
            <div className="max-w-xl">
              <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 border border-indigo-100 px-4 py-1.5 text-sm font-medium text-indigo-700 mb-6 animate-[fadeIn_0.6s_ease]">
                <Sparkles className="h-4 w-4 text-indigo-500" />
                AI-Powered Product Intelligence
              </div>

              <h1 className="font-manrope text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-[3.5rem] leading-[1.1]">
                Find Winning Ecommerce Products{' '}
                <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Before They Go Viral
                </span>
              </h1>

              <p className="mt-6 text-lg text-slate-600 leading-relaxed">
                TrendScout scans real market signals from TikTok, Amazon, and Google Trends to detect
                emerging products — then helps you launch stores and generate ads in minutes.
              </p>

              <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-indigo-600 hover:bg-indigo-700 text-base px-8 h-13 font-semibold shadow-lg shadow-indigo-200/50 hover:shadow-xl hover:shadow-indigo-300/50 transition-all"
                    data-testid="hero-cta-btn"
                  >
                    <Zap className="mr-2 h-5 w-5" />
                    Find My Winning Product
                  </Button>
                </Link>
                <a href="#how-it-works">
                  <Button
                    variant="outline"
                    size="lg"
                    className="text-base px-8 h-13 border-slate-300 hover:border-indigo-300 hover:text-indigo-600 transition-all"
                    data-testid="hero-secondary-btn"
                  >
                    See How It Works
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </a>
              </div>

              <p className="mt-5 text-sm text-slate-500 flex items-center gap-4">
                <span className="flex items-center gap-1"><Check className="h-3.5 w-3.5 text-emerald-500" /> No credit card</span>
                <span className="flex items-center gap-1"><Check className="h-3.5 w-3.5 text-emerald-500" /> Real data only</span>
                <span className="flex items-center gap-1"><Check className="h-3.5 w-3.5 text-emerald-500" /> Launch in 3 clicks</span>
              </p>
            </div>

            {/* Right: Live Demo Product Card */}
            <div className="relative" data-testid="live-demo-card">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-200/30 to-purple-200/30 rounded-3xl blur-2xl -z-10 scale-105" />
              {featured ? (
                <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl shadow-slate-200/60 overflow-hidden hover:shadow-indigo-100/40 transition-shadow duration-500">
                  {/* Card Header */}
                  <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-5 py-3 flex items-center justify-between">
                    <span className="text-sm font-medium text-white/90 flex items-center gap-1.5">
                      <Sparkles className="h-3.5 w-3.5 text-amber-300" />
                      AI Recommendation — Live
                    </span>
                    <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  </div>
                  {/* Card Body */}
                  <div className="p-6">
                    <div className="flex items-start gap-4">
                      {featured.image_url ? (
                        <img
                          src={featured.image_url}
                          alt={featured.product_name}
                          className="w-20 h-20 rounded-xl object-cover bg-slate-100 flex-shrink-0"
                        />
                      ) : (
                        <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center flex-shrink-0">
                          <Package className="h-8 w-8 text-indigo-400" />
                        </div>
                      )}
                      <div className="min-w-0 flex-1">
                        <h3 className="font-bold text-slate-900 text-base leading-tight line-clamp-2">
                          {featured.product_name}
                        </h3>
                        <div className="flex items-center gap-2 mt-1.5">
                          <Badge variant="outline" className="text-xs">{featured.category}</Badge>
                          <Badge className={`text-xs border ${TREND_BADGE[featured.trend_stage] || TREND_BADGE.Stable}`}>
                            {featured.trend_stage}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-3 gap-3 mt-5">
                      <div className="bg-indigo-50/80 rounded-xl p-3 text-center">
                        <p className="text-2xl font-bold text-indigo-700 font-mono">{featured.launch_score}</p>
                        <p className="text-[11px] text-indigo-500 mt-0.5 font-medium">Launch Score</p>
                      </div>
                      <div className="bg-emerald-50/80 rounded-xl p-3 text-center">
                        <p className="text-2xl font-bold text-emerald-700 font-mono">{featured.success_probability}%</p>
                        <p className="text-[11px] text-emerald-500 mt-0.5 font-medium">Success Prob.</p>
                      </div>
                      <div className="bg-amber-50/80 rounded-xl p-3 text-center">
                        <p className="text-2xl font-bold text-amber-700 font-mono">
                          £{featured.estimated_profit > 0 ? featured.estimated_profit.toFixed(0) : '—'}
                        </p>
                        <p className="text-[11px] text-amber-500 mt-0.5 font-medium">Est. Profit</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 mt-4 text-sm text-slate-500">
                      <Truck className="h-4 w-4" />
                      <span>Supplier: {featured.supplier_source}</span>
                    </div>

                    <Link to="/signup">
                      <Button
                        className="w-full mt-4 bg-indigo-600 hover:bg-indigo-700 font-semibold shadow-sm hover:shadow-md transition-all"
                        data-testid="demo-launch-btn"
                      >
                        <Rocket className="mr-2 h-4 w-4" />
                        Launch This Product
                      </Button>
                    </Link>
                  </div>
                </div>
              ) : (
                <DemoProductSkeleton />
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ───── HOW IT WORKS ───── */}
      <section id="how-it-works" className="py-24 bg-white" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <Badge className="bg-indigo-50 text-indigo-700 border-indigo-100 mb-4">3 Simple Steps</Badge>
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              From discovery to launch in minutes
            </h2>
            <p className="mt-4 text-lg text-slate-600">
              TrendScout automates the entire product research and store launch workflow.
            </p>
          </div>

          <div className="mt-16 grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                icon: Search,
                title: 'Discover',
                description: 'TrendScout analyzes real signals from TikTok, Amazon, and Google Trends to detect products with early momentum — before they saturate.',
                color: 'indigo',
              },
              {
                step: '02',
                icon: Store,
                title: 'Launch',
                description: 'One click generates your complete store — product pages, branding, pricing, policies, and checkout. Export to Shopify instantly.',
                color: 'purple',
              },
              {
                step: '03',
                icon: Video,
                title: 'Advertise',
                description: 'AI creates TikTok ad scripts, Facebook copy, Instagram captions, and video storyboards — ready to drive traffic to your store.',
                color: 'rose',
              },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.step}
                  className="group relative bg-white rounded-2xl border border-slate-200 p-8 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-50/50 transition-all duration-300"
                  data-testid={`how-step-${item.step}`}
                >
                  <span className={`font-mono text-5xl font-black text-${item.color}-100 absolute top-6 right-6`}>
                    {item.step}
                  </span>
                  <div className={`flex h-14 w-14 items-center justify-center rounded-2xl bg-${item.color}-50 text-${item.color}-600 group-hover:bg-${item.color}-600 group-hover:text-white transition-colors duration-300`}>
                    <Icon className="h-7 w-7" />
                  </div>
                  <h3 className="mt-6 font-manrope text-xl font-bold text-slate-900">{item.title}</h3>
                  <p className="mt-3 text-slate-600 leading-relaxed">{item.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ───── SIGNALS ───── */}
      <section className="py-20 bg-slate-50/80">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Powered by real market signals
            </h2>
            <p className="mt-4 text-lg text-slate-600">
              We don't guess. Every score is backed by live data from multiple sources.
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: TrendingUp, label: 'TikTok Trends', sub: 'Hashtag & engagement growth' },
              { icon: BarChart3, label: 'Amazon Movers', sub: 'Rank movement tracking' },
              { icon: Eye, label: 'Google Trends', sub: 'Search interest velocity' },
              { icon: DollarSign, label: 'Supplier Data', sub: 'AliExpress order velocity' },
              { icon: Video, label: 'TikTok Ads', sub: 'New ad campaign detection' },
              { icon: Store, label: 'Meta Ads', sub: 'Facebook ad library activity' },
              { icon: Package, label: 'CJ Dropshipping', sub: 'Supplier demand spikes' },
              { icon: Sparkles, label: 'AI Scoring', sub: '7-signal launch score' },
            ].map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.label} className="bg-white rounded-xl border border-slate-200 p-5 hover:border-indigo-200 hover:shadow-md transition-all duration-200">
                  <Icon className="h-5 w-5 text-indigo-600 mb-2.5" />
                  <p className="font-semibold text-sm text-slate-900">{s.label}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{s.sub}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ───── FEATURES ───── */}
      <section id="features" className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Everything you need to win at ecommerce
            </h2>
            <p className="mt-4 text-lg text-slate-600">
              From product discovery to store launch — one platform, zero guesswork.
            </p>
          </div>
          <div className="mt-16 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Zap, title: 'Early Trend Detection', desc: 'Spot exploding products before your competition.' },
              { icon: Rocket, title: 'One-Click Store Launch', desc: 'Generate a complete store with AI-crafted content.' },
              { icon: Video, title: 'AI Ad Generation', desc: 'TikTok scripts, Facebook copy, and video storyboards.' },
              { icon: Package, title: 'Auto Supplier Match', desc: 'Best suppliers matched automatically with costs.' },
              { icon: BarChart3, title: 'Transparent Scoring', desc: 'See exactly why each product scored the way it did.' },
              { icon: Star, title: 'Daily Opportunities', desc: 'Fresh winning products surfaced every single day.' },
            ].map((f) => {
              const Icon = f.icon;
              return (
                <div key={f.title} className="group rounded-2xl border border-slate-200 bg-white p-7 hover:border-indigo-200 hover:shadow-lg hover:shadow-indigo-50/50 transition-all duration-300">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-300">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-5 font-manrope text-base font-bold text-slate-900">{f.title}</h3>
                  <p className="mt-2 text-sm text-slate-600 leading-relaxed">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ───── PRICING ───── */}
      <section id="pricing" className="py-24 bg-slate-50/80" data-testid="pricing-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-lg text-slate-600">
              Start free. Upgrade when you're ready to scale.
            </p>
          </div>
          <div className="mt-16 grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {pricingPlans.map((plan) => (
              <div
                key={plan.id}
                data-testid={`pricing-card-${plan.id}`}
                className={`relative rounded-2xl border bg-white p-8 transition-all duration-300 ${
                  plan.popular
                    ? 'border-indigo-600 shadow-xl shadow-indigo-100/50 scale-[1.03]'
                    : 'border-slate-200 hover:border-slate-300 hover:shadow-lg'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                    <span className="inline-flex items-center rounded-full bg-indigo-600 px-4 py-1 text-xs font-semibold text-white shadow-sm">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="text-center">
                  <h3 className="font-manrope text-xl font-bold text-slate-900">{plan.name}</h3>
                  <p className="mt-1.5 text-sm text-slate-500">{plan.description}</p>
                  <div className="mt-5">
                    <span className="font-manrope text-5xl font-extrabold text-slate-900">£{plan.price}</span>
                    <span className="text-slate-500">/mo</span>
                  </div>
                </div>
                <ul className="mt-7 space-y-3.5">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2.5">
                      <Check className="h-4 w-4 flex-shrink-0 text-indigo-600 mt-0.5" />
                      <span className="text-sm text-slate-600">{f}</span>
                    </li>
                  ))}
                </ul>
                <Link to="/signup" className="block mt-7">
                  <Button
                    className={`w-full h-11 font-semibold transition-all ${
                      plan.popular
                        ? 'bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-200/50'
                        : 'bg-slate-900 hover:bg-slate-800'
                    }`}
                    data-testid={`pricing-cta-${plan.id}`}
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ───── FINAL CTA ───── */}
      <section className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="relative rounded-3xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-700" />
            <div className="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Ccircle%20cx%3D%221%22%20cy%3D%221%22%20r%3D%221%22%20fill%3D%22white%22/%3E%3C/svg%3E')]" />
            <div className="relative px-8 py-16 sm:px-16 text-center">
              <h2 className="font-manrope text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Ready to find your next winning product?
              </h2>
              <p className="mt-4 text-lg text-indigo-200 max-w-lg mx-auto">
                Join thousands of sellers who discover, launch, and scale with TrendScout.
              </p>
              <div className="mt-8">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-white text-indigo-700 hover:bg-indigo-50 text-base px-8 h-12 font-semibold shadow-lg hover:shadow-xl transition-all"
                    data-testid="final-cta-btn"
                  >
                    <Rocket className="mr-2 h-5 w-5" />
                    Start Free — No Credit Card
                    <ArrowRight className="ml-2 h-5 w-5" />
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

// ── Skeleton while loading ──────────────────────────

function DemoProductSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden animate-pulse">
      <div className="bg-slate-200 h-10" />
      <div className="p-6 space-y-4">
        <div className="flex gap-4">
          <div className="w-20 h-20 rounded-xl bg-slate-100" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-slate-100 rounded w-3/4" />
            <div className="h-3 bg-slate-100 rounded w-1/2" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="h-16 bg-slate-50 rounded-xl" />
          <div className="h-16 bg-slate-50 rounded-xl" />
          <div className="h-16 bg-slate-50 rounded-xl" />
        </div>
        <div className="h-10 bg-slate-100 rounded-lg" />
      </div>
    </div>
  );
}
