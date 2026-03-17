import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Sparkles,
  Rocket,
  TrendingUp,
  Package,
  Truck,
  DollarSign,
  ChevronRight,
  Loader2,
  Star,
  Zap,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import { apiGet } from '@/lib/api';
import { toast } from 'sonner';

const TREND_COLORS = {
  Exploding: 'bg-red-100 text-red-700 border-red-200',
  Emerging: 'bg-orange-100 text-orange-700 border-orange-200',
  Rising: 'bg-amber-100 text-amber-700 border-amber-200',
  Stable: 'bg-blue-100 text-blue-700 border-blue-200',
  Declining: 'bg-slate-100 text-slate-500 border-slate-200',
};

export default function FindWinningProductHero({ onLaunchProduct }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFindProduct = async () => {
    setLoading(true);
    try {
      const res = await apiGet('/api/products/find-winning');
      if (res.ok) {
        const data = await res.json();
        if (data.product) {
          setResult(data);
        } else {
          toast.error('No products available yet — data pipeline is still running');
        }
      } else {
        toast.error('Failed to find product');
      }
    } catch (err) {
      console.error(err);
      toast.error('Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleLaunchThis = () => {
    if (result?.product) {
      if (onLaunchProduct) {
        onLaunchProduct(result.product, result.supplier);
      } else {
        navigate(`/launch/${result.product.id}`);
      }
    }
  };

  // Initial state — big CTA button
  if (!result) {
    return (
      <Card className="border-0 shadow-xl overflow-hidden bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800" data-testid="find-winning-hero">
        <CardContent className="p-8 md:p-12 text-center">
          <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur-sm rounded-full px-4 py-1.5 mb-6">
            <Sparkles className="h-4 w-4 text-amber-300" />
            <span className="text-sm font-medium text-white/90">AI Product Co-Pilot</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-3 font-manrope">
            Ready to launch your next winner?
          </h2>
          <p className="text-indigo-200 mb-8 max-w-lg mx-auto">
            Our AI analyses thousands of products across TikTok, Amazon, and Google Trends to find the best product for you right now.
          </p>
          <Button
            size="lg"
            onClick={handleFindProduct}
            disabled={loading}
            className="bg-white text-indigo-700 hover:bg-indigo-50 font-bold text-lg px-8 py-6 rounded-xl shadow-lg hover:shadow-xl transition-all"
            data-testid="find-winning-product-btn"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Analyzing market data...
              </>
            ) : (
              <>
                <Zap className="mr-2 h-5 w-5" />
                Find Me a Winning Product
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Result state — show the winning product
  const { product, supplier, recommendation, alternatives } = result;

  return (
    <Card className="border-0 shadow-xl overflow-hidden" data-testid="find-winning-result">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-white">
          <Sparkles className="h-5 w-5 text-amber-300" />
          <span className="font-semibold">AI Recommendation</span>
          <Badge className="bg-white/20 text-white border-white/30 ml-2">
            {recommendation?.confidence === 'high' ? 'High Confidence' : 'Moderate Confidence'}
          </Badge>
        </div>
        <Button
          size="sm"
          variant="ghost"
          className="text-white/80 hover:text-white hover:bg-white/10"
          onClick={handleFindProduct}
          disabled={loading}
          data-testid="refresh-recommendation-btn"
        >
          <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
          New Pick
        </Button>
      </div>

      <CardContent className="p-0">
        <div className="grid md:grid-cols-3 gap-0 divide-y md:divide-y-0 md:divide-x divide-slate-100">
          {/* Product Info */}
          <div className="p-6 md:col-span-2">
            <div className="flex items-start gap-4">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.product_name}
                  className="w-20 h-20 rounded-xl object-cover bg-slate-100 flex-shrink-0"
                />
              ) : (
                <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center flex-shrink-0">
                  <Package className="h-8 w-8 text-indigo-400" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h3
                  className="font-bold text-lg text-slate-900 leading-tight cursor-pointer hover:text-indigo-600 transition-colors"
                  onClick={() => navigate(`/product/${product.id}`)}
                  data-testid="winning-product-name"
                >
                  {product.product_name}
                </h3>
                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                  <Badge variant="outline" className="text-xs">{product.category}</Badge>
                  <Badge className={`text-xs border ${TREND_COLORS[product.trend_stage] || TREND_COLORS.Stable}`}>
                    {product.trend_stage}
                  </Badge>
                  {product.amazon_rating && (
                    <span className="text-xs text-slate-500 flex items-center gap-0.5">
                      <Star className="h-3 w-3 text-amber-400 fill-amber-400" />
                      {product.amazon_rating}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Key Metrics Row */}
            <div className="grid grid-cols-3 gap-4 mt-5">
              <div className="bg-indigo-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-indigo-700 font-mono">{product.launch_score}</p>
                <p className="text-xs text-indigo-500 mt-0.5">Launch Score</p>
              </div>
              <div className="bg-emerald-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-emerald-700 font-mono">{product.success_probability}%</p>
                <p className="text-xs text-emerald-500 mt-0.5">Success Probability</p>
              </div>
              <div className="bg-amber-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-amber-700 font-mono">£{product.estimated_profit}</p>
                <p className="text-xs text-amber-500 mt-0.5">Est. Profit</p>
              </div>
            </div>

            {/* Reasons */}
            {recommendation?.reasons?.length > 0 && (
              <div className="mt-4 space-y-1">
                {recommendation.reasons.slice(0, 3).map((reason, i) => (
                  <p key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                    <TrendingUp className="h-3 w-3 text-indigo-400 mt-0.5 flex-shrink-0" />
                    {reason}
                  </p>
                ))}
              </div>
            )}
          </div>

          {/* Supplier + Actions */}
          <div className="p-6 bg-slate-50/50 flex flex-col">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Supplier Match</h4>
            <div className="space-y-2.5 flex-1">
              <div className="flex items-center gap-2">
                <Package className="h-4 w-4 text-slate-400" />
                <span className="text-sm text-slate-700">{supplier?.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-slate-400" />
                <span className="text-sm text-slate-700">Cost: £{supplier?.cost?.toFixed(2) || '—'}</span>
              </div>
              <div className="flex items-center gap-2">
                <Truck className="h-4 w-4 text-slate-400" />
                <span className="text-sm text-slate-700">{supplier?.delivery_estimate}</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-slate-400" />
                <span className="text-sm font-medium text-emerald-600">{product.profit_margin_pct}% margin</span>
              </div>
            </div>

            <div className="space-y-2 mt-4">
              <Button
                className="w-full bg-indigo-600 hover:bg-indigo-700 font-semibold"
                onClick={handleLaunchThis}
                data-testid="launch-this-product-btn"
              >
                <Rocket className="mr-2 h-4 w-4" />
                Launch This Product
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => navigate(`/product/${product.id}`)}
                data-testid="view-details-btn"
              >
                View Full Details
              </Button>
            </div>
          </div>
        </div>

        {/* Alternatives */}
        {alternatives?.length > 0 && (
          <div className="border-t border-slate-100 px-6 py-3 bg-slate-50/30 flex items-center gap-3 overflow-x-auto">
            <span className="text-xs text-slate-500 whitespace-nowrap">Also consider:</span>
            {alternatives.map((alt) => (
              <button
                key={alt.id}
                onClick={() => navigate(`/product/${alt.id}`)}
                className="inline-flex items-center gap-1.5 text-xs bg-white border border-slate-200 rounded-full px-3 py-1 hover:border-indigo-300 hover:text-indigo-600 transition-colors whitespace-nowrap"
                data-testid={`alternative-${alt.id}`}
              >
                <span className="font-medium truncate max-w-[140px]">{alt.product_name}</span>
                <Badge variant="outline" className="text-[10px] px-1.5 py-0">{alt.launch_score}</Badge>
              </button>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
