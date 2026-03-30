import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { apiPost, apiGet } from '@/lib/api';
import { toast } from 'sonner';
import {
  Rocket, Loader2, Copy, Check, Download, ShoppingBag,
  TrendingUp, PoundSterling, Target, Sparkles, Package,
  BarChart3, Store, Globe, Zap, ArrowRight, Video, MessageSquare,
} from 'lucide-react';

function CopyButton({ text, label }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(typeof text === 'string' ? text : JSON.stringify(text, null, 2));
    setCopied(true);
    toast.success(`${label || 'Text'} copied!`);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={copy} className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 transition" data-testid={`copy-${(label || 'text').toLowerCase().replace(/\s+/g, '-')}`}>
      {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
      {copied ? 'Copied' : `Copy ${label || ''}`}
    </button>
  );
}

function ExportButton({ data, platform, icon: Icon }) {
  const download = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${platform}-import.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`${platform} export downloaded`);
  };
  return (
    <Button onClick={download} variant="outline" size="sm" className="gap-2" data-testid={`export-${platform}`}>
      <Icon className="h-4 w-4" /> Export for {platform}
    </Button>
  );
}

export default function QuickLaunchPage() {
  const { productId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    launch();
  }, [productId]);

  const launch = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiPost(`/api/products/${productId}/quick-launch`);
      if (res.ok) {
        setData(await res.json());
      } else {
        const err = await res.json().catch(() => ({}));
        setError(err.detail || 'Launch failed');
      }
    } catch {
      setError('Network error');
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4" data-testid="quick-launch-loading">
          <div className="relative">
            <div className="absolute inset-0 rounded-full bg-indigo-200 animate-ping opacity-30" />
            <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center">
              <Rocket className="h-7 w-7 text-white animate-pulse" />
            </div>
          </div>
          <p className="text-lg font-semibold text-slate-800">Generating your launch pack...</p>
          <p className="text-sm text-slate-400">AI is creating ad copy, profit projections & platform exports</p>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
          <p className="text-red-500 font-medium">{error}</p>
          <Button onClick={launch} className="bg-indigo-600 hover:bg-indigo-700">Retry</Button>
        </div>
      </DashboardLayout>
    );
  }

  if (!data) return null;

  const { product: p, ai_content: ai, projections, suppliers, platform_exports } = data;
  const maxRev = Math.max(...projections.map(x => x.revenue), 1);

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-6" data-testid="quick-launch-page">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-4">
            {p.image_url && <img src={p.image_url} alt="" className="h-16 w-16 rounded-xl object-cover border border-slate-200 shadow-sm" />}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Rocket className="h-5 w-5 text-indigo-600" />
                <h1 className="text-xl font-bold text-slate-900 font-manrope">Launch Pack Ready</h1>
              </div>
              <p className="text-sm text-slate-500">{p.name}</p>
            </div>
          </div>
          <Badge className={`text-sm px-3 py-1 ${p.launch_score >= 70 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : p.launch_score >= 40 ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
            Score: {p.launch_score}
          </Badge>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <Stat icon={PoundSterling} label="Retail Price" value={`£${p.retail_price}`} />
          <Stat icon={Package} label="Supplier Cost" value={`£${p.supplier_cost}`} />
          <Stat icon={TrendingUp} label="Margin" value={`${p.margin_pct}%`} positive />
          <Stat icon={PoundSterling} label="Margin/Unit" value={`£${p.margin}`} positive />
          <Stat icon={Target} label="VAT/Unit" value={`£${p.vat_per_unit}`} />
        </div>

        {/* Tabs */}
        <Tabs defaultValue="ads" className="w-full">
          <TabsList className="grid grid-cols-4 w-full">
            <TabsTrigger value="ads" className="gap-1.5 text-xs"><Sparkles className="h-3.5 w-3.5" /> Ad Copy</TabsTrigger>
            <TabsTrigger value="projections" className="gap-1.5 text-xs"><BarChart3 className="h-3.5 w-3.5" /> Projections</TabsTrigger>
            <TabsTrigger value="exports" className="gap-1.5 text-xs"><Store className="h-3.5 w-3.5" /> Exports</TabsTrigger>
            <TabsTrigger value="suppliers" className="gap-1.5 text-xs"><Globe className="h-3.5 w-3.5" /> Suppliers</TabsTrigger>
          </TabsList>

          {/* Ad Copy Tab */}
          <TabsContent value="ads" className="space-y-4 mt-4">
            {ai.headline && (
              <Card className="border border-slate-200">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-indigo-600" />
                      <h3 className="text-sm font-semibold text-slate-800">Product Copy</h3>
                    </div>
                    <CopyButton text={ai.product_description} label="Description" />
                  </div>
                  <h2 className="text-xl font-bold text-slate-900 mb-1">{ai.headline}</h2>
                  <p className="text-sm text-indigo-600 font-medium mb-3">{ai.tagline}</p>
                  <p className="text-sm text-slate-600 leading-relaxed">{ai.product_description}</p>
                  {ai.target_audience && (
                    <div className="mt-4 p-3 bg-indigo-50 rounded-lg">
                      <p className="text-xs font-semibold text-indigo-700 mb-1 flex items-center gap-1"><Target className="h-3 w-3" /> Target Audience</p>
                      <p className="text-sm text-indigo-600">{ai.target_audience}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Platform Ads */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {ai.facebook_ad && (
                <Card className="border border-slate-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2"><MessageSquare className="h-4 w-4 text-blue-600" /><span className="text-xs font-semibold text-slate-700">Facebook Ad</span></div>
                      <CopyButton text={`${ai.facebook_ad.primary_text}\n\n${ai.facebook_ad.headline}\n${ai.facebook_ad.description}`} label="Facebook" />
                    </div>
                    <p className="text-sm text-slate-700 mb-2">{ai.facebook_ad.primary_text}</p>
                    <p className="text-sm font-bold text-slate-900">{ai.facebook_ad.headline}</p>
                    <p className="text-xs text-slate-500 mt-1">{ai.facebook_ad.description}</p>
                  </CardContent>
                </Card>
              )}
              {ai.tiktok_script && (
                <Card className="border border-slate-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2"><Video className="h-4 w-4 text-pink-600" /><span className="text-xs font-semibold text-slate-700">TikTok Script</span></div>
                      <CopyButton text={ai.tiktok_script} label="TikTok" />
                    </div>
                    <p className="text-sm text-slate-600 whitespace-pre-line">{ai.tiktok_script}</p>
                  </CardContent>
                </Card>
              )}
              {ai.instagram_caption && (
                <Card className="border border-slate-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2"><Sparkles className="h-4 w-4 text-purple-600" /><span className="text-xs font-semibold text-slate-700">Instagram</span></div>
                      <CopyButton text={ai.instagram_caption} label="Instagram" />
                    </div>
                    <p className="text-sm text-slate-600 whitespace-pre-line">{ai.instagram_caption}</p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* SEO */}
            {ai.seo_title && (
              <Card className="border border-slate-200">
                <CardContent className="p-4">
                  <p className="text-xs font-semibold text-slate-500 uppercase mb-2">SEO Metadata</p>
                  <p className="text-sm font-bold text-slate-900">{ai.seo_title}</p>
                  <p className="text-xs text-slate-500 mt-1">{ai.seo_description}</p>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {(ai.keywords || []).map((k, i) => <Badge key={i} variant="outline" className="text-[10px]">{k}</Badge>)}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Projections Tab */}
          <TabsContent value="projections" className="space-y-4 mt-4">
            <Card className="border border-slate-200">
              <CardContent className="p-5">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <BarChart3 className="h-3.5 w-3.5 text-indigo-600" /> 30 / 60 / 90 Day Projections (£500/mo ad budget)
                </p>
                <div className="space-y-5">
                  {projections.map(pr => (
                    <div key={pr.month} className="flex items-end gap-3">
                      <div className="w-20 text-right shrink-0">
                        <p className="text-xs font-semibold text-slate-700">Month {pr.month}</p>
                        <p className="text-[10px] text-slate-400">{pr.label}</p>
                      </div>
                      <div className="flex-1 space-y-1.5">
                        <div className="flex-1 h-6 bg-slate-100 rounded-md overflow-hidden relative">
                          <div className="h-full bg-indigo-500 rounded-md" style={{ width: `${(pr.revenue / maxRev) * 100}%` }} />
                          <span className="absolute inset-0 flex items-center justify-center text-[10px] font-semibold text-white mix-blend-difference">Rev: £{pr.revenue.toLocaleString()}</span>
                        </div>
                        <div className="flex-1 h-5 bg-slate-100 rounded-md overflow-hidden relative">
                          <div className={`h-full rounded-md ${pr.profit > 0 ? 'bg-emerald-500' : 'bg-red-400'}`} style={{ width: `${Math.min((Math.abs(pr.profit) / maxRev) * 100, 100)}%` }} />
                          <span className="absolute inset-0 flex items-center justify-center text-[10px] font-semibold text-white mix-blend-difference">{pr.profit > 0 ? 'Profit' : 'Loss'}: £{Math.abs(pr.profit).toLocaleString()}</span>
                        </div>
                      </div>
                      <div className="w-14 text-right shrink-0">
                        <p className={`text-sm font-bold font-mono ${pr.profit > 0 ? 'text-emerald-600' : 'text-red-500'}`}>{pr.roas}x</p>
                        <p className="text-[10px] text-slate-400">ROAS</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-5 pt-4 border-t border-slate-100 grid grid-cols-3 gap-3 text-center">
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase">90-Day Revenue</p>
                    <p className="text-lg font-bold font-mono text-slate-900">£{projections[2]?.revenue?.toLocaleString() || 0}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase">Cumulative Profit</p>
                    <p className={`text-lg font-bold font-mono ${(projections[2]?.cumulative_profit || 0) > 0 ? 'text-emerald-600' : 'text-red-500'}`}>£{projections[2]?.cumulative_profit?.toLocaleString() || 0}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-400 uppercase">Total Orders</p>
                    <p className="text-lg font-bold font-mono text-slate-900">{projections.reduce((a, b) => a + b.orders, 0).toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Platform Exports Tab */}
          <TabsContent value="exports" className="space-y-4 mt-4">
            <Card className="border border-slate-200">
              <CardContent className="p-5">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Export to your store</p>
                <p className="text-sm text-slate-500 mb-5">Download import-ready JSON files for your platform. Import them directly into your store to create a draft product listing.</p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <PlatformCard
                    name="Shopify"
                    icon={ShoppingBag}
                    color="emerald"
                    data={platform_exports.shopify}
                    desc="CSV/JSON import via Shopify Admin"
                  />
                  <PlatformCard
                    name="WooCommerce"
                    icon={Store}
                    color="violet"
                    data={platform_exports.woocommerce}
                    desc="REST API or WP-CLI import"
                  />
                  <PlatformCard
                    name="Etsy"
                    icon={Globe}
                    color="orange"
                    data={platform_exports.etsy}
                    desc="Etsy listing manager import"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Suppliers Tab */}
          <TabsContent value="suppliers" className="space-y-4 mt-4">
            <Card className="border border-slate-200">
              <CardContent className="p-5">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Matched Suppliers</p>
                {suppliers.length === 0 ? (
                  <p className="text-sm text-slate-400">No suppliers matched yet.</p>
                ) : (
                  <div className="space-y-3">
                    {suppliers.map((s, i) => (
                      <div key={i} className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-100">
                        <div>
                          <p className="font-semibold text-slate-800">{s.name}</p>
                          <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                            {s.country && <span>Country: {s.country}</span>}
                            {s.lead_time_days && <span>{s.lead_time_days} day lead time</span>}
                            {s.min_order && <span>MOQ: {s.min_order}</span>}
                          </div>
                        </div>
                        <p className="text-lg font-bold text-slate-900 font-mono">£{(s.unit_cost || s.price || 0).toFixed(2)}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}

function Stat({ icon: Icon, label, value, positive }) {
  return (
    <div className="rounded-xl bg-white border border-slate-200 p-3.5 shadow-sm">
      <div className="flex items-center gap-2 mb-1">
        <Icon className="h-3.5 w-3.5 text-slate-400" />
        <span className="text-[10px] text-slate-400 uppercase tracking-wide">{label}</span>
      </div>
      <p className={`text-base font-bold font-mono ${positive ? 'text-emerald-600' : 'text-slate-900'}`}>{value}</p>
    </div>
  );
}

function PlatformCard({ name, icon: Icon, color, data, desc }) {
  const download = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name.toLowerCase()}-product-import.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`${name} export downloaded`);
  };

  return (
    <div className={`rounded-xl border border-slate-200 p-4 hover:shadow-md transition-all`} data-testid={`platform-${name.toLowerCase()}`}>
      <div className="flex items-center gap-2 mb-2">
        <div className={`w-8 h-8 rounded-lg bg-${color}-50 flex items-center justify-center`}>
          <Icon className={`h-4 w-4 text-${color}-600`} />
        </div>
        <span className="font-semibold text-slate-800">{name}</span>
      </div>
      <p className="text-xs text-slate-400 mb-3">{desc}</p>
      <Button onClick={download} size="sm" variant="outline" className="w-full text-xs gap-1.5">
        <Download className="h-3 w-3" /> Download JSON
      </Button>
    </div>
  );
}
