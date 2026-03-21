import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { SignupGate } from '@/components/SignupGate';
import { 
  TrendingUp, 
  Lock,
  Rocket,
  Share2,
  ArrowLeft,
  PieChart,
  Users,
  BarChart3,
  Eye,
  Twitter,
  Facebook,
  Link2,
  MessageCircle
} from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

import { API_URL } from '@/lib/config';

function getMarketInfo(label) {
  const map = {
    massive: { text: 'Massive Opportunity', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
    strong: { text: 'Strong Opportunity', color: 'bg-blue-100 text-blue-800 border-blue-200' },
    competitive: { text: 'Competitive', color: 'bg-amber-100 text-amber-800 border-amber-200' },
    saturated: { text: 'Saturated', color: 'bg-red-100 text-red-800 border-red-200' },
  };
  return map[label] || { text: 'Unknown', color: 'bg-slate-100 text-slate-800 border-slate-200' };
}

function getEarlyTrendInfo(label) {
  const map = {
    exploding: { text: 'Exploding', color: 'bg-red-100 text-red-800 border-red-200' },
    rising: { text: 'Rising Fast', color: 'bg-orange-100 text-orange-800 border-orange-200' },
    early_trend: { text: 'Early Trend', color: 'bg-blue-100 text-blue-800 border-blue-200' },
    stable: { text: 'Stable', color: 'bg-slate-100 text-slate-800 border-slate-200' },
  };
  return map[label] || { text: '', color: '' };
}

function ShareMenu({ product, onClose }) {
  const shareUrl = `${window.location.origin}/p/${product.id}`;
  const shareText = `Check out ${product.product_name} on TrendScout - trending ecommerce product!`;

  const shareOptions = [
    {
      name: 'Twitter / X',
      icon: Twitter,
      onClick: () => window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`, '_blank'),
    },
    {
      name: 'Facebook',
      icon: Facebook,
      onClick: () => window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`, '_blank'),
    },
    {
      name: 'LinkedIn',
      icon: Share2,
      onClick: () => window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`, '_blank'),
    },
    {
      name: 'Reddit',
      icon: MessageCircle,
      onClick: () => window.open(`https://reddit.com/submit?url=${encodeURIComponent(shareUrl)}&title=${encodeURIComponent(shareText)}`, '_blank'),
    },
    {
      name: 'WhatsApp',
      icon: MessageCircle,
      onClick: () => window.open(`https://wa.me/?text=${encodeURIComponent(shareText + ' ' + shareUrl)}`, '_blank'),
    },
    {
      name: 'Copy Link',
      icon: Link2,
      onClick: () => {
        navigator.clipboard.writeText(shareUrl);
        toast.success('Link copied to clipboard!');
      },
    },
  ];

  return (
    <div className="absolute right-0 top-full mt-2 bg-white rounded-xl shadow-lg border border-slate-200 p-2 min-w-[180px] z-50" data-testid="share-menu">
      {shareOptions.map((opt) => (
        <button
          key={opt.name}
          onClick={() => { opt.onClick(); onClose(); }}
          className="flex items-center gap-3 w-full px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
          data-testid={`share-${opt.name.toLowerCase().replace(/[\s\/]/g, '-')}`}
        >
          <opt.icon className="h-4 w-4" />
          {opt.name}
        </button>
      ))}
    </div>
  );
}

export default function PublicProductPage() {
  const { isAuthenticated } = useAuth();
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showShare, setShowShare] = useState(false);

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
          <Link to="/trending-products">
            <Button>View Trending Products</Button>
          </Link>
        </div>
      </div>
    );
  }

  const marketInfo = getMarketInfo(product.market_label);
  const earlyTrendInfo = getEarlyTrendInfo(product.early_trend_label);
  const productName = product.product_name || 'Trending Product';
  const productId = product.id || id;

  const siteUrl = 'https://www.trendscout.click';
  const canonicalUrl = `${siteUrl}/p/${productId}`;
  const margin = product.estimated_margin && product.estimated_retail_price
    ? Math.round((product.estimated_margin / product.estimated_retail_price) * 100)
    : 0;
  const ogDescription = `${marketInfo.text} | Launch Score: ${product.launch_score || product.market_score || 0}/100 | ${margin}% margin | ${earlyTrendInfo.text || 'Trending'} — Discover winning products before they go viral.`;
  const ogImage = product.image_url || product.gallery_images?.[0] || '';

  return (
    <>
      <Helmet>
        <title>{`${productName} - TrendScout Product Insights`}</title>
        <meta name="description" content={ogDescription} />
        {/* Open Graph */}
        <meta property="og:title" content={`${productName} - TrendScout`} />
        <meta property="og:description" content={ogDescription} />
        <meta property="og:type" content="product" />
        <meta property="og:url" content={canonicalUrl} />
        {ogImage && <meta property="og:image" content={ogImage} />}
        <meta property="og:site_name" content="TrendScout" />
        {/* Twitter Card */}
        <meta name="twitter:card" content={ogImage ? 'summary_large_image' : 'summary'} />
        <meta name="twitter:title" content={`${productName} - TrendScout`} />
        <meta name="twitter:description" content={ogDescription} />
        {ogImage && <meta name="twitter:image" content={ogImage} />}
        {/* Product structured data */}
        <meta property="product:price:amount" content={String(product.estimated_retail_price || 0)} />
        <meta property="product:price:currency" content="GBP" />
        <link rel="canonical" href={canonicalUrl} />
        {/* JSON-LD Structured Data */}
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Product",
            "name": productName,
            "description": ogDescription,
            "image": ogImage || undefined,
            "url": canonicalUrl,
            "brand": { "@type": "Brand", "name": product.category || "TrendScout" },
            "offers": {
              "@type": "Offer",
              "price": product.estimated_retail_price || 0,
              "priceCurrency": "GBP",
              "availability": "https://schema.org/InStock",
            },
            "aggregateRating": {
              "@type": "AggregateRating",
              "ratingValue": Math.min(5, ((product.launch_score || 50) / 20)).toFixed(1),
              "bestRating": "5",
              "ratingCount": Math.max(1, Math.floor((product.tiktok_views || 0) / 10000)),
            },
          })}
        </script>
      </Helmet>

      <div className="min-h-screen bg-slate-50">
        {/* Header */}
        <header className="bg-white border-b border-slate-200">
          <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-xl text-slate-900">TrendScout</span>
            </Link>
            <div className="flex items-center gap-3">
              <div className="relative">
                <Button variant="outline" onClick={() => setShowShare(!showShare)} data-testid="public-share-btn">
                  <Share2 className="mr-2 h-4 w-4" />
                  Share
                </Button>
                {showShare && <ShareMenu product={product} onClose={() => setShowShare(false)} />}
              </div>
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
            to="/trending-products" 
            className="inline-flex items-center text-sm text-slate-500 hover:text-slate-700"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Trending Products
          </Link>
        </div>

        {/* Product Hero */}
        <main className="max-w-4xl mx-auto px-6 py-8">
          <Card className="border-0 shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 p-8">
              <div className="flex gap-6">
                {product.image_url && (
                  <img 
                    src={product.image_url} 
                    alt={product.product_name}
                    className="w-32 h-32 rounded-xl object-cover shadow-md"
                   loading="lazy" />
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
                  <h1 className="text-3xl font-bold text-slate-900 mb-2" data-testid="public-product-name">
                    {productName}
                  </h1>
                  <p className="text-slate-600">{product.category}</p>
                </div>
              </div>
            </div>

            <CardContent className="p-6 sm:p-8">
              {/* Public Scores — gated for non-authenticated */}
              {isAuthenticated ? (
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
              ) : (
              <div className="mb-8">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-slate-50 rounded-xl p-4 text-center">
                    <BarChart3 className="h-6 w-6 mx-auto mb-2 text-slate-400" />
                    <p className="font-mono text-lg font-bold text-slate-700 capitalize">{product.trend_stage}</p>
                    <p className="text-xs text-slate-500">Trend Stage</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4 text-center">
                    <Users className="h-6 w-6 mx-auto mb-2 text-slate-400" />
                    <p className="font-mono text-lg font-bold text-slate-600 capitalize">{product.competition_level}</p>
                    <p className="text-xs text-slate-500">Competition</p>
                  </div>
                  <div className="bg-slate-100 rounded-xl p-4 text-center col-span-2 flex items-center justify-center gap-3">
                    <Lock className="h-5 w-5 text-indigo-500" />
                    <div className="text-left">
                      <p className="text-sm font-semibold text-slate-700">Scores locked</p>
                      <p className="text-xs text-slate-500">Sign up to see market & trend scores</p>
                    </div>
                  </div>
                </div>
              </div>
              )}

              {/* Locked Insights */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-slate-400" />
                  Full Insights (Sign up to unlock)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-100 rounded-xl p-4 relative overflow-hidden">
                    <div className="absolute inset-0 backdrop-blur-sm bg-white/50 flex items-center justify-center">
                      <div className="text-center">
                        <p className="font-semibold text-slate-700">{product.margin_range}</p>
                        <p className="text-xs text-slate-500">Est. Margin Range</p>
                      </div>
                    </div>
                    <p className="text-slate-400">Exact margin: £XX.XX</p>
                  </div>
                  {['Supplier data locked', 'Competitor data locked', 'Ad activity locked'].map((label) => (
                    <div key={label} className="bg-slate-100 rounded-xl p-4 relative overflow-hidden">
                      <div className="absolute inset-0 backdrop-blur-md bg-slate-200/80 flex items-center justify-center">
                        <div className="text-center">
                          <Lock className="h-5 w-5 mx-auto mb-1 text-slate-400" />
                          <p className="text-xs text-slate-500">{label}</p>
                        </div>
                      </div>
                      <p className="text-slate-400">Hidden data...</p>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* CTA */}
          <div className="mt-8 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-center text-white">
            <h2 className="text-2xl font-bold mb-2">
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
              <Link to="/trending-products">
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
              <strong className="text-slate-700">TrendScout</strong> - Find winning products before they go viral
            </p>
            <p>Powered by AI-driven trend detection - Updated daily</p>
          </div>
        </footer>
      </div>
    </>
  );
}
