import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, Package, ChevronRight, Loader2, Flame, Zap,
  Clock, Tag, ArrowRight, BarChart3,
} from 'lucide-react';
import { API_URL } from '@/lib/config';
import { SeoInternalLinks } from '@/pages/SeoTrendingPage';

function getConfidence(score) {
  if (score >= 75) return { label: 'High Confidence', icon: Flame, color: 'text-emerald-600 bg-emerald-50 border-emerald-200' };
  if (score >= 50) return { label: 'Emerging', icon: Zap, color: 'text-amber-600 bg-amber-50 border-amber-200' };
  return { label: 'Experimental', icon: Clock, color: 'text-slate-500 bg-slate-50 border-slate-200' };
}

export default function SeoCategoryPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    setNotFound(false);

    Promise.all([
      fetch(`${API_URL}/api/public/seo/category/${slug}`).then(r => {
        if (!r.ok) throw new Error('Not found');
        return r.json();
      }),
      fetch(`${API_URL}/api/public/seo/all-categories`).then(r => r.ok ? r.json() : []),
    ]).then(([pageData, cats]) => {
      setData(pageData);
      setCategories(cats || []);
      setLoading(false);
    }).catch(() => {
      setNotFound(true);
      setLoading(false);
    });
  }, [slug]);

  const siteUrl = typeof window !== 'undefined' ? window.location.origin : '';
  const categoryName = data?.category || slug?.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || '';
  const products = data?.products || [];

  const seoTitle = `Trending ${categoryName} Products - Best ${categoryName} to Sell | TrendScout`;
  const seoDesc = `Discover the best trending ${categoryName.toLowerCase()} products to sell. ${products.length} products ranked by AI trend score with supplier costs and profit margins.`;

  const breadcrumbLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: `${siteUrl}/` },
      { '@type': 'ListItem', position: 2, name: 'Trending Products', item: `${siteUrl}/trending-products` },
      { '@type': 'ListItem', position: 3, name: `${categoryName} Products`, item: `${siteUrl}/category/${slug}` },
    ],
  };

  const itemListLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: `Trending ${categoryName} Products`,
    numberOfItems: products.length,
    itemListElement: products.slice(0, 20).map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      url: `${siteUrl}/trending/${p.slug}`,
      name: p.product_name,
    })),
  };

  if (loading) {
    return (
      <LandingLayout>
        <div className="flex items-center justify-center py-32">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </LandingLayout>
    );
  }

  if (notFound) {
    return (
      <LandingLayout>
        <div className="text-center py-32">
          <Package className="h-16 w-16 text-slate-300 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Category not found</h1>
          <p className="text-slate-500 mb-6">We couldn't find products in this category.</p>
          <Link to="/trending-products" className="text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1 justify-center">
            <ArrowRight className="h-4 w-4" /> Browse all trending products
          </Link>
        </div>
      </LandingLayout>
    );
  }

  return (
    <LandingLayout>
      <Helmet>
        <title>{seoTitle}</title>
        <meta name="description" content={seoDesc} />
        <meta property="og:title" content={seoTitle} />
        <meta property="og:description" content={seoDesc} />
        <link rel="canonical" href={`${siteUrl}/category/${slug}`} />
        <script type="application/ld+json">{JSON.stringify(breadcrumbLd)}</script>
        <script type="application/ld+json">{JSON.stringify(itemListLd)}</script>
      </Helmet>

      <div className="mx-auto max-w-6xl px-6 py-10" data-testid="seo-category-page">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-slate-400 mb-8" data-testid="breadcrumb">
          <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
          <ChevronRight className="h-3 w-3" />
          <Link to="/trending-products" className="hover:text-indigo-600 transition-colors">Trending Products</Link>
          <ChevronRight className="h-3 w-3" />
          <span className="text-slate-600 font-medium">{categoryName}</span>
        </nav>

        {/* Hero */}
        <div className="text-center mb-10">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Tag className="h-7 w-7 text-white" />
          </div>
          <h1 className="font-manrope text-4xl sm:text-5xl font-extrabold text-slate-900" data-testid="category-page-title">
            Trending {categoryName} Products
          </h1>
          <p className="mt-3 text-slate-500 max-w-lg mx-auto text-base">
            The best {categoryName.toLowerCase()} products to sell right now, ranked by AI trend score.
          </p>
          <p className="mt-2 text-sm text-slate-400">{products.length} products found</p>
        </div>

        {/* Other category links */}
        {categories.length > 1 && (
          <div className="flex items-center justify-center gap-2 flex-wrap mb-8" data-testid="other-categories">
            {categories.filter(c => c.slug !== slug).slice(0, 10).map(cat => (
              <Link
                key={cat.slug}
                to={`/category/${cat.slug}`}
                className="px-3 py-1.5 rounded-full text-xs font-medium bg-white text-slate-600 border border-slate-200 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 transition-all"
                data-testid={`other-cat-${cat.slug}`}
              >
                {cat.name} ({cat.count})
              </Link>
            ))}
          </div>
        )}

        {/* Product grid */}
        {products.length === 0 ? (
          <div className="text-center py-20">
            <Package className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 font-medium">No products found in this category</p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="category-product-grid">
            {products.map((product) => (
              <CategoryProductCard key={product.id} product={product} />
            ))}
          </div>
        )}

        {/* Internal links */}
        <SeoInternalLinks currentPath={`/category/${slug}`} categories={categories} />

        {/* CTA */}
        <div className="text-center mt-12 py-8 bg-gradient-to-r from-indigo-50 to-violet-50 rounded-2xl">
          <h2 className="font-manrope text-xl font-bold text-slate-900 mb-2">Want full {categoryName.toLowerCase()} product intelligence?</h2>
          <p className="text-slate-500 text-sm mb-4 max-w-md mx-auto">
            Get AI-powered launch simulations, supplier intel, and ad creative generation.
          </p>
          <Link
            to="/signup"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold px-6 py-2.5 rounded-xl hover:shadow-lg transition-shadow"
            data-testid="category-cta-signup"
          >
            <Zap className="h-4 w-4" /> Start Free Trial
          </Link>
        </div>
      </div>
    </LandingLayout>
  );
}

function CategoryProductCard({ product }) {
  return (
    <Link
      to={`/trending/${product.slug}`}
      className="group block bg-white rounded-2xl border border-slate-100 overflow-hidden hover:border-slate-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5"
      data-testid={`category-product-${product.id}`}
    >
      <div className="relative h-36 bg-gradient-to-br from-slate-50 to-slate-100 overflow-hidden">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Package className="h-10 w-10 text-slate-200" />
          </div>
        )}
        <div className="absolute top-2.5 left-2.5 bg-white/95 backdrop-blur-sm rounded-lg px-2 py-1 shadow-sm">
          <span className="font-mono text-sm font-bold text-indigo-600">{product.launch_score}</span>
        </div>
        {product.rank && (
          <div className="absolute top-2.5 right-2.5 bg-slate-900/80 backdrop-blur-sm rounded-lg px-2 py-1 shadow-sm">
            <span className="text-xs font-bold text-white">#{product.rank}</span>
          </div>
        )}
        {product.trend_stage && (
          <div className="absolute bottom-2.5 left-2.5">
            <Badge className="text-[10px] border rounded-full bg-white/90 text-slate-700 border-slate-200">
              {product.trend_stage}
            </Badge>
          </div>
        )}
      </div>
      <div className="p-3.5">
        <h3 className="font-semibold text-slate-900 text-sm line-clamp-1 group-hover:text-indigo-600 transition-colors">
          {product.product_name}
        </h3>
        {product.short_description && (
          <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-2">{product.short_description}</p>
        )}
        <div className="grid grid-cols-3 gap-1.5 mt-3">
          <div className="rounded-lg px-2 py-1.5 text-center bg-emerald-50">
            <p className="text-xs font-semibold text-emerald-700">{product.margin_percent}%</p>
            <p className="text-[10px] text-slate-400">Margin</p>
          </div>
          <div className="rounded-lg px-2 py-1.5 text-center bg-slate-50">
            <p className="text-xs font-semibold text-slate-700">{product.supplier_cost > 0 ? `£${product.supplier_cost}` : '—'}</p>
            <p className="text-[10px] text-slate-400">Supplier</p>
          </div>
          <div className="rounded-lg px-2 py-1.5 text-center bg-slate-50">
            <p className="text-xs font-semibold text-slate-700">{product.retail_price > 0 ? `£${product.retail_price}` : '—'}</p>
            <p className="text-[10px] text-slate-400">Retail</p>
          </div>
        </div>
        <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-50">
          <span className="text-[11px] text-slate-400 flex items-center gap-1">
            <TrendingUp className="h-3 w-3" />
            {product.growth_rate || 0}% growth
          </span>
          <span className="text-[11px] text-indigo-500 font-medium group-hover:text-indigo-600 flex items-center gap-0.5">
            View Details <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </div>
    </Link>
  );
}
