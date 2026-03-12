import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  TrendingUp, Pause, XCircle, Clock, Gauge, ChevronDown,
  ChevronUp, AlertTriangle, Loader2, Zap, Brain,
} from 'lucide-react';
import { apiPost } from '@/lib/api';
import { toast } from 'sonner';

const ACTION_CONFIG = {
  increase_budget: {
    label: 'Scale Up',
    color: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    badgeColor: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    icon: TrendingUp,
    iconColor: 'text-emerald-600',
  },
  maintain: {
    label: 'Maintain',
    color: 'bg-sky-50 border-sky-200 text-sky-800',
    badgeColor: 'bg-sky-100 text-sky-700 border-sky-200',
    icon: Gauge,
    iconColor: 'text-sky-600',
  },
  pause: {
    label: 'Pause',
    color: 'bg-amber-50 border-amber-200 text-amber-800',
    badgeColor: 'bg-amber-100 text-amber-700 border-amber-200',
    icon: Pause,
    iconColor: 'text-amber-600',
  },
  kill: {
    label: 'Kill',
    color: 'bg-red-50 border-red-200 text-red-800',
    badgeColor: 'bg-red-100 text-red-700 border-red-200',
    icon: XCircle,
    iconColor: 'text-red-600',
  },
  needs_more_data: {
    label: 'Collecting Data',
    color: 'bg-slate-50 border-slate-200 text-slate-700',
    badgeColor: 'bg-slate-100 text-slate-600 border-slate-200',
    icon: Clock,
    iconColor: 'text-slate-500',
  },
};

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100);
  const color = pct >= 70 ? 'bg-emerald-500' : pct >= 40 ? 'bg-amber-500' : 'bg-slate-400';
  return (
    <div className="flex items-center gap-2" data-testid="confidence-bar">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] font-mono text-slate-500 w-8 text-right">{pct}%</span>
    </div>
  );
}

function RecommendationRow({ rec }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = ACTION_CONFIG[rec.action] || ACTION_CONFIG.needs_more_data;
  const Icon = cfg.icon;

  return (
    <div className={`rounded-xl border p-3 ${cfg.color}`} data-testid={`rec-${rec.variation_id}`}>
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-white/80 flex items-center justify-center flex-shrink-0">
          <Icon className={`h-4 w-4 ${cfg.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold truncate">{rec.label}</span>
            <Badge className={`text-[10px] ${cfg.badgeColor}`}>{cfg.label}</Badge>
          </div>
          <p className="text-[10px] text-slate-500 mt-0.5">{rec.hook_type}</p>
        </div>
        {rec.action === 'increase_budget' && (
          <div className="text-right flex-shrink-0">
            <p className="text-xs font-bold text-emerald-700">
              £{rec.current_budget} → £{rec.recommended_budget}
            </p>
          </div>
        )}
        <button onClick={() => setExpanded(!expanded)} className="p-1 hover:bg-white/50 rounded">
          {expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>
      </div>

      <div className="mt-2">
        <ConfidenceBar value={rec.confidence} />
      </div>

      {expanded && (
        <div className="mt-3 space-y-2" data-testid={`rec-details-${rec.variation_id}`}>
          <div className="grid grid-cols-4 gap-2 text-center text-[10px] bg-white/60 rounded-lg p-2">
            <div><p className="font-bold">£{rec.metrics?.spend || 0}</p><p className="text-slate-400">Spend</p></div>
            <div><p className="font-bold">{rec.metrics?.ctr || 0}%</p><p className="text-slate-400">CTR</p></div>
            <div><p className="font-bold">£{rec.metrics?.cpc || 0}</p><p className="text-slate-400">CPC</p></div>
            <div><p className="font-bold">{rec.metrics?.purchases || 0}</p><p className="text-slate-400">Sales</p></div>
          </div>

          <div className="space-y-1">
            {rec.reasoning?.map((r, i) => (
              <p key={i} className="text-[11px] text-slate-600 flex items-start gap-1.5">
                <span className="text-slate-400 mt-0.5">•</span>
                {r}
              </p>
            ))}
          </div>

          {rec.flags?.length > 0 && (
            <div className="space-y-1">
              {rec.flags.map((f, i) => (
                <p key={i} className="text-[11px] text-amber-700 flex items-start gap-1.5">
                  <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                  {f}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function BudgetOptimizerCard({ testId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = useCallback(async () => {
    if (!testId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiPost(`/api/optimization/recommend/${testId}`, {});
      if (res.ok) {
        setData(await res.json());
      } else {
        setError('Could not load recommendations');
      }
    } catch (e) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  }, [testId]);

  useEffect(() => { fetchRecommendations(); }, [fetchRecommendations]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-6 text-sm text-slate-400 gap-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        Analyzing performance...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-6">
        <p className="text-xs text-slate-400">{error}</p>
        <Button size="sm" variant="outline" className="mt-2 text-xs h-7" onClick={fetchRecommendations}>
          Retry
        </Button>
      </div>
    );
  }

  if (!data) return null;

  const { recommendations, summary } = data;

  return (
    <div className="space-y-3" data-testid="budget-optimizer-card">
      {/* Summary bar */}
      <div className="flex items-center gap-2 p-3 bg-gradient-to-r from-indigo-50 to-violet-50 border border-indigo-100 rounded-xl">
        <Brain className="h-4 w-4 text-indigo-600 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-xs font-semibold text-indigo-900">Budget Optimizer</p>
          <p className="text-[10px] text-indigo-600">
            {summary.to_scale > 0 && `${summary.to_scale} to scale · `}
            {summary.to_pause > 0 && `${summary.to_pause} to pause · `}
            {summary.to_maintain > 0 && `${summary.to_maintain} steady · `}
            {summary.waiting_data > 0 && `${summary.waiting_data} collecting data`}
          </p>
        </div>
        <Badge className={`text-[10px] ${
          summary.overall_status === 'scaling' ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
          : summary.overall_status === 'struggling' ? 'bg-red-100 text-red-700 border-red-200'
          : 'bg-slate-100 text-slate-600 border-slate-200'
        }`}>
          {summary.overall_status}
        </Badge>
      </div>

      {/* Top performer callout */}
      {summary.top_performer && (
        <div className="flex items-center gap-2 p-2 bg-amber-50/60 border border-amber-100 rounded-lg">
          <Zap className="h-3.5 w-3.5 text-amber-500" />
          <p className="text-[11px] text-amber-800">
            <strong>{summary.top_performer.label}</strong> leads with {summary.top_performer.ctr}% CTR
          </p>
        </div>
      )}

      {/* Recommendations */}
      <div className="space-y-2">
        {recommendations.map((rec) => (
          <RecommendationRow key={rec.variation_id} rec={rec} />
        ))}
      </div>

      {/* Refresh */}
      <Button
        size="sm"
        variant="ghost"
        className="w-full text-xs text-slate-400 hover:text-slate-600 h-7"
        onClick={fetchRecommendations}
        data-testid="refresh-optimizer-btn"
      >
        Refresh Recommendations
      </Button>
    </div>
  );
}
