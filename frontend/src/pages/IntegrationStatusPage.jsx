import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Wifi, WifiOff, RefreshCw, CheckCircle2, AlertTriangle, XCircle,
  Clock, Loader2, Key, Zap, Database, Activity,
} from 'lucide-react';
import { SourceTrustBadge, FreshnessIndicator } from '@/components/SourceTrustBadge';
import { apiGet, apiPost } from '@/lib/api';
import { toast } from 'sonner';

const STATUS_MAP = {
  healthy:        { icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', label: 'Healthy' },
  degraded:       { icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', label: 'Degraded' },
  failed:         { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', label: 'Failed' },
  not_configured: { icon: Key, color: 'text-slate-500', bg: 'bg-slate-50', border: 'border-slate-200', label: 'No Credentials' },
};

const SOURCE_META = {
  aliexpress:      { label: 'AliExpress Open Platform', env: ['ALIEXPRESS_API_KEY', 'ALIEXPRESS_API_SECRET'], desc: 'Product search, pricing, orders, shipping, ratings', obtainUrl: 'https://openservice.aliexpress.com' },
  cj_dropshipping: { label: 'CJ Dropshipping API v2', env: ['CJ_API_KEY'], desc: 'Supplier intelligence: pricing, shipping, variants, stock, warehouse', obtainUrl: 'https://developers.cjdropshipping.com' },
  meta_ads:        { label: 'Meta Ad Library API', env: ['META_AD_LIBRARY_TOKEN'], desc: 'Active ad counts, advertisers, creation dates, platforms', obtainUrl: 'https://developers.facebook.com/docs/graph-api/reference/ads_archive/' },
  tiktok:          { label: 'TikTok Trends', env: [], desc: 'Trend views, engagement, ad counts (public scraper)', obtainUrl: null },
};

function IntegrationCard({ sourceKey, data }) {
  const meta = SOURCE_META[sourceKey] || { label: sourceKey, env: [], desc: '' };
  const cfg = STATUS_MAP[data.status] || STATUS_MAP.not_configured;
  const Icon = cfg.icon;

  return (
    <Card className={`border ${cfg.border} overflow-hidden`} data-testid={`integration-${sourceKey}`}>
      <CardContent className="p-0">
        <div className={`${cfg.bg} p-4`}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/80 flex items-center justify-center shadow-sm flex-shrink-0">
              <Icon className={`h-5 w-5 ${cfg.color}`} />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-bold text-slate-900">{meta.label}</h3>
              <p className="text-[11px] text-slate-500 mt-0.5">{meta.desc}</p>
            </div>
            <Badge className={`${cfg.bg} ${cfg.color} border ${cfg.border} text-[10px]`}>
              {cfg.label}
            </Badge>
          </div>
        </div>

        <div className="p-4 space-y-3">
          {/* Mode */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">Current Mode</span>
            <SourceTrustBadge confidence={data.mode === 'live' ? 'live' : data.mode === 'estimation' ? 'estimated' : 'fallback'} size="xs" />
          </div>

          {/* Credentials */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">Credentials</span>
            {data.credential_detected ? (
              <span className="flex items-center gap-1 text-emerald-600 font-medium">
                <CheckCircle2 className="h-3 w-3" /> Detected
              </span>
            ) : (
              <span className="flex items-center gap-1 text-slate-400">
                <Key className="h-3 w-3" /> Not set
              </span>
            )}
          </div>

          {/* Env vars needed */}
          {meta.env.length > 0 && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Required .env</span>
              <code className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                {meta.env.join(', ')}
              </code>
            </div>
          )}

          {/* Message */}
          <div className="text-[11px] text-slate-500 bg-slate-50 rounded-lg p-2">
            {data.message}
          </div>

          {/* Last check */}
          {data.last_check && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Last Check</span>
              <FreshnessIndicator timestamp={data.last_check} />
            </div>
          )}

          {/* Where to get credentials */}
          {meta.obtainUrl && !data.credential_detected && (
            <a
              href={meta.obtainUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-center text-[11px] text-indigo-600 hover:text-indigo-700 hover:underline mt-1"
            >
              Get API credentials →
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function IntegrationStatusPage() {
  const [health, setHealth] = useState(null);
  const [ingestion, setIngestion] = useState(null);
  const [sourceHealth, setSourceHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);

  const fetchAll = useCallback(async (showToast = false) => {
    try {
      const [hRes, iRes, sRes] = await Promise.all([
        apiGet('/api/data-integration/integration-health'),
        apiGet('/api/data-integration/ingestion-status'),
        apiGet('/api/data-integration/source-health'),
      ]);
      if (hRes.ok) setHealth(await hRes.json());
      if (iRes.ok) setIngestion(await iRes.json());
      if (sRes.ok) setSourceHealth(await sRes.json());
      if (showToast) toast.success('Integration status refreshed');
    } catch (e) {
      toast.error('Failed to load integration status');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const runIngestion = async () => {
    setEnriching(true);
    try {
      const res = await apiPost('/api/data-integration/run-ingestion?limit=20', {});
      if (res.ok) {
        toast.success('Data ingestion started in background');
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || 'Failed to start ingestion');
      }
    } catch (e) {
      toast.error('Network error');
    }
    setEnriching(false);
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </DashboardLayout>
    );
  }

  const sourceOrder = ['aliexpress', 'cj_dropshipping', 'meta_ads', 'tiktok'];

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-6" data-testid="integration-status-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <Wifi className="h-6 w-6 text-indigo-600" />
              Data Integrations
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Official API connections and data source health
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchAll(true)}
              data-testid="refresh-integrations-btn"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={runIngestion}
              disabled={enriching}
              data-testid="run-ingestion-btn"
            >
              <Zap className="h-4 w-4 mr-2" />
              {enriching ? 'Starting...' : 'Run Ingestion'}
            </Button>
          </div>
        </div>

        {/* Data confidence summary */}
        {ingestion && (
          <div className="grid grid-cols-4 gap-4" data-testid="confidence-summary">
            <Card className="border-0 shadow-sm">
              <CardContent className="p-4 text-center">
                <p className="text-2xl font-bold text-slate-900">{ingestion.total_products}</p>
                <p className="text-[11px] text-slate-500">Total Products</p>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-sm bg-emerald-50">
              <CardContent className="p-4 text-center">
                <p className="text-2xl font-bold text-emerald-700">{ingestion.confidence_breakdown?.live || 0}</p>
                <p className="text-[11px] text-emerald-600">Live Data</p>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-sm bg-amber-50">
              <CardContent className="p-4 text-center">
                <p className="text-2xl font-bold text-amber-700">{ingestion.confidence_breakdown?.estimated || 0}</p>
                <p className="text-[11px] text-amber-600">Estimated</p>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-sm bg-slate-50">
              <CardContent className="p-4 text-center">
                <p className="text-2xl font-bold text-slate-600">
                  {ingestion.total_products - (ingestion.confidence_breakdown?.live || 0) - (ingestion.confidence_breakdown?.estimated || 0)}
                </p>
                <p className="text-[11px] text-slate-500">Not Enriched</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Integration cards */}
        <div className="grid md:grid-cols-2 gap-4">
          {health && sourceOrder.map((key) => {
            const data = health[key];
            if (!data) return null;
            return <IntegrationCard key={key} sourceKey={key} data={data} />;
          })}
        </div>

        {/* Source pull health */}
        {sourceHealth?.sources?.length > 0 && (
          <Card className="border-0 shadow-md" data-testid="pull-health-table">
            <CardHeader className="py-3 px-4 border-b border-slate-100">
              <CardTitle className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                <Database className="h-4 w-4 text-slate-600" />
                Source Pull History
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-slate-50 text-slate-500">
                    <th className="text-left py-2 px-4 font-medium">Source</th>
                    <th className="text-left py-2 px-4 font-medium">Method</th>
                    <th className="text-center py-2 px-4 font-medium">Success Rate</th>
                    <th className="text-center py-2 px-4 font-medium">Total Pulls</th>
                    <th className="text-center py-2 px-4 font-medium">Avg Latency</th>
                    <th className="text-left py-2 px-4 font-medium">Last Error</th>
                  </tr>
                </thead>
                <tbody>
                  {sourceHealth.sources.map((s, i) => (
                    <tr key={i} className="border-t border-slate-50 hover:bg-slate-50/50">
                      <td className="py-2 px-4 font-medium text-slate-700">{s.source}</td>
                      <td className="py-2 px-4 text-slate-500">{s.method}</td>
                      <td className="py-2 px-4 text-center">
                        <span className={`font-semibold ${
                          s.success_rate >= 80 ? 'text-emerald-600' :
                          s.success_rate >= 50 ? 'text-amber-600' : 'text-red-600'
                        }`}>{s.success_rate}%</span>
                      </td>
                      <td className="py-2 px-4 text-center text-slate-600">{s.total_pulls}</td>
                      <td className="py-2 px-4 text-center text-slate-500">{s.avg_latency_ms}ms</td>
                      <td className="py-2 px-4 text-slate-400 truncate max-w-[200px]">{s.last_error || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        )}

        {/* Setup guide */}
        <Card className="border-0 shadow-md" data-testid="setup-guide">
          <CardHeader className="py-3 px-4 border-b border-slate-100">
            <CardTitle className="text-sm font-semibold text-slate-800 flex items-center gap-2">
              <Activity className="h-4 w-4 text-indigo-600" />
              How to Upgrade to Live Data
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-3 text-xs text-slate-600">
            <p className="text-slate-700 font-medium">Add credentials to <code className="bg-slate-100 px-1.5 py-0.5 rounded">backend/.env</code> — the system auto-upgrades:</p>
            <div className="space-y-2">
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="font-semibold text-slate-700">Meta Ad Library</p>
                <code className="text-[10px] text-indigo-600 block mt-1">META_AD_LIBRARY_TOKEN=your_facebook_access_token</code>
                <p className="text-[10px] text-slate-400 mt-1">Get from: developers.facebook.com → Create App → Generate Token</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="font-semibold text-slate-700">CJ Dropshipping</p>
                <code className="text-[10px] text-indigo-600 block mt-1">CJ_API_KEY=your_cj_access_token</code>
                <p className="text-[10px] text-slate-400 mt-1">Get from: cjdropshipping.com → My CJ → Authorization → API → API Key</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="font-semibold text-slate-700">AliExpress</p>
                <code className="text-[10px] text-indigo-600 block mt-1">ALIEXPRESS_API_KEY=your_app_key</code>
                <code className="text-[10px] text-indigo-600 block">ALIEXPRESS_API_SECRET=your_app_secret</code>
                <p className="text-[10px] text-slate-400 mt-1">Get from: openservice.aliexpress.com → App Management → Create App</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
