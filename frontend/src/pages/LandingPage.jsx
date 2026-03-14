import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import {
  TrendingUp, Rocket, Zap, Check, ArrowRight,
  Search, Package, Target, Eye, ChevronRight,
  Flame, Clock, Lightbulb, ArrowDown,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

function getShortReason(product) {
  const reasons = [];
  if (product.launch_score >= 80) reasons.push('Very strong trend signals');
  else if (product.launch_score >= 65) reasons.push('Strong trend momentum');
  else if (product.launch_score >= 50) reasons.push('Growing market interest');

  if (product.margin_percent >= 60) reasons.push('high margins');
  else if (product.margin_percent >= 40) reasons.push('solid margins');

  if (product.growth_rate >= 100) reasons.push('rapid growth');
  else if (product.growth_rate >= 40) reasons.push('steady growth');

  if (product.tiktok_views >= 1000000) reasons.push('viral social proof');
  else if (product.tiktok_views >= 100000) reasons.push('strong social traction');

  if (product.trend_stage === 'Exploding') reasons.push('exploding demand');
  else if (product.trend_stage === 'Emerging') reasons.push('emerging opportunity');

  if (reasons.length === 0) return 'Monitored for growth potential';
  if (reasons.length === 1) return reasons[0].charAt(0).toUpperCase() + reasons[0].slice(1);
  return reasons[0].charAt(0).toUpperCase() + reasons[0].slice(1) + ' and ' + reasons[1];
}

export default function LandingPage() {
  const [trendingProducts, setTrendingProducts] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/api/public/trending-products?limit=6`)
      .then(r => r.json())
      .then(d => setTrendingProducts(d.products || []))
      .catch(() => {});
  }, []);

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
          <div className="text-center max-w-3xl mx-auto">
            <h1
              className="font-manrope text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl leading-[1.08]"
              style={{ animation: 'fadeSlideUp 0.6s ease forwards' }}
              data-testid="hero-headline"
            >
              Find products worth testing{' '}
              <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
                before you waste money on ads
              </span>
            </h1>

            <p
              className="mt-6 text-lg text-slate-400 leading-relaxed max-w-2xl mx-auto"
              style={{ animation: 'fadeSlideUp 0.7s ease forwards' }}
              data-testid="hero-subheadline"
            >
              TrendScout helps ecommerce sellers discover trending products, evaluate their potential, and get simple launch ideas quickly.
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
                  onClick={() => trackEvent(EVENTS.TRENDING_VIEW, { source: 'hero' })}
                >
                  <Search className="mr-2 h-5 w-5" />
                  See Trending Products
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button
                  variant="ghost"
                  size="lg"
                  className="text-base px-8 h-13 text-slate-300 hover:text-white hover:bg-white/[0.06] transition-all duration-300 rounded-xl"
                  data-testid="hero-secondary-btn"
                >
                  <ArrowDown className="mr-2 h-4 w-4" />
                  How It Works
                </Button>
              </a>
            </div>

            <div className="mt-8 flex items-center justify-center gap-6 text-sm text-slate-500" style={{ animation: 'fadeSlideUp 0.9s ease forwards' }}>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-400" /> Free to start</span>
              <span className="flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-400" /> No credit card required</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── HOW TRENDSCOUT WORKS ── */}
      <section id="how-it-works" className="py-24 bg-white" data-testid="how-it-works-section">
        <div className="mx-auto max-w-5xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              How TrendScout Works
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-14 left-[16.5%] right-[16.5%] h-px bg-gradient-to-r from-indigo-200 via-violet-200 to-emerald-200" />
            {[
              {
                step: '1',
                icon: Search,
                title: 'Find products',
                description: 'Browse products gaining traction online.',
                gradient: 'from-indigo-500 to-sky-500',
              },
              {
                step: '2',
                icon: Eye,
                title: 'Check potential',
                description: 'See whether a product looks worth testing.',
                gradient: 'from-violet-500 to-purple-500',
              },
              {
                step: '3',
                icon: Rocket,
                title: 'Launch faster',
                description: 'Get ad ideas and a simple launch plan.',
                gradient: 'from-emerald-500 to-teal-500',
              },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.step}
                  className="group relative bg-white rounded-3xl border border-slate-100 p-8 hover:border-slate-200 hover:shadow-2xl hover:shadow-slate-100/80 transition-all duration-500 text-center"
                  data-testid={`how-step-${item.step}`}
                >
                  <div className={`relative z-10 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${item.gradient} text-white shadow-lg mx-auto group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="h-7 w-7" />
                  </div>
                  <h3 className="mt-6 font-manrope text-lg font-bold text-slate-900">{item.title}</h3>
                  <p className="mt-2 text-slate-500 text-sm">{item.description}</p>
                </div>
              );
            })}
          </div>

          {/* Start Here Panel */}
          <div className="mt-16 bg-gradient-to-br from-slate-50 to-indigo-50/50 rounded-2xl border border-slate-200/60 p-8" data-testid="start-here-panel">
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shadow-lg">
                  <Lightbulb className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="flex-1">
                <h3 className="font-manrope text-lg font-bold text-slate-900">New here? Start with these 3 steps.</h3>
                <ol className="mt-3 space-y-2">
                  <li className="flex items-center gap-3 text-sm text-slate-600">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex items-center justify-center">1</span>
                    Browse trending products
                  </li>
                  <li className="flex items-center gap-3 text-sm text-slate-600">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-100 text-violet-600 text-xs font-bold flex items-center justify-center">2</span>
                    Open a product analysis
                  </li>
                  <li className="flex items-center gap-3 text-sm text-slate-600">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 text-xs font-bold flex items-center justify-center">3</span>
                    Decide if it's worth testing
                  </li>
                </ol>
              </div>
              <div className="flex-shrink-0">
                <Link to="/trending-products">
                  <Button
                    className="bg-slate-900 hover:bg-slate-800 text-white font-semibold px-6 h-11 rounded-xl"
                    data-testid="start-now-btn"
                    onClick={() => trackEvent(EVENTS.TRENDING_VIEW, { source: 'start_here' })}
                  >
                    Start Now
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── TRENDING PRODUCTS ── */}
      <section className="py-24 bg-gradient-to-b from-slate-50/80 to-white" data-testid="winning-products-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Trending products right now
            </h2>
            <p className="mt-4 text-base text-slate-500">
              Real products our AI flagged as trending. Updated daily.
            </p>
          </div>

          {trendingProducts.length > 0 ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {trendingProducts.slice(0, 6).map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 text-slate-400">
              <Package className="h-10 w-10 mx-auto mb-3 text-slate-300" />
              <p>Loading trending products...</p>
            </div>
          )}

          <div className="text-center mt-10">
            <Link to="/trending-products">
              <Button
                size="lg"
                className="bg-slate-900 hover:bg-slate-800 text-base px-8 h-12 font-semibold rounded-xl"
                data-testid="see-all-products-btn"
              >
                See All Trending Products
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ── WHY USE TRENDSCOUT ── */}
      <section className="py-24 bg-white" data-testid="why-section">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
              Why use TrendScout
            </h2>
            <p className="mt-4 text-base text-slate-500">
              Stop guessing. Start with data.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { icon: TrendingUp, title: 'Real trend data', desc: 'Every product score is backed by live signals from TikTok, Amazon, and Google Trends.', color: 'from-indigo-500 to-sky-500' },
              { icon: Target, title: 'Know before you spend', desc: 'See margins, supplier costs, and competition levels before investing in ads.', color: 'from-violet-500 to-purple-500' },
              { icon: Zap, title: 'Ad ideas included', desc: 'Get AI-generated ad angles and target audience suggestions for every product.', color: 'from-amber-500 to-orange-500' },
              { icon: Flame, title: 'Updated daily', desc: 'New products and scores every day so you never miss an opportunity.', color: 'from-emerald-500 to-teal-500' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="group rounded-2xl border border-slate-100 bg-white p-7 hover:border-slate-200 hover:shadow-xl hover:shadow-slate-100/60 transition-all duration-400 hover:-translate-y-1" data-testid={`why-card-${item.title.toLowerCase().replace(/\s/g, '-')}`}>
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

      {/* ── FINAL CTA ── */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="relative rounded-[2rem] overflow-hidden">
            <div className="absolute inset-0 bg-[#030712]" />
            <div className="absolute inset-0 opacity-[0.04]" style={{backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)', backgroundSize: '24px 24px'}} />
            <div className="absolute top-[-30%] right-[10%] w-[400px] h-[400px] rounded-full bg-indigo-600/10 blur-[100px]" />
            <div className="relative px-8 py-16 sm:px-16 text-center">
              <h2 className="font-manrope text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Ready to find your next product?
              </h2>
              <p className="mt-4 text-lg text-slate-400 max-w-lg mx-auto">
                Browse trending products now — no account needed.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link to="/trending-products">
                  <Button
                    size="lg"
                    className="bg-white text-slate-900 hover:bg-slate-100 text-base px-10 h-13 font-semibold shadow-xl hover:shadow-2xl transition-all duration-300 rounded-xl"
                    data-testid="final-cta-btn"
                    onClick={() => trackEvent(EVENTS.TRENDING_VIEW, { source: 'final_cta' })}
                  >
                    See Trending Products
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button
                    variant="ghost"
                    size="lg"
                    className="text-base px-8 h-13 text-slate-400 hover:text-white hover:bg-white/[0.06] rounded-xl"
                    data-testid="final-signup-btn"
                    onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'final_cta' })}
                  >
                    Create Free Account
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

/* ── Product Card ── */
function ProductCard({ product }) {
  const scoreColor = product.launch_score >= 75
    ? 'text-emerald-600 bg-emerald-50'
    : product.launch_score >= 50
    ? 'text-amber-600 bg-amber-50'
    : 'text-slate-600 bg-slate-50';

  const reason = getShortReason(product);

  return (
    <Link
      to={`/trending/${product.slug}`}
      className="group block bg-white rounded-2xl border border-slate-100 overflow-hidden hover:border-slate-200 hover:shadow-xl hover:shadow-slate-100/60 transition-all duration-400 hover:-translate-y-1"
      data-testid={`product-card-${product.id}`}
    >
      <div className="relative h-40 bg-gradient-to-br from-slate-50 to-slate-100 overflow-hidden">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Package className="h-12 w-12 text-slate-300" />
          </div>
        )}
        <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-sm rounded-xl px-2.5 py-1 shadow-sm">
          <span className="font-mono text-sm font-bold text-indigo-600">{product.launch_score}</span>
          <span className="text-[10px] text-slate-400 ml-0.5">/100</span>
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-slate-900 text-sm line-clamp-1 group-hover:text-indigo-600 transition-colors">
          {product.product_name}
        </h3>
        <p className="mt-1.5 text-xs text-slate-500 leading-relaxed line-clamp-2">
          {reason}
        </p>
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-50">
          <div className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${scoreColor}`}>
            Score: {product.launch_score}/100
          </div>
          <span className="text-xs text-indigo-500 font-medium group-hover:text-indigo-600 flex items-center gap-0.5">
            View <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </div>
    </Link>
  );
}
