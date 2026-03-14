import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Compass, Bell, Bookmark, Store, Rocket, Eye, Zap, Sparkles,
  TrendingUp, ArrowRight, ChevronRight, Loader2,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const ICON_MAP = {
  bell: Bell,
  bookmark: Bookmark,
  store: Store,
  rocket: Rocket,
  eye: Eye,
  zap: Zap,
  sparkles: Sparkles,
  'trending-up': TrendingUp,
};

const PRIORITY_COLORS = {
  1: 'border-l-amber-500 bg-amber-50/40',
  2: 'border-l-indigo-500 bg-indigo-50/30',
  3: 'border-l-emerald-500 bg-emerald-50/30',
  4: 'border-l-violet-500 bg-violet-50/30',
  5: 'border-l-sky-500 bg-sky-50/30',
  6: 'border-l-orange-500 bg-orange-50/30',
  7: 'border-l-fuchsia-500 bg-fuchsia-50/30',
  8: 'border-l-slate-400 bg-slate-50/30',
};

export default function ProductDecisionPanel() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiGet('/api/dashboard/next-steps');
        if (res.ok) {
          const d = await res.json();
          setData(d);
        }
      } catch {}
      setLoading(false);
    })();
  }, []);

  if (loading) {
    return (
      <Card className="border-0 shadow-lg" data-testid="decision-panel-loading">
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.steps?.length) return null;

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="product-decision-panel">
      <CardHeader className="border-b border-slate-100 pb-5 bg-gradient-to-r from-sky-50 via-indigo-50 to-violet-50">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="font-manrope text-xl font-bold text-slate-900 flex items-center gap-2">
              <Compass className="h-6 w-6 text-indigo-600" />
              What Should I Do Next?
            </CardTitle>
            <p className="text-sm text-slate-600 mt-1">Personalised actions to move you forward</p>
          </div>
          <Badge className="bg-indigo-100 text-indigo-700 border-indigo-200 text-xs">
            {data.steps.length} action{data.steps.length !== 1 ? 's' : ''}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-slate-100">
          {data.steps.map((step, idx) => {
            const Icon = ICON_MAP[step.icon] || TrendingUp;
            const bgClass = PRIORITY_COLORS[step.priority] || PRIORITY_COLORS[8];

            return (
              <div
                key={step.id}
                className={`flex items-center gap-4 p-5 border-l-4 transition-colors hover:bg-slate-50/60 ${bgClass}`}
                data-testid={`decision-step-${step.id}`}
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white shadow-sm shrink-0">
                  <Icon className="h-5 w-5 text-indigo-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-slate-900 text-sm truncate">{step.title}</p>
                  <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{step.description}</p>
                </div>
                {step.product && (
                  <div className="hidden sm:flex items-center gap-2 shrink-0">
                    <span className="font-mono text-sm font-bold text-indigo-600">{step.product.score}</span>
                    <span className="text-xs text-slate-400">/100</span>
                  </div>
                )}
                <Link to={step.action.href} className="shrink-0">
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs font-semibold border-indigo-200 text-indigo-700 hover:bg-indigo-50"
                    data-testid={`decision-action-${step.id}`}
                  >
                    {step.action.label}
                    <ChevronRight className="h-3 w-3 ml-1" />
                  </Button>
                </Link>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
