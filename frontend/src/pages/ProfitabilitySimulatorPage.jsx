import React, { useState } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  DollarSign, TrendingUp, Calculator, AlertTriangle, CheckCircle,
  XCircle, Clock, BarChart3, Loader2, ArrowRight,
} from 'lucide-react';
import api from '@/lib/api';

const COMPETITION_OPTIONS = [
  { value: 'low', label: 'Low', desc: 'Few competitors, niche product' },
  { value: 'medium', label: 'Medium', desc: 'Some competitors, growing market' },
  { value: 'high', label: 'High', desc: 'Many competitors, saturated niche' },
];

export default function ProfitabilitySimulatorPage() {
  const [form, setForm] = useState({
    product_cost: 12, selling_price: 29.99, cpm: 15,
    conversion_rate: 2, monthly_ad_budget: 1000, shipping_cost: 3,
    competition_level: 'medium',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const update = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const simulate = async () => {
    setLoading(true);
    try {
      const res = await api.post('/api/tools/profitability-simulator', form);
      if (res.ok) setResult(res.data);
    } catch {}
    setLoading(false);
  };

  const verdictConfig = {
    'Strong opportunity': { color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200', icon: CheckCircle },
    'Promising with optimisation': { color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200', icon: TrendingUp },
    'Risky — needs lower CPA or higher margin': { color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200', icon: AlertTriangle },
    'Not viable at current metrics': { color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200', icon: XCircle },
  };

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto p-6 space-y-6" data-testid="profitability-simulator-page">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Profitability Simulator</h1>
          <p className="text-sm text-slate-500 mt-1">Estimate break-even CPA, time-to-saturation, and monthly profit before you launch.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Input Panel */}
          <Card className="lg:col-span-2 border-0 shadow-lg" data-testid="simulator-inputs">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Calculator className="h-5 w-5 text-indigo-600" /> Inputs
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs text-slate-600">Product Cost ($)</Label>
                  <Input type="number" value={form.product_cost} onChange={e => update('product_cost', +e.target.value)} className="mt-1" data-testid="input-product-cost" />
                </div>
                <div>
                  <Label className="text-xs text-slate-600">Selling Price ($)</Label>
                  <Input type="number" value={form.selling_price} onChange={e => update('selling_price', +e.target.value)} className="mt-1" data-testid="input-selling-price" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs text-slate-600">Shipping Cost ($)</Label>
                  <Input type="number" value={form.shipping_cost} onChange={e => update('shipping_cost', +e.target.value)} className="mt-1" data-testid="input-shipping-cost" />
                </div>
                <div>
                  <Label className="text-xs text-slate-600">CPM ($)</Label>
                  <Input type="number" value={form.cpm} onChange={e => update('cpm', +e.target.value)} className="mt-1" data-testid="input-cpm" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs text-slate-600">Conversion Rate (%)</Label>
                  <Input type="number" step="0.1" value={form.conversion_rate} onChange={e => update('conversion_rate', +e.target.value)} className="mt-1" data-testid="input-cvr" />
                </div>
                <div>
                  <Label className="text-xs text-slate-600">Monthly Ad Budget ($)</Label>
                  <Input type="number" value={form.monthly_ad_budget} onChange={e => update('monthly_ad_budget', +e.target.value)} className="mt-1" data-testid="input-budget" />
                </div>
              </div>
              <div>
                <Label className="text-xs text-slate-600 mb-2 block">Competition Level</Label>
                <div className="flex gap-2">
                  {COMPETITION_OPTIONS.map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => update('competition_level', opt.value)}
                      className={`flex-1 p-2 rounded-lg border text-xs font-medium transition-all ${
                        form.competition_level === opt.value
                          ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                          : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                      }`}
                      data-testid={`comp-${opt.value}`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
              <Button onClick={simulate} disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700" data-testid="simulate-btn">
                {loading ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Simulating...</> : <><BarChart3 className="h-4 w-4 mr-2" /> Run Simulation</>}
              </Button>
            </CardContent>
          </Card>

          {/* Results Panel */}
          <div className="lg:col-span-3 space-y-4">
            {!result ? (
              <Card className="border-0 shadow-lg">
                <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                  <BarChart3 className="h-12 w-12 text-slate-300 mb-4" />
                  <p className="text-sm text-slate-500">Configure your product inputs and click "Run Simulation" to see profitability projections.</p>
                </CardContent>
              </Card>
            ) : (
              <>
                {/* Verdict */}
                {(() => {
                  const vc = verdictConfig[result.verdict] || verdictConfig['Not viable at current metrics'];
                  const VIcon = vc.icon;
                  return (
                    <Card className={`border ${vc.border} ${vc.bg} shadow-lg`} data-testid="simulator-verdict">
                      <CardContent className="py-4 flex items-center gap-3">
                        <VIcon className={`h-6 w-6 ${vc.color}`} />
                        <div>
                          <p className={`text-base font-bold ${vc.color}`}>{result.verdict}</p>
                          <p className="text-xs text-slate-600">
                            {result.break_even_possible ? 'Break-even is achievable with these metrics' : 'CPA exceeds margin — adjust pricing or targeting'}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })()}

                {/* Unit Economics */}
                <Card className="border-0 shadow-lg" data-testid="unit-economics">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-bold flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-emerald-600" /> Unit Economics
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      <MetricCard label="Margin/Unit" value={`$${result.unit_economics.margin_per_unit}`} sub={`${result.unit_economics.margin_percent}%`} positive={result.unit_economics.margin_per_unit > 0} />
                      <MetricCard label="Est. CPA" value={`$${result.unit_economics.estimated_cpa}`} sub="cost per acquisition" positive={result.unit_economics.is_profitable_per_sale} />
                      <MetricCard label="Break-even CPA" value={`$${result.unit_economics.break_even_cpa}`} sub="max affordable CPA" />
                      <MetricCard label="Profitable?" value={result.unit_economics.is_profitable_per_sale ? 'Yes' : 'No'} positive={result.unit_economics.is_profitable_per_sale} highlight />
                    </div>
                  </CardContent>
                </Card>

                {/* Monthly Projection */}
                <Card className="border-0 shadow-lg" data-testid="monthly-projection">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-bold flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-indigo-600" /> Monthly Projection
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      <MetricCard label="Ad Budget" value={`$${result.monthly_projection.ad_budget.toLocaleString()}`} />
                      <MetricCard label="Est. Orders" value={result.monthly_projection.estimated_orders} sub={`${result.monthly_projection.estimated_clicks?.toLocaleString()} clicks`} />
                      <MetricCard label="Revenue" value={`$${result.monthly_projection.revenue.toLocaleString()}`} positive={result.monthly_projection.revenue > result.monthly_projection.ad_budget} />
                      <MetricCard label="Net Profit" value={`$${result.monthly_projection.profit.toLocaleString()}`} positive={result.monthly_projection.profit > 0} highlight />
                    </div>
                    <div className="mt-3 flex items-center gap-4">
                      <Badge className="bg-slate-100 text-slate-700 border-slate-200 text-xs">
                        ROAS: {result.monthly_projection.roas}x
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                {/* Saturation */}
                <Card className="border-0 shadow-lg" data-testid="saturation-analysis">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-bold flex items-center gap-2">
                      <Clock className="h-4 w-4 text-amber-600" /> Saturation Risk
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                      <MetricCard label="Competition" value={result.saturation_analysis.competition_level} />
                      <MetricCard label="Time to Saturation" value={`~${result.saturation_analysis.estimated_months_to_saturation} months`} />
                      <MetricCard label="Risk Level" value={result.saturation_analysis.saturation_risk} positive={result.saturation_analysis.saturation_risk === 'Low'} />
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

function MetricCard({ label, value, sub, positive, highlight }) {
  return (
    <div className={`rounded-lg p-3 ${highlight ? (positive ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200') : 'bg-slate-50'}`}>
      <p className="text-[10px] text-slate-500 uppercase tracking-wide">{label}</p>
      <p className={`text-lg font-bold mt-0.5 ${positive === true ? 'text-emerald-700' : positive === false ? 'text-red-600' : 'text-slate-900'}`}>{value}</p>
      {sub && <p className="text-[10px] text-slate-400">{sub}</p>}
    </div>
  );
}
