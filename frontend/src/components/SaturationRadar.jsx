import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, ShieldAlert, Store, Megaphone, Search, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { apiGet } from '@/lib/api';

const RISK_CONFIG = {
  Low: { color: 'bg-emerald-100 text-emerald-700 border-emerald-200', barColor: '#10b981', label: 'Low Risk', desc: 'Low competition - good entry window.' },
  Medium: { color: 'bg-amber-100 text-amber-700 border-amber-200', barColor: '#f59e0b', label: 'Medium Risk', desc: 'Moderate competition. Differentiate your offer.' },
  High: { color: 'bg-red-100 text-red-700 border-red-200', barColor: '#ef4444', label: 'High Risk', desc: 'Crowded market. Find a niche angle or skip.' },
};

function GaugeMeter({ value, size = 140, strokeWidth = 14 }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = Math.PI * radius;
  const pct = Math.min(100, Math.max(0, value));
  const offset = circumference - (pct / 100) * circumference;

  let color = '#10b981';
  if (pct >= 70) color = '#ef4444';
  else if (pct >= 40) color = '#f59e0b';

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size / 2 + 10 }}>
      <svg width={size} height={size / 2 + 10} viewBox={`0 0 ${size} ${size / 2 + 10}`}>
        {/* Background arc */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Value arc */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="absolute bottom-0 text-center" style={{ width: size }}>
        <span className="text-2xl font-bold font-mono" style={{ color }} data-testid="saturation-score">{value}</span>
        <span className="text-xs text-slate-400">/100</span>
      </div>
    </div>
  );
}

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
  const score = data.saturation_score || 0;

  const breakdownData = [
    { name: 'Stores', value: Math.min(100, (data.stores_detected || 0) * 2) },
    { name: 'Ads', value: Math.min(100, (data.ads_detected || 0)) },
    { name: 'Remaining', value: Math.max(0, 100 - score) },
  ];
  const pieColors = ['#ef4444', '#f59e0b', '#e2e8f0'];

  return (
    <Card className="border-0 shadow-md" data-testid="saturation-radar">
      <CardContent className="p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-slate-600" />
            <p className="text-sm font-semibold text-slate-900">Saturation Meter</p>
          </div>
          <Badge className={`text-xs border ${cfg.color}`} data-testid="saturation-risk-level">
            {cfg.label}
          </Badge>
        </div>

        {/* Gauge + Mini pie */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex-1 flex justify-center" data-testid="saturation-gauge">
            <GaugeMeter value={score} />
          </div>
          <div className="w-[80px]">
            <ResponsiveContainer width="100%" height={80}>
              <PieChart>
                <Pie data={breakdownData} dataKey="value" cx="50%" cy="50%" innerRadius={22} outerRadius={34} startAngle={90} endAngle={-270} paddingAngle={2}>
                  {breakdownData.map((_, i) => <Cell key={i} fill={pieColors[i]} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center">
              <span className="text-[9px] text-slate-400">Breakdown</span>
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-xs text-slate-500 mb-3 text-center">{cfg.desc}</p>

        {/* Signal rows */}
        <div className="space-y-2 border-t border-slate-100 pt-3">
          <SignalRow icon={Store} label="Stores detected" value={data.stores_detected} warn={data.stores_detected > 30} />
          <SignalRow icon={Megaphone} label="Active ads" value={data.ads_detected} warn={data.ads_detected > 200} />
          <SignalRow icon={Search} label="Search growth" value={data.search_growth} isText />
          <SignalRow icon={TrendingUp} label="Trend stage" value={data.trend_stage} isText />
        </div>

        {/* Warning or opportunity */}
        {data.risk_level === 'High' && (
          <div className="mt-3 p-2.5 bg-red-50 rounded-lg text-xs text-red-700 border border-red-100 flex items-start gap-2">
            <AlertTriangle className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
            High saturation detected. Consider a niche variation or different audience.
          </div>
        )}
        {data.risk_level === 'Low' && (
          <div className="mt-3 p-2.5 bg-emerald-50 rounded-lg text-xs text-emerald-700 border border-emerald-100 flex items-start gap-2">
            <CheckCircle2 className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
            Low saturation - great window of opportunity to enter this market.
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function SignalRow({ icon: Icon, label, value, isText, warn }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-slate-500 flex items-center gap-2">
        <Icon className="h-3.5 w-3.5 text-slate-400" />
        {label}
      </span>
      <span className={`font-medium ${isText ? 'text-slate-700 capitalize' : warn ? 'font-mono text-red-600' : 'font-mono text-slate-800'}`}>
        {typeof value === 'number' && !isText ? value.toLocaleString() : value}
      </span>
    </div>
  );
}
