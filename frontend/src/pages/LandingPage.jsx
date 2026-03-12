import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, Rocket, Store, Zap, Check, ArrowRight,
  Sparkles, Package, Star, Eye, BarChart3, Search,
  Video, DollarSign, Truck, Shield, Radio, Target,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const pricingPlans = [
  {
    id: 'free', name: 'Free', price: '0',
    description: 'Get started with product research',
    features: ['Limited product insights', 'Report previews', '1 store', 'Limited watchlist & alerts', 'Community support'],
    cta: 'Get Started Free', popular: false,
  },
  {
    id: 'pro', name: 'Pro', price: '39',
    description: 'Full insights & multiple stores',
    features: ['Full product insights', 'Complete reports + PDF export', 'Up to 5 stores', 'Full watchlist & alerts', 'Ad discovery', 'Priority support'],
    cta: 'Upgrade to Pro', popular: true,
  },
  {
    id: 'elite', name: 'Elite', price: '99',
    description: 'Everything you need to dominate',
    features: ['Everything in Pro', 'Unlimited stores', 'Early trend detection', 'Automated reports & priority alerts', 'Direct Shopify publish', 'Dedicated support'],
    cta: 'Go Elite', popular: false,
  },
];

const TREND_BADGE = {
  Exploding: 'bg-red-100 text-red-700 border-red-200',
  Emerging: 'bg-orange-100 text-orange-700 border-orange-200',
  Rising: 'bg-amber-100 text-amber-700 border-amber-200',
  Stable: 'bg-sky-100 text-sky-700 border-sky-200',
  Declining: 'bg-slate-100 text-slate-500 border-slate-200',
};

export default function LandingPage() {
  const [featured, setFeatured] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/public/featured-product`)
      .then((r) => r.json())
      .then((d) => d.product && setFeatured(d.product))
      .catch(() => {});
  }, []);

  return (
    <LandingLayout>
      {/* ── HERO ── */}
      <section className="relative overflow-hidden" data-testid="hero-section">
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-[-30%] left-[5%] w-[700px] h-[700px] rounded-full bg-gradient-to-br from-indigo-100/70 to-sky-100/40 blur-[140px]" />
          <div className="absolute bottom-[-15%] right-[0%] w-[600px] h-[600px] rounded-full bg-gradient-to-tl from-violet-100/50 to-rose-100/30 blur-[120px]" />
          <div className="absolute top-[40%] left-[50%] w-[400px] h-[400px] rounded-full bg-gradient-to-r from-amber-50/40 to-transparent blur-[100px]" />
        </div>

        <div className="mx-auto max-w-7xl px-6 pt-20 pb-20 lg:px-8 lg:pt-28">
          <div className="grid lg:grid-cols-2 gap-14 items-center">
            {/* Copy */}
            <div className="max-w-xl">
              <div
                className="inline-flex items-center gap-2 rounded-full bg-white/80 backdrop-blur-sm border border-indigo-100/80 px-4 py-1.5 text-sm font-medium text-indigo-700 mb-6 shadow-sm"
                style={{ animation: 'fadeSlideUp 0.6s ease forwards' }}
              >
                <Sparkles className="h-4 w-4 text-indigo-500" />
                AI-Powered Product Intelligence
              </div>

              <h1
                className="font-manrope text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-[3.4rem] leading-[1.08]"
                style={{ animation: 'fadeSlideUp 0.7s ease forwards' }}
              >
                Find Winning Ecommerce Products{' '}
                <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 bg-clip-text text-transparent">
                  Before They Go Viral
                </span>
              </h1>

              <p
                className="mt-6 text-lg text-slate-600 leading-relaxed"
                style={{ animation: 'fadeSlideUp 0.8s ease forwards' }}
              >
                TrendScout scans real market signals to detect emerging products and helps you launch stores and ads in minutes.
              </p>

              <div
                className="mt-8 flex flex-col sm:flex-row gap-3"
                style={{ animation: 'fadeSlideUp 0.9s ease forwards' }}
              >
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-base px-8 h-13 font-semibold shadow-lg shadow-indigo-200/60 hover:shadow-xl hover:shadow-indigo-300/60 transition-all duration-300 rounded-xl"
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
                    className="text-base px-8 h-13 border-slate-200 bg-white/70 backdrop-blur-sm hover:border-indigo-300 hover:text-indigo-600 hover:bg-white transition-all duration-300 rounded-xl"
                    data-testid="hero-secondary-btn"
                  >
                    See How It Works
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </a>
              </div>

              <p className="mt-6 text-sm text-slate-500 flex items-center gap-5">
                <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-500" /> No credit card</span>
                <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-500" /> Real data only</span>
                <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-500" /> Launch in 3 clicks</span>
              </p>
            </div>

            {/* Live Demo Card */}
            <div className="relative" data-testid="live-demo-card" style={{ animation: 'fadeSlideUp 1s ease forwards' }}>
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-200/25 to-violet-200/25 rounded-3xl blur-3xl -z-10 scale-110" />
              {featured ? <LiveDemoCard featured={featured} /> : <DemoProductSkeleton />}
            </div>
          </div>
        </div>
      </section>

      {/* ── SOCIAL PROOF BAR ── */}
      <section className="py-6 border-y border-slate-100 bg-white/60 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-12 text-sm text-slate-500">
            <span className="flex items-center gap-2"><BarChart3 className="h-4 w-4 text-indigo-500" /> <strong className="text-slate-700">137+</strong> Products Analyzed</span>
            <span className="flex items-center gap-2"><Radio className="h-4 w-4 text-emerald-500" /> <strong className="text-slate-700">8</strong> Live Data Sources</span>
            <span className="flex items-center gap-2"><Target className="h-4 w-4 text-violet-500" /> <strong className="text-slate-700">7-Signal</strong> AI Scoring</span>
            <span className="flex items-center gap-2"><Shield className="h-4 w-4 text-amber-500" /> <strong className="text-slate-700">Real</strong> Data Only</span>
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" className="py-28 bg-white" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <Badge className="bg-indigo-50 text-indigo-600 border-indigo-100 mb-5 text-xs px-3 py-1 rounded-full">3 Simple Steps</Badge>
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              From discovery to launch in minutes
            </h2>
            <p className="mt-4 text-lg text-slate-500">
              TrendScout automates the entire product research and store launch workflow.
            </p>
          </div>

          <div className="mt-20 grid md:grid-cols-3 gap-8 relative">
            {/* Connector line (desktop) */}
            <div className="hidden md:block absolute top-16 left-[16.5%] right-[16.5%] h-px bg-gradient-to-r from-indigo-200 via-violet-200 to-rose-200" />
            {[
              { step: '01', icon: Search, title: 'Discover', description: 'TrendScout analyzes multiple data signals to detect early product trends.', gradient: 'from-indigo-500 to-sky-500', bg: 'bg-indigo-50' },
              { step: '02', icon: Store, title: 'Launch', description: 'Automatically generate store, product page and pricing.', gradient: 'from-violet-500 to-purple-500', bg: 'bg-violet-50' },
              { step: '03', icon: Video, title: 'Advertise', description: 'Generate TikTok ads and marketing creatives instantly.', gradient: 'from-rose-500 to-pink-500', bg: 'bg-rose-50' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.step}
                  className="group relative bg-white rounded-3xl border border-slate-100 p-8 hover:border-slate-200 hover:shadow-2xl hover:shadow-slate-100/80 transition-all duration-500"
                  data-testid={`how-step-${item.step}`}
                >
                  <div className={`relative z-10 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${item.gradient} text-white shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="h-7 w-7" />
                  </div>
                  <span className="font-mono text-6xl font-black text-slate-50 absolute top-4 right-6 select-none group-hover:text-slate-100 transition-colors">
                    {item.step}
                  </span>
                  <h3 className="mt-6 font-manrope text-xl font-bold text-slate-900">{item.title}</h3>
                  <p className="mt-3 text-slate-500 leading-relaxed text-sm">{item.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── SIGNALS ── */}
      <section className="py-24 bg-gradient-to-b from-slate-50/80 to-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Powered by real market signals
            </h2>
            <p className="mt-4 text-lg text-slate-500">
              We don't guess. Every score is backed by live data from multiple sources.
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: TrendingUp, label: 'TikTok Trends', sub: 'Hashtag & engagement growth', color: 'text-rose-500' },
              { icon: BarChart3, label: 'Amazon Movers', sub: 'Rank movement tracking', color: 'text-amber-500' },
              { icon: Eye, label: 'Google Trends', sub: 'Search interest velocity', color: 'text-sky-500' },
              { icon: DollarSign, label: 'Supplier Data', sub: 'AliExpress order velocity', color: 'text-emerald-500' },
              { icon: Video, label: 'TikTok Ads', sub: 'New ad campaign detection', color: 'text-violet-500' },
              { icon: Store, label: 'Meta Ads', sub: 'Facebook ad library activity', color: 'text-blue-500' },
              { icon: Package, label: 'CJ Dropshipping', sub: 'Supplier demand spikes', color: 'text-teal-500' },
              { icon: Sparkles, label: 'AI Scoring', sub: '7-signal launch score', color: 'text-indigo-500' },
            ].map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.label} className="group bg-white rounded-2xl border border-slate-100 p-5 hover:border-slate-200 hover:shadow-lg hover:shadow-slate-100/60 transition-all duration-300 hover:-translate-y-0.5">
                  <Icon className={`h-5 w-5 ${s.color} mb-3 group-hover:scale-110 transition-transform duration-300`} />
                  <p className="font-semibold text-sm text-slate-800">{s.label}</p>
                  <p className="text-xs text-slate-500 mt-1">{s.sub}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section id="features" className="py-28 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Everything you need to win at ecommerce
            </h2>
            <p className="mt-4 text-lg text-slate-500">
              From product discovery to store launch — one platform, zero guesswork.
            </p>
          </div>
          <div className="mt-16 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: Zap, title: 'Early Trend Detection', desc: 'Spot exploding products before your competition.', gradient: 'from-amber-500 to-orange-500' },
              { icon: Rocket, title: 'One-Click Store Launch', desc: 'Generate a complete store with AI-crafted content.', gradient: 'from-indigo-500 to-violet-500' },
              { icon: Video, title: 'AI Ad Generation', desc: 'TikTok scripts, Facebook copy, and video storyboards.', gradient: 'from-rose-500 to-pink-500' },
              { icon: Package, title: 'Auto Supplier Match', desc: 'Best suppliers matched automatically with costs.', gradient: 'from-emerald-500 to-teal-500' },
              { icon: BarChart3, title: 'Transparent Scoring', desc: 'See exactly why each product scored the way it did.', gradient: 'from-sky-500 to-blue-500' },
              { icon: Star, title: 'Daily Opportunities', desc: 'Fresh winning products surfaced every single day.', gradient: 'from-violet-500 to-purple-500' },
            ].map((f) => {
              const Icon = f.icon;
              return (
                <div key={f.title} className="group rounded-2xl border border-slate-100 bg-white p-7 hover:border-slate-200 hover:shadow-xl hover:shadow-slate-100/60 transition-all duration-400 hover:-translate-y-1">
                  <div className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${f.gradient} text-white shadow-sm group-hover:shadow-md group-hover:scale-105 transition-all duration-300`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-5 font-manrope text-base font-bold text-slate-900">{f.title}</h3>
                  <p className="mt-2 text-sm text-slate-500 leading-relaxed">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── PRICING ── */}
      <section id="pricing" className="py-28 bg-gradient-to-b from-slate-50/60 to-white" data-testid="pricing-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-lg text-slate-500">
              Start free. Upgrade when you're ready to scale.
            </p>
          </div>
          <div className="mt-16 grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {pricingPlans.map((plan) => (
              <div
                key={plan.id}
                data-testid={`pricing-card-${plan.id}`}
                className={`relative rounded-3xl border bg-white p-8 transition-all duration-400 hover:-translate-y-1 ${
                  plan.popular
                    ? 'border-indigo-500 shadow-2xl shadow-indigo-100/70 scale-[1.03]'
                    : 'border-slate-100 hover:border-slate-200 hover:shadow-xl hover:shadow-slate-100/60'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                    <span className="inline-flex items-center rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-1 text-xs font-semibold text-white shadow-md shadow-indigo-200/50">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="text-center">
                  <h3 className="font-manrope text-xl font-bold text-slate-900">{plan.name}</h3>
                  <p className="mt-1.5 text-sm text-slate-500">{plan.description}</p>
                  <div className="mt-5">
                    <span className="font-manrope text-5xl font-extrabold text-slate-900">&pound;{plan.price}</span>
                    <span className="text-slate-400 text-sm">/mo</span>
                  </div>
                </div>
                <ul className="mt-7 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2.5">
                      <Check className="h-4 w-4 flex-shrink-0 text-emerald-500 mt-0.5" />
                      <span className="text-sm text-slate-600">{f}</span>
                    </li>
                  ))}
                </ul>
                <Link to="/signup" className="block mt-7">
                  <Button
                    className={`w-full h-11 font-semibold rounded-xl transition-all duration-300 ${
                      plan.popular
                        ? 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 shadow-md shadow-indigo-200/50 hover:shadow-lg'
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

      {/* ── FINAL CTA ── */}
      <section className="py-28 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="relative rounded-[2rem] overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700" />
            <div className="absolute inset-0 opacity-[0.07]" style={{backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)', backgroundSize: '24px 24px'}} />
            <div className="relative px-8 py-20 sm:px-16 text-center">
              <h2 className="font-manrope text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Ready to find your next winning product?
              </h2>
              <p className="mt-5 text-lg text-indigo-200/90 max-w-lg mx-auto">
                Join sellers who discover, launch, and scale with TrendScout.
              </p>
              <div className="mt-10">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-white text-indigo-700 hover:bg-indigo-50 text-base px-10 h-13 font-semibold shadow-xl shadow-black/10 hover:shadow-2xl transition-all duration-300 rounded-xl"
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

      {/* Keyframe animation */}
      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </LandingLayout>
  );
}

/* ── Live Demo Card ── */

function LiveDemoCard({ featured }) {
  return (
    <div className="bg-white/90 backdrop-blur-md rounded-3xl border border-slate-200/70 shadow-2xl shadow-slate-200/50 overflow-hidden hover:shadow-indigo-100/40 transition-shadow duration-500">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 px-5 py-3.5 flex items-center justify-between">
        <span className="text-sm font-medium text-white/90 flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-amber-300" />
          AI Recommendation — Live
        </span>
        <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
      </div>
      {/* Body */}
      <div className="p-6">
        <div className="flex items-start gap-4">
          {featured.image_url ? (
            <img
              src={featured.image_url}
              alt={featured.product_name}
              className="w-20 h-20 rounded-2xl object-cover bg-slate-100 flex-shrink-0 shadow-sm"
            />
          ) : (
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-100 to-violet-100 flex items-center justify-center flex-shrink-0">
              <Package className="h-8 w-8 text-indigo-400" />
            </div>
          )}
          <div className="min-w-0 flex-1">
            <h3 className="font-bold text-slate-900 text-base leading-tight line-clamp-2">{featured.product_name}</h3>
            <div className="flex items-center gap-2 mt-1.5">
              <Badge variant="outline" className="text-xs rounded-full">{featured.category}</Badge>
              <Badge className={`text-xs border rounded-full ${TREND_BADGE[featured.trend_stage] || TREND_BADGE.Stable}`}>
                {featured.trend_stage}
              </Badge>
            </div>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-3 mt-5">
          <MetricPill value={featured.launch_score} label="Launch Score" color="indigo" />
          <MetricPill value={`${featured.success_probability}%`} label="Success Prob." color="emerald" />
          <MetricPill
            value={featured.estimated_profit > 0 ? `£${featured.estimated_profit.toFixed(0)}` : '—'}
            label="Est. Profit"
            color="amber"
          />
        </div>

        <div className="flex items-center gap-2 mt-4 text-sm text-slate-500">
          <Truck className="h-4 w-4" />
          <span>Supplier: {featured.supplier_source}</span>
        </div>

        <Link to="/signup">
          <Button
            className="w-full mt-4 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 font-semibold shadow-md shadow-indigo-200/40 hover:shadow-lg transition-all duration-300 rounded-xl"
            data-testid="demo-launch-btn"
          >
            <Rocket className="mr-2 h-4 w-4" />
            Launch This Product
          </Button>
        </Link>
      </div>
    </div>
  );
}

function MetricPill({ value, label, color }) {
  const bg = { indigo: 'bg-indigo-50/80', emerald: 'bg-emerald-50/80', amber: 'bg-amber-50/80' }[color] || 'bg-slate-50';
  const text = { indigo: 'text-indigo-700', emerald: 'text-emerald-700', amber: 'text-amber-700' }[color] || 'text-slate-700';
  const sub = { indigo: 'text-indigo-500', emerald: 'text-emerald-500', amber: 'text-amber-500' }[color] || 'text-slate-500';
  return (
    <div className={`${bg} rounded-2xl p-3 text-center`}>
      <p className={`text-2xl font-bold font-mono ${text}`}>{value}</p>
      <p className={`text-[11px] mt-0.5 font-medium ${sub}`}>{label}</p>
    </div>
  );
}

function DemoProductSkeleton() {
  return (
    <div className="bg-white/90 backdrop-blur-md rounded-3xl border border-slate-200/70 shadow-2xl overflow-hidden animate-pulse">
      <div className="bg-gradient-to-r from-slate-200 to-slate-300 h-12" />
      <div className="p-6 space-y-4">
        <div className="flex gap-4">
          <div className="w-20 h-20 rounded-2xl bg-slate-100" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-slate-100 rounded-lg w-3/4" />
            <div className="h-3 bg-slate-100 rounded-lg w-1/2" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="h-16 bg-slate-50 rounded-2xl" />
          <div className="h-16 bg-slate-50 rounded-2xl" />
          <div className="h-16 bg-slate-50 rounded-2xl" />
        </div>
        <div className="h-10 bg-slate-100 rounded-xl" />
      </div>
    </div>
  );
}
