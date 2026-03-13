import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Store, Search, Loader2, ArrowLeft, Package, Tag, DollarSign,
  BarChart3, TrendingUp, Clock, ExternalLink, AlertTriangle, Layers,
  Truck, ShoppingBag, ChevronRight, Sparkles, ArrowRight,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function ShopifyAnalyzerPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/api/tools/analyze-store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        toast.error(data.detail || 'Failed to analyze store');
        setLoading(false);
        return;
      }
      setResult(data);
    } catch {
      toast.error('Connection error. Please try again.');
    }
    setLoading(false);
  };

  return (
    <LandingLayout>
      <div className="mx-auto max-w-4xl px-6 py-12" data-testid="shopify-analyzer-page">
        <Link to="/tools" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-600 mb-6 transition-colors">
          <ArrowLeft className="h-4 w-4" /> Back to Tools
        </Link>

        {/* Hero */}
        <div className="text-center mb-10">
          <div className="w-14 h-14 rounded-2xl bg-emerald-100 flex items-center justify-center mx-auto mb-4">
            <Store className="h-7 w-7 text-emerald-600" />
          </div>
          <h1 className="font-manrope text-3xl font-bold text-slate-900">Shopify Store Analyzer</h1>
          <p className="mt-2 text-slate-500 max-w-lg mx-auto">
            Paste any Shopify store URL to instantly see their product catalog, pricing, categories, and newest additions.
          </p>
        </div>

        {/* Input */}
        <form onSubmit={handleAnalyze} className="flex gap-3 max-w-xl mx-auto mb-10" data-testid="analyzer-form">
          <Input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="e.g. gymshark.com or myshopifystore.com"
            className="h-12 text-base rounded-xl border-slate-200 focus:border-indigo-300 focus:ring-indigo-200"
            data-testid="analyzer-url-input"
          />
          <Button
            type="submit"
            disabled={loading || !url.trim()}
            className="h-12 px-6 bg-emerald-600 hover:bg-emerald-700 rounded-xl font-semibold whitespace-nowrap"
            data-testid="analyzer-submit-btn"
          >
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <><Search className="h-4 w-4 mr-2" /> Analyze</>}
          </Button>
        </form>

        {/* Results */}
        {result && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500" data-testid="analyzer-results">
            {/* Store Overview */}
            <Card className="border-slate-200 overflow-hidden">
              <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-5 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold">{result.domain}</h2>
                    <p className="text-emerald-100 text-sm mt-0.5">{result.analysis?.assessment}</p>
                  </div>
                  <a href={result.store_url} target="_blank" rel="noopener noreferrer" className="p-2 rounded-lg bg-white/15 hover:bg-white/25 transition-colors" data-testid="store-external-link">
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              </div>
              <CardContent className="p-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <StatCard icon={Package} label="Products" value={result.product_count} color="text-indigo-600 bg-indigo-50" />
                  <StatCard icon={Layers} label="Categories" value={result.analysis?.total_categories || 0} color="text-violet-600 bg-violet-50" />
                  <StatCard icon={DollarSign} label="Avg Price" value={`$${result.price_range?.avg || 0}`} color="text-emerald-600 bg-emerald-50" />
                  <StatCard icon={Tag} label="Store Size" value={result.store_size || '—'} color="text-amber-600 bg-amber-50" />
                </div>
              </CardContent>
            </Card>

            {/* Price Range */}
            {result.price_range && (
              <Card className="border-slate-200">
                <CardContent className="p-5">
                  <h3 className="font-semibold text-slate-900 text-sm mb-3 flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-emerald-500" /> Price Analysis
                  </h3>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="relative h-2 bg-slate-100 rounded-full">
                        <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full" style={{ width: '100%' }} />
                      </div>
                      <div className="flex justify-between mt-1.5 text-xs text-slate-500">
                        <span>${result.price_range.min}</span>
                        <span className="font-semibold text-emerald-600">${result.price_range.avg} avg</span>
                        <span>${result.price_range.max}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Categories & Vendors */}
            <div className="grid sm:grid-cols-2 gap-4">
              {result.categories?.length > 0 && (
                <Card className="border-slate-200">
                  <CardContent className="p-5">
                    <h3 className="font-semibold text-slate-900 text-sm mb-3 flex items-center gap-2">
                      <Tag className="h-4 w-4 text-violet-500" /> Top Categories
                    </h3>
                    <div className="space-y-2">
                      {result.categories.slice(0, 8).map((cat, i) => (
                        <div key={cat.name} className="flex items-center justify-between text-sm">
                          <span className="text-slate-700 truncate">{cat.name}</span>
                          <Badge className="bg-slate-100 text-slate-600 border-0 rounded-full text-xs">{cat.count}</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
              {result.top_vendors?.length > 0 && (
                <Card className="border-slate-200">
                  <CardContent className="p-5">
                    <h3 className="font-semibold text-slate-900 text-sm mb-3 flex items-center gap-2">
                      <Truck className="h-4 w-4 text-blue-500" /> Top Vendors/Brands
                    </h3>
                    <div className="space-y-2">
                      {result.top_vendors.map((v) => (
                        <div key={v.name} className="flex items-center justify-between text-sm">
                          <span className="text-slate-700 truncate">{v.name}</span>
                          <Badge className="bg-slate-100 text-slate-600 border-0 rounded-full text-xs">{v.count}</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Newest Products */}
            {result.newest_products?.length > 0 && (
              <Card className="border-slate-200">
                <CardContent className="p-5">
                  <h3 className="font-semibold text-slate-900 text-sm mb-4 flex items-center gap-2">
                    <Clock className="h-4 w-4 text-amber-500" /> Recently Added Products
                  </h3>
                  <div className="space-y-3">
                    {result.newest_products.map((p, i) => (
                      <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100" data-testid={`newest-product-${i}`}>
                        <div className="w-12 h-12 rounded-lg bg-white border border-slate-100 flex-shrink-0 overflow-hidden">
                          {p.image_url ? (
                            <img src={p.image_url} alt={p.title} className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center"><Package className="h-5 w-5 text-slate-300" /></div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-slate-900 text-sm truncate">{p.title}</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-xs text-slate-500">{p.product_type}</span>
                            <span className="text-xs font-semibold text-emerald-600">${p.price}</span>
                            {p.variants_count > 1 && <span className="text-xs text-slate-400">{p.variants_count} variants</span>}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* CTA */}
            <div className="text-center pt-4">
              <p className="text-sm text-slate-500 mb-3">Want to track this store and get notified of changes?</p>
              <Link to="/signup">
                <Button className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-xl font-semibold px-6" data-testid="analyzer-cta-btn">
                  <Sparkles className="h-4 w-4 mr-2" /> Start Tracking with TrendScout <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!result && !loading && (
          <div className="text-center py-8">
            <div className="grid sm:grid-cols-3 gap-4 max-w-2xl mx-auto">
              {[
                { icon: BarChart3, title: 'Product Catalog', desc: 'See total products, categories, and pricing' },
                { icon: TrendingUp, title: 'New Additions', desc: 'Discover their most recently added products' },
                { icon: ShoppingBag, title: 'Competitor Intel', desc: 'Understand their store size and strategy' },
              ].map((f, i) => {
                const Icon = f.icon;
                return (
                  <div key={i} className="p-5 rounded-xl bg-slate-50 border border-slate-100 text-center">
                    <Icon className="h-6 w-6 text-indigo-500 mx-auto mb-2" />
                    <p className="font-semibold text-slate-900 text-sm">{f.title}</p>
                    <p className="text-xs text-slate-500 mt-1">{f.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </LandingLayout>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  const [bg, text] = color.split(' ');
  return (
    <div className="text-center p-3 rounded-xl bg-slate-50">
      <div className={`w-9 h-9 rounded-lg ${color} flex items-center justify-center mx-auto mb-2`}>
        <Icon className="h-4 w-4" />
      </div>
      <p className="text-lg font-bold text-slate-900">{value}</p>
      <p className="text-[11px] text-slate-500">{label}</p>
    </div>
  );
}
