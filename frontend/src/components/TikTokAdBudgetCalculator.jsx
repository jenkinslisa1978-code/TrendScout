import React, { useState, useMemo } from 'react';
import { trackEvent, EVENTS } from '@/services/analytics';
import ShareResult from '@/components/ShareResult';
import { PoundSterling } from 'lucide-react';

/**
 * TikTok Ad Budget Calculator
 * Helps sellers estimate required ad spend for TikTok Shop UK campaigns.
 */
export default function TikTokAdBudgetCalculator() {
  const [dailyBudget, setDailyBudget] = useState('');
  const [cpc, setCpc] = useState('');
  const [convRate, setConvRate] = useState('');
  const [aov, setAov] = useState('');
  const [days, setDays] = useState('7');

  const dailyNum = parseFloat(dailyBudget) || 0;
  const cpcNum = parseFloat(cpc) || 0;
  const convNum = parseFloat(convRate) || 0;
  const aovNum = parseFloat(aov) || 0;
  const daysNum = parseInt(days) || 7;

  const totalBudget = dailyNum * daysNum;
  const totalClicks = cpcNum > 0 ? Math.floor(totalBudget / cpcNum) : 0;
  const expectedSales = convNum > 0 ? Math.floor(totalClicks * (convNum / 100)) : 0;
  const expectedRevenue = expectedSales * aovNum;
  const roas = totalBudget > 0 ? (expectedRevenue / totalBudget) : 0;
  const cpa = expectedSales > 0 ? (totalBudget / expectedSales) : 0;
  const hasResult = dailyNum > 0 && cpcNum > 0;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="tiktok-ad-budget-calculator">
      <h3 className="font-manrope text-lg font-semibold text-slate-900 mb-1">TikTok Ad Budget Calculator</h3>
      <p className="text-sm text-slate-500 mb-5">Estimate your TikTok Shop UK campaign costs, clicks, and expected return.</p>
      <div className="grid sm:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Daily budget (GBP)</label>
          <div className="relative">
            <PoundSterling className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input type="number" value={dailyBudget} onChange={e => setDailyBudget(e.target.value)} placeholder="20" className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="tiktok-daily-budget" />
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Avg cost per click (GBP)</label>
          <div className="relative">
            <PoundSterling className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input type="number" value={cpc} onChange={e => setCpc(e.target.value)} placeholder="0.30" step="0.01" className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="tiktok-cpc" />
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Conversion rate (%)</label>
          <input type="number" value={convRate} onChange={e => setConvRate(e.target.value)} placeholder="2.5" step="0.1" className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="tiktok-conv-rate" />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Avg order value (GBP)</label>
          <div className="relative">
            <PoundSterling className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input type="number" value={aov} onChange={e => setAov(e.target.value)} placeholder="24.99" step="0.01" className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="tiktok-aov" />
          </div>
        </div>
      </div>
      <div className="mb-4">
        <label className="block text-xs font-medium text-slate-600 mb-1">Campaign duration</label>
        <select value={days} onChange={e => setDays(e.target.value)} className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:border-indigo-500 outline-none" data-testid="tiktok-days">
          <option value="7">7 days</option>
          <option value="14">14 days</option>
          <option value="30">30 days</option>
        </select>
      </div>
      {hasResult && (
        <div className="rounded-lg bg-slate-50 p-4 grid grid-cols-3 gap-4 text-center" data-testid="tiktok-result">
          <div>
            <p className="text-xs text-slate-500">Total budget</p>
            <p className="font-mono text-base font-bold text-slate-900">&pound;{totalBudget.toFixed(0)}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Est. clicks</p>
            <p className="font-mono text-base font-bold text-slate-900">{totalClicks.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Est. sales</p>
            <p className="font-mono text-base font-bold text-emerald-600">{expectedSales}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Revenue</p>
            <p className="font-mono text-base font-bold text-emerald-600">&pound;{expectedRevenue.toFixed(0)}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">ROAS</p>
            <p className={`font-mono text-base font-bold ${roas >= 2 ? 'text-emerald-600' : roas >= 1 ? 'text-amber-600' : 'text-red-600'}`}>{roas.toFixed(2)}x</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Cost per sale</p>
            <p className="font-mono text-base font-bold text-slate-900">&pound;{cpa.toFixed(2)}</p>
          </div>
        </div>
      )}
      {hasResult && (
        <ShareResult
          tool="TikTok Ad Budget"
          resultText={`£${totalBudget.toFixed(0)} budget = ${expectedSales} est. sales (${roas.toFixed(2)}x ROAS)`}
          detail={`${daysNum}-day TikTok campaign at £${dailyNum}/day`}
        />
      )}
    </div>
  );
}
