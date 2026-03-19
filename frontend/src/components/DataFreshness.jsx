import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Clock, Database, RefreshCw, CheckCircle2 } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const SOURCE_LABELS = {
  amazon_movers: { label: 'Amazon Movers', color: 'bg-orange-50 text-orange-700 border-orange-200' },
  tiktok_trends: { label: 'TikTok Trends', color: 'bg-pink-50 text-pink-700 border-pink-200' },
  aliexpress: { label: 'AliExpress', color: 'bg-red-50 text-red-700 border-red-200' },
  amazon_trends: { label: 'Amazon Trends', color: 'bg-amber-50 text-amber-700 border-amber-200' },
  cj_dropshipping: { label: 'CJ Dropshipping', color: 'bg-blue-50 text-blue-700 border-blue-200' },
  unknown: { label: 'Multi-Source', color: 'bg-slate-50 text-slate-600 border-slate-200' },
};

function timeAgo(dateStr) {
  if (!dateStr) return 'Unknown';
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days} days ago`;
  if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
  return `${Math.floor(days / 30)} months ago`;
}

function freshness(dateStr) {
  if (!dateStr) return { label: 'Unknown', color: 'text-slate-400', dotColor: 'bg-slate-300' };
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = diff / 3600000;
  if (hours < 6) return { label: 'Fresh', color: 'text-emerald-600', dotColor: 'bg-emerald-400' };
  if (hours < 24) return { label: 'Recent', color: 'text-blue-600', dotColor: 'bg-blue-400' };
  if (hours < 72) return { label: 'Recent', color: 'text-amber-600', dotColor: 'bg-amber-400' };
  return { label: 'Aging', color: 'text-slate-500', dotColor: 'bg-slate-400' };
}

export function DataFreshnessBadge({ lastUpdated, dataSource, size = 'default' }) {
  const f = freshness(lastUpdated);
  const source = SOURCE_LABELS[dataSource] || SOURCE_LABELS.unknown;

  if (size === 'compact') {
    return (
      <TooltipProvider delayDuration={200}>
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="inline-flex items-center gap-1 text-[10px] text-slate-400 cursor-help">
              <span className={`w-1.5 h-1.5 rounded-full ${f.dotColor}`} />
              {timeAgo(lastUpdated)}
            </span>
          </TooltipTrigger>
          <TooltipContent side="top" className="text-xs max-w-[200px]">
            <p>Source: {source.label}</p>
            <p>Updated: {lastUpdated ? new Date(lastUpdated).toLocaleDateString() : 'N/A'}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <div className="flex items-center gap-2 flex-wrap" data-testid="data-freshness-badge">
      <Badge className={`${source.color} border text-[10px] gap-1`}>
        <Database className="h-2.5 w-2.5" />
        {source.label}
      </Badge>
      <span className={`inline-flex items-center gap-1 text-xs ${f.color}`}>
        <span className={`w-1.5 h-1.5 rounded-full ${f.dotColor} animate-pulse`} />
        Updated {timeAgo(lastUpdated)}
      </span>
    </div>
  );
}

export function DataFreshnessCard({ product }) {
  if (!product) return null;

  const lastUpdated = product.last_updated || product.updated_at || product.scores_updated_at;
  const scoresUpdated = product.scores_updated_at;
  const dataSource = product.data_source || 'unknown';
  const dataSourceType = product.data_source_type || 'unknown';
  const source = SOURCE_LABELS[dataSource] || SOURCE_LABELS.unknown;
  const f = freshness(lastUpdated);

  return (
    <div className="bg-slate-50 rounded-xl border border-slate-100 p-4" data-testid="data-freshness-card">
      <div className="flex items-center gap-2 mb-3">
        <RefreshCw className="h-4 w-4 text-slate-500" />
        <h4 className="text-sm font-semibold text-slate-700">Data Freshness</h4>
        <span className={`inline-flex items-center gap-1 text-xs ${f.color} ml-auto`}>
          <span className={`w-1.5 h-1.5 rounded-full ${f.dotColor}`} />
          {f.label}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-[10px] text-slate-400 uppercase tracking-wider">Source</p>
          <Badge className={`${source.color} border text-[10px] mt-1`}>
            {source.label}
          </Badge>
        </div>
        <div>
          <p className="text-[10px] text-slate-400 uppercase tracking-wider">Type</p>
          <p className="text-xs text-slate-600 mt-1 capitalize">{dataSourceType}</p>
        </div>
        <div>
          <p className="text-[10px] text-slate-400 uppercase tracking-wider">Last Updated</p>
          <p className="text-xs text-slate-600 mt-1 flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {timeAgo(lastUpdated)}
          </p>
        </div>
        <div>
          <p className="text-[10px] text-slate-400 uppercase tracking-wider">Scores Refreshed</p>
          <p className="text-xs text-slate-600 mt-1 flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3" />
            {timeAgo(scoresUpdated)}
          </p>
        </div>
      </div>
      <p className="text-[10px] text-slate-400 mt-3 pt-2 border-t border-slate-200">
        Scores are automatically refreshed every 4 hours. Product data is sourced from live marketplaces.
      </p>
    </div>
  );
}
