import React, { useState, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Calculator, TrendingUp, DollarSign, Package, Megaphone, Truck, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function ProductProfitCalculator({ product }) {
  const defaultCost = product?.supplier_cost || 0;
  const defaultPrice = product?.estimated_retail_price || 0;

  const [cost, setCost] = useState(defaultCost.toString());
  const [price, setPrice] = useState(defaultPrice.toString());
  const [shipping, setShipping] = useState('2.50');
  const [adCost, setAdCost] = useState('5.00');
  const [dailyOrders, setDailyOrders] = useState('5');

  const costNum = parseFloat(cost) || 0;
  const priceNum = parseFloat(price) || 0;
  const shipNum = parseFloat(shipping) || 0;
  const adNum = parseFloat(adCost) || 0;
  const ordersNum = parseInt(dailyOrders) || 0;

  const profitPerUnit = priceNum - costNum - shipNum - adNum;
  const margin = priceNum > 0 ? (profitPerUnit / priceNum) * 100 : 0;
  const roi = costNum > 0 ? (profitPerUnit / (costNum + shipNum + adNum)) * 100 : 0;
  const dailyProfit = profitPerUnit * ordersNum;
  const monthlyProfit = dailyProfit * 30;
  const monthlyRevenue = priceNum * ordersNum * 30;
  const monthlyAdSpend = adNum * ordersNum * 30;

  const breakdownData = useMemo(() => [
    { name: 'Product', value: costNum, color: '#6366f1' },
    { name: 'Shipping', value: shipNum, color: '#0ea5e9' },
    { name: 'Ads', value: adNum, color: '#f59e0b' },
    { name: 'Profit', value: Math.max(0, profitPerUnit), color: '#10b981' },
  ], [costNum, shipNum, adNum, profitPerUnit]);

  const getMarginColor = () => {
    if (margin >= 30) return 'text-emerald-600';
    if (margin >= 15) return 'text-amber-600';
    return 'text-red-600';
  };

  const getMarginBg = () => {
    if (margin >= 30) return 'bg-emerald-50 border-emerald-200';
    if (margin >= 15) return 'bg-amber-50 border-amber-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <Card className="border-0 shadow-lg" data-testid="product-profit-calculator">
      <CardContent className="p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
            <Calculator className="h-4 w-4 text-emerald-600" />
            Profit Calculator
          </h3>
          {priceNum > 0 && (
            <Badge className={`border text-xs ${getMarginBg()} ${getMarginColor()}`} data-testid="margin-badge">
              {margin.toFixed(1)}% margin
            </Badge>
          )}
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div>
            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Supplier Cost</Label>
            <div className="relative">
              <Package className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
              <Input type="number" min={0} step={0.01} value={cost} onChange={(e) => setCost(e.target.value)}
                className="pl-8 h-9 text-sm font-mono" data-testid="calc-cost" />
            </div>
          </div>
          <div>
            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Selling Price</Label>
            <div className="relative">
              <DollarSign className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
              <Input type="number" min={0} step={0.01} value={price} onChange={(e) => setPrice(e.target.value)}
                className="pl-8 h-9 text-sm font-mono" data-testid="calc-price" />
            </div>
          </div>
          <div>
            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Shipping</Label>
            <div className="relative">
              <Truck className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
              <Input type="number" min={0} step={0.01} value={shipping} onChange={(e) => setShipping(e.target.value)}
                className="pl-8 h-9 text-sm font-mono" data-testid="calc-shipping" />
            </div>
          </div>
          <div>
            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Ad Cost/Sale</Label>
            <div className="relative">
              <Megaphone className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
              <Input type="number" min={0} step={0.01} value={adCost} onChange={(e) => setAdCost(e.target.value)}
                className="pl-8 h-9 text-sm font-mono" data-testid="calc-ad" />
            </div>
          </div>
        </div>

        {/* Daily orders slider */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1">
            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Daily Orders</Label>
            <span className="text-sm font-bold font-mono text-indigo-600">{ordersNum}</span>
          </div>
          <input type="range" min={1} max={100} value={dailyOrders}
            onChange={(e) => setDailyOrders(e.target.value)}
            className="w-full h-1.5 bg-slate-200 rounded-full appearance-none cursor-pointer accent-indigo-600"
            data-testid="calc-orders-slider" />
          <div className="flex justify-between text-[9px] text-slate-400 mt-0.5">
            <span>1/day</span><span>50/day</span><span>100/day</span>
          </div>
        </div>

        {priceNum > 0 && (
          <>
            {/* Cost breakdown chart */}
            <div className="mb-3" data-testid="calc-breakdown-chart">
              <ResponsiveContainer width="100%" height={40}>
                <BarChart data={[{ ...Object.fromEntries(breakdownData.map(d => [d.name, d.value])) }]} layout="horizontal" barSize={20} stackOffset="expand">
                  <XAxis type="category" hide />
                  <YAxis type="number" hide />
                  {breakdownData.map(d => (
                    <Bar key={d.name} dataKey={d.name} stackId="a" fill={d.color} radius={d.name === 'Product' ? [4,0,0,4] : d.name === 'Profit' ? [0,4,4,0] : 0} />
                  ))}
                </BarChart>
              </ResponsiveContainer>
              <div className="flex items-center gap-3 justify-center mt-1">
                {breakdownData.map(d => (
                  <span key={d.name} className="flex items-center gap-1 text-[9px] text-slate-500">
                    <span className="w-2 h-2 rounded-sm" style={{ backgroundColor: d.color }} />
                    {d.name} ({d.value > 0 ? `£${d.value.toFixed(2)}` : '£0'})
                  </span>
                ))}
              </div>
            </div>

            {/* Results */}
            <div className="bg-slate-50 rounded-xl p-4 space-y-2.5" data-testid="calc-results">
              <ResultRow label="Profit per unit" value={`£${profitPerUnit.toFixed(2)}`} positive={profitPerUnit > 0} bold />
              <ResultRow label="Profit margin" value={`${margin.toFixed(1)}%`} positive={margin >= 15} />
              <ResultRow label="ROI per sale" value={`${roi.toFixed(0)}%`} positive={roi > 0} />
              <div className="border-t border-slate-200 pt-2.5 mt-2.5" />
              <ResultRow label="Daily profit" value={`£${dailyProfit.toFixed(2)}`} positive={dailyProfit > 0} />
              <ResultRow label="Monthly revenue" value={`£${monthlyRevenue.toFixed(0)}`} positive={true} />
              <ResultRow label="Monthly ad spend" value={`£${monthlyAdSpend.toFixed(0)}`} positive={false} neutral />
              <ResultRow label="Monthly profit" value={`£${monthlyProfit.toFixed(0)}`} positive={monthlyProfit > 0} bold />
            </div>

            {/* Insight */}
            <div className={`mt-3 p-2.5 rounded-lg text-xs border ${
              margin >= 30 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
              margin >= 15 ? 'bg-amber-50 text-amber-700 border-amber-200' :
              'bg-red-50 text-red-700 border-red-200'
            }`}>
              {margin >= 30 ? 'Excellent margins! Strong profit potential at current pricing.' :
               margin >= 15 ? 'Decent margins. Consider testing lower ad costs or optimizing conversion rates.' :
               margin > 0 ? 'Thin margins. Focus on reducing costs or finding a unique selling angle.' :
               'Unprofitable at current pricing. Increase selling price or find cheaper suppliers.'}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

function ResultRow({ label, value, positive, bold, neutral }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-slate-600">{label}</span>
      <span className={`font-mono text-sm ${bold ? 'font-bold' : 'font-medium'} ${
        neutral ? 'text-slate-600' : positive ? 'text-emerald-600' : 'text-red-600'
      }`}>{value}</span>
    </div>
  );
}
