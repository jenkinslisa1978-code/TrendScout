import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, ShieldAlert, Store, Megaphone, Search, TrendingUp } from 'lucide-react';
import { apiGet } from '@/lib/api';

const RISK_CONFIG = {
  Low: { color: 'bg-emerald-100 text-emerald-700 border-emerald-200', barColor: 'bg-emerald-500', label: 'Low Risk' },
  Medium: { color: 'bg-amber-100 text-amber-700 border-amber-200', barColor: 'bg-amber-500', label: 'Medium Risk' },
  High: { color: 'bg-red-100 text-red-700 border-red-200', barColor: 'bg-red-500', label: 'High Risk' },
};

export default function SaturationRadar({ productId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await apiGet(`/api/products/${productId}/saturation`);
        if (res.ok) setData(await res.json());
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, [productId]);

  if (loading) {
    return (
      <Card className="border-0 shadow-md">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 animate-spin text-indigo-400" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const cfg = RISK_CONFIG[data.risk_level] || RISK_CONFIG.Medium;

  return (
    <Card className="border-0 shadow-md" data-testid="saturation-radar">
      <CardContent className="p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-slate-600" />
            <p className="text-sm font-semibold text-slate-900">Saturation Radar</p>
          </div>
          <Badge className={`text-xs border ${cfg.color}`} data-testid="saturation-risk-level">
            {cfg.label}
          </Badge>
        </div>

        {/* Score bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-slate-500">Saturation Score</span>
            <span className="text-sm font-bold font-mono text-slate-700" data-testid="saturation-score">{data.saturation_score}/100</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div className={`h-2.5 rounded-full transition-all ${cfg.barColor}`} style={{ width: `${data.saturation_score}%` }} />
          </div>
        </div>

        {/* Signals */}
        <div className="space-y-2.5">
          <SignalRow icon={Store} label="Stores detected" value={data.stores_detected} />
          <SignalRow icon={Megaphone} label="Active ads detected" value={data.ads_detected} />
          <SignalRow icon={Search} label="Search growth" value={data.search_growth} isText />
          <SignalRow icon={TrendingUp} label="Trend stage" value={data.trend_stage} isText />
        </div>

        {data.risk_level === 'High' && (
          <div className="mt-4 p-2.5 bg-red-50 rounded-lg text-xs text-red-700 border border-red-100">
            High saturation detected. Consider finding a more niche variation or targeting a different audience.
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function SignalRow({ icon: Icon, label, value, isText }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-slate-500 flex items-center gap-2">
        <Icon className="h-3.5 w-3.5 text-slate-400" />
        {label}
      </span>
      <span className={`font-medium ${isText ? 'text-slate-700 capitalize' : 'font-mono text-slate-800'}`}>
        {value}
      </span>
    </div>
  );
}
