import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, Star, Tag, Loader2, ArrowRight, Zap,
  CheckCircle, Eye,
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function TrendingIndexPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/api/public/trending-index`);
        if (res.ok) {
          const d = await res.json();
          setProducts(d.products || []);
          setCategories(d.categories || []);
        }
      } catch {}
      setLoading(false);
    })();
  }, []);

  const filtered = filter === 'all' ? products : products.filter(p => p.category === filter);

  return (
    <>
      <Helmet>
        <title>Trending Products to Dropship in 2026 | TrendScout</title>
        <meta name="description" content="Discover the highest-scoring trending products for dropshipping. AI-analyzed launch scores, competition levels, and profit estimates updated daily." />
        <meta property="og:title" content="Trending Products to Dropship | TrendScout" />
        <meta property="og:description" content="AI-scored trending products for dropshipping. Updated daily." />
        <link rel="canonical" href={`${window.location.origin}/trending`} />
      </Helmet>

      <div className="min-h-screen bg-slate-50" data-testid="trending-index-page">
        {/* Nav */}
        <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
          <Link to="/" className="text-lg font-bold text-slate-900">TrendScout</Link>
          <Link to="/register">
            <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700" data-testid="seo-signup-btn">
              Start Free Trial
            </Button>
          </Link>
        </nav>

        <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
          {/* Hero */}
          <div className="text-center max-w-2xl mx-auto">
            <h1 className="text-3xl sm:text-4xl font-black text-slate-900">Trending Products to Dropship</h1>
            <p className="text-sm text-slate-500 mt-3">AI-scored products ranked by launch potential. Updated daily with TikTok signals, ad activity, and competition data.</p>
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap justify-center gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${filter === 'all' ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'}`}
              data-testid="filter-all"
            >
              All ({products.length})
            </button>
            {categories.map(c => (
              <button
                key={c}
                onClick={() => setFilter(c)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${filter === c ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'}`}
              >
                {c}
              </button>
            ))}
          </div>

          {/* Products Grid */}
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5" data-testid="trending-grid">
              {filtered.map(p => {
                const slug = p.slug || p.id;
                const score = p.launch_score || 0;
                return (
                  <Link key={p.id} to={`/trending/${slug}`} className="group" data-testid="trending-card">
                    <Card className="border-0 shadow-md hover:shadow-xl transition-all overflow-hidden">
                      <div className="aspect-video bg-slate-100 relative overflow-hidden">
                        {p.image_url ? (
                          <img src={p.image_url} alt={p.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Eye className="h-8 w-8 text-slate-300" />
                          </div>
                        )}
                        <div className={`absolute top-2 right-2 h-10 w-10 rounded-xl flex items-center justify-center text-sm font-black text-white ${score >= 70 ? 'bg-emerald-500' : score >= 50 ? 'bg-amber-500' : 'bg-red-400'}`}>
                          {score}
                        </div>
                        {p.verified_winner && (
                          <Badge className="absolute top-2 left-2 bg-emerald-500 text-white border-0 text-[10px]">
                            <CheckCircle className="h-3 w-3 mr-0.5" /> Winner
                          </Badge>
                        )}
                      </div>
                      <CardContent className="p-4 space-y-2">
                        <p className="text-sm font-semibold text-slate-900 line-clamp-2 group-hover:text-indigo-700 transition-colors">{p.product_name}</p>
                        {p.ai_summary && <p className="text-xs text-slate-500 line-clamp-2">{p.ai_summary}</p>}
                        <div className="flex items-center justify-between">
                          {p.category && <Badge className="text-[10px] bg-slate-50 text-slate-600 border-slate-200">{p.category}</Badge>}
                          {p.trend_stage && <span className="text-[10px] text-slate-400 capitalize">{p.trend_stage}</span>}
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                );
              })}
            </div>
          )}

          {/* CTA */}
          <div className="text-center py-10 bg-white rounded-2xl shadow-lg">
            <h2 className="text-xl font-bold text-slate-900 mb-2">Want deeper insights?</h2>
            <p className="text-sm text-slate-500 mb-4">Get full 7-signal breakdowns, profitability simulators, and competitor intelligence.</p>
            <Link to="/register">
              <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="seo-bottom-cta">
                <Zap className="h-4 w-4 mr-1.5" /> Start Free Trial
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
