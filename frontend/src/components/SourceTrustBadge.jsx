import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Wifi, BarChart3, AlertCircle, Clock } from 'lucide-react';

const CONFIDENCE_CONFIG = {
  live: {
    label: 'Live Data',
    icon: Wifi,
    className: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dotColor: 'bg-emerald-500',
  },
  estimated: {
    label: 'Estimated',
    icon: BarChart3,
    className: 'bg-amber-50 text-amber-700 border-amber-200',
    dotColor: 'bg-amber-500',
  },
  fallback: {
    label: 'Fallback',
    icon: AlertCircle,
    className: 'bg-slate-50 text-slate-500 border-slate-200',
    dotColor: 'bg-slate-400',
  },
};

/**
 * Source trust badge — displays "Live Data", "Estimated", or "Fallback"
 * Usage: <SourceTrustBadge confidence="live" />
 */
export function SourceTrustBadge({ confidence, size = 'sm', showIcon = true }) {
  const cfg = CONFIDENCE_CONFIG[confidence] || CONFIDENCE_CONFIG.fallback;
  const Icon = cfg.icon;
  const isSmall = size === 'xs';

  return (
    <Badge
      className={`inline-flex items-center gap-1 font-medium border ${cfg.className} ${
        isSmall ? 'text-[9px] px-1.5 py-0' : 'text-[10px] px-2 py-0.5'
      }`}
      data-testid={`trust-badge-${confidence}`}
    >
      {showIcon && <Icon className={isSmall ? 'h-2.5 w-2.5' : 'h-3 w-3'} />}
      {cfg.label}
    </Badge>
  );
}

/**
 * Source dot indicator — small colored dot (green/amber/gray)
 * Usage: <SourceDot confidence="live" />
 */
export function SourceDot({ confidence }) {
  const cfg = CONFIDENCE_CONFIG[confidence] || CONFIDENCE_CONFIG.fallback;
  return (
    <span
      className={`inline-block w-1.5 h-1.5 rounded-full ${cfg.dotColor}`}
      title={cfg.label}
      data-testid={`source-dot-${confidence}`}
    />
  );
}

/**
 * Freshness indicator — shows how recently data was updated
 * Usage: <FreshnessIndicator timestamp="2026-03-12T10:00:00Z" />
 */
export function FreshnessIndicator({ timestamp, className = '' }) {
  if (!timestamp) {
    return (
      <span className={`text-[10px] text-slate-400 ${className}`} data-testid="freshness-indicator">
        No data
      </span>
    );
  }

  const date = new Date(timestamp);
  const now = new Date();
  const hoursAgo = Math.round((now - date) / (1000 * 60 * 60));

  let label = '';
  let color = 'text-slate-400';

  if (hoursAgo < 1) {
    label = 'Just now';
    color = 'text-emerald-600';
  } else if (hoursAgo < 6) {
    label = `${hoursAgo}h ago`;
    color = 'text-emerald-600';
  } else if (hoursAgo < 24) {
    label = `${hoursAgo}h ago`;
    color = 'text-amber-600';
  } else {
    const daysAgo = Math.round(hoursAgo / 24);
    label = `${daysAgo}d ago`;
    color = daysAgo > 7 ? 'text-red-500' : 'text-amber-600';
  }

  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] ${color} ${className}`}
      data-testid="freshness-indicator"
    >
      <Clock className="h-2.5 w-2.5" />
      {label}
    </span>
  );
}

/**
 * Source breakdown panel — shows where each signal comes from
 * Usage: <SourceBreakdownPanel metadata={product.scoring_metadata} />
 */
export function SourceBreakdownPanel({ metadata }) {
  if (!metadata?.source_breakdown) return null;

  const entries = Object.entries(metadata.source_breakdown);

  return (
    <div className="space-y-1.5" data-testid="source-breakdown-panel">
      <p className="text-[11px] font-semibold text-slate-600">Signal Sources</p>
      <div className="grid grid-cols-2 gap-1">
        {entries.map(([key, info]) => (
          <div
            key={key}
            className="flex items-center gap-1.5 text-[10px] bg-slate-50 rounded px-2 py-1"
          >
            <SourceDot confidence={info.confidence} />
            <span className="text-slate-600 capitalize">{key.replace(/_/g, ' ')}</span>
            <span className="ml-auto text-slate-400">{info.source}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
