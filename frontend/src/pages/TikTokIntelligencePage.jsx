import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Video, TrendingUp, Eye, Flame, BarChart3, Package,
  Loader2, Hash, Zap, ChevronRight, ArrowUpRight, Clock,
  Sparkles, Target,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

function formatViews(n) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`;
  return String(n);
}

export default function TikTokIntelligencePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/tools/tiktok-intelligence`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </DashboardLayout>
    );
  }

  if (!data) return <DashboardLayout><p className="text-center py-20 text-slate-500">No data available</p></DashboardLayout>;

  const { viral_products, categories, trending_patterns, stats } = data;

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="tiktok-intelligence-page">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="p-2 rounded-xl bg-gradient-to-br from-rose-500 to-pink-600">
              <Video className="h-5 w-5 text-white" />
            </div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">TikTok Ad Intelligence</h1>
          </div>
          <p className="text-slate-500 text-sm ml-12">Products trending on TikTok — spot viral opportunities before they saturate</p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard icon={Eye} label="Total TikTok Views" value={formatViews(stats.total_tiktok_views)} color="bg-rose-50 text-rose-600" />
          <StatCard icon={Package} label="Products Tracked" value={stats.products_tracked} color="bg-indigo-50 text-indigo-600" />
          <StatCard icon={BarChart3} label="Avg Launch Score" value={stats.avg_launch_score} color="bg-emerald-50 text-emerald-600" />
          <StatCard icon={Flame} label="Top Category" value={stats.top_category} color="bg-amber-50 text-amber-600" />
        </div>

        {/* Top Viral Products */}
        <Card className="border-slate-200">
          <CardContent className="p-5">
            <h2 className="font-semibold text-slate-900 text-sm mb-4 flex items-center gap-2">
              <Flame className="h-4 w-4 text-rose-500" /> Top Viral Products on TikTok
            </h2>
            <div className="space-y-2">
              {viral_products.map((p, i) => {
                const scoreColor = p.launch_score >= 70 ? 'text-emerald-600 bg-emerald-50' : p.launch_score >= 50 ? 'text-amber-600 bg-amber-50' : 'text-slate-600 bg-slate-50';
                return (
                  <Link
                    key={p.id}
                    to={`/trending/${p.slug}`}
                    className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 transition-colors group"
                    data-testid={`viral-product-${p.id}`}
                  >
                    <span className="w-6 text-sm font-bold text-slate-300 text-right">#{i + 1}</span>
                    <div className="w-10 h-10 rounded-lg bg-slate-100 overflow-hidden flex-shrink-0">
                      {p.image_url ? (
                        <img src={p.image_url} alt="" className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center"><Package className="h-4 w-4 text-slate-300" /></div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-slate-900 text-sm truncate group-hover:text-indigo-600 transition-colors">{p.product_name}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-slate-400">{p.category}</span>
                        <Badge className="text-[10px] rounded-full bg-rose-50 text-rose-600 border-0">
                          <Eye className="h-2.5 w-2.5 mr-0.5" />{formatViews(p.tiktok_views)}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <Badge className={`text-xs rounded-full border-0 ${scoreColor}`}>
                        {p.launch_score}
                      </Badge>
                      <span className="text-xs font-semibold text-emerald-600">{p.margin_percent}%</span>
                      {p.growth_rate > 0 && (
                        <span className="text-xs text-indigo-500 flex items-center gap-0.5">
                          <TrendingUp className="h-3 w-3" />{p.growth_rate}%
                        </span>
                      )}
                      <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-indigo-500 transition-colors" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <div className="grid sm:grid-cols-2 gap-4">
          {/* Category Performance */}
          <Card className="border-slate-200">
            <CardContent className="p-5">
              <h2 className="font-semibold text-slate-900 text-sm mb-4 flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-indigo-500" /> Category Performance
              </h2>
              <div className="space-y-3">
                {categories.map((cat) => {
                  const maxViews = categories[0]?.total_views || 1;
                  const pct = Math.min(100, (cat.total_views / maxViews) * 100);
                  return (
                    <div key={cat.name} data-testid={`tiktok-category-${cat.name}`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-slate-700">{cat.name}</span>
                        <div className="flex items-center gap-2">
                          <Badge className="text-[10px] rounded-full bg-slate-50 text-slate-500 border-0">{cat.product_count} products</Badge>
                          <span className="text-xs font-semibold text-rose-600">{formatViews(cat.total_views)}</span>
                        </div>
                      </div>
                      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-rose-400 to-pink-500 rounded-full transition-all duration-700" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Trending Patterns */}
          <Card className="border-slate-200">
            <CardContent className="p-5">
              <h2 className="font-semibold text-slate-900 text-sm mb-4 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-amber-500" /> Trending Ad Patterns
              </h2>
              <div className="space-y-3">
                {trending_patterns.map((tp) => {
                  const relevanceColor = tp.relevance === 'high' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200';
                  return (
                    <div key={tp.pattern} className="p-3 rounded-xl bg-slate-50 border border-slate-100" data-testid={`trend-pattern-${tp.pattern.replace(/\s/g, '-')}`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-slate-800 text-sm">{tp.pattern}</span>
                        <Badge className={`text-[10px] border rounded-full ${relevanceColor}`}>{tp.relevance}</Badge>
                      </div>
                      <p className="text-xs text-slate-500">{tp.description}</p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <Card className="border-slate-200">
      <CardContent className="p-4 text-center">
        <div className={`w-9 h-9 rounded-lg ${color} flex items-center justify-center mx-auto mb-2`}>
          <Icon className="h-4 w-4" />
        </div>
        <p className="text-lg font-bold text-slate-900">{value}</p>
        <p className="text-[11px] text-slate-500">{label}</p>
      </CardContent>
    </Card>
  );
}
