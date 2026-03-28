import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Clock, CheckCircle2, XCircle, RefreshCw, ChevronDown, ChevronUp,
  Activity,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const PLATFORM_NAMES = {
  shopify: 'Shopify', etsy: 'Etsy', woocommerce: 'WooCommerce',
  amazon_seller: 'Amazon', tiktok_shop: 'TikTok Shop',
};

function timeAgo(dateStr) {
  if (!dateStr) return 'Never';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export default function SyncHistory() {
  const [summary, setSummary] = useState({});
  const [history, setHistory] = useState([]);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const [sumRes, histRes] = await Promise.all([
          apiGet('/api/sync/history/summary'),
          apiGet('/api/sync/history'),
        ]);
        const sumData = await sumRes.json();
        const histData = await histRes.json();
        setSummary(sumData.summary || {});
        setHistory(histData.history || []);
      } catch {}
      setLoading(false);
    };
    fetch();
  }, []);

  const platforms = Object.values(summary);
  if (loading || platforms.length === 0) return null;

  return (
    <Card className="border-slate-200" data-testid="sync-history-card">
      <CardContent className="p-4">
        <button
          className="flex items-center justify-between w-full text-left"
          onClick={() => setExpanded(!expanded)}
          data-testid="sync-history-toggle"
        >
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-indigo-500" />
            <span className="text-sm font-semibold text-slate-900">Sync Activity</span>
            <Badge className="bg-slate-100 text-slate-600 text-[10px]">
              {platforms.reduce((s, p) => s + (p.total_syncs || 0), 0)} syncs
            </Badge>
          </div>
          {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
        </button>

        {/* Summary row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3">
          {platforms.map((p) => (
            <div
              key={p.platform}
              className={`rounded-lg border p-2 text-xs ${
                p.last_status === 'error' ? 'border-red-200 bg-red-50/50' : 'border-slate-200'
              }`}
              data-testid={`sync-summary-${p.platform}`}
            >
              <p className="font-semibold text-slate-900">{PLATFORM_NAMES[p.platform] || p.platform}</p>
              <div className="flex items-center gap-1 mt-1">
                {p.last_status === 'success' ? (
                  <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                ) : (
                  <XCircle className="h-3 w-3 text-red-500" />
                )}
                <span className="text-slate-500">{timeAgo(p.last_sync)}</span>
              </div>
              <p className="text-slate-400 mt-0.5">{p.current_products || p.last_count || 0} products</p>
            </div>
          ))}
        </div>

        {/* Expanded history */}
        {expanded && history.length > 0 && (
          <div className="mt-4 space-y-1 max-h-[300px] overflow-y-auto">
            <p className="text-[10px] font-semibold text-slate-400 uppercase mb-2">Recent Sync Log</p>
            {history.slice(0, 20).map((h, i) => (
              <div
                key={i}
                className="flex items-center justify-between py-1.5 px-2 rounded text-xs hover:bg-slate-50"
                data-testid={`sync-history-item-${i}`}
              >
                <div className="flex items-center gap-2">
                  {h.status === 'success' ? (
                    <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0" />
                  ) : (
                    <XCircle className="h-3 w-3 text-red-500 shrink-0" />
                  )}
                  <span className="font-medium text-slate-700">{PLATFORM_NAMES[h.platform] || h.platform}</span>
                  <span className="text-slate-400">{h.shop?.substring(0, 30)}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-slate-500">{h.synced_count || 0} products</span>
                  <Badge variant="outline" className={`text-[9px] ${
                    h.trigger === 'scheduled' ? 'bg-blue-50 text-blue-600 border-blue-200' : 'bg-slate-50 text-slate-500'
                  }`}>
                    {h.trigger || 'manual'}
                  </Badge>
                  <span className="text-slate-400 w-16 text-right">{timeAgo(h.completed_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
