/**
 * Public Trending Products Page
 * 
 * SEO-optimized page showcasing top trending products.
 * Limited info shown - premium insights require signup.
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  Flame,
  Rocket,
  Lock,
  ArrowRight,
  Sparkles,
  BarChart3,
  Zap,
  RefreshCw,
  Share2,
  Twitter,
  Link2
} from 'lucide-react';
import api from '@/lib/api';

// Get trend stage info
function getTrendStageInfo(stage) {
  const stages = {
    exploding: { label: 'Exploding', color: 'bg-red-500', icon: Flame },
    rising: { label: 'Rising', color: 'bg-orange-500', icon: TrendingUp },
    early_trend: { label: 'Early Trend', color: 'bg-blue-500', icon: Zap },
    stable: { label: 'Stable', color: 'bg-slate-500', icon: BarChart3 }
  };
  return stages[stage] || stages.stable;
}

// Get launch score label
function getLaunchScoreLabel(score) {
  if (score >= 80) return { label: 'Strong Launch', color: 'text-green-600', bg: 'bg-green-50' };
  if (score >= 60) return { label: 'Promising', color: 'text-blue-600', bg: 'bg-blue-50' };
  if (score >= 40) return { label: 'Risky', color: 'text-amber-600', bg: 'bg-amber-50' };
  return { label: 'Avoid', color: 'text-red-600', bg: 'bg-red-50' };
}

// Product Card Component
function TrendingProductCard({ product, rank }) {
  const trendInfo = getTrendStageInfo(product.early_trend_label || product.trend_stage);
  const scoreInfo = getLaunchScoreLabel(product.launch_score || 0);
  const TrendIcon = trendInfo.icon;
  
  return (
    <Card className="group hover:shadow-lg transition-all duration-300 overflow-hidden">
      <CardContent className="p-0">
        <div className="flex flex-col sm:flex-row">
          {/* Product Image */}
          <div className="relative w-full sm:w-48 h-48 bg-slate-100 flex-shrink-0">
            {product.image_url ? (
              <img 
                src={product.image_url} 
                alt={product.product_name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Sparkles className="h-12 w-12 text-slate-300" />
              </div>
            )}
            {/* Rank Badge */}
            <div className="absolute top-2 left-2 w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">
              {rank}
            </div>
          </div>
          
          {/* Product Info */}
          <div className="flex-1 p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <Link to={`/p/${product.slug || product.id}`}>
                  <h3 className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-2">
                    {product.product_name}
                  </h3>
                </Link>
                <p className="text-sm text-slate-500 mt-1">
                  {product.category || 'Trending Product'}
                </p>
              </div>
              
              {/* Launch Score */}
              <div className={`text-center px-3 py-2 rounded-lg ${scoreInfo.bg}`}>
                <div className={`text-2xl font-bold ${scoreInfo.color}`}>
                  {product.launch_score || 0}
                </div>
                <div className={`text-xs font-medium ${scoreInfo.color}`}>
                  {scoreInfo.label}
                </div>
              </div>
            </div>
            
            {/* Badges */}
            <div className="flex flex-wrap items-center gap-2 mt-3">
              <Badge className={`${trendInfo.color} text-white`}>
                <TrendIcon className="h-3 w-3 mr-1" />
                {trendInfo.label}
              </Badge>
              {product.launch_score >= 80 && (
                <Badge className="bg-green-100 text-green-700">
                  <Rocket className="h-3 w-3 mr-1" />
                  High Potential
                </Badge>
              )}
            </div>
            
            {/* Locked Premium Insights */}
            <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-dashed border-slate-200">
              <div className="flex items-center gap-2 text-slate-500 text-sm">
                <Lock className="h-4 w-4" />
                <span>Supplier cost, margins, and detailed analytics</span>
              </div>
            </div>
            
            {/* CTA */}
            <div className="mt-4 flex items-center gap-3">
              <Link to={`/p/${product.slug || product.id}`}>
                <Button variant="outline" size="sm" data-testid={`view-product-${rank}`}>
                  View Details
                </Button>
              </Link>
              <Link to="/signup">
                <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700" data-testid={`unlock-product-${rank}`}>
                  Unlock Insights
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </Link>
              <Button
                variant="ghost"
                size="sm"
                data-testid={`share-product-${rank}`}
                onClick={() => {
                  const url = `${window.location.origin}/p/${product.slug || product.id}`;
                  if (navigator.share) {
                    navigator.share({ title: product.product_name, url });
                  } else {
                    navigator.clipboard.writeText(url);
                    import('sonner').then(m => m.toast.success('Link copied!'));
                  }
                }}
              >
                <Share2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function TrendingProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  useEffect(() => {
    const fetchTrendingProducts = async () => {
      try {
        const response = await api.get('/api/public/trending-products?limit=10');
        if (response.data) {
          setProducts(response.data.products || []);
          setLastUpdated(response.data.last_updated);
        }
      } catch (error) {
        console.error('Failed to fetch trending products:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchTrendingProducts();
  }, []);
  
  return (
    <>
      <Helmet>
        <title>Trending Ecommerce Products Today | TrendScout</title>
        <meta 
          name="description" 
          content="Discover trending ecommerce products before they go viral using TrendScout's market intelligence platform. See today's top opportunities ranked by Launch Score."
        />
        <meta property="og:title" content="Trending Ecommerce Products Today | TrendScout" />
        <meta property="og:description" content="Discover trending ecommerce products before they go viral." />
        <meta property="og:type" content="website" />
        <link rel="canonical" href="https://www.trendscout.click/trending-products" />
      </Helmet>
      
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
        {/* Header */}
        <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-xl text-slate-900">TrendScout</span>
            </Link>
            <div className="flex items-center gap-3">
              <Link to="/login">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700">
                  Start Free
                </Button>
              </Link>
            </div>
          </div>
        </header>
        
        {/* Hero Section */}
        <section className="py-12 px-4">
          <div className="max-w-6xl mx-auto text-center">
            <Badge className="bg-indigo-100 text-indigo-700 mb-4">
              <RefreshCw className="h-3 w-3 mr-1" />
              Updated Daily
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Trending Ecommerce Products Today
            </h1>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
              TrendScout analyzes millions of ecommerce signals daily to detect emerging product opportunities. 
              See which products are gaining momentum and could become the next bestsellers.
            </p>
            
            {/* Quick Stats */}
            <div className="flex justify-center gap-8 mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-600">{products.length}</div>
                <div className="text-sm text-slate-500">Top Products</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {products.filter(p => p.launch_score >= 80).length}
                </div>
                <div className="text-sm text-slate-500">Strong Launches</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600">
                  {products.filter(p => p.early_trend_label === 'exploding').length}
                </div>
                <div className="text-sm text-slate-500">Exploding Trends</div>
              </div>
            </div>
          </div>
        </section>
        
        {/* Products Grid */}
        <section className="pb-16 px-4">
          <div className="max-w-6xl mx-auto">
            {loading ? (
              <div className="text-center py-12">
                <RefreshCw className="h-8 w-8 animate-spin mx-auto text-indigo-500" />
                <p className="text-slate-500 mt-4">Loading trending products...</p>
              </div>
            ) : products.length > 0 ? (
              <div className="space-y-4">
                {products.map((product, index) => (
                  <TrendingProductCard 
                    key={product.id} 
                    product={product} 
                    rank={index + 1}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Sparkles className="h-12 w-12 text-slate-300 mx-auto" />
                <p className="text-slate-500 mt-4">No trending products available</p>
              </div>
            )}
            
            {/* CTA Section */}
            <div className="mt-12 text-center bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
              <h2 className="text-2xl font-bold mb-2">
                Want Full Access to Product Intelligence?
              </h2>
              <p className="text-indigo-100 mb-6">
                Unlock supplier costs, profit margins, competition analysis, and more.
              </p>
              <div className="flex justify-center gap-4">
                <Link to="/signup">
                  <Button size="lg" className="bg-white text-indigo-600 hover:bg-indigo-50">
                    Start Free
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
                <Link to="/pricing">
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                    View Pricing
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
        
        {/* Footer */}
        <footer className="border-t bg-slate-50 py-8 px-4">
          <div className="max-w-6xl mx-auto text-center text-slate-500 text-sm">
            <p>© {new Date().getFullYear()} TrendScout. All rights reserved.</p>
            <p className="mt-2">
              {lastUpdated && `Last updated: ${new Date(lastUpdated).toLocaleDateString()}`}
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
