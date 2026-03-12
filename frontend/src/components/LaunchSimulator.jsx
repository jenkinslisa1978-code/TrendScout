import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Loader2, Rocket, TrendingUp, DollarSign, ShoppingCart,
  AlertTriangle, CheckCircle2, Clock, Target, BarChart3, Info,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const POTENTIAL_CONFIG = {
  High: { color: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: Rocket, barColor: 'bg-emerald-500' },
  Moderate: { color: 'bg-amber-100 text-amber-700 border-amber-200', icon: TrendingUp, barColor: 'bg-amber-500' },
  Risky: { color: 'bg-red-100 text-red-700 border-red-200', icon: AlertTriangle, barColor: 'bg-red-500' },
};

export default function LaunchSimulator({ productId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await apiGet(`/api/ad-tests/simulate/${productId}`);
        if (res.ok) setData(await res.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, [productId]);

  if (loading) {
    return (
      <Card className="border-0 shadow-lg">
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-400" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const sim = data.simulation;
  const cfg = POTENTIAL_CONFIG[data.potential] || POTENTIAL_CONFIG.Moderate;
  const PotentialIcon = cfg.icon;

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="launch-simulator">
      <CardHeader className="bg-gradient-to-r from-teal-600 via-emerald-600 to-green-600 text-white py-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Rocket className="h-5 w-5 text-amber-300" />
          Launch Simulator
          <Badge className={`ml-auto text-[10px] border ${cfg.color}`}>
            <PotentialIcon className="h-3 w-3 mr-1" />
            {data.potential} Potential
          </Badge>
        </CardTitle>
        <p className="text-xs text-emerald-200 mt-1">
          Projected outcomes based on product signals and market data
        </p>
      </CardHeader>

      <CardContent className="p-5">
        {/* Key projections grid */}
        <div className="grid grid-cols-2 gap-3 mb-5" data-testid="sim-projections">
          <ProjectionCard
            icon={DollarSign}
            label="Profit per Sale"
            value={`£${sim.profit_per_sale}`}
            color="text-emerald-600"
            bg="bg-emerald-50"
          />
          <ProjectionCard
            icon={Target}
            label="Est. Conversion"
            value={`${sim.estimated_cvr}%`}
            color="text-indigo-600"
            bg="bg-indigo-50"
          />
          <ProjectionCard
            icon={BarChart3}
            label="Break-even Ad Cost"
            value={`£${sim.breakeven_ad_cost}`}
            color="text-amber-600"
            bg="bg-amber-50"
          />
          <ProjectionCard
            icon={ShoppingCart}
            label="Daily Sales Range"
            value={`${sim.daily_sales_range.low}–${sim.daily_sales_range.high}`}
            sub="units/day"
            color="text-teal-600"
            bg="bg-teal-50"
          />
        </div>

        {/* Detailed metrics */}
        <div className="space-y-2 mb-4">
          <MetricRow label="Estimated CPC" value={`£${sim.estimated_cpc}`} />
          <MetricRow label="Estimated CPA" value={`£${sim.estimated_cpa}`} />
          <MetricRow label="Daily Profit Range" value={`£${sim.daily_profit_range.low} – £${sim.daily_profit_range.high}`} highlight={sim.daily_profit_range.high > 0} />
          {sim.breakeven_days && <MetricRow label="Break-even Timeline" value={`~${sim.breakeven_days} days`} />}
          <MetricRow label="Assumed Daily Budget" value={`£${sim.assumed_daily_budget}`} />
        </div>

        {/* Profit visualization */}
        <div className="mb-4">
          <p className="text-xs text-slate-500 mb-2">Daily Profit Projection (£{sim.assumed_daily_budget}/day budget)</p>
          <div className="relative h-8 bg-slate-100 rounded-full overflow-hidden">
            {sim.daily_profit_range.low < 0 && (
              <div
                className="absolute left-0 top-0 h-full bg-red-200 rounded-l-full"
                style={{ width: `${Math.min(50, Math.abs(sim.daily_profit_range.low) / Math.max(Math.abs(sim.daily_profit_range.low), sim.daily_profit_range.high) * 50)}%` }}
              />
            )}
            <div
              className={`absolute top-0 h-full ${cfg.barColor} rounded-r-full`}
              style={{ left: sim.daily_profit_range.low < 0 ? '50%' : '0', width: `${Math.min(100, Math.max(5, sim.daily_profit_range.high / (sim.daily_profit_range.high + 50) * 100))}%` }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-bold text-slate-700">
                £{sim.daily_profit_range.low} to £{sim.daily_profit_range.high}/day
              </span>
            </div>
          </div>
        </div>

        {/* Risks */}
        {data.risks.length > 0 && (
          <div className="mb-4" data-testid="sim-risks">
            <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-500" /> Risk Factors
            </p>
            <div className="space-y-1.5">
              {data.risks.map((r, i) => (
                <p key={i} className="text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-1.5 border border-amber-100">{r}</p>
              ))}
            </div>
          </div>
        )}

        {/* Beginner Guidance */}
        <div className="p-3.5 bg-gradient-to-r from-indigo-50/80 to-violet-50/60 rounded-xl border border-indigo-100" data-testid="sim-guidance">
          <div className="flex items-start gap-2">
            <Info className="h-4 w-4 text-indigo-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-indigo-700 leading-relaxed">{data.guidance}</p>
          </div>
        </div>

        {/* Inputs used */}
        <details className="mt-3">
          <summary className="text-[10px] text-slate-400 cursor-pointer hover:text-slate-600">View simulation inputs</summary>
          <div className="mt-2 grid grid-cols-3 gap-2 text-[10px]">
            {Object.entries(data.inputs_used).map(([k, v]) => (
              <div key={k} className="bg-slate-50 rounded-lg p-1.5 text-center">
                <p className="text-slate-400 capitalize">{k.replace('_', ' ')}</p>
                <p className="font-mono font-bold text-slate-700">{v}</p>
              </div>
            ))}
          </div>
        </details>
      </CardContent>
    </Card>
  );
}

function ProjectionCard({ icon: Icon, label, value, sub, color, bg }) {
  return (
    <div className={`${bg} rounded-xl p-3.5 text-center`}>
      <Icon className={`h-4 w-4 ${color} mx-auto mb-1.5`} />
      <p className={`text-xl font-bold font-mono ${color}`}>{value}</p>
      {sub && <p className={`text-[10px] ${color} opacity-70`}>{sub}</p>}
      <p className="text-[10px] text-slate-500 mt-0.5">{label}</p>
    </div>
  );
}

function MetricRow({ label, value, highlight }) {
  return (
    <div className="flex items-center justify-between text-sm py-1 border-b border-slate-50 last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className={`font-mono font-medium ${highlight ? 'text-emerald-600' : 'text-slate-800'}`}>{value}</span>
    </div>
  );
}
