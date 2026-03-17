import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Brain, TrendingUp, Pause, XCircle, Clock, ArrowRight, Loader2,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const STATUS_ICONS = {
  increase_budget: { icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  pause: { icon: Pause, color: 'text-amber-600', bg: 'bg-amber-50' },
  kill: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50' },
  needs_more_data: { icon: Clock, color: 'text-slate-500', bg: 'bg-slate-50' },
};

export default function OptimizationDashboardWidget() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiGet('/api/optimization/dashboard-summary');
        if (res.ok) setData(await res.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  if (loading) {
    return (
      <Card className="border-0 shadow-md">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 animate-spin text-indigo-400" />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.total_active_tests === 0) return null;

  const actionItems = [
    ...data.candidates_to_scale.map((d) => ({ ...d, type: 'increase_budget' })),
    ...data.losers_to_pause.map((d) => ({ ...d, type: d.action })),
  ];

  const hasActions = actionItems.length > 0;

  return (
    <Card className="border-0 shadow-md overflow-hidden" data-testid="optimization-dashboard-widget">
      <CardHeader className="py-3 px-4 bg-gradient-to-r from-indigo-600 to-violet-600">
        <CardTitle className="text-sm font-semibold text-white flex items-center gap-2">
          <Brain className="h-4 w-4" />
          Budget Optimiser
          {hasActions && (
            <Badge className="ml-auto bg-white/20 text-white border-white/30 text-[10px]">
              {actionItems.length} action{actionItems.length !== 1 ? 's' : ''} needed
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        {/* Summary stats */}
        <div className="grid grid-cols-4 gap-2 text-center">
          <div className="bg-emerald-50 rounded-lg p-2">
            <p className="text-lg font-bold text-emerald-700">{data.candidates_to_scale.length}</p>
            <p className="text-[10px] text-emerald-600">Scale</p>
          </div>
          <div className="bg-amber-50 rounded-lg p-2">
            <p className="text-lg font-bold text-amber-700">
              {data.losers_to_pause.filter((d) => d.action === 'pause').length}
            </p>
            <p className="text-[10px] text-amber-600">Pause</p>
          </div>
          <div className="bg-red-50 rounded-lg p-2">
            <p className="text-lg font-bold text-red-700">
              {data.losers_to_pause.filter((d) => d.action === 'kill').length}
            </p>
            <p className="text-[10px] text-red-600">Kill</p>
          </div>
          <div className="bg-slate-50 rounded-lg p-2">
            <p className="text-lg font-bold text-slate-600">{data.waiting_data.length}</p>
            <p className="text-[10px] text-slate-500">Waiting</p>
          </div>
        </div>

        {/* Action items (top 3) */}
        {hasActions && (
          <div className="space-y-1.5">
            {actionItems.slice(0, 3).map((item, i) => {
              const cfg = STATUS_ICONS[item.type] || STATUS_ICONS.needs_more_data;
              const Icon = cfg.icon;
              return (
                <div
                  key={i}
                  className={`flex items-center gap-2.5 p-2 rounded-lg ${cfg.bg} cursor-pointer hover:opacity-80 transition-opacity`}
                  onClick={() => navigate(`/product/${item.test_id}`)}
                  data-testid={`opt-action-${i}`}
                >
                  <Icon className={`h-3.5 w-3.5 ${cfg.color} flex-shrink-0`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-slate-800 truncate">{item.product_name || 'Ad Test'}</p>
                    <p className="text-[10px] text-slate-500 truncate">
                      {item.label} — {item.reasoning?.[0]}
                    </p>
                  </div>
                  <Badge className="text-[10px] bg-white/80 text-slate-600 border-slate-200">
                    {Math.round(item.confidence * 100)}%
                  </Badge>
                </div>
              );
            })}
          </div>
        )}

        {!hasActions && data.waiting_data.length > 0 && (
          <div className="text-center py-2">
            <p className="text-xs text-slate-500">
              {data.waiting_data.length} test{data.waiting_data.length !== 1 ? 's' : ''} collecting data
            </p>
            <p className="text-[10px] text-slate-400 mt-1">Recommendations will appear once enough data is collected</p>
          </div>
        )}

        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="flex-1 text-xs text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 h-8"
            onClick={() => navigate('/optimization')}
            data-testid="open-optimiser-btn"
          >
            <Brain className="mr-1 h-3 w-3" />
            Open Optimiser
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="flex-1 text-xs text-slate-500 hover:text-slate-700 hover:bg-slate-50 h-8"
            onClick={() => navigate('/ad-tests')}
            data-testid="view-all-tests-btn"
          >
            View Tests
            <ArrowRight className="ml-1 h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
