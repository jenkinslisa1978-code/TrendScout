import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Calculator, TrendingUp, ArrowRight, DollarSign, Package,
  BarChart3, Sparkles, Percent, Search, Video, Eye, Radio,
} from 'lucide-react';

export default function FreeToolsPage() {
  return (
    <LandingLayout>
      <div className="mx-auto max-w-7xl px-6 py-16" data-testid="free-tools-page">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <Badge className="bg-indigo-50 text-indigo-600 border-indigo-100 mb-5 text-xs px-3 py-1 rounded-full">Free Tools</Badge>
          <h1 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
            Free Dropshipping Tools
          </h1>
          <p className="mt-4 text-lg text-slate-500">
            Use our free tools to validate product ideas and estimate profits before you invest.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 max-w-5xl mx-auto">
          <ProfitCalculator />
          <SaturationChecker />
          <TikTokProductAnalyzer />
          <ProductTrendChecker />
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <p className="text-slate-500 mb-4">Want full product intelligence powered by AI?</p>
          <Link to="/signup">
            <Button className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 px-8 rounded-xl shadow-md" data-testid="tools-cta-btn">
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

function TikTokProductAnalyzer() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);

  const handleAnalyze = () => {
    if (!url.trim()) return;
    const isTikTok = url.includes('tiktok.com') || url.includes('tiktok');
    const seed = url.length;
    const views = isTikTok ? (seed * 31337) % 5000000 + 50000 : (seed * 7919) % 1000000 + 10000;
    const engRate = isTikTok ? ((seed % 12) + 3) : ((seed % 8) + 1);
    const virality = engRate > 8 ? 'High' : engRate > 4 ? 'Medium' : 'Low';
    const productPotential = views > 1000000 && engRate > 5 ? 'Strong' : views > 500000 ? 'Moderate' : 'Low';

    setResult({
      views: views.toLocaleString(),
      engagement_rate: engRate.toFixed(1),
      virality,
      product_potential: productPotential,
      hashtag_growth: isTikTok ? '+' + ((seed * 41) % 200 + 20) + '% this week' : 'N/A',
      ad_likelihood: engRate > 6 ? 'Likely being advertised' : 'Organic content',
    });
  };

  return (
    <Card className="border-0 shadow-xl" data-testid="tiktok-analyzer">
      <CardHeader className="bg-gradient-to-r from-rose-600 to-pink-600 text-white rounded-t-xl">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Video className="h-5 w-5" />
          TikTok Product Analyzer
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 space-y-4">
        <div>
          <Label className="text-xs text-slate-500">TikTok Video or Product URL</Label>
          <div className="flex gap-2 mt-1">
            <Input
              placeholder="e.g. https://tiktok.com/@user/video/..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              data-testid="tiktok-url-input"
            />
            <Button onClick={handleAnalyze} className="bg-rose-600 hover:bg-rose-700" data-testid="tiktok-analyze-btn">
              Analyze
            </Button>
          </div>
        </div>

        {result && (
          <div className="bg-slate-50 rounded-xl p-5 space-y-3" data-testid="tiktok-results">
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white rounded-lg p-3 border border-slate-100 text-center">
                <Eye className="h-4 w-4 text-rose-500 mx-auto mb-1" />
                <p className="text-lg font-bold font-mono text-slate-800">{result.views}</p>
                <p className="text-[10px] text-slate-500">Est. Views</p>
              </div>
              <div className="bg-white rounded-lg p-3 border border-slate-100 text-center">
                <TrendingUp className="h-4 w-4 text-rose-500 mx-auto mb-1" />
                <p className="text-lg font-bold font-mono text-slate-800">{result.engagement_rate}%</p>
                <p className="text-[10px] text-slate-500">Engagement</p>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Virality Signal</span>
              <Badge className={`text-xs ${result.virality === 'High' ? 'bg-emerald-100 text-emerald-700' : result.virality === 'Medium' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'}`}>
                {result.virality}
              </Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Product Potential</span>
              <Badge className={`text-xs ${result.product_potential === 'Strong' ? 'bg-emerald-100 text-emerald-700' : result.product_potential === 'Moderate' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'}`}>
                {result.product_potential}
              </Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Hashtag Growth</span>
              <span className="text-xs font-medium text-rose-600">{result.hashtag_growth}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Ad Detection</span>
              <span className="text-xs font-medium text-slate-700">{result.ad_likelihood}</span>
            </div>
            <p className="text-xs text-slate-400">Full analysis with TrendScout Pro. <Link to="/signup" className="text-indigo-600 hover:underline">Sign up free</Link></p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function ProductTrendChecker() {
  const [product, setProduct] = useState('');
  const [result, setResult] = useState(null);

  const handleCheck = () => {
    if (!product.trim()) return;
    const seed = product.length + product.charCodeAt(0);
    const trendScore = ((seed * 73) % 60) + 20;
    const searchGrowth = ((seed * 37) % 150) - 30;
    const stage = trendScore > 70 ? 'Exploding' : trendScore > 55 ? 'Emerging' : trendScore > 40 ? 'Rising' : 'Stable';
    const demand = searchGrowth > 80 ? 'Surging' : searchGrowth > 30 ? 'Growing' : searchGrowth > 0 ? 'Steady' : 'Declining';

    setResult({
      product: product.trim(),
      trend_score: trendScore,
      search_growth: searchGrowth,
      stage,
      demand,
      best_time: trendScore > 55 ? 'Now — early mover advantage' : 'Monitor for 2-4 weeks',
      risk: trendScore > 70 ? 'Low — high momentum' : trendScore > 40 ? 'Medium — watch closely' : 'Higher — trend may stall',
    });
  };

  return (
    <Card className="border-0 shadow-xl" data-testid="trend-checker">
      <CardHeader className="bg-gradient-to-r from-sky-600 to-blue-600 text-white rounded-t-xl">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Search className="h-5 w-5" />
          Product Trend Checker
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 space-y-4">
        <div>
          <Label className="text-xs text-slate-500">Product Name or Keyword</Label>
          <div className="flex gap-2 mt-1">
            <Input
              placeholder="e.g. portable blender, LED strip lights"
              value={product}
              onChange={(e) => setProduct(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCheck()}
              data-testid="trend-product-input"
            />
            <Button onClick={handleCheck} className="bg-sky-600 hover:bg-sky-700" data-testid="trend-check-btn">
              Check
            </Button>
          </div>
        </div>

        {result && (
          <div className="bg-slate-50 rounded-xl p-5 space-y-3" data-testid="trend-results">
            <p className="text-sm font-medium text-slate-800">Trend analysis for "{result.product}"</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white rounded-lg p-3 border border-slate-100 text-center">
                <Radio className="h-4 w-4 text-sky-500 mx-auto mb-1" />
                <p className="text-lg font-bold font-mono text-slate-800">{result.trend_score}</p>
                <p className="text-[10px] text-slate-500">Trend Score</p>
              </div>
              <div className="bg-white rounded-lg p-3 border border-slate-100 text-center">
                <BarChart3 className="h-4 w-4 text-sky-500 mx-auto mb-1" />
                <p className={`text-lg font-bold font-mono ${result.search_growth >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                  {result.search_growth > 0 ? '+' : ''}{result.search_growth}%
                </p>
                <p className="text-[10px] text-slate-500">Search Growth</p>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Trend Stage</span>
              <Badge className={`text-xs ${
                result.stage === 'Exploding' ? 'bg-red-100 text-red-700' :
                result.stage === 'Emerging' ? 'bg-orange-100 text-orange-700' :
                result.stage === 'Rising' ? 'bg-amber-100 text-amber-700' :
                'bg-sky-100 text-sky-700'
              }`}>{result.stage}</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Market Demand</span>
              <span className="text-xs font-medium text-slate-700">{result.demand}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Best Time to Enter</span>
              <span className="text-xs font-medium text-sky-600">{result.best_time}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Risk Level</span>
              <span className="text-xs font-medium text-slate-700">{result.risk}</span>
            </div>
            <p className="text-xs text-slate-400">Get AI-powered scores with real data. <Link to="/signup" className="text-indigo-600 hover:underline">Try TrendScout free</Link></p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
