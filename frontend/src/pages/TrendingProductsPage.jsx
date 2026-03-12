import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, ArrowRight, Package, Zap, Radar, Lock,
  Sparkles, BarChart3, Eye,
} from 'lucide-react';
import { API_URL } from '@/lib/config';

const STAGE_COLORS = {
  exploding: 'bg-red-100 text-red-700 border-red-200',
  rising: 'bg-amber-100 text-amber-700 border-amber-200',
  emerging: 'bg-blue-100 text-blue-700 border-blue-200',
  early_trend: 'bg-violet-100 text-violet-700 border-violet-200',
  Rising: 'bg-amber-100 text-amber-700 border-amber-200',
  Unknown: 'bg-slate-100 text-slate-600 border-slate-200',
};

export default function TrendingProductsPage() {
  const [products, setProducts] = useState([]);
  const [weekCount, setWeekCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const catParam = searchParams.get('category');
    if (catParam) setSelectedCategory(catParam);
  }, [searchParams]);

  useEffect(() => {
    (async () => {
      try {
        const [prodRes, catRes] = await Promise.all([
          fetch(`${API_URL}/api/public/trending-products?limit=20`),
          fetch(`${API_URL}/api/public/categories`),
        ]);
        if (prodRes.ok) {
          const data = await prodRes.json();
          setProducts(data.products || []);
          setWeekCount(data.detected_this_week || 0);
        }
        if (catRes.ok) {
          setCategories(await catRes.json());
        }
      } catch (e) { console.error(e); }
      setLoading(false);
    })();
  }, []);

  const filteredProducts = selectedCategory
    ? products.filter(p => p.category === selectedCategory)
    : products;

  const seoTitle = 'Trending Dropshipping Products — Detected by TrendScout AI';
  const seoDescription = "Discover trending ecommerce products detected by TrendScout's AI scoring engine. Find winning products before competitors.";
  const siteUrl = typeof window !== 'undefined' ? window.location.origin : '';

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: seoTitle,
    description: seoDescription,
    url: `${siteUrl}/trending-products`,
    numberOfItems: products.length,
    itemListElement: products.map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      item: {
        '@type': 'Product',
        name: p.product_name,
        url: `${siteUrl}/trending/${p.slug}`,
        image: p.image_url,
        category: p.category,
      },
    })),
  };

  return (
    <>
      <Helmet>
        <title>{seoTitle}</title>
        <meta name="description" content={seoDescription} />
        <meta property="og:title" content={seoTitle} />
        <meta property="og:description" content={seoDescription} />
        <meta property="og:type" content="website" />
        <meta property="og:url" content={`${siteUrl}/trending-products`} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={seoTitle} />
        <meta name="twitter:description" content={seoDescription} />
        <link rel="canonical" href={`${siteUrl}/trending-products`} />
        <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      </Helmet>

      <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" data-testid="trending-products-page">
        {/* Nav */}
        <nav className="border-b border-white/5 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
          <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                <Radar className="h-4 w-4 text-white" />
              </div>
              <span className="font-manrope font-bold text-white text-lg">TrendScout</span>
            </Link>
            <div className="flex items-center gap-3">
              <Link to="/login">
                <Button variant="ghost" className="text-slate-400 hover:text-white text-sm">Log in</Button>
              </Link>
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-sm" data-testid="nav-signup-btn">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </nav>

        {/* Hero */}
        <header className="mx-auto max-w-7xl px-6 pt-16 pb-10">
          <div className="flex items-center gap-2 mb-4">
            <div className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-sm font-medium text-emerald-400" data-testid="week-count">
              {weekCount} products detected this week
            </span>
          </div>
          <h1 className="font-manrope text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight" data-testid="trending-h1">
            Trending Products Detected by{' '}
            <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">TrendScout AI</span>
          </h1>
          <p className="mt-4 text-lg text-slate-400 max-w-2xl">
            Real-time product intelligence powered by AI. These products are scoring high across trend signals, demand, and profitability.
          </p>
        </header>

        {/* Category Filter Strip */}
        {categories.length > 0 && (
          <div className="mx-auto max-w-7xl px-6 pb-6" data-testid="category-filter">
            <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  !selectedCategory
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white/[0.06] text-slate-400 hover:bg-white/[0.1] hover:text-white border border-white/[0.08]'
                }`}
                data-testid="category-all"
              >
                All ({products.length})
              </button>
              {categories.map(cat => (
                <button
                  key={cat.name}
                  onClick={() => setSelectedCategory(cat.name === selectedCategory ? null : cat.name)}
                  className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    selectedCategory === cat.name
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white/[0.06] text-slate-400 hover:bg-white/[0.1] hover:text-white border border-white/[0.08]'
                  }`}
                  data-testid={`category-${cat.slug}`}
                >
                  {cat.name} ({cat.count})
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Product Grid */}
        <section className="mx-auto max-w-7xl px-6 pb-24">
          {loading ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="bg-white/5 rounded-2xl h-72 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5" data-testid="product-grid">
              {filteredProducts.map((product, idx) => (
                <ProductCard key={product.id} product={product} idx={idx} />
              ))}
            </div>
          )}

          {/* Bottom CTA */}
          {!loading && products.length > 0 && (
            <div className="mt-16 text-center">
              <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-2xl px-8 py-6 backdrop-blur-sm">
                <Lock className="h-5 w-5 text-indigo-400" />
                <div className="text-left ml-2">
                  <p className="text-white font-semibold">Want the full analysis?</p>
                  <p className="text-slate-400 text-sm">Unlock detailed supplier data, ad creatives, and launch tools.</p>
                </div>
                <Link to="/signup" className="ml-4">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 whitespace-nowrap" data-testid="bottom-cta-btn">
                    Start with TrendScout
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </section>

        {/* Footer */}
        <footer className="border-t border-white/5 py-8">
          <div className="mx-auto max-w-7xl px-6 flex items-center justify-between">
            <p className="text-sm text-slate-500">TrendScout — AI-powered product intelligence</p>
            <div className="flex items-center gap-4 text-sm text-slate-500">
              <Link to="/pricing" className="hover:text-white transition-colors">Pricing</Link>
              <Link to="/" className="hover:text-white transition-colors">Home</Link>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}

function ProductCard({ product, idx }) {
  const stageClass = STAGE_COLORS[product.trend_stage] || STAGE_COLORS.Unknown;
  const hasImage = product.image_url && !product.image_url.includes('01jrA-8DXYL');

  return (
    <div
      className="group bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.06] hover:border-indigo-500/30 rounded-2xl overflow-hidden transition-all duration-300"
      style={{ animationDelay: `${idx * 50}ms` }}
      data-testid={`trending-card-${idx}`}
    >
      {/* Image */}
      <div className="h-36 bg-gradient-to-br from-slate-800 to-slate-900 relative overflow-hidden">
        {hasImage ? (
          <img src={product.image_url} alt={product.product_name} className="w-full h-full object-contain p-3 opacity-90 group-hover:opacity-100 transition-opacity" />
        ) : (
          <div className="flex items-center justify-center h-full">
            <Package className="h-12 w-12 text-slate-700" />
          </div>
        )}
        {product.radar_detected && (
          <div className="absolute top-2 left-2 flex items-center gap-1 bg-indigo-600/90 backdrop-blur-sm rounded-full px-2 py-0.5">
            <Radar className="h-3 w-3 text-white" />
            <span className="text-[10px] text-white font-medium">Radar</span>
          </div>
        )}
        <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-sm rounded-full px-2.5 py-1 flex items-center gap-1">
          <BarChart3 className="h-3 w-3 text-indigo-400" />
          <span className="font-mono text-sm font-bold text-white">{product.launch_score}</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-white text-sm line-clamp-2 leading-snug mb-2 min-h-[2.5rem]">
          {product.product_name}
        </h3>
        <div className="flex items-center gap-2 mb-3">
          <Badge className={`text-[10px] border rounded-full ${stageClass}`}>
            {product.trend_stage}
          </Badge>
          {product.category && (
            <span className="text-[10px] text-slate-500 truncate">{product.category}</span>
          )}
        </div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-1">
            <TrendingUp className="h-3 w-3 text-emerald-400" />
            <span className="text-sm font-semibold text-emerald-400">{product.margin_percent}%</span>
            <span className="text-[10px] text-slate-500 ml-0.5">margin</span>
          </div>
          <div className="flex items-center gap-1">
            <Eye className="h-3 w-3 text-slate-500" />
            <span className="text-[10px] text-slate-500">Score {product.launch_score}</span>
          </div>
        </div>
        <Link to={`/trending/${product.slug}`}>
          <Button
            variant="outline"
            size="sm"
            className="w-full border-indigo-500/30 text-indigo-400 hover:bg-indigo-600 hover:text-white hover:border-indigo-600 transition-all text-xs"
            data-testid={`unlock-btn-${idx}`}
          >
            <Lock className="mr-1.5 h-3 w-3" />
            Unlock full analysis
          </Button>
        </Link>
      </div>
    </div>
  );
}
