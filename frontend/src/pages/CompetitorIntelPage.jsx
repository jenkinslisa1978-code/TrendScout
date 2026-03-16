import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Search, Store, Package, DollarSign, TrendingUp, BarChart3,
  Loader2, AlertTriangle, CheckCircle, Users, Tag, Clock,
  ArrowRight, ExternalLink, ShieldAlert, Layers, Scale,
  ChevronDown, ChevronUp, X,
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function CompetitorIntelPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [compareMode, setCompareMode] = useState(false);
  const [compareUrl, setCompareUrl] = useState('');
  const [compareLoading, setCompareLoading] = useState(false);
  const [comparison, setComparison] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/api/competitor-intel/history');
        if (res.ok) setHistory(res.data.analyses || []);
      } catch {}
    })();
  }, []);

  const analyzeStore = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setAnalysis(null);
    try {
      const res = await api.post('/api/competitor-intel/analyze', { url: url.trim() });
      if (res.ok && res.data.success) {
        setAnalysis(res.data);
        // Refresh history
        const h = await api.get('/api/competitor-intel/history');
        if (h.ok) setHistory(h.data.analyses || []);
      } else {
        toast.error(res.data?.error || 'Analysis failed');
      }
    } catch { toast.error('Could not analyze store'); }
    setLoading(false);
  };

  const compareStores = async (e) => {
    e.preventDefault();
    if (!url.trim() || !compareUrl.trim()) return;
    setCompareLoading(true);
    setComparison(null);
    try {
      const res = await api.post('/api/competitor-intel/compare', { urls: [url.trim(), compareUrl.trim()] });
      if (res.ok) setComparison(res.data);
    } catch { toast.error('Comparison failed'); }
    setCompareLoading(false);
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6 space-y-6" data-testid="competitor-intel-page">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Competitor Intelligence</h1>
          <p className="text-sm text-slate-500 mt-1">Deep-analyze any Shopify store: revenue estimates, pricing strategy, supplier risk, and top products.</p>
        </div>

        {/* Search */}
        <Card className="border-0 shadow-lg" data-testid="store-analyzer-form">
          <CardContent className="py-5 space-y-3">
            <form onSubmit={analyzeStore} className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Store className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  value={url}
                  onChange={e => setUrl(e.target.value)}
                  placeholder="Enter Shopify store URL (e.g. gymshark.com)"
                  className="pl-10"
                  data-testid="store-url-input"
                />
              </div>
              <Button type="submit" disabled={loading || !url.trim()} className="bg-indigo-600 hover:bg-indigo-700" data-testid="analyze-store-btn">
                {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Search className="h-4 w-4 mr-2" />}
                Analyze Store
              </Button>
            </form>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setCompareMode(!compareMode)}
                className="text-xs text-indigo-600 hover:underline font-medium"
                data-testid="toggle-compare"
              >
                <Scale className="h-3 w-3 inline mr-1" />
                {compareMode ? 'Hide comparison' : 'Compare two stores'}
              </button>
              {history.length > 0 && (
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="text-xs text-slate-500 hover:text-slate-700"
                  data-testid="toggle-history"
                >
                  <Clock className="h-3 w-3 inline mr-1" /> Recent analyses ({history.length})
                </button>
              )}
            </div>
            {compareMode && (
              <form onSubmit={compareStores} className="flex flex-col sm:flex-row gap-3 pt-2 border-t border-slate-100">
                <div className="relative flex-1">
                  <Store className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <Input
                    value={compareUrl}
                    onChange={e => setCompareUrl(e.target.value)}
                    placeholder="Second store URL to compare..."
                    className="pl-10"
                    data-testid="compare-url-input"
                  />
                </div>
                <Button type="submit" disabled={compareLoading || !compareUrl.trim()} variant="outline" data-testid="compare-btn">
                  {compareLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Scale className="h-4 w-4 mr-2" />}
                  Compare
                </Button>
              </form>
            )}
          </CardContent>
        </Card>

        {/* History */}
        {showHistory && history.length > 0 && (
          <Card className="border-0 shadow-md" data-testid="analysis-history">
            <CardContent className="py-3">
              <p className="text-xs font-semibold text-slate-500 uppercase mb-2">Recent Analyses</p>
              <div className="flex flex-wrap gap-2">
                {history.map(h => (
                  <button
                    key={h.domain}
                    onClick={() => { setUrl(h.domain); }}
                    className="text-xs bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg px-3 py-1.5 text-slate-700 transition-colors"
                  >
                    {h.domain} <span className="text-slate-400 ml-1">{h.product_count} products</span>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Comparison Result */}
        {comparison && (
          <ComparisonTable data={comparison} onClose={() => setComparison(null)} />
        )}

        {/* Analysis Result */}
        {analysis && <StoreAnalysis data={analysis} />}

        {/* Loading State */}
        {loading && !analysis && (
          <Card className="border-0 shadow-lg">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <Loader2 className="h-10 w-10 animate-spin text-indigo-500 mb-4" />
              <p className="text-sm text-slate-500">Scanning store catalog and analyzing data...</p>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!loading && !analysis && !comparison && (
          <Card className="border-0 shadow-lg">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <Store className="h-12 w-12 text-slate-300 mb-4" />
              <p className="text-sm text-slate-500">Enter a Shopify store URL above to get a full competitive analysis.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}

function StoreAnalysis({ data }) {
  const [showAllProducts, setShowAllProducts] = useState(false);
  const displayProducts = showAllProducts ? data.top_products : (data.top_products || []).slice(0, 4);

  const riskColor = {
    Low: 'text-emerald-700 bg-emerald-50 border-emerald-200',
    Medium: 'text-amber-700 bg-amber-50 border-amber-200',
    High: 'text-red-700 bg-red-50 border-red-200',
  };
  const riskCls = riskColor[data.suppliers?.risk_level] || riskColor.Medium;

  return (
    <div className="space-y-4" data-testid="store-analysis-results">
      {/* Store Header */}
      <Card className="border-0 shadow-lg bg-gradient-to-r from-slate-900 to-slate-800 text-white">
        <CardContent className="py-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-lg font-bold">{data.domain}</h2>
                <a href={data.store_url} target="_blank" rel="noreferrer" className="text-slate-400 hover:text-white">
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
              <div className="flex items-center gap-3 mt-2">
                <Badge className="bg-white/10 text-white border-white/20 text-xs">{data.store_tier}</Badge>
                {data.store_age_months && (
                  <span className="text-xs text-slate-400"><Clock className="h-3 w-3 inline mr-1" /> ~{data.store_age_months} months old</span>
                )}
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-black text-white">{data.product_count}</p>
              <p className="text-xs text-slate-400">products</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={DollarSign} label="Est. Monthly Revenue" value={`$${(data.revenue_estimate?.monthly_revenue || 0).toLocaleString()}`} sub={`~${data.revenue_estimate?.daily_orders || 0} orders/day`} />
        <StatCard icon={BarChart3} label="Avg Price" value={`$${data.pricing?.avg || 0}`} sub={`$${data.pricing?.min} — $${data.pricing?.max}`} />
        <StatCard icon={Layers} label="Categories" value={data.categories?.length || 0} sub={data.categories?.[0]?.name || '—'} />
        <StatCard icon={Users} label="Vendors" value={data.suppliers?.vendor_count || 0} sub={data.suppliers?.top_vendors?.[0]?.name || '—'} />
      </div>

      {/* Pricing Strategy + Supplier Risk */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="border-0 shadow-md" data-testid="pricing-strategy">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-emerald-600" /> Pricing Strategy
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Strategy</span>
              <Badge className="bg-indigo-50 text-indigo-700 border-indigo-200">{data.pricing?.strategy}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Price Spread</span>
              <span className="text-sm font-semibold text-slate-800">{data.pricing?.consistency}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Median Price</span>
              <span className="text-sm font-semibold text-slate-800">${data.pricing?.median}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md" data-testid="supplier-risk">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-amber-600" /> Supplier Risk
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Risk Level</span>
              <Badge className={`border ${riskCls}`}>{data.suppliers?.risk_level}</Badge>
            </div>
            <p className="text-xs text-slate-500">{data.suppliers?.risk_reason}</p>
            {data.suppliers?.top_vendors?.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {data.suppliers.top_vendors.map(v => (
                  <Badge key={v.name} className="bg-slate-50 text-slate-600 border-slate-200 text-[10px]">
                    {v.name} ({v.count})
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Category Breakdown */}
      {data.categories?.length > 0 && (
        <Card className="border-0 shadow-md" data-testid="category-breakdown">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <Tag className="h-4 w-4 text-indigo-600" /> Category Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.categories.slice(0, 8).map(cat => (
                <div key={cat.name} className="flex items-center gap-3">
                  <span className="text-xs text-slate-600 w-32 truncate">{cat.name}</span>
                  <div className="flex-1">
                    <Progress value={cat.pct} className="h-2" />
                  </div>
                  <span className="text-xs font-semibold text-slate-700 w-16 text-right">{cat.count} ({cat.pct}%)</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top Products */}
      {data.top_products?.length > 0 && (
        <Card className="border-0 shadow-md" data-testid="top-products">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <Package className="h-4 w-4 text-purple-600" /> Top Products (by price)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {displayProducts.map((p, i) => (
                <div key={i} className="bg-slate-50 rounded-lg p-3 space-y-2">
                  {p.image_url && <img src={p.image_url} alt="" className="w-full h-24 object-cover rounded-lg" />}
                  <p className="text-xs font-semibold text-slate-800 line-clamp-2">{p.title}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-slate-900">${p.price}</span>
                    <Badge className="text-[10px] bg-slate-100 text-slate-500 border-slate-200">{p.product_type}</Badge>
                  </div>
                </div>
              ))}
            </div>
            {data.top_products.length > 4 && (
              <button onClick={() => setShowAllProducts(!showAllProducts)} className="text-xs text-indigo-600 hover:underline mt-3 font-medium" data-testid="show-more-products">
                {showAllProducts ? 'Show less' : `Show all ${data.top_products.length} products`}
              </button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Revenue Confidence Note */}
      <div className="flex items-start gap-2 px-4 py-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-700">
        <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
        <p>Revenue estimates are based on catalog size heuristics and should be treated as rough approximations. Actual revenue depends on traffic, conversion rates, and marketing spend.</p>
      </div>
    </div>
  );
}

function ComparisonTable({ data, onClose }) {
  if (!data.stores || data.stores.length < 2) return null;
  const metrics = ['product_count', 'avg_price', 'est_monthly_revenue', 'est_daily_orders', 'categories', 'top_category'];
  const labels = { product_count: 'Products', avg_price: 'Avg Price', est_monthly_revenue: 'Est. Revenue/mo', est_daily_orders: 'Est. Orders/day', categories: 'Categories', top_category: 'Top Category' };

  return (
    <Card className="border-0 shadow-lg" data-testid="comparison-table">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-bold flex items-center gap-2">
            <Scale className="h-4 w-4 text-indigo-600" /> Store Comparison
          </CardTitle>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X className="h-4 w-4" /></button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left py-2 text-xs text-slate-400 font-medium">Metric</th>
                {data.stores.map(s => (
                  <th key={s.domain} className="text-right py-2 text-xs font-semibold text-slate-700">{s.domain}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metrics.map(m => (
                <tr key={m} className="border-b border-slate-50">
                  <td className="py-2.5 text-xs text-slate-600">{labels[m]}</td>
                  {data.stores.map(s => {
                    let val = s[m];
                    if (m === 'avg_price') val = `$${val}`;
                    if (m === 'est_monthly_revenue') val = `$${(val || 0).toLocaleString()}`;
                    return <td key={s.domain} className="text-right py-2.5 text-xs font-semibold text-slate-800">{val ?? '—'}</td>;
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function StatCard({ icon: Icon, label, value, sub }) {
  return (
    <Card className="border-0 shadow-md">
      <CardContent className="py-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-indigo-50 flex items-center justify-center">
            <Icon className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <p className="text-lg font-bold text-slate-900">{value}</p>
            <p className="text-[10px] text-slate-400 uppercase">{label}</p>
            {sub && <p className="text-[10px] text-slate-500">{sub}</p>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
