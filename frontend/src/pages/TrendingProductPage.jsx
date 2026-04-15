import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { SignupGate } from '@/components/SignupGate';
import {
  TrendingUp, ArrowRight, Package, Radar, Lock, ArrowLeft,
  BarChart3, Eye, DollarSign, Truck, ShieldCheck, Loader2,
  ChevronLeft, ChevronRight, Flame, Zap, Clock, ZoomIn, Tag,
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

export default function TrendingProductPage() {
  const { slug } = useParams();
  const { isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!slug) return;
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/public/trending/${slug}`);
        if (res.ok) {
          const data = await res.json(); setProduct(data.product || data);
        } else {
          setNotFound(true);
        }
      } catch { setNotFound(true); }
      setLoading(false);
    })();
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (notFound || !product) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 flex flex-col items-center justify-center text-white">
        <Package className="h-16 w-16 text-slate-600 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Product not found</h1>
        <p className="text-slate-400 mb-6">This product may no longer be trending.</p>
        <Link to="/trending-products">
          <Button className="bg-indigo-600 hover:bg-indigo-700">
            <ArrowLeft className="mr-2 h-4 w-4" /> Browse trending products
          </Button>
        </Link>
      </div>
    );
  }

  const siteUrl = typeof window !== 'undefined' ? window.location.origin : '';
  const stageClass = STAGE_COLORS[product.trend_stage] || STAGE_COLORS.Unknown;
  const hasImage = product.image_url && !product.image_url.includes('01jrA-8DXYL');
  const seoTitle = `${product.product_name} — Trending Product Analysis | TrendScout`;
  const seoDesc = `${product.product_name} has a TrendScout Launch Score of ${product.launch_score}. Trend stage: ${product.trend_stage}. Estimated margin: ${product.margin_percent}%.`;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.product_name,
    description: seoDesc,
    image: product.image_url,
    url: `${siteUrl}/trending/${slug}`,
    category: product.category,
    offers: product.estimated_retail_price > 0 ? {
      '@type': 'Offer',
      price: product.estimated_retail_price,
      priceCurrency: 'GBP',
      availability: 'https://schema.org/InStock',
    } : undefined,
  };

  const breadcrumbLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: `${siteUrl}/` },
      { '@type': 'ListItem', position: 2, name: 'Trending Products', item: `${siteUrl}/trending-products` },
      ...(product.category ? [{ '@type': 'ListItem', position: 3, name: product.category, item: `${siteUrl}/category/${encodeURIComponent(product.category.toLowerCase().replace(/\s+/g, '-'))}` }] : []),
      { '@type': 'ListItem', position: product.category ? 4 : 3, name: product.product_name, item: `${siteUrl}/trending/${slug}` },
    ],
  };

  const confidenceLabel = product.launch_score >= 75 ? 'High Confidence' : product.launch_score >= 50 ? 'Emerging Opportunity' : 'Experimental';

  const faqLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: `What is the TrendScout score for ${product.product_name}?`,
        acceptedAnswer: { '@type': 'Answer', text: `${product.product_name} has a TrendScout Launch Score of ${product.launch_score}/100, placing it in the ${product.trend_stage} stage.` },
      },
      {
        '@type': 'Question',
        name: `What is the profit margin for ${product.product_name}?`,
        acceptedAnswer: { '@type': 'Answer', text: `The estimated profit margin is ${product.margin_percent}%. Supplier cost is £${product.supplier_cost} with an estimated retail price of £${product.estimated_retail_price}.` },
      },
      {
        '@type': 'Question',
        name: `Is ${product.product_name} a good product to sell?`,
        acceptedAnswer: { '@type': 'Answer', text: `With a Launch Score of ${product.launch_score}/100${product.success_probability > 0 ? ` and a ${product.success_probability}% success probability` : ''}, ${product.product_name} is rated as "${confidenceLabel}" by our AI analysis.` },
      },
    ],
  };
  const confidenceColor = product.launch_score >= 75 ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : product.launch_score >= 50 ? 'text-amber-400 bg-amber-500/10 border-amber-500/20' : 'text-slate-400 bg-slate-500/10 border-slate-500/20';
  const CIcon = product.launch_score >= 75 ? Flame : product.launch_score >= 50 ? Zap : Clock;

  // Build gallery from all available images
  const allImages = [];
  if (hasImage) allImages.push(product.image_url);
  if (product.gallery_images) {
    product.gallery_images.forEach(url => {
      if (url && !allImages.includes(url)) allImages.push(url);
    });
  }

  return (
    <>
      <Helmet>
        <title>{seoTitle}</title>
        <meta name="description" content={seoDesc} />
        <meta property="og:title" content={seoTitle} />
        <meta property="og:description" content={seoDesc} />
        <meta property="og:type" content="product" />
        <meta property="og:url" content={`${siteUrl}/trending/${slug}`} />
        {product.image_url && <meta property="og:image" content={product.image_url} />}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={seoTitle} />
        <meta name="twitter:description" content={seoDesc} />
        <link rel="canonical" href={`${siteUrl}/trending/${slug}`} />
        <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
        <script type="application/ld+json">{JSON.stringify(breadcrumbLd)}</script>
        <script type="application/ld+json">{JSON.stringify(faqLd)}</script>
      </Helmet>

      <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" data-testid="trending-product-page">
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
              <Link to="/trending-products">
                <Button variant="ghost" className="text-slate-400 hover:text-white text-sm">
                  <ArrowLeft className="mr-1 h-4 w-4" /> All Trending
                </Button>
              </Link>
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-sm" data-testid="nav-signup-btn">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </nav>

        {/* Content */}
        <div className="mx-auto max-w-5xl px-6 py-12">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-slate-500 mb-8" data-testid="breadcrumb">
            <Link to="/" className="hover:text-indigo-400 transition-colors">Home</Link>
            <span className="text-slate-600">/</span>
            <Link to="/trending-products" className="hover:text-indigo-400 transition-colors">Trending Products</Link>
            {product.category && (
              <>
                <span className="text-slate-600">/</span>
                <Link to={`/category/${encodeURIComponent(product.category.toLowerCase().replace(/\s+/g, '-'))}`} className="hover:text-indigo-400 transition-colors">
                  {product.category}
                </Link>
              </>
            )}
            <span className="text-slate-600">/</span>
            <span className="text-slate-400 truncate max-w-[300px]">{product.product_name}</span>
          </nav>

          <div className="grid lg:grid-cols-5 gap-8">
            {/* Left: Image Gallery + Score */}
            <div className="lg:col-span-2 space-y-4">
              <ImageGallery images={allImages} productName={product.product_name} radarDetected={product.radar_detected} />

              {/* Confidence Badge */}
              <div className="bg-white/[0.04] border border-white/[0.06] rounded-2xl p-4 flex items-center gap-3">
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm font-medium ${confidenceColor}`}>
                  <CIcon className="h-4 w-4" />
                  {confidenceLabel}
                </div>
                <span className="text-xs text-slate-500">Based on multi-signal AI analysis</span>
              </div>

              {/* Score Circle */}
              <div className="bg-white/[0.04] border border-white/[0.06] rounded-2xl p-6 text-center" data-testid="score-card">
                <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-indigo-600/20 to-violet-600/20 border-2 border-indigo-500/30 mb-3">
                  <span className="font-mono text-4xl font-black text-indigo-400">{product.launch_score}</span>
                </div>
                <p className="text-sm font-semibold text-white">Launch Score</p>
                <p className="text-xs text-slate-500 mt-1">AI-calculated product viability</p>
              </div>
            </div>

            {/* Right: Details */}
            <div className="lg:col-span-3 space-y-5">
              {/* Title */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Badge className={`text-xs border rounded-full ${stageClass}`}>
                    {product.trend_stage}
                  </Badge>
                  {product.category && (
                    <Link to={`/trending-products?category=${encodeURIComponent(product.category)}`}>
                      <Badge variant="outline" className="text-xs text-slate-400 border-slate-700 hover:border-indigo-500/50 hover:text-indigo-400 cursor-pointer transition-colors">
                        {product.category}
                      </Badge>
                    </Link>
                  )}
                  <Badge variant="outline" className="text-xs text-slate-500 border-slate-700">
                    {product.data_confidence}
                  </Badge>
                </div>
                <h1 className="text-2xl sm:text-3xl font-bold text-white leading-tight" data-testid="product-title">
                  {product.product_name}
                </h1>
              </div>

              {/* Key Metrics Grid */}
              {isAuthenticated ? (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3" data-testid="metrics-grid">
                <MetricCard icon={BarChart3} label="Launch Score" value={product.launch_score} color="indigo" />
                <MetricCard icon={TrendingUp} label="Margin" value={`${product.margin_percent}%`} color="emerald" />
                <MetricCard icon={DollarSign} label="Est. Retail" value={product.estimated_retail_price > 0 ? `£${product.estimated_retail_price}` : '—'} color="amber" />
                <MetricCard icon={Truck} label="Supplier Cost" value={product.supplier_cost > 0 ? `£${product.supplier_cost}` : '—'} color="blue" />
              </div>
              ) : (
              <div className="relative">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 filter blur-md pointer-events-none select-none" aria-hidden="true">
                  <MetricCard icon={BarChart3} label="Launch Score" value="??" color="indigo" />
                  <MetricCard icon={TrendingUp} label="Margin" value="??%" color="emerald" />
                  <MetricCard icon={DollarSign} label="Est. Retail" value="£??" color="amber" />
                  <MetricCard icon={Truck} label="Supplier Cost" value="£??" color="blue" />
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <Link to="/signup" className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-5 py-2.5 rounded-xl text-sm transition-colors" data-testid="metrics-gate-btn">
                    <Lock className="h-4 w-4" /> Sign up to reveal scores
                  </Link>
                </div>
              </div>
              )}

              {/* Product Overview */}
              {isAuthenticated ? (
              <>
              <Card className="bg-white/[0.04] border-white/[0.06]" data-testid="overview-card">
                <CardContent className="p-5">
                  <h2 className="font-semibold text-white text-sm mb-3 flex items-center gap-2">
                    <Eye className="h-4 w-4 text-indigo-400" />
                    Product Overview
                  </h2>
                  <div className="space-y-3 text-sm text-slate-400">
                    <p>
                      <span className="font-semibold text-white">{product.product_name}</span> is currently in the{' '}
                      <span className="font-semibold text-indigo-400">{product.trend_stage}</span> stage with a TrendScout
                      Launch Score of <span className="font-semibold text-white">{product.launch_score}/100</span>.
                    </p>
                    {product.success_probability > 0 && (
                      <p>
                        Our AI estimates a <span className="font-semibold text-emerald-400">{product.success_probability}% success probability</span> based
                        on current market signals.
                      </p>
                    )}
                    {product.margin_percent > 0 && (
                      <p>
                        With an estimated margin of <span className="font-semibold text-emerald-400">{product.margin_percent}%</span>,
                        this product shows strong profitability potential for dropshipping.
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Market Opportunity */}
              <Card className="bg-white/[0.04] border-white/[0.06]" data-testid="market-opportunity-card">
                <CardContent className="p-5">
                  <h2 className="font-semibold text-white text-sm mb-3 flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-emerald-400" />
                    Market Opportunity
                  </h2>
                  <div className="space-y-3 text-sm text-slate-400">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-white/[0.04] rounded-lg p-3">
                        <p className="text-xs text-slate-500">Supplier Cost</p>
                        <p className="text-lg font-bold text-white">{product.supplier_cost > 0 ? `£${product.supplier_cost}` : '—'}</p>
                      </div>
                      <div className="bg-white/[0.04] rounded-lg p-3">
                        <p className="text-xs text-slate-500">Est. Retail Price</p>
                        <p className="text-lg font-bold text-white">{product.estimated_retail_price > 0 ? `£${product.estimated_retail_price}` : '—'}</p>
                      </div>
                    </div>
                    {product.margin_percent > 0 && (
                      <p>
                        With a <span className="font-semibold text-emerald-400">{product.margin_percent}% profit margin</span>,
                        sellers can expect approximately <span className="text-white font-semibold">
                        £{(product.estimated_retail_price - product.supplier_cost).toFixed(2)}
                        </span> profit per unit sold.
                      </p>
                    )}
                    {product.growth_rate > 0 && (
                      <p>
                        Currently showing <span className="text-amber-400 font-semibold">{product.growth_rate}% growth</span>,
                        indicating strong market demand and trending momentum.
                      </p>
                    )}
                    {product.tiktok_views > 0 && (
                      <p>
                        This product has accumulated <span className="text-rose-400 font-semibold">
                        {product.tiktok_views >= 1e6 ? `${(product.tiktok_views / 1e6).toFixed(1)}M` : product.tiktok_views >= 1e3 ? `${(product.tiktok_views / 1e3).toFixed(0)}K` : product.tiktok_views}
                        </span> TikTok views, demonstrating viral potential and social proof.
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Locked CTA */}
              </>
              ) : (
              <Card className="bg-white/[0.04] border-white/[0.06]">
                <CardContent className="p-6 text-center">
                  <Lock className="h-8 w-8 text-indigo-400 mx-auto mb-3" />
                  <h3 className="font-bold text-white text-lg mb-2">Full analysis behind login</h3>
                  <p className="text-sm text-slate-400 mb-4 max-w-md mx-auto">
                    Sign up to see detailed scores, profit margins, supplier costs, AI ad creatives, and the complete launch assessment.
                  </p>
                  <div className="flex flex-col sm:flex-row justify-center gap-3">
                    <Link to="/signup">
                      <Button className="bg-indigo-600 hover:bg-indigo-700 gap-2" data-testid="gate-signup-btn">
                        <Radar className="h-4 w-4" /> Start Free Trial
                      </Button>
                    </Link>
                    <Link to="/login">
                      <Button variant="ghost" className="text-slate-400 hover:text-white">Log in</Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
              )}
              {isAuthenticated && (
              <div className="bg-gradient-to-r from-indigo-600/20 to-violet-600/20 border border-indigo-500/20 rounded-2xl p-6" data-testid="unlock-cta">
                <div className="flex items-start gap-3">
                  <Lock className="h-6 w-6 text-indigo-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="font-bold text-white text-lg mb-1">Unlock full analysis with TrendScout</h3>
                    <p className="text-sm text-slate-400 mb-4">
                      Get detailed supplier intelligence, AI-generated ad creatives, launch simulator,
                      and the full scoring breakdown.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-3">
                      <Link to="/signup">
                        <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="signup-cta-btn">
                          <Radar className="mr-2 h-4 w-4" />
                          Start with TrendScout — £19/mo
                        </Button>
                      </Link>
                      <Link to="/login">
                        <Button variant="ghost" className="text-slate-400 hover:text-white">
                          Already have an account? Log in
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
              )}
            </div>
          </div>

          {/* Related Products */}
          {product.related_products?.length > 0 && (
            <div className="mt-16" data-testid="related-products">
              <h2 className="font-bold text-white text-lg mb-6">Related Trending Products</h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {product.related_products.map((r, i) => (
                  <Link
                    key={r.id}
                    to={`/trending/${r.slug}`}
                    className="group bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.06] hover:border-indigo-500/30 rounded-xl p-4 transition-all"
                    data-testid={`related-${i}`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
                        {r.image_url && !r.image_url.includes('01jrA-8DXYL') ? (
                          <img src={r.image_url} alt="" className="w-full h-full rounded-lg object-contain"  loading="lazy" />
                        ) : (
                          <Package className="h-5 w-5 text-slate-600" />
                        )}
                      </div>
                      <div className="font-mono text-lg font-bold text-indigo-400">{r.launch_score}</div>
                    </div>
                    <h3 className="font-medium text-white text-sm line-clamp-2 group-hover:text-indigo-300 transition-colors">
                      {r.product_name}
                    </h3>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge className={`text-[9px] border rounded-full ${STAGE_COLORS[r.trend_stage] || STAGE_COLORS.Unknown}`}>
                        {r.trend_stage}
                      </Badge>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Internal SEO Links */}
        <div className="mx-auto max-w-5xl px-6 mt-16 pt-8 border-t border-white/5" data-testid="seo-internal-links">
          <h2 className="font-semibold text-white text-sm mb-4">Explore More Trending Products</h2>
          <div className="grid sm:grid-cols-3 gap-6">
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">By Time Period</h3>
              <ul className="space-y-1.5">
                <li><Link to="/trending-products-today" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Trending Today</Link></li>
                <li><Link to="/trending-products-this-week" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Trending This Week</Link></li>
                <li><Link to="/trending-products-this-month" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Trending This Month</Link></li>
                <li><Link to="/top-trending-products" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Top Trending Leaderboard</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Popular Categories</h3>
              <ul className="space-y-1.5">
                {['beauty', 'health', 'home', 'electronics', 'fashion'].map(cat => (
                  <li key={cat}>
                    <Link to={`/category/${cat}`} className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors capitalize">
                      {cat} Products
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Resources</h3>
              <ul className="space-y-1.5">
                <li><Link to="/trending-products" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">All Trending Products</Link></li>
                <li><Link to="/blog" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Blog</Link></li>
                <li><Link to="/tools" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Free Tools</Link></li>
                <li><Link to="/pricing" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Pricing</Link></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="border-t border-white/5 py-8 mt-12">
          <div className="mx-auto max-w-7xl px-6 flex items-center justify-between">
            <p className="text-sm text-slate-500">TrendScout — AI-powered product intelligence</p>
            <div className="flex items-center gap-4 text-sm text-slate-500">
              <Link to="/trending-products" className="hover:text-white transition-colors">Trending</Link>
              <Link to="/pricing" className="hover:text-white transition-colors">Pricing</Link>
              <Link to="/" className="hover:text-white transition-colors">Home</Link>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}

function MetricCard({ icon: Icon, label, value, color }) {
  const colors = {
    indigo: 'text-indigo-400 bg-indigo-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
    blue: 'text-blue-400 bg-blue-500/10',
  };
  const cls = colors[color] || colors.indigo;

  return (
    <div className="bg-white/[0.04] border border-white/[0.06] rounded-xl p-3 text-center">
      <div className={`inline-flex items-center justify-center w-8 h-8 rounded-lg ${cls} mb-1.5`}>
        <Icon className="h-4 w-4" />
      </div>
      <p className="font-mono text-lg font-bold text-white">{value}</p>
      <p className="text-[10px] text-slate-500">{label}</p>
    </div>
  );
}


/* ── Image Gallery with carousel + zoom ── */
function ImageGallery({ images, productName, radarDetected }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [zoomed, setZoomed] = useState(false);
  const hasMultiple = images.length > 1;
  const currentImage = images[currentIdx] || null;

  const next = (e) => { e.stopPropagation(); setCurrentIdx((i) => (i + 1) % images.length); };
  const prev = (e) => { e.stopPropagation(); setCurrentIdx((i) => (i - 1 + images.length) % images.length); };

  return (
    <>
      <div className="bg-white/[0.04] border border-white/[0.06] rounded-2xl overflow-hidden" data-testid="product-image-card">
        {/* Main Image */}
        <div
          className="aspect-square bg-gradient-to-br from-slate-800 to-slate-900 relative group cursor-pointer overflow-hidden"
          onClick={() => currentImage && setZoomed(true)}
        >
          {currentImage ? (
            <img
              src={currentImage}
              alt={productName}
              className="w-full h-full object-contain p-6 group-hover:scale-110 transition-transform duration-500"
             loading="lazy" />
          ) : (
            <div className="flex items-center justify-center h-full">
              <Package className="h-20 w-20 text-slate-700" />
            </div>
          )}

          {/* Radar badge */}
          {radarDetected && (
            <div className="absolute top-3 left-3 flex items-center gap-1 bg-indigo-600/90 backdrop-blur-sm rounded-full px-2.5 py-1">
              <Radar className="h-3 w-3 text-white" />
              <span className="text-xs text-white font-medium">Radar Detected</span>
            </div>
          )}

          {/* Zoom hint */}
          {currentImage && (
            <div className="absolute bottom-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity bg-black/50 backdrop-blur-sm rounded-full p-2">
              <ZoomIn className="h-4 w-4 text-white" />
            </div>
          )}

          {/* Carousel arrows */}
          {hasMultiple && (
            <>
              <button onClick={prev} className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/40 backdrop-blur-sm hover:bg-black/60 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity" data-testid="gallery-prev">
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button onClick={next} className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/40 backdrop-blur-sm hover:bg-black/60 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity" data-testid="gallery-next">
                <ChevronRight className="h-4 w-4" />
              </button>
            </>
          )}
        </div>

        {/* Thumbnail strip */}
        {hasMultiple && (
          <div className="flex gap-1 p-2 overflow-x-auto scrollbar-hide" data-testid="gallery-thumbs">
            {images.map((url, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentIdx(idx)}
                className={`flex-shrink-0 w-14 h-14 rounded-lg overflow-hidden border-2 transition-all ${
                  idx === currentIdx ? 'border-indigo-500 opacity-100' : 'border-transparent opacity-50 hover:opacity-80'
                }`}
              >
                <img src={url} alt="" className="w-full h-full object-cover"  loading="lazy" />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Full-screen zoom modal */}
      {zoomed && currentImage && (
        <div
          className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-md flex items-center justify-center cursor-zoom-out"
          onClick={() => setZoomed(false)}
          data-testid="zoom-modal"
        >
          <img
            src={currentImage}
            alt={productName}
            className="max-w-[90vw] max-h-[90vh] object-contain rounded-lg"
           loading="lazy" />
          <button
            onClick={() => setZoomed(false)}
            className="absolute top-6 right-6 text-white/70 hover:text-white text-2xl font-light"
          >
            &times;
          </button>
          {hasMultiple && (
            <>
              <button onClick={prev} className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/10 hover:bg-white/20 text-white rounded-full p-3"><ChevronLeft className="h-6 w-6" /></button>
              <button onClick={next} className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/10 hover:bg-white/20 text-white rounded-full p-3"><ChevronRight className="h-6 w-6" /></button>
            </>
          )}
          {/* Dots */}
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2">
            {images.map((_, idx) => (
              <button
                key={idx}
                onClick={(e) => { e.stopPropagation(); setCurrentIdx(idx); }}
                className={`w-2 h-2 rounded-full transition-all ${idx === currentIdx ? 'bg-white w-6' : 'bg-white/30 hover:bg-white/50'}`}
              />
            ))}
          </div>
        </div>
      )}
    </>
  );
}
