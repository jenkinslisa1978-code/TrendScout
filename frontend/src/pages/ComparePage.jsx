import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useParams, Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeftRight, Copy, Check, Share2, Trash2, ExternalLink,
  TrendingUp, TrendingDown, Minus, Package, Loader2, Plus,
  BarChart3, DollarSign, Target, Zap, Eye, Search,
  Image as ImageIcon, X, Link2,
} from 'lucide-react';
import { apiGet, apiPost, apiDelete } from '@/lib/api';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

function ScoreBar({ value, max = 100, color = 'indigo' }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const colorMap = {
    indigo: 'bg-indigo-500', emerald: 'bg-emerald-500', amber: 'bg-amber-500',
    red: 'bg-red-500', blue: 'bg-blue-500',
  };
  return (
    <div className="w-full bg-slate-100 rounded-full h-2">
      <div className={`h-2 rounded-full transition-all duration-500 ${colorMap[color] || colorMap.indigo}`}
        style={{ width: `${pct}%` }} />
    </div>
  );
}

function TrendIcon({ stage }) {
  const s = (stage || '').toLowerCase();
  if (s.includes('explod') || s.includes('rising') || s.includes('emerg')) {
    return <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />;
  }
  if (s.includes('declin') || s.includes('fading')) {
    return <TrendingDown className="h-3.5 w-3.5 text-red-500" />;
  }
  return <Minus className="h-3.5 w-3.5 text-slate-400" />;
}

function MetricRow({ label, icon: Icon, values, format = 'number', highlight = 'high' }) {
  const best = highlight === 'high'
    ? Math.max(...values.map(v => typeof v === 'number' ? v : 0))
    : Math.min(...values.filter(v => typeof v === 'number' && v > 0));

  return (
    <tr className="border-b border-slate-100 last:border-0">
      <td className="py-3 pr-3 text-xs font-medium text-slate-500 whitespace-nowrap">
        <div className="flex items-center gap-1.5">
          {Icon && <Icon className="h-3.5 w-3.5 text-slate-400" />}
          {label}
        </div>
      </td>
      {values.map((v, i) => {
        const isBest = typeof v === 'number' && v === best && values.filter(x => x === v).length === 1;
        let display = v;
        if (format === 'currency') display = v ? `£${Number(v).toFixed(2)}` : '—';
        else if (format === 'percent') display = v ? `${Number(v).toFixed(0)}%` : '—';
        else if (format === 'score') display = v || 0;
        else if (typeof v === 'number') display = v.toLocaleString();
        else display = v || '—';

        return (
          <td key={i} className={`py-3 px-3 text-center text-sm ${isBest ? 'font-bold text-indigo-700 bg-indigo-50/50' : 'text-slate-700'}`}>
            {display}
          </td>
        );
      })}
    </tr>
  );
}

export function ComparePageContent({ shareId: propShareId }) {
  const params = useParams();
  const [searchParams] = useSearchParams();
  const shareId = propShareId || params.shareId;
  const idsParam = searchParams.get('ids');

  const [products, setProducts] = useState([]);
  const [title, setTitle] = useState('Product Comparison');
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [currentShareId, setCurrentShareId] = useState(shareId);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        if (shareId) {
          const res = await fetch(`${API_URL}/api/compare/shared/${shareId}`);
          const data = await res.json();
          if (data.success) {
            setProducts(data.comparison.products || []);
            setTitle(data.comparison.title || 'Product Comparison');
            setCurrentShareId(shareId);
          }
        } else if (idsParam) {
          const ids = idsParam.split(',').filter(Boolean);
          if (ids.length >= 2) {
            const res = await apiPost('/api/compare/quick', { product_ids: ids });
            const data = await res.json();
            if (data.success) {
              setProducts(data.products || []);
            }
          }
        }
      } catch {}
      setLoading(false);
    }
    load();
  }, [shareId, idsParam]);

  const handleSave = async () => {
    if (products.length < 2) return;
    setSaving(true);
    try {
      const res = await apiPost('/api/compare', {
        product_ids: products.map(p => p.id),
        title,
      });
      const data = await res.json();
      if (data.success) {
        setCurrentShareId(data.share_id);
        toast.success('Comparison saved! Share link is ready.');
      }
    } catch {
      toast.error('Failed to save comparison');
    }
    setSaving(false);
  };

  const handleCopy = () => {
    if (!currentShareId) return;
    const url = `${window.location.origin}/compare/${currentShareId}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    toast.success('Share link copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]" data-testid="compare-loading">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (products.length < 2) {
    return (
      <div className="text-center py-16" data-testid="compare-empty">
        <div className="mx-auto w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mb-4">
          <ArrowLeftRight className="h-8 w-8 text-indigo-400" />
        </div>
        <h2 className="text-lg font-semibold text-slate-900 mb-2">No Products to Compare</h2>
        <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">
          Select 2-4 products from the trending products page to compare them side by side.
        </p>
        <Link to="/trending-products">
          <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="browse-products-btn">
            <Search className="h-4 w-4 mr-2" /> Browse Products
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="compare-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <ArrowLeftRight className="h-6 w-6 text-indigo-500" />
            {title}
          </h1>
          <p className="text-sm text-slate-500 mt-1">Comparing {products.length} products side by side</p>
        </div>
        <div className="flex items-center gap-2">
          {!currentShareId && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleSave}
              disabled={saving}
              data-testid="save-comparison-btn"
            >
              {saving ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" /> : <Share2 className="h-3.5 w-3.5 mr-1.5" />}
              Save & Share
            </Button>
          )}
          {currentShareId && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              data-testid="copy-link-btn"
            >
              {copied ? <Check className="h-3.5 w-3.5 mr-1.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5 mr-1.5" />}
              {copied ? 'Copied!' : 'Copy Link'}
            </Button>
          )}
        </div>
      </div>

      {/* Product Headers */}
      <div className="overflow-x-auto">
        <table className="w-full" data-testid="compare-table">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="w-40 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Metric</th>
              {products.map((p) => (
                <th key={p.id} className="py-3 px-3 text-center min-w-[180px]">
                  <div className="space-y-2">
                    {p.image_url ? (
                      <img
                        src={p.image_url}
                        alt={p.product_name}
                        className="w-16 h-16 rounded-lg object-cover mx-auto bg-slate-100"
                        loading="lazy"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-lg bg-slate-100 flex items-center justify-center mx-auto">
                        <ImageIcon className="h-6 w-6 text-slate-300" />
                      </div>
                    )}
                    <p className="text-xs font-medium text-slate-900 line-clamp-2 leading-tight max-w-[180px] mx-auto" data-testid={`compare-product-${p.id}`}>
                      {p.product_name}
                    </p>
                    <Badge className="text-[9px] bg-slate-100 text-slate-600">{p.category}</Badge>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Score Section */}
            <tr className="bg-slate-50">
              <td colSpan={products.length + 1} className="py-2 px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Performance Scores
              </td>
            </tr>
            <MetricRow
              label="Launch Score"
              icon={Zap}
              values={products.map(p => p.launch_score || p.metrics?.demand_score || 0)}
              format="score"
            />
            <MetricRow
              label="Demand Score"
              icon={Target}
              values={products.map(p => p.metrics?.demand_score || p.launch_score || 0)}
              format="score"
            />
            <MetricRow
              label="Competition"
              icon={BarChart3}
              values={products.map(p => p.metrics?.competition_score || 0)}
              format="score"
              highlight="low"
            />
            <MetricRow
              label="UK Search Volume"
              icon={Search}
              values={products.map(p => p.metrics?.uk_search_volume || 0)}
            />

            {/* Financial Section */}
            <tr className="bg-slate-50">
              <td colSpan={products.length + 1} className="py-2 px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Financial Metrics
              </td>
            </tr>
            <MetricRow
              label="Retail Price"
              icon={DollarSign}
              values={products.map(p => p.retail_price || 0)}
              format="currency"
            />
            <MetricRow
              label="Supplier Cost"
              icon={Package}
              values={products.map(p => p.supplier_cost || 0)}
              format="currency"
              highlight="low"
            />
            <MetricRow
              label="Margin"
              icon={TrendingUp}
              values={products.map(p => p.margin_percent || p.metrics?.estimated_margin || 0)}
              format="percent"
            />

            {/* Trend Section */}
            <tr className="bg-slate-50">
              <td colSpan={products.length + 1} className="py-2 px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Trend & Growth
              </td>
            </tr>
            <tr className="border-b border-slate-100">
              <td className="py-3 pr-3 text-xs font-medium text-slate-500">
                <div className="flex items-center gap-1.5">
                  <TrendingUp className="h-3.5 w-3.5 text-slate-400" />Trend Stage
                </div>
              </td>
              {products.map((p, i) => (
                <td key={i} className="py-3 px-3 text-center">
                  <div className="flex items-center justify-center gap-1.5">
                    <TrendIcon stage={p.trend_stage} />
                    <span className="text-xs text-slate-700 capitalize">{p.trend_stage || '—'}</span>
                  </div>
                </td>
              ))}
            </tr>
            <MetricRow
              label="Growth Rate"
              icon={TrendingUp}
              values={products.map(p => p.growth_rate || 0)}
              format="percent"
            />
            <MetricRow
              label="TikTok Views"
              icon={Eye}
              values={products.map(p => p.tiktok_views || 0)}
            />

            {/* Competition */}
            <tr className="border-b border-slate-100">
              <td className="py-3 pr-3 text-xs font-medium text-slate-500">
                <div className="flex items-center gap-1.5">
                  <Target className="h-3.5 w-3.5 text-slate-400" />Competition Level
                </div>
              </td>
              {products.map((p, i) => (
                <td key={i} className="py-3 px-3 text-center">
                  <Badge variant="outline" className={`text-[10px] capitalize ${
                    (p.competition_level || '').toLowerCase() === 'low' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' :
                    (p.competition_level || '').toLowerCase() === 'high' ? 'bg-red-50 text-red-600 border-red-200' :
                    'bg-amber-50 text-amber-600 border-amber-200'
                  }`}>
                    {p.competition_level || '—'}
                  </Badge>
                </td>
              ))}
            </tr>

            {/* Visual Score Bars */}
            <tr className="bg-slate-50">
              <td colSpan={products.length + 1} className="py-2 px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Score Comparison
              </td>
            </tr>
            <tr>
              <td className="py-3 pr-3 text-xs font-medium text-slate-500">Launch Score</td>
              {products.map((p, i) => (
                <td key={i} className="py-3 px-3">
                  <div className="space-y-1">
                    <ScoreBar value={p.launch_score || 0} color="indigo" />
                    <p className="text-[10px] text-center text-slate-500">{p.launch_score || 0}/100</p>
                  </div>
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 pr-3 text-xs font-medium text-slate-500">Margin</td>
              {products.map((p, i) => (
                <td key={i} className="py-3 px-3">
                  <div className="space-y-1">
                    <ScoreBar value={p.margin_percent || 0} color="emerald" />
                    <p className="text-[10px] text-center text-slate-500">{p.margin_percent || 0}%</p>
                  </div>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Data Source */}
      <div className="flex items-center justify-center gap-4 text-[10px] text-slate-400 pt-4 border-t border-slate-100">
        {products.map(p => (
          <span key={p.id}>{p.product_name?.substring(0, 25)}... — Source: {p.data_source || 'TrendScout'}</span>
        ))}
      </div>
    </div>
  );
}


export default function ComparePage() {
  return (
    <DashboardLayout>
      <ComparePageContent />
    </DashboardLayout>
  );
}


export function SharedComparePage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-white border-b border-slate-200 px-6 py-3">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-indigo-600 font-bold text-sm">
            <TrendingUp className="h-4 w-4" /> TrendScout
          </Link>
          <Link to="/register">
            <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-xs">
              Try TrendScout Free
            </Button>
          </Link>
        </div>
      </div>
      <div className="max-w-5xl mx-auto p-6">
        <ComparePageContent />
      </div>
    </div>
  );
}
