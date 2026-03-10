import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  Lock,
  Rocket,
  Share2,
  Sparkles,
  ArrowLeft,
  PieChart,
  Users,
  BarChart3,
  Eye
} from 'lucide-react';
import { getMarketOpportunityInfo, getEarlyTrendInfo } from '@/lib/utils';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function PublicProductPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await fetch(`${API_URL}/api/viral/public/product/${id}`);
        if (response.ok) {
          const data = await response.json();
          setProduct(data);
        }
      } catch (err) {
        console.error('Error fetching product:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  const handleShare = () => {
    const shareUrl = window.location.href;
    const shareText = product 
      ? `Check out ${product.product_name} on ViralScout - ${getMarketOpportunityInfo(product.market_label).text}!`
      : 'Check out this product on ViralScout!';
    
    if (navigator.share) {
      navigator.share({
        title: `${product?.product_name} - ViralScout`,
        text: shareText,
        url: shareUrl
      });
    } else {
      navigator.clipboard.writeText(shareUrl);
      toast.success('Link copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-900 mb-4">Product Not Found</h1>
          <Link to="/weekly-winners">
            <Button>View Weekly Winners</Button>
          </Link>
        </div>
      </div>
    );
  }

  const marketInfo = getMarketOpportunityInfo(product.market_label);
  const earlyTrendInfo = getEarlyTrendInfo(product.early_trend_label);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="font-manrope font-bold text-xl text-slate-900">ViralScout</span>
          </Link>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={handleShare} data-testid="public-share-btn">
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
            <Link to="/signup">
              <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="public-signup-cta">
                <Rocket className="mr-2 h-4 w-4" />
                Sign Up Free
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Back Link */}
      <div className="max-w-4xl mx-auto px-6 pt-6">
        <Link 
          to="/weekly-winners" 
          className="inline-flex items-center text-sm text-slate-500 hover:text-slate-700"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Weekly Winners
        </Link>
      </div>

      {/* Product Hero */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <Card className="border-0 shadow-lg overflow-hidden">
          {/* Header with image */}
          <div className="bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 p-8">
            <div className="flex gap-6">
              {product.image_url && (
                <img 
                  src={product.image_url} 
                  alt={product.product_name}
                  className="w-32 h-32 rounded-xl object-cover shadow-md"
                />
              )}
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Badge className={`${marketInfo.color} border px-3 py-1`}>
                    {marketInfo.text}
                  </Badge>
                  {product.early_trend_label && product.early_trend_label !== 'stable' && (
                    <Badge className={`${earlyTrendInfo.color} border`}>
                      {earlyTrendInfo.text}
                    </Badge>
                  )}
                </div>
                <h1 className="font-manrope text-3xl font-bold text-slate-900 mb-2">
                  {product.product_name}
                </h1>
                <p className="text-slate-600">{product.category}</p>
              </div>
            </div>
          </div>

          <CardContent className="p-8">
            {/* Public Scores */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-slate-50 rounded-xl p-4 text-center">
                <PieChart className="h-6 w-6 mx-auto mb-2 text-indigo-600" />
                <p className="font-mono text-2xl font-bold text-indigo-600">{product.market_score}</p>
                <p className="text-xs text-slate-500">Market Score</p>
              </div>
              <div className="bg-slate-50 rounded-xl p-4 text-center">
                <TrendingUp className="h-6 w-6 mx-auto mb-2 text-emerald-600" />
                <p className="font-mono text-2xl font-bold text-emerald-600">{product.trend_score}</p>
                <p className="text-xs text-slate-500">Trend Score</p>
              </div>
              <div className="bg-slate-50 rounded-xl p-4 text-center">
                <BarChart3 className="h-6 w-6 mx-auto mb-2 text-slate-600" />
                <p className="font-mono text-lg font-bold text-slate-700 capitalize">{product.trend_stage}</p>
                <p className="text-xs text-slate-500">Trend Stage</p>
              </div>
              <div className="bg-slate-50 rounded-xl p-4 text-center">
                <Users className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                <p className="font-mono text-lg font-bold text-purple-600 capitalize">{product.competition_level}</p>
                <p className="text-xs text-slate-500">Competition</p>
              </div>
            </div>

            {/* Locked Insights */}
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                <Lock className="h-4 w-4 text-slate-400" />
                Full Insights (Sign up to unlock)
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Margin - Partial */}
                <div className="bg-slate-100 rounded-xl p-4 relative overflow-hidden">
                  <div className="absolute inset-0 backdrop-blur-sm bg-white/50 flex items-center justify-center">
                    <div className="text-center">
                      <p className="font-semibold text-slate-700">{product.margin_range}</p>
                      <p className="text-xs text-slate-500">Est. Margin Range</p>
                    </div>
                  </div>
                  <p className="text-slate-400">Exact margin: £XX.XX</p>
                </div>

                {/* Supplier - Locked */}
                <div className="bg-slate-100 rounded-xl p-4 relative overflow-hidden">
                  <div className="absolute inset-0 backdrop-blur-md bg-slate-200/80 flex items-center justify-center">
                    <div className="text-center">
                      <Lock className="h-5 w-5 mx-auto mb-1 text-slate-400" />
                      <p className="text-xs text-slate-500">Supplier data locked</p>
                    </div>
                  </div>
                  <p className="text-slate-400">Supplier cost, link, ratings...</p>
                </div>

                {/* Competitor - Locked */}
                <div className="bg-slate-100 rounded-xl p-4 relative overflow-hidden">
                  <div className="absolute inset-0 backdrop-blur-md bg-slate-200/80 flex items-center justify-center">
                    <div className="text-center">
                      <Lock className="h-5 w-5 mx-auto mb-1 text-slate-400" />
                      <p className="text-xs text-slate-500">Competitor data locked</p>
                    </div>
                  </div>
                  <p className="text-slate-400">Store count, prices, saturation...</p>
                </div>

                {/* Ad Activity - Locked */}
                <div className="bg-slate-100 rounded-xl p-4 relative overflow-hidden">
                  <div className="absolute inset-0 backdrop-blur-md bg-slate-200/80 flex items-center justify-center">
                    <div className="text-center">
                      <Lock className="h-5 w-5 mx-auto mb-1 text-slate-400" />
                      <p className="text-xs text-slate-500">Ad activity locked</p>
                    </div>
                  </div>
                  <p className="text-slate-400">Ad count, spend, platforms...</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* CTA */}
        <div className="mt-8 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-center text-white">
          <h2 className="font-manrope text-2xl font-bold mb-2">
            Unlock Full Product Insights
          </h2>
          <p className="text-indigo-100 mb-6 max-w-lg mx-auto">
            {product.signup_cta || 'Sign up to unlock full insights and build your store'}
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/signup">
              <Button size="lg" className="bg-white text-indigo-600 hover:bg-indigo-50 font-semibold w-full sm:w-auto" data-testid="public-product-signup-cta">
                <Rocket className="mr-2 h-5 w-5" />
                Sign Up Free
              </Button>
            </Link>
            <Link to="/weekly-winners">
              <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10 w-full sm:w-auto">
                <Eye className="mr-2 h-5 w-5" />
                View More Products
              </Button>
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white mt-12">
        <div className="max-w-4xl mx-auto px-6 py-8 text-center text-sm text-slate-500">
          <p className="mb-2">
            <strong className="text-slate-700">ViralScout</strong> - Find winning products before they go viral
          </p>
          <p>
            Powered by AI-driven trend detection • Updated daily
          </p>
        </div>
      </footer>
    </div>
  );
}
