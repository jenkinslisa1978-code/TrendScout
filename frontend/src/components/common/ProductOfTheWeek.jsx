import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Trophy, TrendingUp, ArrowRight, Flame, Zap, BarChart3 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

function getTrendIcon(label) {
  if (label === 'exploding') return Flame;
  if (label === 'rising') return TrendingUp;
  if (label === 'early_trend') return Zap;
  return BarChart3;
}

function getScoreStyle(score) {
  if (score >= 80) return { color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200' };
  if (score >= 60) return { color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' };
  return { color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200' };
}

export default function ProductOfTheWeek() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPOTW = async () => {
      try {
        const res = await fetch(`${API_URL}/api/email/product-of-the-week`);
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (err) {
        console.error('Failed to fetch POTW:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPOTW();
  }, []);

  if (loading || !data) return null;

  const { product, runners_up } = data;
  const scoreStyle = getScoreStyle(product.launch_score);
  const TrendIcon = getTrendIcon(product.early_trend_label);

  return (
    <section className="py-20 bg-white" data-testid="potw-section">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <Badge className="bg-amber-100 text-amber-700 mb-3">
            <Trophy className="h-3 w-3 mr-1" />
            Updated Weekly
          </Badge>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Product of the Week
          </h2>
          <p className="mt-3 text-base text-slate-600">
            Our top-ranked product this week based on Launch Score analysis
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {/* Featured Product */}
          <Card className={`lg:col-span-2 border-2 ${scoreStyle.border} overflow-hidden`} data-testid="potw-featured-card">
            <CardContent className="p-0">
              <div className={`${scoreStyle.bg} px-6 py-4 flex items-center justify-between`}>
                <div className="flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-amber-500" />
                  <span className="text-sm font-semibold text-slate-700">#1 This Week</span>
                </div>
                <Badge className="bg-white/80 text-slate-700 capitalize">
                  <TrendIcon className="h-3 w-3 mr-1" />
                  {product.trend_stage}
                </Badge>
              </div>
              <div className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-slate-900" data-testid="potw-product-name">
                      {product.product_name}
                    </h3>
                    <p className="text-sm text-slate-500 mt-1">{product.category}</p>
                    <div className="flex items-center gap-4 mt-4">
                      <div>
                        <p className="text-xs text-slate-400 uppercase">Market Score</p>
                        <p className="font-mono text-lg font-bold text-indigo-600">{product.market_score}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400 uppercase">Trend Score</p>
                        <p className="font-mono text-lg font-bold text-slate-700">{product.trend_score}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400 uppercase">Est. Margin</p>
                        <p className="font-mono text-lg font-bold text-emerald-600">{product.margin_range}</p>
                      </div>
                    </div>
                  </div>
                  <div className={`text-center px-5 py-3 rounded-xl ${scoreStyle.bg}`}>
                    <div className={`text-3xl font-bold font-mono ${scoreStyle.color}`} data-testid="potw-launch-score">
                      {product.launch_score}
                    </div>
                    <div className={`text-xs font-medium ${scoreStyle.color}`}>
                      Launch Score
                    </div>
                  </div>
                </div>
                <div className="mt-6 flex gap-3">
                  <Link to={`/p/${product.id}`}>
                    <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="potw-view-btn">
                      View Analysis
                      <ArrowRight className="h-4 w-4 ml-1" />
                    </Button>
                  </Link>
                  <Link to="/signup">
                    <Button variant="outline" data-testid="potw-signup-btn">
                      Unlock Full Insights
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Runners Up */}
          <div className="space-y-4">
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Also Trending</p>
            {runners_up.map((runner, idx) => {
              const rs = getScoreStyle(runner.launch_score);
              return (
                <Card key={runner.id} className="hover:shadow-md transition-shadow" data-testid={`potw-runner-${idx}`}>
                  <CardContent className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500">
                        {idx + 2}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-800 line-clamp-1">{runner.product_name}</p>
                        <p className="text-xs text-slate-400">{runner.category}</p>
                      </div>
                    </div>
                    <div className={`font-mono text-lg font-bold ${rs.color}`}>
                      {runner.launch_score}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
            <Link to="/trending-products" className="block">
              <Button variant="ghost" className="w-full text-indigo-600 hover:text-indigo-700" data-testid="potw-see-all-btn">
                See All Trending
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
