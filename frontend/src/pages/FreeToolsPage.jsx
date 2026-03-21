import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { faqSchema, breadcrumbSchema } from '@/components/PageMeta';
import { trackEvent, EVENTS } from '@/services/analytics';
import EmailCapture from '@/components/EmailCapture';
import ShareResult from '@/components/ShareResult';
import TikTokAdBudgetCalculator from '@/components/TikTokAdBudgetCalculator';
import ProductValidationChecklist from '@/components/ProductValidationChecklist';
import { ArrowRight, Calculator, PoundSterling, BarChart3, TrendingUp, Receipt, CheckCircle, Video, ClipboardCheck } from 'lucide-react';

function ProfitMarginCalculator() {
  const [cost, setCost] = useState('');
  const [selling, setSelling] = useState('');
  const [shipping, setShipping] = useState('');
  const vatRate = 0.2;

  const costNum = parseFloat(cost) || 0;
  const sellingNum = parseFloat(selling) || 0;
  const shippingNum = parseFloat(shipping) || 0;
  const vatAmount = sellingNum * vatRate;
  const totalCost = costNum + shippingNum;
  const grossProfit = sellingNum - totalCost;
  const netProfit = grossProfit - vatAmount;
  const marginPct = sellingNum > 0 ? ((netProfit / sellingNum) * 100) : 0;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="profit-margin-calculator">
      <h3 className="font-manrope text-lg font-semibold text-slate-900 mb-1">UK Profit Margin Calculator</h3>
      <p className="text-sm text-slate-500 mb-5">Calculate your profit margin after VAT, shipping, and product costs.</p>
      <div className="grid sm:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Product cost (&pound;)</label>
          <input type="number" value={cost} onChange={e => setCost(e.target.value)} placeholder="8.50" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="calc-cost-input" />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Selling price (&pound;)</label>
          <input type="number" value={selling} onChange={e => setSelling(e.target.value)} placeholder="24.99" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="calc-selling-input" />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Shipping cost (&pound;)</label>
          <input type="number" value={shipping} onChange={e => setShipping(e.target.value)} placeholder="3.50" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="calc-shipping-input" />
        </div>
      </div>
      {sellingNum > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-slate-100">
          <div className="text-center">
            <p className="text-xs text-slate-500">VAT (20%)</p>
            <p className="font-mono text-base font-bold text-slate-900">&pound;{vatAmount.toFixed(2)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Total cost</p>
            <p className="font-mono text-base font-bold text-slate-900">&pound;{totalCost.toFixed(2)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Net profit</p>
            <p className={`font-mono text-base font-bold ${netProfit >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>&pound;{netProfit.toFixed(2)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Margin</p>
            <p className={`font-mono text-base font-bold ${marginPct >= 20 ? 'text-emerald-600' : marginPct >= 0 ? 'text-amber-600' : 'text-red-600'}`}>{marginPct.toFixed(1)}%</p>
          </div>
        </div>
      )}
      {sellingNum > 0 && (
        <ShareResult
          tool="Profit Margin"
          resultText={`My UK profit margin is ${marginPct.toFixed(1)}%`}
          detail={`£${netProfit.toFixed(2)} net profit per unit (after 20% VAT)`}
        />
      )}
    </div>
  );
}

function RoasCalculator() {
  const [revenue, setRevenue] = useState('');
  const [adSpend, setAdSpend] = useState('');

  const revNum = parseFloat(revenue) || 0;
  const adNum = parseFloat(adSpend) || 0;
  const roas = adNum > 0 ? (revNum / adNum) : 0;
  const breakEvenRoas = 1;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="roas-calculator">
      <h3 className="font-manrope text-lg font-semibold text-slate-900 mb-1">Break-even ROAS Calculator</h3>
      <p className="text-sm text-slate-500 mb-5">Calculate your return on ad spend and check if your campaigns are profitable.</p>
      <div className="grid sm:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Revenue from ads (&pound;)</label>
          <input type="number" value={revenue} onChange={e => setRevenue(e.target.value)} placeholder="500" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="roas-revenue-input" />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Ad spend (&pound;)</label>
          <input type="number" value={adSpend} onChange={e => setAdSpend(e.target.value)} placeholder="150" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="roas-spend-input" />
        </div>
      </div>
      {adNum > 0 && (
        <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100">
          <div className="text-center">
            <p className="text-xs text-slate-500">Your ROAS</p>
            <p className={`font-mono text-xl font-bold ${roas >= 2 ? 'text-emerald-600' : roas >= 1 ? 'text-amber-600' : 'text-red-600'}`}>{roas.toFixed(2)}x</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Status</p>
            <p className={`text-sm font-semibold ${roas >= 2 ? 'text-emerald-600' : roas >= 1 ? 'text-amber-600' : 'text-red-600'}`}>
              {roas >= 2 ? 'Profitable' : roas >= 1 ? 'Break-even' : 'Losing money'}
            </p>
          </div>
        </div>
      )}
      {adNum > 0 && (
        <ShareResult
          tool="ROAS"
          resultText={`My ROAS is ${roas.toFixed(2)}x`}
          detail={roas >= 2 ? 'Profitable!' : roas >= 1 ? 'Break-even' : 'Needs optimisation'}
        />
      )}
    </div>
  );
}

function VatCalculator() {
  const [amount, setAmount] = useState('');
  const [direction, setDirection] = useState('add');

  const num = parseFloat(amount) || 0;
  const vatAmount = direction === 'add' ? num * 0.2 : num - (num / 1.2);
  const total = direction === 'add' ? num * 1.2 : num;
  const exVat = direction === 'add' ? num : num / 1.2;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="vat-calculator">
      <h3 className="font-manrope text-lg font-semibold text-slate-900 mb-1">UK VAT Calculator</h3>
      <p className="text-sm text-slate-500 mb-5">Add or remove 20% UK VAT from any amount.</p>
      <div className="grid sm:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Amount (&pound;)</label>
          <input type="number" value={amount} onChange={e => setAmount(e.target.value)} placeholder="100" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="vat-amount-input" />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Direction</label>
          <select value={direction} onChange={e => setDirection(e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="vat-direction-select">
            <option value="add">Add VAT (ex-VAT price)</option>
            <option value="remove">Remove VAT (inc-VAT price)</option>
          </select>
        </div>
      </div>
      {num > 0 && (
        <div className="grid grid-cols-3 gap-3 pt-4 border-t border-slate-100">
          <div className="text-center">
            <p className="text-xs text-slate-500">Ex-VAT</p>
            <p className="font-mono text-base font-bold text-slate-900">&pound;{exVat.toFixed(2)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">VAT (20%)</p>
            <p className="font-mono text-base font-bold text-amber-600">&pound;{vatAmount.toFixed(2)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Inc-VAT</p>
            <p className="font-mono text-base font-bold text-emerald-600">&pound;{total.toFixed(2)}</p>
          </div>
        </div>
      )}
      {num > 0 && (
        <ShareResult
          tool="UK VAT"
          resultText={`£${exVat.toFixed(2)} + £${vatAmount.toFixed(2)} VAT = £${total.toFixed(2)}`}
          detail="Calculated with UK 20% VAT"
        />
      )}
    </div>
  );
}

function PricingCalculator() {
  const [cost, setCost] = useState('');
  const [targetMargin, setTargetMargin] = useState('');
  const [platformFee, setPlatformFee] = useState('5');

  const costNum = parseFloat(cost) || 0;
  const marginNum = parseFloat(targetMargin) || 0;
  const feeNum = parseFloat(platformFee) || 0;

  const sellingPrice = marginNum > 0 && marginNum < 100
    ? costNum / (1 - (marginNum / 100) - (feeNum / 100))
    : 0;
  const profit = sellingPrice - costNum - (sellingPrice * feeNum / 100);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="pricing-calculator">
      <h3 className="font-manrope text-lg font-semibold text-slate-900 mb-1">Product Pricing Calculator</h3>
      <p className="text-sm text-slate-500 mb-5">Work out the right selling price to hit your target margin.</p>
      <div className="grid sm:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Total product cost (&pound;)</label>
          <input type="number" value={cost} onChange={e => setCost(e.target.value)} placeholder="12" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="price-cost-input" />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Target margin (%)</label>
          <input type="number" value={targetMargin} onChange={e => setTargetMargin(e.target.value)} placeholder="40" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="price-margin-input" />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">Platform fee (%)</label>
          <input type="number" value={platformFee} onChange={e => setPlatformFee(e.target.value)} placeholder="5" className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none" data-testid="price-fee-input" />
        </div>
      </div>
      {sellingPrice > 0 && (
        <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100">
          <div className="text-center">
            <p className="text-xs text-slate-500">Recommended price</p>
            <p className="font-mono text-xl font-bold text-indigo-600">&pound;{sellingPrice.toFixed(2)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-500">Profit per unit</p>
            <p className="font-mono text-xl font-bold text-emerald-600">&pound;{profit.toFixed(2)}</p>
          </div>
        </div>
      )}
      {sellingPrice > 0 && (
        <ShareResult
          tool="Product Pricing"
          resultText={`Recommended selling price: £${sellingPrice.toFixed(2)}`}
          detail={`£${profit.toFixed(2)} profit per unit at ${targetMargin}% margin`}
        />
      )}
    </div>
  );
}

const TOOLS = [
  { id: 'profit', name: 'Profit Margin', icon: PoundSterling, component: ProfitMarginCalculator },
  { id: 'roas', name: 'Break-even ROAS', icon: BarChart3, component: RoasCalculator },
  { id: 'vat', name: 'UK VAT', icon: Receipt, component: VatCalculator },
  { id: 'pricing', name: 'Product Pricing', icon: Calculator, component: PricingCalculator },
  { id: 'tiktok-ads', name: 'TikTok Ad Budget', icon: Video, component: TikTokAdBudgetCalculator },
  { id: 'validation', name: 'Validation Checklist', icon: ClipboardCheck, component: ProductValidationChecklist },
];

export default function FreeToolsPage() {
  const [activeTool, setActiveTool] = useState('profit');
  const ActiveComponent = TOOLS.find(t => t.id === activeTool)?.component;

  return (
    <LandingLayout>
      <PageMeta
        title="Free Ecommerce Calculators"
        description="Free UK ecommerce calculators: profit margin, break-even ROAS, UK VAT, and product pricing. Quick tools for UK sellers."
        canonical="/free-tools"
        schema={[
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Free Tools' }]),
          faqSchema([
            { q: 'Are these tools really free?', a: 'Yes. All calculators are completely free to use with no signup required.' },
            { q: 'Do the calculators account for UK VAT?', a: 'Yes. The profit margin calculator includes 20% UK VAT in its calculations.' },
          ]),
        ]}
      />
      <div className="bg-white" data-testid="free-tools-page">
        <section className="pt-16 pb-8 px-6">
          <div className="max-w-4xl mx-auto">
            <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Free ecommerce calculators
            </h1>
            <p className="mt-4 text-lg text-slate-600 leading-relaxed max-w-2xl">
              Quick calculations for UK ecommerce sellers. Estimate margins, check ROAS, calculate VAT, and work out the right selling price.
            </p>
          </div>
        </section>

        <section className="pb-20 px-6">
          <div className="max-w-4xl mx-auto">
            {/* Tool selector */}
            <div className="flex flex-wrap gap-2 mb-8">
              {TOOLS.map((tool) => {
                const Icon = tool.icon;
                return (
                  <button
                    key={tool.id}
                    onClick={() => { setActiveTool(tool.id); trackEvent(EVENTS.FREE_TOOL_USED, { tool_name: tool.name }); }}
                    className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      activeTool === tool.id
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                    data-testid={`tool-tab-${tool.id}`}
                  >
                    <Icon className="h-4 w-4" />
                    {tool.name}
                  </button>
                );
              })}
            </div>

            {/* Active tool */}
            {ActiveComponent && <ActiveComponent />}

            {/* Email capture — shown after tool delivers value */}
            <div className="mt-8">
              <EmailCapture source="free_tool" context={activeTool} />
            </div>

            {/* CTA */}
            <div className="mt-8 rounded-lg bg-slate-50 border border-slate-200 p-6 text-center">
              <h3 className="font-manrope text-lg font-semibold text-slate-900">Want deeper product analysis?</h3>
              <p className="mt-2 text-sm text-slate-500">TrendScout gives you margin estimates, saturation data, and UK Viability Scores for trending products — not just calculator inputs.</p>
              <div className="mt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
                <Link to="/signup">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold" data-testid="tools-cta" onClick={() => trackEvent(EVENTS.TOOL_RESULT_CTA, { tool_name: activeTool, cta_label: 'Start Free' })}>
                    Start Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/sample-product-analysis">
                  <Button variant="outline" className="border-slate-300 text-slate-700 rounded-lg font-medium" onClick={() => trackEvent(EVENTS.TOOL_RESULT_CTA, { tool_name: activeTool, cta_label: 'See Sample Analysis' })}>
                    See a Sample Product Analysis
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
