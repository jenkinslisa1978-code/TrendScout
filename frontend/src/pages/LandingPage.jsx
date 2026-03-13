import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, Rocket, Store, Zap, Check, ArrowRight,
  Sparkles, Package, Star, Eye, BarChart3, Search,
  Video, DollarSign, Truck, Shield, Radio, Target, Bell,
  ChevronRight, ShoppingBag, Play, Users, Clock, Flame,
  Lock, Globe, Radar,
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
  const [featured, setFeatured] = useState(null);
  const [trendingProducts, setTrendingProducts] = useState([]);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/public/featured-product`).then(r => r.json()).catch(() => ({})),
      fetch(`${API_URL}/api/public/trending-products?limit=6`).then(r => r.json()).catch(() => ({ products: [] })),
    ]).then(([featData, trendData]) => {
      if (featData.product) setFeatured(featData.product);
      setTrendingProducts(trendData.products || []);
    });
  }, []);

  return (
    <LandingLayout>
      {/* ── HERO ── */}
      <section className="relative overflow-hidden bg-[#030712]" data-testid="hero-section">
        {/* Background effects */}
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
              Early Trend Intelligence Platform
            </div>

            <h1
              className="font-manrope text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl leading-[1.08]"
              style={{ animation: 'fadeSlideUp 0.6s ease forwards' }}
            >
              Discover Winning Products{' '}
              <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
                Before They Go Viral
              </span>
            </h1>

            <p
              className="mt-6 text-lg text-slate-400 leading-relaxed max-w-2xl mx-auto"
              style={{ animation: 'fadeSlideUp 0.7s ease forwards' }}
            >
              TrendScout scans TikTok, Amazon and social media to detect early product trends before they explode — giving you a first-mover advantage.
            </p>

            <div
              className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
              style={{ animation: 'fadeSlideUp 0.8s ease forwards' }}
            >
              <Link to="/trending-products">
                <Button
                  size="lg"
                  className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-13 font-semibold shadow-lg hover:shadow-xl transition-all duration-300 rounded-xl"
                  data-testid="hero-cta-btn"
                >
                  <Search className="mr-2 h-5 w-5" />
                  Discover Trending Products
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button
                  variant="ghost"
                  size="lg"
                  className="text-base px-8 h-13 text-slate-300 hover:text-white hover:bg-white/[0.06] transition-all duration-300 rounded-xl"
                  data-testid="hero-secondary-btn"
                >
                  <Play className="mr-2 h-4 w-4" />
                  See How It Works
                </Button>
              </a>
            </div>

            <div className="mt-8 flex items-center justify-center gap-6 text-sm text-slate-500" style={{ animation: 'fadeSlideUp 0.9s ease forwards' }}>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-400" /> Free to start</span>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-400" /> Real data only</span>
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

      {/* ── SOCIAL PROOF BAR ── */}
      <section className="py-5 border-b border-slate-100 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-12 text-sm text-slate-500">
            <span className="flex items-center gap-2"><Users className="h-4 w-4 text-indigo-500" /> <strong className="text-slate-700">2,400+</strong> Sellers using TrendScout</span>
            <span className="flex items-center gap-2"><TrendingUp className="h-4 w-4 text-emerald-500" /> <strong className="text-slate-700">137+</strong> Products tracked</span>
            <span className="flex items-center gap-2"><Radar className="h-4 w-4 text-violet-500" /> <strong className="text-slate-700">5</strong> Live data sources</span>
            <span className="flex items-center gap-2"><Zap className="h-4 w-4 text-amber-500" /> <strong className="text-slate-700">Early</strong> Trend detection</span>
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" className="py-28 bg-white" data-testid="how-it-works-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <Badge className="bg-indigo-50 text-indigo-600 border-indigo-100 mb-5 text-xs px-3 py-1 rounded-full">How TrendScout Works</Badge>
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Spot trends before your competitors
            </h2>
            <p className="mt-4 text-base text-slate-500">
              Our AI continuously monitors multiple platforms to detect products showing early signs of going viral.
            </p>
          </div>

          <div className="mt-20 grid md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-16 left-[16.5%] right-[16.5%] h-px bg-gradient-to-r from-indigo-200 via-violet-200 to-rose-200" />
            {[
              { step: '01', icon: Radar, title: 'AI Scans Trending Platforms', description: 'TrendScout monitors TikTok, Amazon movers, Google Trends and ad libraries 24/7 for early growth signals.', gradient: 'from-indigo-500 to-sky-500' },
              { step: '02', icon: Sparkles, title: 'Detects Early Growth Signals', description: 'Our algorithm identifies products with unusual velocity — rising searches, new ads, and supplier demand spikes.', gradient: 'from-violet-500 to-purple-500' },
              { step: '03', icon: Target, title: 'Surfaces High-Margin Opportunities', description: 'You get a scored list of products with supplier costs, margins, and confidence levels — ready to launch.', gradient: 'from-emerald-500 to-teal-500' },
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

      {/* ── WINNING PRODUCTS EXAMPLES ── */}
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

      {/* ── SIGNALS ── */}
      <section id="features" className="py-24 bg-gradient-to-b from-slate-50/80 to-white">
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
              Start free. Upgrade when you're ready.
            </h2>
            <p className="mt-4 text-base text-slate-500">
              See trending products for free. Unlock full intelligence with a paid plan.
            </p>
          </div>
          <div className="mt-16 grid md:grid-cols-4 gap-5 max-w-5xl mx-auto">
            {[
              {
                id: 'free', name: 'Free', price: '0',
                description: 'Browse trending products',
                features: ['3 product insights per day', 'Public trending feed', 'Basic trend scores', 'Category filters'],
                cta: 'Get Started Free', popular: false, gradient: false,
              },
              {
                id: 'starter', name: 'Starter', price: '19',
                description: 'Start finding winners',
                features: ['5 full analyses per day', 'Supplier intelligence', 'Ad generator', '3 launch simulations', '2 stores'],
                cta: 'Start for £19/mo', popular: false, gradient: false,
              },
              {
                id: 'pro', name: 'Pro', price: '39',
                description: 'Full research toolkit',
                features: ['Unlimited analysis', 'Full supplier intel', 'Ad A/B testing', 'Unlimited simulations', '5 stores', 'Advanced filters'],
                cta: 'Upgrade to Pro', popular: true, gradient: false,
              },
              {
                id: 'elite', name: 'Elite', price: '79',
                description: 'Scale with AI automation',
                features: ['Everything in Pro', 'Budget Optimizer', 'Radar alerts', 'LaunchPad', 'Unlimited stores', 'Priority support'],
                cta: 'Go Elite', popular: false, gradient: false,
              },
            ].map((plan) => (
              <div
                key={plan.id}
                data-testid={`pricing-card-${plan.id}`}
                className={`relative rounded-2xl border bg-white p-6 transition-all duration-400 hover:-translate-y-1 ${
                  plan.popular
                    ? 'border-indigo-500 shadow-2xl shadow-indigo-100/70 scale-[1.02]'
                    : 'border-slate-100 hover:border-slate-200 hover:shadow-xl hover:shadow-slate-100/60'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="inline-flex items-center rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-3 py-0.5 text-[11px] font-semibold text-white shadow-md">
                      Most Popular
                    </span>
                  </div>
                )}
                <div>
                  <h3 className="font-manrope text-lg font-bold text-slate-900">{plan.name}</h3>
                  <p className="mt-1 text-xs text-slate-500">{plan.description}</p>
                  <div className="mt-4">
                    <span className="font-manrope text-4xl font-extrabold text-slate-900">&pound;{plan.price}</span>
                    <span className="text-slate-400 text-sm">/mo</span>
                  </div>
                </div>
                <ul className="mt-5 space-y-2.5">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2">
                      <Check className="h-3.5 w-3.5 flex-shrink-0 text-emerald-500 mt-0.5" />
                      <span className="text-xs text-slate-600">{f}</span>
                    </li>
                  ))}
                </ul>
                <Link to="/signup" className="block mt-6">
                  <Button
                    className={`w-full h-10 text-sm font-semibold rounded-xl transition-all duration-300 ${
                      plan.popular
                        ? 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 shadow-md'
                        : plan.id === 'free' ? 'bg-slate-100 text-slate-900 hover:bg-slate-200' : 'bg-slate-900 hover:bg-slate-800'
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
                  >
                    <Rocket className="mr-2 h-5 w-5" />
                    Get Started Free
                  </Button>
                </Link>
                <Link to="/trending-products">
                  <Button
                    variant="ghost"
                    size="lg"
                    className="text-base px-8 h-13 text-slate-400 hover:text-white hover:bg-white/[0.06] rounded-xl"
                  >
                    Browse Trending Products
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
      `}</style>
    </LandingLayout>
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

/* ── Product Showcase Card (Winning Products Section) ── */
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
      {/* Image */}
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

      {/* Content */}
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

        {/* Metrics row */}
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
