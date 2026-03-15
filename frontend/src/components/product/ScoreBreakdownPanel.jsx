import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  TrendingUp, DollarSign, Users, Megaphone, Package, Search, MessageCircle,
  ChevronDown, ChevronUp, Info, Loader2,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const SIGNAL_CONFIG = {
  trend: { icon: TrendingUp, color: '#6366f1', label: 'Trend Momentum' },
  margin: { icon: DollarSign, color: '#10b981', label: 'Profit Margin' },
  competition: { icon: Users, color: '#f59e0b', label: 'Competition Gap' },
  ad_activity: { icon: Megaphone, color: '#ec4899', label: 'Ad Activity' },
  search_growth: { icon: Search, color: '#3b82f6', label: 'Search Growth' },
  social_buzz: { icon: MessageCircle, color: '#8b5cf6', label: 'Social Buzz' },
  supplier_demand: { icon: Package, color: '#14b8a6', label: 'Supplier Reliability' },
};

export default function ScoreBreakdownPanel({ productId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await apiGet(`/api/products/${productId}/launch-score-breakdown`);
        if (res.ok) setData(await res.json());
      } catch {}
      setLoading(false);
    })();
  }, [productId]);

  if (loading) {
    return (
      <Card className="border-0 shadow-lg" data-testid="score-breakdown-loading">
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const { launch_score, components, formula, summary } = data;
  const scoreColor = launch_score >= 70 ? '#10b981' : launch_score >= 50 ? '#f59e0b' : '#ef4444';

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="score-breakdown-panel">
      <CardHeader className="pb-3 bg-gradient-to-r from-slate-900 to-slate-800">
        <div className="flex items-center justify-between">
          <CardTitle className="font-manrope text-lg font-bold text-white flex items-center gap-2">
            7-Signal Launch Score
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="font-mono text-3xl font-black" style={{ color: scoreColor }}>{launch_score}</span>
            <span className="text-slate-400 text-sm">/100</span>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-1">{formula?.description}</p>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-slate-100">
          {components?.map((c) => {
            const cfg = SIGNAL_CONFIG[c.key] || {};
            const Icon = cfg.icon || Info;
            return (
              <div key={c.key} className="px-5 py-3.5 hover:bg-slate-50/60 transition-colors" data-testid={`signal-${c.key}`}>
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg" style={{ background: `${cfg.color}15` }}>
                    <Icon className="h-4 w-4" style={{ color: cfg.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-semibold text-slate-800">{c.name}</span>
                      <div className="flex items-center gap-2">
                        <Badge className="text-[10px] font-mono px-1.5 py-0" style={{ background: `${cfg.color}15`, color: cfg.color, border: `1px solid ${cfg.color}30` }}>
                          +{c.contribution}
                        </Badge>
                        <span className="text-xs text-slate-400">{c.weight_percent}</span>
                      </div>
                    </div>
                    <Progress value={c.raw_score} className="h-1.5" />
                    <p className="text-[11px] text-slate-500 mt-1">{c.explanation}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {summary && (
          <div className="border-t border-slate-100">
            <button
              onClick={() => setExpanded(!expanded)}
              className="w-full px-5 py-3 flex items-center justify-between text-sm font-semibold text-indigo-600 hover:bg-indigo-50/50 transition-colors"
              data-testid="score-insights-toggle"
            >
              <span>Insights & Recommendations</span>
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
            {expanded && (
              <div className="px-5 pb-4 space-y-3" data-testid="score-insights-content">
                {summary.strengths?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-emerald-700 mb-1">Strengths</p>
                    {summary.strengths.map((s, i) => (
                      <p key={i} className="text-xs text-slate-600 pl-3 border-l-2 border-emerald-300 mb-1">{s.name}: {s.explanation}</p>
                    ))}
                  </div>
                )}
                {summary.weaknesses?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-amber-700 mb-1">Areas to Watch</p>
                    {summary.weaknesses.map((w, i) => (
                      <p key={i} className="text-xs text-slate-600 pl-3 border-l-2 border-amber-300 mb-1">{w.name}: {w.explanation}</p>
                    ))}
                  </div>
                )}
                {summary.improvements && (
                  <div>
                    <p className="text-xs font-semibold text-indigo-700 mb-1">Improvement Tips</p>
                    {Object.entries(summary.improvements).map(([key, tip]) => (
                      <p key={key} className="text-xs text-slate-600 pl-3 border-l-2 border-indigo-300 mb-1">{tip}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
