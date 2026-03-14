import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calculator, TrendingUp, PoundSterling, ArrowRight } from 'lucide-react';

export default function ProfitabilityCalculator({ productId, productName }) {
  const [inputs, setInputs] = useState({
    daily_ad_budget: 10,
    conversion_rate: 2.0,
    avg_cpc: 0.50,
    days: 30,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const calculate = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('trendscout_token');
      const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/profitability-calculator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ product_id: productId, ...inputs }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      // silent
    }
    setLoading(false);
  };

  const verdictStyles = {
    green: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    amber: 'bg-amber-50 border-amber-200 text-amber-800',
    red: 'bg-red-50 border-red-200 text-red-800',
  };

  return (
    <Card className="border-slate-200" data-testid="profitability-calculator">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-manrope flex items-center gap-2">
          <Calculator className="h-5 w-5 text-indigo-500" />
          Profitability Calculator
        </CardTitle>
        <p className="text-xs text-slate-500">Estimate your ROI before spending on ads</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label className="text-xs text-slate-600">Daily Ad Budget (£)</Label>
            <Input
              type="number"
              value={inputs.daily_ad_budget}
              onChange={(e) => setInputs({ ...inputs, daily_ad_budget: +e.target.value })}
              className="mt-1"
              data-testid="calc-budget"
            />
          </div>
          <div>
            <Label className="text-xs text-slate-600">Conversion Rate (%)</Label>
            <Input
              type="number"
              step="0.1"
              value={inputs.conversion_rate}
              onChange={(e) => setInputs({ ...inputs, conversion_rate: +e.target.value })}
              className="mt-1"
              data-testid="calc-conversion"
            />
          </div>
          <div>
            <Label className="text-xs text-slate-600">Avg Cost Per Click (£)</Label>
            <Input
              type="number"
              step="0.01"
              value={inputs.avg_cpc}
              onChange={(e) => setInputs({ ...inputs, avg_cpc: +e.target.value })}
              className="mt-1"
              data-testid="calc-cpc"
            />
          </div>
          <div>
            <Label className="text-xs text-slate-600">Test Duration (days)</Label>
            <Input
              type="number"
              value={inputs.days}
              onChange={(e) => setInputs({ ...inputs, days: +e.target.value })}
              className="mt-1"
              data-testid="calc-days"
            />
          </div>
        </div>

        <Button onClick={calculate} disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700" data-testid="calc-submit">
          {loading ? 'Calculating...' : 'Calculate ROI'}
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>

        {result && result.projections && (
          <div className="space-y-3 pt-2">
            {/* Verdict */}
            <div className={`p-3 rounded-lg border ${verdictStyles[result.verdict_color] || verdictStyles.amber}`}>
              <p className="text-sm font-semibold" data-testid="calc-verdict">{result.verdict}</p>
            </div>

            {/* Key Numbers */}
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-slate-50 rounded-lg p-2.5 text-center">
                <p className="text-[10px] text-slate-500">Total Revenue</p>
                <p className="text-sm font-bold text-slate-900" data-testid="calc-revenue">£{result.projections.total_revenue.toFixed(2)}</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-2.5 text-center">
                <p className="text-[10px] text-slate-500">Ad Spend</p>
                <p className="text-sm font-bold text-slate-900">£{result.projections.total_ad_spend.toFixed(2)}</p>
              </div>
              <div className={`rounded-lg p-2.5 text-center ${result.projections.total_profit >= 0 ? 'bg-emerald-50' : 'bg-red-50'}`}>
                <p className="text-[10px] text-slate-500">Net Profit</p>
                <p className={`text-sm font-bold ${result.projections.total_profit >= 0 ? 'text-emerald-700' : 'text-red-700'}`} data-testid="calc-profit">
                  £{result.projections.total_profit.toFixed(2)}
                </p>
              </div>
            </div>

            {/* Details */}
            <div className="text-xs text-slate-500 space-y-1">
              <div className="flex justify-between">
                <span>ROI</span>
                <span className="font-semibold text-slate-700" data-testid="calc-roi">{result.projections.roi_percent.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Est. {result.inputs.days}-day sales</span>
                <span className="font-semibold text-slate-700">{result.projections.total_sales} units</span>
              </div>
              <div className="flex justify-between">
                <span>Cost per acquisition</span>
                <span className="font-semibold text-slate-700">£{result.break_even.cost_per_acquisition.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Break-even conversion</span>
                <span className="font-semibold text-slate-700">{result.break_even.break_even_conversion_rate.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
