import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import LandingLayout from '@/components/layouts/LandingLayout';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { SignupGate } from '@/components/SignupGate';
import {
  Trophy, TrendingUp, Flame, Eye, Package, ChevronRight,
  Loader2, Crown, Zap, ArrowUp, Clock, Star,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

function formatViews(n) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`;
  return String(n);
}

const SCORE_CONFIG = {
  viral: { label: 'Viral', color: 'bg-rose-500 text-white', min: 85 },
  strong: { label: 'Strong', color: 'bg-emerald-500 text-white', min: 70 },
  emerging: { label: 'Emerging', color: 'bg-amber-500 text-white', min: 50 },
  weak: { label: 'Weak', color: 'bg-slate-400 text-white', min: 30 },
  dead: { label: 'Dead', color: 'bg-slate-300 text-slate-600', min: 0 },
};

function getScoreConfig(score) {
  if (score >= 85) return SCORE_CONFIG.viral;
  if (score >= 70) return SCORE_CONFIG.strong;
  if (score >= 50) return SCORE_CONFIG.emerging;
  if (score >= 30) return SCORE_CONFIG.weak;
  return SCORE_CONFIG.dead;
}

export default function TopTrendingPage() {
  const { isAuthenticated } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/public/top-trending`)
      .then(r => r.json())
      .then(d => { setProducts(d.products || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <LandingLayout>
      <Helmet>
        <title>Top 50 Trending Products - TrendScout Viral Leaderboard</title>
        <meta name="description" content="Discover the top 50 trending ecommerce products ranked by AI trend score. Find winning dropshipping products, viral TikTok products, and emerging trends." />
        <meta property="og:title" content="Top 50 Trending Products - TrendScout" />
        <meta property="og:description" content="The daily leaderboard of trending ecommerce products. AI-scored, real-time data." />
        <meta name="twitter:card" content="summary" />
        <link rel="canonical" href="https://www.trendscout.click/top-trending-products" />
      </Helmet>

      <div className="mx-auto max-w-5xl px-6 py-12" data-testid="top-trending-page">
        {/* Hero */}
        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-amber-200/50">
            <Trophy className="h-8 w-8 text-white" />
          </div>
          <h1 className="font-manrope text-4xl font-extrabold text-slate-900">
            Top Trending Products
          </h1>
          <p className="mt-3 text-slate-500 max-w-lg mx-auto">
            The daily leaderboard of the hottest ecommerce products, ranked by our AI trend score.
            Updated every 24 hours.
          </p>
        </div>

        {/* Score Legend */}
        <div className="flex items-center justify-center gap-3 mb-8 flex-wrap">
          {Object.entries(SCORE_CONFIG).map(([key, cfg]) => (
            <Badge key={key} className={`${cfg.color} rounded-full text-[10px] px-2.5 py-0.5`}>
              {cfg.min}+ {cfg.label}
            </Badge>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          </div>
        ) : (
          <div className="space-y-2">
            {(isAuthenticated ? products : products.slice(0, 3)).map((product) => {
              const sc = getScoreConfig(product.launch_score);
              const isTop3 = product.rank <= 3;
              const RankIcon = product.rank === 1 ? Crown : product.rank <= 3 ? Star : null;

              return (
                <Link
                  key={product.id}
                  to={`/trending/${product.slug}`}
                  className={`flex items-center gap-4 p-4 rounded-xl border transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 group ${
                    isTop3 ? 'bg-gradient-to-r from-amber-50/80 to-orange-50/40 border-amber-200 hover:border-amber-300' : 'bg-white border-slate-100 hover:border-indigo-200'
                  }`}
                  data-testid={`leaderboard-rank-${product.rank}`}
                >
                  {/* Rank */}
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    product.rank === 1 ? 'bg-gradient-to-br from-amber-400 to-orange-500 text-white shadow-md shadow-amber-200/50' :
                    product.rank === 2 ? 'bg-gradient-to-br from-slate-300 to-slate-400 text-white' :
                    product.rank === 3 ? 'bg-gradient-to-br from-amber-600 to-amber-700 text-white' :
                    'bg-slate-100 text-slate-500'
                  }`}>
                    {RankIcon ? <RankIcon className="h-4 w-4" /> : <span className="text-sm font-bold">{product.rank}</span>}
                  </div>

                  {/* Image */}
                  <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0 bg-slate-50 border border-slate-100">
                    {product.image_url ? (
                      <img src={product.image_url} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center"><Package className="h-5 w-5 text-slate-300" /></div>
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-slate-900 text-sm truncate group-hover:text-indigo-600 transition-colors">
                      {product.product_name}
                    </h3>
                    <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                      <span className="text-xs text-slate-400">{product.category}</span>
                      {product.tiktok_views > 0 && (
                        <Badge className="bg-rose-50 text-rose-600 border-0 rounded-full text-[10px]">
                          <Eye className="h-2.5 w-2.5 mr-0.5" />{formatViews(product.tiktok_views)}
                        </Badge>
                      )}
                      {product.growth_rate > 0 && (
                        <Badge className="bg-emerald-50 text-emerald-600 border-0 rounded-full text-[10px]">
                          <ArrowUp className="h-2.5 w-2.5 mr-0.5" />{product.growth_rate}%
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="hidden sm:flex items-center gap-4 flex-shrink-0">
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Margin</p>
                      <p className="text-sm font-bold text-emerald-600">{product.margin_percent}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-400">Competition</p>
                      <p className="text-sm font-medium text-slate-700">{product.competition_level}</p>
                    </div>
                  </div>

                  {/* Score */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Badge className={`${sc.color} rounded-lg text-sm font-bold px-2.5 py-1 min-w-[3rem] text-center`}>
                      {product.launch_score}
                    </Badge>
                    <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-indigo-500 transition-colors" />
                  </div>
                </Link>
              );
            })}
          </div>
        )}
        {!isAuthenticated && products.length > 3 && (
          <SignupGate
            title={`${products.length - 3} more top products`}
            description="Sign up to see the full leaderboard with scores, margins, and supplier data."
          />
        )}

        {/* CTA */}
        <div className="text-center mt-12 py-8 bg-gradient-to-r from-indigo-50 to-violet-50 rounded-2xl">
          <h2 className="font-manrope text-xl font-bold text-slate-900 mb-2">Want deeper intelligence?</h2>
          <p className="text-slate-500 text-sm mb-4 max-w-md mx-auto">
            Get AI-powered launch simulations, supplier intel, and ad creative generation for every product.
          </p>
          <Link to="/signup" className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold px-6 py-2.5 rounded-xl hover:shadow-lg transition-shadow" data-testid="leaderboard-cta">
            <Zap className="h-4 w-4" /> Start Free Trial
          </Link>
        </div>
      </div>
    </LandingLayout>
  );
}
