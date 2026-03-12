import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calculator, TrendingUp, ArrowRight, DollarSign, Package, BarChart3, Sparkles, Percent, Truck } from 'lucide-react';

export default function FreeToolsPage() {
  return (
    <LandingLayout>
      <div className="mx-auto max-w-7xl px-6 py-16" data-testid="free-tools-page">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <Badge className="bg-indigo-50 text-indigo-700 border-indigo-100 mb-4">Free Tools</Badge>
          <h1 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
            Free Dropshipping Tools
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            Use our free tools to validate product ideas and estimate profits before you invest.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <ProfitCalculator />
          <SaturationChecker />
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <p className="text-slate-600 mb-4">Want full product intelligence powered by AI?</p>
          <Link to="/signup">
            <Button className="bg-indigo-600 hover:bg-indigo-700 px-8" data-testid="tools-cta-btn">
              <Sparkles className="mr-2 h-4 w-4" />
              Start Free with TrendScout
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>
    </LandingLayout>
  );
}

function ProfitCalculator() {
  const [cost, setCost] = useState('');
  const [price, setPrice] = useState('');
  const [shipping, setShipping] = useState('');
  const [adCost, setAdCost] = useState('');

  const costNum = parseFloat(cost) || 0;
  const priceNum = parseFloat(price) || 0;
  const shipNum = parseFloat(shipping) || 0;
  const adNum = parseFloat(adCost) || 0;

  const profit = priceNum - costNum - shipNum - adNum;
  const margin = priceNum > 0 ? ((profit / priceNum) * 100) : 0;
  const roiPerUnit = costNum > 0 ? ((profit / costNum) * 100) : 0;

  return (
    <Card className="border-0 shadow-xl" data-testid="profit-calculator">
      <CardHeader className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-t-xl">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Calculator className="h-5 w-5" />
          Dropshipping Profit Calculator
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-xs text-slate-500">Supplier Cost (£)</Label>
            <Input type="number" placeholder="5.00" value={cost} onChange={(e) => setCost(e.target.value)} data-testid="calc-cost" />
          </div>
          <div>
            <Label className="text-xs text-slate-500">Selling Price (£)</Label>
            <Input type="number" placeholder="24.99" value={price} onChange={(e) => setPrice(e.target.value)} data-testid="calc-price" />
          </div>
          <div>
            <Label className="text-xs text-slate-500">Shipping Cost (£)</Label>
            <Input type="number" placeholder="2.00" value={shipping} onChange={(e) => setShipping(e.target.value)} data-testid="calc-shipping" />
          </div>
          <div>
            <Label className="text-xs text-slate-500">Ad Cost per Sale (£)</Label>
            <Input type="number" placeholder="5.00" value={adCost} onChange={(e) => setAdCost(e.target.value)} data-testid="calc-ad" />
          </div>
        </div>

        {priceNum > 0 && (
          <div className="bg-slate-50 rounded-xl p-5 space-y-3 mt-4" data-testid="calc-results">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600 flex items-center gap-1"><DollarSign className="h-4 w-4 text-slate-400" /> Profit per Unit</span>
              <span className={`font-bold text-lg font-mono ${profit >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                £{profit.toFixed(2)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600 flex items-center gap-1"><Percent className="h-4 w-4 text-slate-400" /> Profit Margin</span>
              <span className={`font-bold font-mono ${margin >= 30 ? 'text-emerald-600' : margin >= 15 ? 'text-amber-600' : 'text-red-600'}`}>
                {margin.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600 flex items-center gap-1"><BarChart3 className="h-4 w-4 text-slate-400" /> ROI per Unit</span>
              <span className="font-bold font-mono text-indigo-600">{roiPerUnit.toFixed(0)}%</span>
            </div>
            <div className={`text-xs p-2 rounded-lg mt-2 ${margin >= 30 ? 'bg-emerald-50 text-emerald-700' : margin >= 15 ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-700'}`}>
              {margin >= 30 ? 'Great margins! This product has strong profit potential.' :
               margin >= 15 ? 'Decent margins. Consider reducing ad costs to improve profitability.' :
               'Low margins. Look for cheaper suppliers or increase your selling price.'}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function SaturationChecker() {
  const [keyword, setKeyword] = useState('');
  const [result, setResult] = useState(null);

  const handleCheck = () => {
    if (!keyword.trim()) return;
    // Simulate saturation analysis based on keyword characteristics
    const len = keyword.trim().length;
    const words = keyword.trim().split(' ').length;
    const isNiche = words >= 3;
    const saturation = isNiche ? Math.floor(Math.random() * 30 + 10) : Math.floor(Math.random() * 40 + 40);
    const competition = saturation > 60 ? 'High' : saturation > 35 ? 'Moderate' : 'Low';
    const recommendation = saturation > 60
      ? 'This market is highly competitive. Consider finding a more specific niche.'
      : saturation > 35
      ? 'Moderate competition. Differentiation through branding and ads is key.'
      : 'Low saturation — great opportunity for early movers!';

    setResult({ keyword: keyword.trim(), saturation, competition, recommendation });
  };

  return (
    <Card className="border-0 shadow-xl" data-testid="saturation-checker">
      <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-t-xl">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="h-5 w-5" />
          Product Saturation Checker
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 space-y-4">
        <div>
          <Label className="text-xs text-slate-500">Product Keyword</Label>
          <div className="flex gap-2 mt-1">
            <Input
              placeholder="e.g. sunset lamp, pet grooming"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCheck()}
              data-testid="saturation-input"
            />
            <Button onClick={handleCheck} className="bg-indigo-600 hover:bg-indigo-700" data-testid="saturation-check-btn">
              Check
            </Button>
          </div>
        </div>

        {result && (
          <div className="bg-slate-50 rounded-xl p-5 space-y-3" data-testid="saturation-results">
            <p className="text-sm font-medium text-slate-800">Results for "{result.keyword}"</p>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Estimated Saturation</span>
              <span className={`font-bold font-mono ${result.saturation > 60 ? 'text-red-600' : result.saturation > 35 ? 'text-amber-600' : 'text-emerald-600'}`}>
                {result.saturation}%
              </span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${result.saturation > 60 ? 'bg-red-500' : result.saturation > 35 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                style={{ width: `${result.saturation}%` }}
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Competition Level</span>
              <Badge className={`text-xs ${result.competition === 'High' ? 'bg-red-100 text-red-700' : result.competition === 'Moderate' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                {result.competition}
              </Badge>
            </div>
            <p className="text-xs text-slate-600 bg-white rounded-lg p-3 border">{result.recommendation}</p>
            <p className="text-xs text-slate-400">Want detailed insights? <Link to="/signup" className="text-indigo-600 hover:underline">Sign up for free</Link></p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
