import React, { useState, useCallback } from 'react';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import PageMeta from '@/components/PageMeta';
import { Link } from 'react-router-dom';
import {
  Calculator, TrendingUp, PoundSterling, BarChart3, Loader2,
  CheckCircle, AlertTriangle, XCircle, ArrowRight, Lock, Zap,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const VERDICT_CONFIG = {
  'Strong opportunity': { color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', icon: CheckCircle },
  'Promising with optimisation': { color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', icon: TrendingUp },
  'Risky — needs lower CPA or higher margin': { color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', icon: AlertTriangle },
  'Not viable at current metrics': { color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', icon: XCircle },
};

function SliderInput({ label, value, onChange, min, max, step, prefix, suffix, helpText }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-xs font-medium text-slate-600">{label}</label>
        <span className="text-sm font-bold font-mono text-slate-900">
          {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
        </span>
      </div>
      <Slider
        value={[value]}
        onValueChange={([v]) => onChange(v)}
        min={min}
        max={max}
        step={step}
        className="w-full"
      />
      {helpText && <p className="text-[10px] text-slate-400 mt-1">{helpText}</p>}
    </div>
  );
}

function ProjectionBar({ month, data, maxRevenue }) {
  const revPct = maxRevenue > 0 ? (data.revenue / maxRevenue) * 100 : 0;
  const profitPct = maxRevenue > 0 ? (Math.abs(data.profit) / maxRevenue) * 100 : 0;
  const isProfitable = data.profit > 0;

  return (
    <div className="flex items-end gap-3" data-testid={`projection-month-${month}`}>
      <div className="w-20 text-right shrink-0">
        <p className="text-xs font-semibold text-slate-700">Month {month}</p>
        <p className="text-[10px] text-slate-400">{data.label}</p>
      </div>
      <div className="flex-1 space-y-1.5">
        <div className="flex items-center gap-2">
          <div className="flex-1 h-6 bg-slate-100 rounded-md overflow-hidden relative">
            <div
              className="h-full bg-indigo-500 rounded-md transition-all duration-700"
              style={{ width: `${revPct}%` }}
            />
            <span className="absolute inset-0 flex items-center justify-center text-[10px] font-semibold text-white mix-blend-difference">
              Revenue: {'\u00A3'}{data.revenue.toLocaleString()}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 h-5 bg-slate-100 rounded-md overflow-hidden relative">
            <div
              className={`h-full rounded-md transition-all duration-700 ${isProfitable ? 'bg-emerald-500' : 'bg-red-400'}`}
              style={{ width: `${Math.min(profitPct, 100)}%` }}
            />
            <span className="absolute inset-0 flex items-center justify-center text-[10px] font-semibold text-white mix-blend-difference">
              {isProfitable ? 'Profit' : 'Loss'}: {'\u00A3'}{Math.abs(data.profit).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
      <div className="w-16 text-right shrink-0">
        <p className={`text-sm font-bold font-mono ${isProfitable ? 'text-emerald-600' : 'text-red-500'}`}>
          {data.roas}x
        </p>
        <p className="text-[10px] text-slate-400">ROAS</p>
      </div>
    </div>
  );
}

export default function ProfitSimulatorPage() {
  const [form, setForm] = useState({
    product_cost: 8,
    selling_price: 25,
    shipping_cost: 3,
    monthly_ad_budget: 500,
    cpm: 15,
    conversion_rate: 2,
    competition_level: 'medium',
    include_vat: true,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const update = useCallback((key, value) => {
    setForm(prev => ({ ...prev, [key]: value }));
  }, []);

  const simulate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/public/profit-simulator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (res.ok) setResult(await res.json());
    } catch {}
    setLoading(false);
  };

  const vc = result ? (VERDICT_CONFIG[result.verdict] || VERDICT_CONFIG['Not viable at current metrics']) : null;
  const maxRevenue = result ? Math.max(...result.projections.map(p => p.revenue), 1) : 1;

  return (
    <LandingLayout>
      <PageMeta
        title="Profit Simulator — Will This Product Make Money? | TrendScout"
        description="Free profit simulator for UK ecommerce sellers. Calculate margins after VAT, project 30/60/90 day revenue, and get a clear go/no-go verdict."
      />

      <div className="mx-auto max-w-6xl px-6 py-12 lg:py-16" data-testid="profit-simulator-page">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 border border-indigo-100 px-3.5 py-1.5 mb-4">
            <Calculator className="h-3.5 w-3.5 text-indigo-600" />
            <span className="text-xs font-semibold text-indigo-700">Free tool — no signup required</span>
          </div>
          <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Will this product <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">actually make money?</span>
          </h1>
          <p className="mt-3 text-base text-slate-500 max-w-xl mx-auto">
            Adjust the sliders, hit simulate, and see 30/60/90 day projections with UK VAT factored in.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Input Panel */}
          <Card className="lg:col-span-2 border border-slate-200 shadow-lg" data-testid="simulator-inputs">
            <CardContent className="p-6 space-y-5">
              <SliderInput label="Product Cost" value={form.product_cost} onChange={v => update('product_cost', v)} min={1} max={100} step={0.5} prefix={'\u00A3'} />
              <SliderInput label="Selling Price" value={form.selling_price} onChange={v => update('selling_price', v)} min={5} max={200} step={1} prefix={'\u00A3'} />
              <SliderInput label="Shipping Cost" value={form.shipping_cost} onChange={v => update('shipping_cost', v)} min={0} max={20} step={0.5} prefix={'\u00A3'} />
              <SliderInput label="Monthly Ad Budget" value={form.monthly_ad_budget} onChange={v => update('monthly_ad_budget', v)} min={100} max={5000} step={50} prefix={'\u00A3'} />
              <SliderInput label="CPM (Cost per 1000 impressions)" value={form.cpm} onChange={v => update('cpm', v)} min={3} max={50} step={1} prefix={'\u00A3'} />
              <SliderInput label="Conversion Rate" value={form.conversion_rate} onChange={v => update('conversion_rate', v)} min={0.5} max={10} step={0.1} suffix="%" />

              <div>
                <label className="text-xs font-medium text-slate-600 mb-2 block">Competition Level</label>
                <div className="flex gap-2">
                  {['low', 'medium', 'high'].map(level => (
                    <button
                      key={level}
                      onClick={() => update('competition_level', level)}
                      className={`flex-1 py-2 rounded-xl border text-xs font-semibold capitalize transition-all ${
                        form.competition_level === level
                          ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                          : 'bg-white border-slate-200 text-slate-500 hover:border-slate-300'
                      }`}
                      data-testid={`comp-${level}`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-slate-600">Include UK VAT (20%)</label>
                <button
                  onClick={() => update('include_vat', !form.include_vat)}
                  className={`w-10 h-5 rounded-full transition-all ${form.include_vat ? 'bg-indigo-600' : 'bg-slate-300'}`}
                  data-testid="vat-toggle"
                >
                  <div className={`w-4 h-4 bg-white rounded-full shadow transition-transform ${form.include_vat ? 'translate-x-5' : 'translate-x-0.5'}`} />
                </button>
              </div>

              <Button onClick={simulate} disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl h-12 text-sm font-semibold" data-testid="simulate-btn">
                {loading ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Simulating...</> : <><Zap className="h-4 w-4 mr-2" /> Run Simulation</>}
              </Button>
            </CardContent>
          </Card>

          {/* Results Panel */}
          <div className="lg:col-span-3 space-y-5">
            {!result ? (
              <Card className="border border-slate-200 shadow-lg">
                <CardContent className="flex flex-col items-center justify-center py-20 text-center">
                  <BarChart3 className="h-14 w-14 text-slate-200 mb-4" />
                  <p className="text-sm text-slate-400 max-w-xs">Adjust the sliders on the left and hit "Run Simulation" to see your projected profits.</p>
                </CardContent>
              </Card>
            ) : (
              <>
                {/* Verdict */}
                {vc && (() => {
                  const VIcon = vc.icon;
                  return (
                    <Card className={`border ${vc.border} ${vc.bg} shadow-lg`} data-testid="simulator-verdict">
                      <CardContent className="py-5 flex items-center gap-4">
                        <VIcon className={`h-7 w-7 ${vc.color} shrink-0`} />
                        <div>
                          <p className={`text-lg font-bold ${vc.color}`}>{result.verdict}</p>
                          <p className="text-xs text-slate-600">{result.verdict_detail}</p>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })()}

                {/* Unit Economics */}
                <Card className="border border-slate-200 shadow-lg" data-testid="unit-economics">
                  <CardContent className="p-5">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                      <PoundSterling className="h-3.5 w-3.5 text-emerald-600" /> Unit Economics
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <Metric label="Margin/Unit" value={`\u00A3${result.unit_economics.margin_per_unit}`} sub={`${result.unit_economics.margin_percent}%`} positive={result.unit_economics.margin_per_unit > 0} />
                      <Metric label="Est. CPA" value={`\u00A3${result.unit_economics.estimated_cpa}`} sub="cost per acquisition" positive={result.unit_economics.is_profitable_per_sale} />
                      <Metric label="Break-even CPA" value={`\u00A3${result.unit_economics.break_even_cpa}`} sub="max affordable" />
                      <Metric label="VAT/Unit" value={`\u00A3${result.unit_economics.vat_per_unit}`} sub="20% UK VAT" />
                    </div>
                  </CardContent>
                </Card>

                {/* 30/60/90 Day Projections */}
                <Card className="border border-slate-200 shadow-lg" data-testid="projections">
                  <CardContent className="p-5">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-5 flex items-center gap-2">
                      <BarChart3 className="h-3.5 w-3.5 text-indigo-600" /> 30 / 60 / 90 Day Projections
                    </p>
                    <div className="space-y-5">
                      {result.projections.map(p => (
                        <ProjectionBar key={p.month} month={p.month} data={p} maxRevenue={maxRevenue} />
                      ))}
                    </div>

                    {/* Cumulative summary */}
                    <div className="mt-5 pt-4 border-t border-slate-100 grid grid-cols-3 gap-3">
                      <div className="text-center">
                        <p className="text-[10px] text-slate-400 uppercase">Total Revenue</p>
                        <p className="text-lg font-bold font-mono text-slate-900">
                          {'\u00A3'}{result.projections[result.projections.length - 1]?.cumulative_revenue?.toLocaleString() || 0}
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-[10px] text-slate-400 uppercase">Total Profit</p>
                        <p className={`text-lg font-bold font-mono ${(result.projections[result.projections.length - 1]?.cumulative_profit || 0) > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                          {'\u00A3'}{result.projections[result.projections.length - 1]?.cumulative_profit?.toLocaleString() || 0}
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-[10px] text-slate-400 uppercase">Total Orders</p>
                        <p className="text-lg font-bold font-mono text-slate-900">
                          {result.projections[result.projections.length - 1]?.cumulative_orders?.toLocaleString() || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Upgrade CTA */}
                <div className="flex items-center justify-between gap-3 p-4 rounded-xl bg-indigo-50 border border-indigo-100">
                  <div className="flex items-center gap-2 text-sm text-indigo-700">
                    <Lock className="h-4 w-4" />
                    <span>Get AI-powered recommendations, competitor data & launch playbook</span>
                  </div>
                  <Link to="/signup">
                    <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs px-4 shrink-0" data-testid="sim-upgrade-cta">
                      Start Free <ArrowRight className="ml-1 h-3 w-3" />
                    </Button>
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </LandingLayout>
  );
}

function Metric({ label, value, sub, positive }) {
  return (
    <div className="rounded-xl p-3 bg-slate-50">
      <p className="text-[10px] text-slate-400 uppercase tracking-wide">{label}</p>
      <p className={`text-base font-bold mt-0.5 font-mono ${positive === true ? 'text-emerald-600' : positive === false ? 'text-red-500' : 'text-slate-900'}`}>{value}</p>
      {sub && <p className="text-[10px] text-slate-400">{sub}</p>}
    </div>
  );
}
