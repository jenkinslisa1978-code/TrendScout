import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import PageMeta from '@/components/PageMeta';
import { useAuth } from '@/contexts/AuthContext';
import { apiPost } from '@/lib/api';
import { toast } from 'sonner';
import {
  Search, Loader2, ShieldCheck, AlertTriangle, XCircle, Lock,
  ArrowRight, TrendingUp, Package, PoundSterling, BarChart3,
  Zap, Clock, Tag, Store, Globe, Eye, Sparkles, Target, Users,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const THREAT_CONFIG = {
  High: { color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/25', icon: AlertTriangle },
  Medium: { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/25', icon: ShieldCheck },
  Low: { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', icon: ShieldCheck },
};

const VELOCITY_CONFIG = {
  'Very active': 'text-red-400',
  'Active': 'text-amber-400',
  'Moderate': 'text-sky-400',
  'Slow': 'text-zinc-500',
};

export default function CompetitorSpyPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [scan, setScan] = useState(null);
  const [deepLoading, setDeepLoading] = useState(false);
  const [deep, setDeep] = useState(null);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuth();

  const runScan = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError('');
    setScan(null);
    setDeep(null);
    try {
      const res = await fetch(`${API_URL}/api/competitor-spy/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Scan failed');
      setScan(data);
    } catch (err) {
      setError(err.message || 'Could not scan this store. Check the URL.');
    }
    setLoading(false);
  };

  const runDeepScan = async () => {
    if (!isAuthenticated) {
      toast.info('Sign up to unlock AI deep analysis');
      return;
    }
    setDeepLoading(true);
    try {
      const res = await apiPost('/api/competitor-spy/deep-analysis', { url: url.trim() });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Deep analysis failed');
      setDeep(data);
    } catch (err) {
      toast.error(err.message || 'Deep analysis failed');
    }
    setDeepLoading(false);
  };

  const tc = scan?.threat ? (THREAT_CONFIG[scan.threat.level] || THREAT_CONFIG.Medium) : null;

  return (
    <LandingLayout>
      <PageMeta
        title="Competitor Store Spy — Analyse Any Shopify Store | TrendScout"
        description="Paste any Shopify store URL and instantly see their products, pricing strategy, estimated revenue, and competitive threat level. Free surface scan."
      />

      <div className="bg-[#09090b] min-h-screen">
        <div className="mx-auto max-w-5xl px-6 pt-16 pb-20 lg:pt-20" data-testid="competitor-spy-page">
          {/* Header */}
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3.5 py-1.5 mb-4">
              <Eye className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-xs font-bold text-emerald-400 tracking-[0.15em] uppercase">Free tool — no signup needed</span>
            </div>
            <h1 className="font-manrope text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tighter">
              Spy on any <span className="bg-gradient-to-r from-emerald-400 to-emerald-300 bg-clip-text text-transparent">Shopify competitor</span>
            </h1>
            <p className="mt-3 text-base text-zinc-500 max-w-xl mx-auto">
              Paste a Shopify store URL and instantly see their pricing strategy, best sellers, product velocity, and estimated revenue.
            </p>
          </div>

          {/* Search */}
          <form onSubmit={runScan} className="max-w-2xl mx-auto mb-10">
            <div className="flex items-center bg-black/50 backdrop-blur-xl rounded-xl border border-white/10 focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/30 transition-all shadow-[0_4px_30px_rgba(0,0,0,0.3)]">
              <Globe className="h-5 w-5 text-zinc-500 ml-5 shrink-0" />
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="e.g. gymshark.com or https://allbirds.co.uk"
                className="flex-1 px-4 py-4 text-base text-white placeholder:text-zinc-600 bg-transparent outline-none"
                data-testid="spy-url-input"
              />
              <Button
                type="submit"
                disabled={loading || !url.trim()}
                className="mr-2 bg-emerald-500 hover:bg-emerald-400 text-white rounded-lg px-6 h-10 text-sm font-bold tracking-wide shrink-0 shadow-[0_0_15px_rgba(16,185,129,0.3)]"
                data-testid="spy-scan-btn"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Scan Store'}
              </Button>
            </div>
          </form>

          {error && <p className="text-sm text-red-400 text-center mb-6" data-testid="spy-error">{error}</p>}

          {/* Surface Scan Results */}
          {scan && (
            <div className="space-y-5 animate-in fade-in slide-in-from-bottom-3 duration-500">
              {/* Top Stats */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <StatCard icon={Package} label="Products" value={scan.product_count} sub={scan.store_size} />
                <StatCard icon={PoundSterling} label="Avg Price" value={`$${scan.pricing?.avg || 0}`} sub={scan.pricing?.strategy} />
                <StatCard icon={BarChart3} label="Est. Revenue" value={`$${(scan.revenue_estimate?.low || 0).toLocaleString()}-${(scan.revenue_estimate?.high || 0).toLocaleString()}`} sub="/month" small />
                <StatCard icon={Clock} label="Velocity" value={scan.velocity?.level} sub={scan.velocity?.detail} color={VELOCITY_CONFIG[scan.velocity?.level]} />
              </div>

              {/* Threat Level */}
              {tc && (
                <Card className={`border ${tc.border} ${tc.bg} shadow-lg`} data-testid="spy-threat-level">
                  <CardContent className="py-4 flex items-center gap-4">
                    <tc.icon className={`h-6 w-6 ${tc.color} shrink-0`} />
                    <div>
                      <p className={`text-base font-bold ${tc.color}`}>Threat Level: {scan.threat.level}</p>
                      <p className="text-xs text-zinc-400">{scan.threat.detail}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                {/* Categories */}
                <Card className="border border-white/[0.08] bg-[#18181b]">
                  <CardContent className="p-5">
                    <p className="text-xs font-bold text-zinc-500 uppercase tracking-[0.15em] mb-4 flex items-center gap-2">
                      <Tag className="h-3.5 w-3.5 text-violet-400" /> Categories
                    </p>
                    <div className="space-y-2.5">
                      {(scan.categories || []).map((cat) => (
                        <div key={cat.name} className="flex items-center justify-between">
                          <span className="text-sm text-zinc-300">{cat.name}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                              <div className="h-full bg-violet-500 rounded-full" style={{ width: `${cat.pct}%` }} />
                            </div>
                            <span className="text-xs text-zinc-500 font-mono w-8 text-right">{cat.count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Pricing Breakdown */}
                <Card className="border border-white/[0.08] bg-[#18181b]">
                  <CardContent className="p-5">
                    <p className="text-xs font-bold text-zinc-500 uppercase tracking-[0.15em] mb-4 flex items-center gap-2">
                      <PoundSterling className="h-3.5 w-3.5 text-emerald-400" /> Pricing Breakdown
                    </p>
                    <div className="grid grid-cols-2 gap-3 mb-4">
                      <PriceBox label="Min" value={`$${scan.pricing?.min}`} />
                      <PriceBox label="Max" value={`$${scan.pricing?.max}`} />
                      <PriceBox label="Average" value={`$${scan.pricing?.avg}`} highlight />
                      <PriceBox label="Median" value={`$${scan.pricing?.median}`} />
                    </div>
                    <p className="text-xs text-zinc-500">
                      Strategy: <span className="text-zinc-300 font-medium">{scan.pricing?.strategy}</span>
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Best Sellers */}
              <Card className="border border-white/[0.08] bg-[#18181b]">
                <CardContent className="p-5">
                  <p className="text-xs font-bold text-zinc-500 uppercase tracking-[0.15em] mb-4 flex items-center gap-2">
                    <TrendingUp className="h-3.5 w-3.5 text-amber-400" /> Likely Best Sellers
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
                    {(scan.best_sellers || []).map((p, i) => (
                      <div key={i} className="rounded-xl bg-[#121214] border border-white/[0.06] p-3 text-center">
                        {p.image_url && <img src={p.image_url} alt="" className="w-full h-20 object-cover rounded-lg mb-2" />}
                        <p className="text-xs text-zinc-300 font-medium line-clamp-2">{p.title}</p>
                        <p className="text-xs text-emerald-400 font-bold mt-1">${p.price}</p>
                        <p className="text-[10px] text-zinc-600">{p.variants_count} variants</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Newest Products */}
              <Card className="border border-white/[0.08] bg-[#18181b]">
                <CardContent className="p-5">
                  <p className="text-xs font-bold text-zinc-500 uppercase tracking-[0.15em] mb-4 flex items-center gap-2">
                    <Zap className="h-3.5 w-3.5 text-sky-400" /> Newest Additions
                  </p>
                  <div className="space-y-2">
                    {(scan.newest_products || []).map((p, i) => (
                      <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg bg-[#121214] border border-white/[0.06]">
                        {p.image_url && <img src={p.image_url} alt="" className="h-10 w-10 rounded-lg object-cover shrink-0" />}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-zinc-300 font-medium truncate">{p.title}</p>
                          <p className="text-xs text-zinc-600">{p.product_type}</p>
                        </div>
                        <span className="text-sm text-emerald-400 font-bold shrink-0">${p.price}</span>
                        {p.days_old !== null && (
                          <span className="text-[10px] text-zinc-600 shrink-0">{p.days_old}d ago</span>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Deep Analysis CTA or Results */}
              {!deep ? (
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-6 flex flex-col sm:flex-row items-center justify-between gap-4" data-testid="spy-deep-cta">
                  <div className="flex items-center gap-3">
                    <Sparkles className="h-6 w-6 text-emerald-400 shrink-0" />
                    <div>
                      <p className="text-sm font-bold text-white">AI Deep Analysis</p>
                      <p className="text-xs text-zinc-500">Revenue breakdown, ad strategy, weaknesses, and how to beat this competitor</p>
                    </div>
                  </div>
                  {isAuthenticated ? (
                    <Button
                      onClick={runDeepScan}
                      disabled={deepLoading}
                      className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold tracking-wide rounded-lg px-6 shadow-[0_0_15px_rgba(16,185,129,0.3)] shrink-0"
                      data-testid="spy-deep-btn"
                    >
                      {deepLoading ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Analysing...</> : <><Sparkles className="h-4 w-4 mr-2" /> Run Deep Analysis</>}
                    </Button>
                  ) : (
                    <Link to="/signup">
                      <Button className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold tracking-wide rounded-lg px-6 shadow-[0_0_15px_rgba(16,185,129,0.3)]" data-testid="spy-signup-cta">
                        <Lock className="h-4 w-4 mr-2" /> Sign Up to Unlock
                      </Button>
                    </Link>
                  )}
                </div>
              ) : (
                <Card className="border border-emerald-500/20 bg-[#18181b] shadow-[0_0_30px_rgba(16,185,129,0.06)]" data-testid="spy-deep-results">
                  <CardContent className="p-6 space-y-5">
                    <div className="flex items-center gap-2 mb-1">
                      <Sparkles className="h-5 w-5 text-emerald-400" />
                      <span className="text-xs font-bold text-emerald-400 tracking-[0.15em] uppercase">AI Deep Analysis</span>
                    </div>

                    {deep.ai_analysis?.verdict && (
                      <p className="text-base font-bold text-white">{deep.ai_analysis.verdict}</p>
                    )}
                    {deep.ai_analysis?.store_profile && (
                      <p className="text-sm text-zinc-400">{deep.ai_analysis.store_profile}</p>
                    )}

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {deep.ai_analysis?.strengths && (
                        <div>
                          <p className="text-xs font-bold text-zinc-500 uppercase mb-2">Strengths</p>
                          <ul className="space-y-1.5">
                            {deep.ai_analysis.strengths.map((s, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                                <TrendingUp className="h-3.5 w-3.5 text-emerald-500 mt-0.5 shrink-0" /> {s}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {deep.ai_analysis?.weaknesses && (
                        <div>
                          <p className="text-xs font-bold text-zinc-500 uppercase mb-2">Weaknesses</p>
                          <ul className="space-y-1.5">
                            {deep.ai_analysis.weaknesses.map((w, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                                <Target className="h-3.5 w-3.5 text-red-400 mt-0.5 shrink-0" /> {w}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {deep.ai_analysis?.how_to_compete && (
                      <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/15">
                        <p className="text-xs font-bold text-emerald-400 uppercase mb-2 flex items-center gap-1.5">
                          <Zap className="h-3.5 w-3.5" /> How to compete
                        </p>
                        <p className="text-sm text-zinc-300">{deep.ai_analysis.how_to_compete}</p>
                      </div>
                    )}

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                      {deep.ai_analysis?.target_audience && (
                        <div className="p-3 rounded-lg bg-[#121214] border border-white/[0.06]">
                          <p className="text-[10px] text-zinc-600 uppercase mb-1">Target Audience</p>
                          <p className="text-zinc-300">{deep.ai_analysis.target_audience}</p>
                        </div>
                      )}
                      {deep.ai_analysis?.ad_strategy_likely && (
                        <div className="p-3 rounded-lg bg-[#121214] border border-white/[0.06]">
                          <p className="text-[10px] text-zinc-600 uppercase mb-1">Likely Ad Strategy</p>
                          <p className="text-zinc-300">{deep.ai_analysis.ad_strategy_likely}</p>
                        </div>
                      )}
                      {deep.ai_analysis?.estimated_monthly_revenue && (
                        <div className="p-3 rounded-lg bg-[#121214] border border-white/[0.06]">
                          <p className="text-[10px] text-zinc-600 uppercase mb-1">Revenue Estimate</p>
                          <p className="text-zinc-300">{deep.ai_analysis.estimated_monthly_revenue}</p>
                        </div>
                      )}
                    </div>

                    {deep.ai_analysis?.product_gaps && (
                      <div>
                        <p className="text-xs font-bold text-zinc-500 uppercase mb-2">Product Gaps (Opportunities for you)</p>
                        <div className="flex flex-wrap gap-2">
                          {deep.ai_analysis.product_gaps.map((g, i) => (
                            <Badge key={i} className="bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs">{g}</Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {deep.ai_analysis?.opportunity_score && (
                      <div className="text-center pt-3 border-t border-white/[0.06]">
                        <p className="text-[10px] text-zinc-600 uppercase">Opportunity Score</p>
                        <p className={`text-3xl font-extrabold font-mono ${deep.ai_analysis.opportunity_score >= 60 ? 'text-emerald-400' : 'text-amber-400'}`}>
                          {deep.ai_analysis.opportunity_score}<span className="text-lg text-zinc-600">/100</span>
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </LandingLayout>
  );
}

function StatCard({ icon: Icon, label, value, sub, color, small, highlight }) {
  return (
    <div className="rounded-xl bg-[#18181b] border border-white/[0.08] p-4">
      <div className="flex items-center gap-2 mb-1">
        <Icon className="h-3.5 w-3.5 text-zinc-500" />
        <span className="text-[10px] text-zinc-600 uppercase tracking-wide">{label}</span>
      </div>
      <p className={`${small ? 'text-sm' : 'text-lg'} font-bold font-mono ${color || 'text-white'}`}>{value}</p>
      {sub && <p className="text-[10px] text-zinc-600 mt-0.5 line-clamp-1">{sub}</p>}
    </div>
  );
}

function PriceBox({ label, value, highlight }) {
  return (
    <div className={`rounded-lg p-3 ${highlight ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-[#121214] border border-white/[0.06]'}`}>
      <p className="text-[10px] text-zinc-600 uppercase">{label}</p>
      <p className={`text-base font-bold font-mono ${highlight ? 'text-emerald-400' : 'text-white'}`}>{value}</p>
    </div>
  );
}
