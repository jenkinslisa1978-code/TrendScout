import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, Package, ChevronRight, Loader2, Flame, Zap,
  Clock, ArrowRight, Calendar, BarChart3, Eye,
} from 'lucide-react';
import { API_URL } from '@/lib/config';

const PAGE_CONFIG = {
  '/trending-products-today': {
    endpoint: '/api/public/seo/trending-today',
    title: 'Trending Products Today',
    h1: 'Trending Products Today',
    description: 'Discover the hottest trending products today. Updated daily with real-time AI trend analysis, supplier data, and profit margins.',
    canonical: '/trending-products-today',
    icon: Flame,
    iconColor: 'from-rose-500 to-orange-500',
    subtitle: "Today's top trending ecommerce products, scored by our AI engine.",
  },
  '/trending-products-this-week': {
    endpoint: '/api/public/seo/trending-this-week',
    title: 'Trending Products This Week',
    h1: 'Trending Products This Week',
    description: 'The top trending ecommerce products this week. AI-scored trend analysis with supplier costs and profit margins.',
    canonical: '/trending-products-this-week',
    icon: Calendar,
    iconColor: 'from-sky-500 to-indigo-500',
    subtitle: 'Products gaining the most momentum this week.',
  },
  '/trending-products-this-month': {
    endpoint: '/api/public/seo/trending-this-month',
    title: 'Trending Products This Month',
    h1: 'Trending Products This Month',
    description: 'Monthly trending products report. Find the best products to sell this month with AI-powered market intelligence.',
    canonical: '/trending-products-this-month',
    icon: BarChart3,
    iconColor: 'from-emerald-500 to-teal-500',
    subtitle: "This month's strongest product trends and opportunities.",
  },
};

function getConfidence(score) {
  if (score >= 75) return { label: 'High Confidence', icon: Flame, color: 'text-emerald-600 bg-emerald-50 border-emerald-200' };
  if (score >= 50) return { label: 'Emerging', icon: Zap, color: 'text-amber-600 bg-amber-50 border-amber-200' };
  return { label: 'Experimental', icon: Clock, color: 'text-slate-500 bg-slate-50 border-slate-200' };
}

export default function SeoTrendingPage() {
  const location = useLocation();
  const config = PAGE_CONFIG[location.pathname];
  const [data, setData] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!config) return;
    setLoading(true);
    Promise.all([
      fetch(`${API_URL}${config.endpoint}`).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/api/public/seo/all-categories`).then(r => r.ok ? r.json() : []),
    ]).then(([pageData, cats]) => {
      setData(pageData);
      setCategories(cats || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [location.pathname]);

  if (!config) return null;

  const PageIcon = config.icon;
  const siteUrl = typeof window !== 'undefined' ? window.location.origin : '';
  const products = data?.products || [];

  const breadcrumbLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: `${siteUrl}/` },
      { '@type': 'ListItem', position: 2, name: 'Trending Products', item: `${siteUrl}/trending-products` },
      { '@type': 'ListItem', position: 3, name: config.h1, item: `${siteUrl}${config.canonical}` },
    ],
  };

  const itemListLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: config.title,
    numberOfItems: products.length,
    itemListElement: products.slice(0, 20).map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      url: `${siteUrl}/trending/${p.slug}`,
      name: p.product_name,
    })),
  };

  return (
    <LandingLayout>
      <Helmet>
        <title>{`${config.title} - TrendScout`}</title>
        <meta name="description" content={config.description} />
        <meta property="og:title" content={`${config.title} - TrendScout`} />
        <meta property="og:description" content={config.description} />
        <link rel="canonical" href={`${siteUrl}${config.canonical}`} />
        <script type="application/ld+json">{JSON.stringify(breadcrumbLd)}</script>
        <script type="application/ld+json">{JSON.stringify(itemListLd)}</script>
      </Helmet>

      <div className="mx-auto max-w-6xl px-6 py-10" data-testid="seo-trending-page">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-slate-400 mb-8" data-testid="breadcrumb">
          <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
          <ChevronRight className="h-3 w-3" />
          <Link to="/trending-products" className="hover:text-indigo-600 transition-colors">Trending Products</Link>
          <ChevronRight className="h-3 w-3" />
          <span className="text-slate-600 font-medium">{config.h1}</span>
        </nav>

        {/* Hero */}
        <div className="text-center mb-10">
          <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${config.iconColor} flex items-center justify-center mx-auto mb-4 shadow-lg`}>
            <PageIcon className="h-7 w-7 text-white" />
          </div>
          <h1 className="font-manrope text-4xl sm:text-5xl font-extrabold text-slate-900" data-testid="seo-page-title">
            {config.h1}
          </h1>
          <p className="mt-3 text-slate-500 max-w-lg mx-auto text-base">
            {config.subtitle}
          </p>
          {data?.count != null && (
            <p className="mt-2 text-sm text-slate-400">{data.count} products found</p>
          )}
        </div>

        {/* Time-period navigation */}
        <div className="flex items-center justify-center gap-2 mb-8 flex-wrap" data-testid="period-nav">
          {Object.entries(PAGE_CONFIG).map(([path, cfg]) => (
            <Link
              key={path}
              to={path}
              className={`px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                location.pathname === path
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
              data-testid={`period-link-${path.replace(/\//g, '')}`}
            >
              {cfg.h1.replace('Trending Products ', '')}
            </Link>
          ))}
        </div>

        {/* Category quick links */}
        {categories.length > 0 && (
          <div className="mb-8">
            <h2 className="text-sm font-semibold text-slate-600 mb-3 text-center">Browse by Category</h2>
            <div className="flex items-center justify-center gap-2 flex-wrap" data-testid="category-links">
              {categories.slice(0, 12).map(cat => (
                <Link
                  key={cat.slug}
                  to={`/category/${cat.slug}`}
                  className="px-3 py-1.5 rounded-full text-xs font-medium bg-white text-slate-600 border border-slate-200 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 transition-all"
                  data-testid={`cat-link-${cat.slug}`}
                >
                  {cat.name} ({cat.count})
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Product grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-20">
            <Package className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 font-medium">No trending products found</p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="seo-product-grid">
            {products.map((product) => (
              <SeoProductCard key={product.id} product={product} />
            ))}
          </div>
        )}

        {/* Internal links footer */}
        <SeoInternalLinks currentPath={location.pathname} categories={categories} />

        {/* CTA */}
        <div className="text-center mt-12 py-8 bg-gradient-to-r from-indigo-50 to-violet-50 rounded-2xl">
          <h2 className="font-manrope text-xl font-bold text-slate-900 mb-2">Want deeper product intelligence?</h2>
          <p className="text-slate-500 text-sm mb-4 max-w-md mx-auto">
            Get AI-powered launch simulations, supplier intel, and ad creative generation for every product.
          </p>
          <Link
            to="/signup"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold px-6 py-2.5 rounded-xl hover:shadow-lg transition-shadow"
            data-testid="seo-cta-signup"
          >
            <Zap className="h-4 w-4" /> Start Free Trial
          </Link>
        </div>
      </div>
    </LandingLayout>
  );
}

function SeoProductCard({ product }) {
  const conf = getConfidence(product.launch_score);
  const CIcon = conf.icon;

  return (
    <Link
      to={`/trending/${product.slug}`}
      className="group block bg-white rounded-2xl border border-slate-100 overflow-hidden hover:border-slate-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5"
      data-testid={`seo-product-card-${product.id}`}
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
      </div>
      <div className="p-3.5">
        <h3 className="font-semibold text-slate-900 text-sm line-clamp-1 group-hover:text-indigo-600 transition-colors">
          {product.product_name}
        </h3>
        {product.category && (
          <p className="text-[11px] text-slate-400 mt-0.5">{product.category}</p>
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
            Details <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </div>
    </Link>
  );
}

export function SeoInternalLinks({ currentPath, categories = [] }) {
  const timePages = [
    { path: '/trending-products-today', label: 'Trending Today' },
    { path: '/trending-products-this-week', label: 'Trending This Week' },
    { path: '/trending-products-this-month', label: 'Trending This Month' },
    { path: '/top-trending-products', label: 'Top Trending Products' },
    { path: '/trending-products', label: 'All Trending Products' },
  ];

  return (
    <div className="mt-16 pt-8 border-t border-slate-200" data-testid="seo-internal-links">
      <h2 className="text-sm font-bold text-slate-700 mb-4">Explore More Trending Products</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">By Time Period</h3>
          <ul className="space-y-1.5">
            {timePages.filter(p => p.path !== currentPath).map(p => (
              <li key={p.path}>
                <Link to={p.path} className="text-sm text-indigo-600 hover:text-indigo-800 transition-colors flex items-center gap-1">
                  <ChevronRight className="h-3 w-3" />{p.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        {categories.length > 0 && (
          <div className="sm:col-span-2">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">By Category</h3>
            <div className="flex flex-wrap gap-2">
              {categories.slice(0, 15).map(cat => (
                <Link
                  key={cat.slug}
                  to={`/category/${cat.slug}`}
                  className="text-sm text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-3 py-1 rounded-full transition-all"
                >
                  {cat.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
