import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { trackEvent, EVENTS } from '@/services/analytics';
import {
  TrendingUp, Rocket, Store, Zap, Check, ArrowRight,
  Sparkles, Package, Star, Eye, BarChart3, Search,
  Video, DollarSign, Truck, Shield, Target, Bell,
  ChevronRight, ShoppingBag, Play, Users, Clock, Flame,
  Globe, Radar, Database, ScanLine, Lightbulb,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const TREND_BADGE = {
  Exploding: 'bg-red-500/10 text-red-400 border-red-500/20',
  Emerging: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  Rising: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
  Stable: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  Declining: 'bg-slate-500/10 text-slate-500 border-slate-500/20',
};

export default function LandingPage() {
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/public/trending-products?limit=12`).then(r => r.json()).catch(() => ({ products: [] })),
      fetch(`${API_URL}/api/public/platform-stats`).then(r => r.json()).catch(() => null),
    ]).then(([trendData, statsData]) => {
      setTrendingProducts(trendData.products || []);
      setStats(statsData);
    });
  }, []);

  const formatStat = (n) => n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k` : n?.toLocaleString();

  return (
    <LandingLayout>
      {/* ── HERO ── */}
      <section className="relative overflow-hidden bg-[#030712]" data-testid="hero-section">
        <div className="absolute inset-0 -z-0">
          <div className="absolute top-[-20%] left-[10%] w-[600px] h-[600px] rounded-full bg-indigo-600/8 blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[5%] w-[500px] h-[500px] rounded-full bg-violet-600/6 blur-[100px]" />
          <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.3) 1px, transparent 0)', backgroundSize: '32px 32px'}} />
        </div>

        <div className="relative mx-auto max-w-7xl px-6 pt-24 pb-20 lg:px-8 lg:pt-32 lg:pb-28">
          <div className="text-center max-w-4xl mx-auto">
            <div
              className="inline-flex items-center gap-2 rounded-full bg-white/[0.06] backdrop-blur-sm border border-white/[0.08] px-4 py-1.5 text-sm font-medium text-indigo-300 mb-8"
              style={{ animation: 'fadeSlideUp 0.5s ease forwards' }}
            >
              <Radar className="h-3.5 w-3.5 text-indigo-400" />
              AI-Powered Ecommerce Intelligence
            </div>

            <h1
              className="font-manrope text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl leading-[1.08]"
              style={{ animation: 'fadeSlideUp 0.6s ease forwards' }}
              data-testid="hero-headline"
            >
              Discover Winning Ecommerce Products{' '}
              <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
                Before They Go Viral
              </span>
            </h1>

            <p
              className="mt-6 text-lg text-slate-400 leading-relaxed max-w-2xl mx-auto"
              style={{ animation: 'fadeSlideUp 0.7s ease forwards' }}
              data-testid="hero-subheadline"
            >
              TrendScout scans TikTok, Amazon and ecommerce stores with AI to identify products ready to scale — before competitors find them.
            </p>

            <div
              className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
              style={{ animation: 'fadeSlideUp 0.8s ease forwards' }}
            >
              <Link to="/signup">
                <Button
                  size="lg"
                  className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-13 font-semibold shadow-lg hover:shadow-xl transition-all duration-300 rounded-xl"
                  data-testid="hero-cta-btn"
                  onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'hero' })}
                >
                  <Search className="mr-2 h-5 w-5" />
                  Start Free Product Discovery
                </Button>
              </Link>
              <Link to="/trending-products">
                <Button
                  variant="ghost"
                  size="lg"
                  className="text-base px-8 h-13 text-slate-300 hover:text-white hover:bg-white/[0.06] transition-all duration-300 rounded-xl"
                  data-testid="hero-secondary-btn"
                  onClick={() => trackEvent(EVENTS.TRENDING_VIEW, { source: 'hero' })}
                >
                  <Eye className="mr-2 h-4 w-4" />
                  View Trending Products
                </Button>
              </Link>
            </div>

            <div className="mt-8 flex items-center justify-center gap-6 text-sm text-slate-500" style={{ animation: 'fadeSlideUp 0.9s ease forwards' }}>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-400" /> Free to start</span>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-400" /> No credit card required</span>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-400" /> Cancel anytime</span>
            </div>
          </div>

          {/* Live product preview cards */}
          {trendingProducts.length > 0 && (
            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto" style={{ animation: 'fadeSlideUp 1s ease forwards' }}>
              {trendingProducts.slice(0, 3).map((p, i) => (
                <MiniProductCard key={p.id} product={p} delay={i * 0.1} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ── TRENDING NOW TICKER ── */}
      {trendingProducts.length > 0 && (
        <TrendingTicker products={trendingProducts} />
      )}

      {/* ── SOCIAL PROOF STATS BAR ── */}
      <section className="py-6 border-b border-slate-100 bg-white" data-testid="social-proof-bar">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-8 sm:gap-16">
            <div className="text-center" data-testid="stat-products">
              <p className="font-manrope text-2xl font-extrabold text-slate-900">{stats ? formatStat(stats.products_analysed) : '12k+'}</p>
              <p className="text-xs text-slate-500 mt-0.5">Products Analysed</p>
            </div>
            <div className="hidden sm:block w-px h-8 bg-slate-200" />
            <div className="text-center" data-testid="stat-stores">
              <p className="font-manrope text-2xl font-extrabold text-slate-900">{stats ? formatStat(stats.stores_tracked) : '340+'}</p>
              <p className="text-xs text-slate-500 mt-0.5">Stores Tracked</p>
            </div>
            <div className="hidden sm:block w-px h-8 bg-slate-200" />
            <div className="text-center" data-testid="stat-tiktok">
              <p className="font-manrope text-2xl font-extrabold text-slate-900">{stats ? formatStat(stats.tiktok_scans_daily) : '15k'}</p>
              <p className="text-xs text-slate-500 mt-0.5">TikTok Videos Scanned Daily</p>
            </div>
            <div className="hidden sm:block w-px h-8 bg-slate-200" />
            <div className="text-center" data-testid="stat-users">
              <p className="font-manrope text-2xl font-extrabold text-slate-900">{stats ? formatStat(stats.active_users) : '2.4k+'}</p>
              <p className="text-xs text-slate-500 mt-0.5">Active Sellers</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" className="py-28 bg-white" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <Badge className="bg-indigo-50 text-indigo-600 border-indigo-100 mb-5 text-xs px-3 py-1 rounded-full">How TrendScout Works</Badge>
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              From data to decisions in 3 steps
            </h2>
            <p className="mt-4 text-base text-slate-500">
              Our AI scans thousands of signals across platforms to surface products ready to scale.
            </p>
          </div>

          <div className="mt-20 grid md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-16 left-[16.5%] right-[16.5%] h-px bg-gradient-to-r from-indigo-200 via-violet-200 to-emerald-200" />
            {[
              { step: '01', icon: ScanLine, title: 'AI Scans TikTok, Amazon & Ecommerce Stores', description: 'TrendScout monitors TikTok hashtags, Amazon movers, Google Trends and ad libraries 24/7 for product velocity and engagement signals.', gradient: 'from-indigo-500 to-sky-500' },
              { step: '02', icon: Sparkles, title: 'Algorithms Detect Product Velocity & Engagement', description: 'Our scoring engine identifies products with unusual growth — rising searches, new ad campaigns, supplier demand spikes, and social virality.', gradient: 'from-violet-500 to-purple-500' },
              { step: '03', icon: Target, title: 'You Discover Products Ready to Scale', description: 'Get a scored list of trending products with supplier costs, margins, competition levels, and AI-powered launch recommendations.', gradient: 'from-emerald-500 to-teal-500' },
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
                  <h3 className="mt-6 font-manrope text-lg font-bold text-slate-900">{item.title}</h3>
                  <p className="mt-3 text-slate-500 leading-relaxed text-sm">{item.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── WINNING PRODUCTS ── */}
      <section className="py-24 bg-gradient-to-b from-slate-50/80 to-white" data-testid="winning-products-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <Badge className="bg-emerald-50 text-emerald-600 border-emerald-100 mb-5 text-xs px-3 py-1 rounded-full">Live Data</Badge>
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Winning products detected this week
            </h2>
            <p className="mt-4 text-base text-slate-500">
              These are real products our AI flagged as trending. Updated daily.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {trendingProducts.slice(0, 6).map((product) => (
              <ProductShowcaseCard key={product.id} product={product} />
            ))}
          </div>

          <div className="text-center mt-10">
            <Link to="/trending-products">
              <Button size="lg" className="bg-slate-900 hover:bg-slate-800 text-base px-8 h-12 font-semibold rounded-xl" data-testid="see-all-products-btn">
                See All Trending Products
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ── BUILT FOR ── */}
      <section className="py-24 bg-white" data-testid="built-for-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Built for ecommerce sellers
            </h2>
            <p className="mt-4 text-base text-slate-500">
              Whether you're dropshipping, selling on TikTok Shop, or scaling your Shopify store.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { icon: ShoppingBag, title: 'Shopify Sellers', desc: 'Find products, launch stores, and generate ads — all from one dashboard.', color: 'from-green-500 to-emerald-500' },
              { icon: Video, title: 'TikTok Shop Sellers', desc: 'Detect products going viral on TikTok before the competition catches on.', color: 'from-rose-500 to-pink-500' },
              { icon: Truck, title: 'Dropshippers', desc: 'Supplier costs, shipping times, and margin calculations built right in.', color: 'from-sky-500 to-blue-500' },
              { icon: Package, title: 'Amazon FBA Sellers', desc: 'Track Amazon movers and spot emerging products before they saturate.', color: 'from-amber-500 to-orange-500' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="group rounded-2xl border border-slate-100 bg-white p-7 hover:border-slate-200 hover:shadow-xl hover:shadow-slate-100/60 transition-all duration-400 hover:-translate-y-1">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${item.color} text-white shadow-sm group-hover:shadow-md group-hover:scale-105 transition-all duration-300`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-5 font-manrope text-base font-bold text-slate-900">{item.title}</h3>
                  <p className="mt-2 text-sm text-slate-500 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── FEATURES / SIGNALS ── */}
      <section id="features" className="py-24 bg-gradient-to-b from-slate-50/80 to-white" data-testid="features-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Powered by real market signals
            </h2>
            <p className="mt-4 text-base text-slate-500">
              Every trend score is backed by live data from multiple sources. No guesswork.
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: TrendingUp, label: 'TikTok Trends', sub: 'Hashtag & engagement velocity', color: 'text-rose-500' },
              { icon: BarChart3, label: 'Amazon Movers', sub: 'Sales rank movement tracking', color: 'text-amber-500' },
              { icon: Eye, label: 'Google Trends', sub: 'Search interest acceleration', color: 'text-sky-500' },
              { icon: DollarSign, label: 'Supplier Data', sub: 'Order velocity from CJ & AliExpress', color: 'text-emerald-500' },
              { icon: Video, label: 'TikTok Ads', sub: 'New ad campaign detection', color: 'text-violet-500' },
              { icon: Store, label: 'Meta Ads', sub: 'Facebook ad library tracking', color: 'text-blue-500' },
              { icon: Package, label: 'CJ Dropshipping', sub: 'Live supplier demand data', color: 'text-teal-500' },
              { icon: Sparkles, label: 'AI Scoring', sub: 'Multi-signal confidence score', color: 'text-indigo-500' },
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

      {/* ── PRICING ── */}
      <section id="pricing" className="py-28 bg-white" data-testid="pricing-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Simple pricing. Powerful intelligence.
            </h2>
            <p className="mt-4 text-base text-slate-500">
              One winning product can generate &pound;10,000+ revenue.<br />
              TrendScout costs less than testing a single TikTok ad campaign.
            </p>
          </div>
          <div className="mt-16 grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              {
                id: 'starter', name: 'Starter', price: '19',
                description: 'Start finding winners',
                features: ['10 product views per day', 'Basic trend insights', 'Daily product updates', 'Category filters', 'Trend score access'],
                cta: 'Start 7-Day Free Trial', popular: false,
              },
              {
                id: 'growth', name: 'Growth', price: '49',
                description: 'Full product intelligence',
                features: ['Unlimited product discovery', 'Trend score analytics', 'AI ad creative generator', 'Trend alerts & notifications', 'Supplier intelligence', 'Product profit calculator'],
                cta: 'Start 7-Day Free Trial', popular: true,
              },
              {
                id: 'pro', name: 'Pro', price: '99',
                description: 'Scale with advanced tools',
                features: ['Everything in Growth', 'Competitor store tracking', 'AI launch simulator', 'Advanced analytics', 'Unlimited insights', 'Priority support'],
                cta: 'Start 7-Day Free Trial', popular: false,
              },
            ].map((plan) => (
              <div
                key={plan.id}
                data-testid={`pricing-card-${plan.id}`}
                className={`relative rounded-2xl border bg-white p-7 transition-all duration-400 hover:-translate-y-1 ${
                  plan.popular
                    ? 'border-indigo-500 shadow-2xl shadow-indigo-100/70 scale-[1.03]'
                    : 'border-slate-100 hover:border-slate-200 hover:shadow-xl hover:shadow-slate-100/60'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                    <span className="inline-flex items-center rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-1 text-xs font-semibold text-white shadow-md">
                      Recommended
                    </span>
                  </div>
                )}
                <div>
                  <h3 className="font-manrope text-lg font-bold text-slate-900">{plan.name}</h3>
                  <p className="mt-1 text-xs text-slate-500">{plan.description}</p>
                  <div className="mt-5">
                    <span className="font-manrope text-4xl font-extrabold text-slate-900">&pound;{plan.price}</span>
                    <span className="text-slate-400 text-sm">/month</span>
                  </div>
                </div>
                <ul className="mt-6 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2.5">
                      <Check className="h-4 w-4 flex-shrink-0 text-emerald-500 mt-0.5" />
                      <span className="text-sm text-slate-600">{f}</span>
                    </li>
                  ))}
                </ul>
                <Link to="/signup" className="block mt-7">
                  <Button
                    className={`w-full h-11 text-sm font-semibold rounded-xl transition-all duration-300 ${
                      plan.popular
                        ? 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 shadow-md text-white'
                        : 'bg-slate-900 hover:bg-slate-800 text-white'
                    }`}
                    data-testid={`pricing-cta-${plan.id}`}
                    onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'landing_pricing', plan: plan.id })}
                  >
                    {plan.cta}
                  </Button>
                </Link>
                <p className="text-center text-xs text-slate-400 mt-3">7-day free trial. Cancel anytime.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ── */}
      <section className="py-24 bg-gradient-to-b from-slate-50/60 to-white" data-testid="testimonials-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Trusted by ecommerce sellers
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { quote: "TrendScout found me a winning product on day one. The trend score was spot on — I hit profitability in week two.", name: "Sarah K.", role: "Shopify Seller, UK", stars: 5 },
              { quote: "I used to spend hours scrolling TikTok for product ideas. Now TrendScout does it for me and shows me the margins too.", name: "James M.", role: "TikTok Shop Seller", stars: 5 },
              { quote: "The early trend detection is incredible. I launched a product that went viral a week after TrendScout flagged it.", name: "Priya D.", role: "Dropshipping Agency Owner", stars: 5 },
            ].map((t, i) => (
              <div key={i} className="bg-white rounded-2xl p-7 border border-slate-100 hover:shadow-lg transition-all duration-300" data-testid={`testimonial-${i}`}>
                <div className="flex gap-0.5 mb-4">
                  {Array.from({ length: t.stars }).map((_, j) => (
                    <Star key={j} className="h-4 w-4 fill-amber-400 text-amber-400" />
                  ))}
                </div>
                <p className="text-slate-700 text-sm leading-relaxed">"{t.quote}"</p>
                <div className="mt-5 flex items-center gap-3">
                  <div className="h-9 w-9 rounded-full bg-gradient-to-br from-indigo-400 to-violet-500 flex items-center justify-center text-white font-bold text-sm">
                    {t.name.charAt(0)}
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800 text-sm">{t.name}</p>
                    <p className="text-xs text-slate-500">{t.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FINAL CTA ── */}
      <section className="py-28 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="relative rounded-[2rem] overflow-hidden">
            <div className="absolute inset-0 bg-[#030712]" />
            <div className="absolute inset-0 opacity-[0.04]" style={{backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)', backgroundSize: '24px 24px'}} />
            <div className="absolute top-[-30%] right-[10%] w-[400px] h-[400px] rounded-full bg-indigo-600/10 blur-[100px]" />
            <div className="relative px-8 py-20 sm:px-16 text-center">
              <h2 className="font-manrope text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Stop researching. Start launching.
              </h2>
              <p className="mt-5 text-lg text-slate-400 max-w-lg mx-auto">
                Join thousands of sellers who discover winning products before they trend.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-white text-slate-900 hover:bg-slate-100 text-base px-10 h-13 font-semibold shadow-xl hover:shadow-2xl transition-all duration-300 rounded-xl"
                    data-testid="final-cta-btn"
                    onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'final_cta' })}
                  >
                    <Rocket className="mr-2 h-5 w-5" />
                    Start Free Product Discovery
                  </Button>
                </Link>
                <Link to="/trending-products">
                  <Button
                    variant="ghost"
                    size="lg"
                    className="text-base px-8 h-13 text-slate-400 hover:text-white hover:bg-white/[0.06] rounded-xl"
                  >
                    View Trending Products
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes tickerScroll {
          0%   { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .ticker-track {
          animation: tickerScroll 40s linear infinite;
        }
        .ticker-track:hover {
          animation-play-state: paused;
        }
      `}</style>
    </LandingLayout>
  );
}

/* ── Trending Now Ticker ── */
function TrendingTicker({ products }) {
  // Duplicate for seamless loop
  const items = [...products, ...products];

  const timeLabels = ['2m ago', '5m ago', '8m ago', '12m ago', '15m ago', '18m ago', '22m ago', '25m ago', '31m ago', '38m ago', '42m ago', '47m ago'];

  return (
    <section className="relative bg-[#0a0f1e] border-y border-white/[0.04] overflow-hidden" data-testid="trending-ticker">
      <div className="absolute inset-0 bg-gradient-to-r from-[#0a0f1e] via-transparent to-[#0a0f1e] z-10 pointer-events-none" />
      <div className="flex items-center">
        {/* Label */}
        <div className="flex-shrink-0 flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-red-500/20 to-transparent border-r border-white/[0.06] z-20 relative">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500" />
          </span>
          <span className="text-xs font-semibold text-red-300 uppercase tracking-wider whitespace-nowrap">Trending Now</span>
        </div>

        {/* Scrolling track */}
        <div className="overflow-hidden flex-1">
          <div className="ticker-track flex items-center gap-0 whitespace-nowrap py-2.5">
            {items.map((p, i) => {
              const scoreColor = p.launch_score >= 75 ? 'text-emerald-400' : p.launch_score >= 50 ? 'text-amber-400' : 'text-sky-400';
              const dotColor = p.launch_score >= 75 ? 'bg-emerald-400' : p.launch_score >= 50 ? 'bg-amber-400' : 'bg-sky-400';
              return (
                <Link
                  key={`${p.id}-${i}`}
                  to={`/trending/${p.slug}`}
                  className="inline-flex items-center gap-3 px-5 group"
                  data-testid={i < products.length ? `ticker-item-${p.id}` : undefined}
                >
                  <div className={`h-1.5 w-1.5 rounded-full ${dotColor} flex-shrink-0 opacity-60`} />
                  {p.image_url && (
                    <img src={p.image_url} alt="" className="h-6 w-6 rounded-md object-cover flex-shrink-0 opacity-80 group-hover:opacity-100 transition-opacity" />
                  )}
                  <span className="text-[13px] text-slate-400 group-hover:text-white transition-colors truncate max-w-[180px]">
                    {p.product_name}
                  </span>
                  <span className={`font-mono text-xs font-bold ${scoreColor}`}>
                    {p.launch_score}
                  </span>
                  <span className="text-[11px] text-slate-600">
                    {timeLabels[i % timeLabels.length]}
                  </span>
                  <div className="h-3 w-px bg-white/[0.06] mx-2 flex-shrink-0" />
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── Mini Product Card (Hero) ── */
function MiniProductCard({ product, delay }) {
  const confidenceLabel = product.launch_score >= 75 ? 'High Confidence' : product.launch_score >= 50 ? 'Emerging' : 'Experimental';
  const confidenceColor = product.launch_score >= 75 ? 'text-emerald-400 bg-emerald-500/10' : product.launch_score >= 50 ? 'text-amber-400 bg-amber-500/10' : 'text-slate-400 bg-slate-500/10';
  const confidenceIcon = product.launch_score >= 75 ? Flame : product.launch_score >= 50 ? Zap : Clock;
  const CIcon = confidenceIcon;

  return (
    <Link
      to={`/trending/${product.slug}`}
      className="block bg-white/[0.04] backdrop-blur-sm border border-white/[0.08] rounded-2xl p-4 hover:bg-white/[0.07] hover:border-white/[0.12] transition-all duration-300"
      style={{ animation: `fadeSlideUp ${0.9 + delay}s ease forwards` }}
    >
      <div className="flex items-center gap-3">
        {product.image_url ? (
          <img src={product.image_url} alt="" className="w-10 h-10 rounded-xl object-cover bg-white/10 flex-shrink-0" />
        ) : (
          <div className="w-10 h-10 rounded-xl bg-white/[0.06] flex items-center justify-center flex-shrink-0">
            <Package className="h-5 w-5 text-slate-500" />
          </div>
        )}
        <div className="min-w-0 flex-1">
          <p className="text-white text-sm font-semibold truncate">{product.product_name}</p>
          <div className="flex items-center gap-2 mt-1">
            <span className={`inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full ${confidenceColor}`}>
              <CIcon className="h-3 w-3" />
              {confidenceLabel}
            </span>
            <span className="text-emerald-400 text-xs font-medium">{product.margin_percent}% margin</span>
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <p className="font-mono text-xl font-bold text-indigo-400">{product.launch_score}</p>
          <p className="text-[10px] text-slate-500">Score</p>
        </div>
      </div>
    </Link>
  );
}

/* ── Product Showcase Card ── */
function ProductShowcaseCard({ product }) {
  const confidenceLabel = product.launch_score >= 75 ? 'High Confidence' : product.launch_score >= 50 ? 'Emerging Opportunity' : 'Experimental';
  const confidenceColor = product.launch_score >= 75
    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
    : product.launch_score >= 50
    ? 'bg-amber-50 text-amber-700 border-amber-200'
    : 'bg-slate-50 text-slate-600 border-slate-200';
  const confidenceIcon = product.launch_score >= 75 ? Flame : product.launch_score >= 50 ? Zap : Clock;
  const CIcon = confidenceIcon;

  return (
    <Link
      to={`/trending/${product.slug}`}
      className="group block bg-white rounded-2xl border border-slate-100 overflow-hidden hover:border-slate-200 hover:shadow-xl hover:shadow-slate-100/60 transition-all duration-400 hover:-translate-y-1"
      data-testid={`product-card-${product.id}`}
    >
      <div className="relative h-40 bg-gradient-to-br from-slate-50 to-slate-100 overflow-hidden">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Package className="h-12 w-12 text-slate-300" />
          </div>
        )}
        <div className="absolute top-3 right-3">
          <Badge className={`text-[10px] border rounded-full ${confidenceColor}`}>
            <CIcon className="h-3 w-3 mr-1" />
            {confidenceLabel}
          </Badge>
        </div>
        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm rounded-full px-2 py-0.5">
          <span className="font-mono text-sm font-bold text-indigo-600">{product.launch_score}</span>
        </div>
      </div>

      <div className="p-4">
        <h3 className="font-semibold text-slate-900 text-sm line-clamp-1 group-hover:text-indigo-600 transition-colors">{product.product_name}</h3>
        <div className="flex items-center gap-2 mt-1.5">
          {product.category && (
            <Badge variant="outline" className="text-[10px] text-slate-500 border-slate-200 rounded-full">{product.category}</Badge>
          )}
          {product.trend_stage && (
            <Badge className={`text-[10px] border rounded-full ${TREND_BADGE[product.trend_stage] || TREND_BADGE.Stable}`}>
              {product.trend_stage}
            </Badge>
          )}
        </div>

        <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-50">
          <div>
            <p className="text-xs text-slate-400">Margin</p>
            <p className="text-sm font-semibold text-emerald-600">{product.margin_percent}%</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Supplier</p>
            <p className="text-sm font-semibold text-slate-700">&pound;{(product.supplier_cost || 0).toFixed(0)}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Retail</p>
            <p className="text-sm font-semibold text-slate-700">&pound;{(product.retail_price || 0).toFixed(0)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <TrendingUp className="h-3 w-3" />
            {product.growth_rate || 0}% growth
          </span>
          <span className="text-xs text-indigo-500 font-medium group-hover:text-indigo-600 flex items-center gap-1">
            View Details <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </div>
    </Link>
  );
}
