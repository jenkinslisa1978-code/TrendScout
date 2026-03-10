import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  Trophy, 
  Flame,
  Eye,
  Store,
  ArrowRight,
  Rocket,
  Lock,
  Sparkles
} from 'lucide-react';
import { formatNumber, getEarlyTrendInfo } from '@/lib/utils';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function PublicProductInsightPage() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPublicProduct = async () => {
      try {
        const response = await fetch(`${API_URL}/api/products/${productId}/public`);
        if (!response.ok) throw new Error('Product not found');
        const data = await response.json();
        setProduct(data.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPublicProduct();
  }, [productId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Product Not Found</h1>
          <p className="text-slate-500 mb-6">This product insight is no longer available.</p>
          <Link to="/">
            <Button className="bg-indigo-600 hover:bg-indigo-700">
              Discover Winning Products
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const earlyTrendInfo = getEarlyTrendInfo(product.early_trend_label);
  const winScore = product.win_score || Math.round((product.trend_score + (product.early_trend_score || 0)) / 2);

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
          <Link to="/signup">
            <Button className="bg-indigo-600 hover:bg-indigo-700">
              <Rocket className="mr-2 h-4 w-4" />
              Start Building Free
            </Button>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        {/* Product Hero */}
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-1 mb-8">
          <div className="bg-white rounded-xl p-8">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  {product.early_trend_label && product.early_trend_label !== 'stable' && (
                    <Badge className={`${earlyTrendInfo.color} border text-sm`}>
                      {earlyTrendInfo.text}
                    </Badge>
                  )}
                  {product.proven_winner && (
                    <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 border text-sm">
                      ✓ Proven Winner
                    </Badge>
                  )}
                </div>
                <h1 className="font-manrope text-3xl font-bold text-slate-900">{product.product_name}</h1>
                <p className="text-slate-500 mt-1">{product.category}</p>
              </div>
              <div className="flex items-center gap-2 bg-amber-50 rounded-xl px-6 py-4">
                <Trophy className="h-8 w-8 text-amber-500" />
                <div>
                  <p className="font-mono text-3xl font-bold text-amber-600">{winScore}</p>
                  <p className="text-sm text-slate-500">Win Score</p>
                </div>
              </div>
            </div>

            {/* Public Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="text-center p-4 rounded-xl bg-slate-50">
                <TrendingUp className="h-6 w-6 text-emerald-600 mx-auto mb-2" />
                <p className="font-mono text-2xl font-bold text-emerald-600">{product.trend_score}</p>
                <p className="text-sm text-slate-500">Trend Score</p>
              </div>
              <div className="text-center p-4 rounded-xl bg-slate-50">
                <Flame className="h-6 w-6 text-red-500 mx-auto mb-2" />
                <p className="font-mono text-2xl font-bold text-red-500">{product.early_trend_score || 0}</p>
                <p className="text-sm text-slate-500">Early Trend</p>
              </div>
              <div className="text-center p-4 rounded-xl bg-slate-50">
                <Eye className="h-6 w-6 text-pink-500 mx-auto mb-2" />
                <p className="font-mono text-2xl font-bold text-pink-500">{formatNumber(product.tiktok_views)}</p>
                <p className="text-sm text-slate-500">TikTok Views</p>
              </div>
              <div className="text-center p-4 rounded-xl bg-slate-50">
                <Store className="h-6 w-6 text-indigo-500 mx-auto mb-2" />
                <p className="font-mono text-2xl font-bold text-indigo-500">{product.stores_created || 0}</p>
                <p className="text-sm text-slate-500">Stores Built</p>
              </div>
            </div>

            {/* Locked Content */}
            <Card className="border-2 border-dashed border-slate-200 bg-slate-50/50">
              <CardContent className="p-8 text-center">
                <Lock className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <h3 className="font-semibold text-lg text-slate-900 mb-2">
                  Unlock Full Product Insights
                </h3>
                <p className="text-slate-500 mb-6 max-w-md mx-auto">
                  Get pricing data, supplier links, AI analysis, margin calculations, and build your own store with this product.
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Link to="/signup">
                    <Button className="bg-indigo-600 hover:bg-indigo-700">
                      <Rocket className="mr-2 h-4 w-4" />
                      Sign Up Free
                    </Button>
                  </Link>
                  <Link to="/login">
                    <Button variant="outline">
                      Already have an account?
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-center text-white">
          <h2 className="font-manrope text-2xl font-bold mb-2">
            Find More Winning Products
          </h2>
          <p className="text-indigo-100 mb-6">
            Discover trending products and launch your Shopify store in minutes
          </p>
          <Link to="/signup">
            <Button size="lg" className="bg-white text-indigo-600 hover:bg-indigo-50 font-semibold">
              Start Building Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>

        {/* SEO Footer */}
        <footer className="mt-12 pt-8 border-t border-slate-200 text-center text-sm text-slate-500">
          <p className="mb-2">
            <strong className="text-slate-700">ViralScout</strong> - Find winning products and launch ecommerce stores fast
          </p>
          <p>
            Powered by AI-driven trend detection, early trend scoring, and success tracking.
          </p>
        </footer>
      </main>
    </div>
  );
}
