import React, { useState, useEffect, useMemo } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, ArrowRight, Package, Zap, Radar, Lock,
  Sparkles, BarChart3, Eye, Flame, Clock, Search, ChevronRight,
  ArrowUpDown, Filter, SlidersHorizontal, ChevronDown,
  ArrowLeftRight, X, Truck,
} from 'lucide-react';
import { API_URL } from '@/lib/config';
import { SignupGate } from '@/components/SignupGate';
import DailyPicksSection from '@/components/common/DailyPicksSection';

const STAGE_COLORS = {
  Exploding: 'bg-red-500/10 text-red-600 border-red-200',
  Rising: 'bg-amber-500/10 text-amber-600 border-amber-200',
  Emerging: 'bg-sky-500/10 text-sky-600 border-sky-200',
  early_trend: 'bg-violet-500/10 text-violet-600 border-violet-200',
  Stable: 'bg-slate-100 text-slate-600 border-slate-200',
  Unknown: 'bg-slate-100 text-slate-600 border-slate-200',
};

const SORT_OPTIONS = [
  { label: 'Highest Score', value: 'score_desc' },
  { label: 'Fastest Growing', value: 'growth_desc' },
  { label: 'Highest Margin', value: 'margin_desc' },
  { label: 'Newest Trends', value: 'newest' },
  { label: 'Lowest Supplier Cost', value: 'cost_asc' },
];

function getConfidence(score) {
  if (score >= 75) return { label: 'High Confidence', icon: Flame, color: 'text-emerald-600 bg-emerald-50 border-emerald-200' };
  if (score >= 50) return { label: 'Emerging Opportunity', icon: Zap, color: 'text-amber-600 bg-amber-50 border-amber-200' };
  return { label: 'Experimental', icon: Clock, color: 'text-slate-500 bg-slate-50 border-slate-200' };
}

export default function TrendingProductsPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [weekCount, setWeekCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [sortBy, setSortBy] = useState('score_desc');
  const [minMargin, setMinMargin] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [searchParams] = useSearchParams();
  const [compareIds, setCompareIds] = useState([]);

  const toggleCompare = (id) => {
    setCompareIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : prev.length < 4 ? [...prev, id] : prev
    );
  };

  useEffect(() => {
    const catParam = searchParams.get('category');
    if (catParam) setSelectedCategory(catParam);
  }, [searchParams]);

  useEffect(() => {
    (async () => {
      try {
        const [prodRes, catRes] = await Promise.all([
          fetch(`${API_URL}/api/public/trending-products?limit=50`),
          fetch(`${API_URL}/api/public/categories`),
        ]);
        if (prodRes.ok) {
          const data = await prodRes.json();
          setProducts(data.products || []);
          setWeekCount(data.detected_this_week || 0);
        }
        if (catRes.ok) {
          setCategories([]); /* categories derived from products after load */;
        }
      } catch (e) { console.error(e); }
      setLoading(false);
    })();
  }, []);

  const filteredAndSorted = useMemo(() => {
    let result = [...products];

    // Category filter
    if (selectedCategory) {
      result = result.filter(p => p.category === selectedCategory);
    }

    // Margin filter
    if (minMargin > 0) {
      result = result.filter(p => (p.margin_percent || 0) >= minMargin);
    }

    // Sorting
    switch (sortBy) {
      case 'score_desc':
        result.sort((a, b) => (b.launch_score || 0) - (a.launch_score || 0));
        break;
      case 'growth_desc':
        result.sort((a, b) => (b.growth_rate || 0) - (a.growth_rate || 0));
        break;
      case 'margin_desc':
        result.sort((a, b) => (b.margin_percent || 0) - (a.margin_percent || 0));
        break;
      case 'newest':
        result.sort((a, b) => new Date(b.detected_at || 0) - new Date(a.detected_at || 0));
        break;
      case 'cost_asc':
        result.sort((a, b) => (a.supplier_cost || 999) - (b.supplier_cost || 999));
        break;
      default:
        break;
    }

    return result;
  }, [products, selectedCategory, sortBy, minMargin]);

  const highConfCount = products.filter(p => p.launch_score >= 65).length;

  return (
    <div className="min-h-screen bg-[#FAFBFC]">
      <Helmet>

                // Derive categories from actual loaded products so counts match what's filterable
                const derivedCategories = useMemo(() => {
                            const catMap = {};
                  products.forEach(p => {
                                if (p.category) {
                                                catMap[p.category] = (catMap[p.category] || 0) + 1;
        }
        });
                  return Object.entries(catMap).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
        }, [products]);
        <title>Trending Products — Discover Winning Products Before They Go Viral | TrendScout</title>
        <meta name="description" content="Browse trending ecommerce products detected by TrendScout AI. Find high-margin opportunities before they go viral on TikTok and Amazon." />
        <meta property="og:title" content="Trending Products — TrendScout" />
        <meta property="og:description" content="Discover winning products before they go viral. Real-time trend intelligence for ecommerce sellers." />
        <link rel="canonical" href="https://trendscout.click/trending-products" />
      </Helmet>

      {/* Header */}
      <header className="bg-[#030712] text-white">
        <div className="mx-auto max-w-7xl px-6 pt-24 pb-12 lg:px-8">
          <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-white mb-6 transition-colors">
            <TrendingUp className="h-4 w-4" /> TrendScout
          </Link>
          <h1 className="font-manrope text-3xl font-extrabold sm:text-4xl" data-testid="page-title">
            Trending Products
          </h1>
          <p className="mt-3 text-slate-400 text-base max-w-xl">
            Products detected with early growth signals. Updated daily from TikTok, Amazon, and social media.
          </p>
          <div className="flex items-center gap-6 mt-6 text-sm">
            <span className="text-slate-400"><strong className="text-white">{products.length}</strong> products tracked</span>
            <span className="text-slate-400"><strong className="text-emerald-400">{highConfCount}</strong> high confidence</span>
            <span className="text-slate-400"><strong className="text-amber-400">{weekCount}</strong> detected this week</span>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 lg:px-8 py-8">
        {/* Toolbar: Categories + Sort + Filters */}
        <div className="flex flex-col gap-4 mb-6">
          {/* Category pills */}
          {derivedCategories.length > 0 && (
            <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide" data-testid="category-filter">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${
                  !selectedCategory
                    ? 'bg-slate-900 text-white border-slate-900'
                    : 'bg-white text-slate-600 hover:bg-slate-50 border-slate-200'
                }`}
                data-testid="category-all"
              >
                All ({products.length})
              </button>
              {derivedCategories.map(cat => (
                <button
                  key={cat.name}
                  onClick={() => setSelectedCategory(cat.name === selectedCategory ? null : cat.name)}
                  className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${
                    selectedCategory === cat.name
                      ? 'bg-slate-900 text-white border-slate-900'
                      : 'bg-white text-slate-600 hover:bg-slate-50 border-slate-200'
                  }`}
                  data-testid={`category-${cat.slug}`}
                >
                  {cat.name} ({cat.count})
                </button>
              ))}
            </div>
          )}

          {/* Sort & Filter bar */}
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                  showFilters ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                }`}
                data-testid="toggle-filters"
              >
                <SlidersHorizontal className="h-3.5 w-3.5" />
                Filters
              </button>
              {minMargin > 0 && (
                <Badge variant="outline" className="text-xs bg-emerald-50 text-emerald-700 border-emerald-200 rounded-full">
                  Margin &ge; {minMargin}%
                  <button onClick={() => setMinMargin(0)} className="ml-1 hover:text-red-500">&times;</button>
                </Badge>
              )}
            </div>

            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="appearance-none bg-white border border-slate-200 rounded-lg px-3 py-1.5 pr-8 text-xs font-medium text-slate-700 cursor-pointer hover:border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                data-testid="sort-select"
              >
                {SORT_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
            </div>
          </div>

          {/* Expanded filters */}
          {showFilters && (
            <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-wrap items-center gap-4" data-testid="filter-panel">
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Min Profit Margin</label>
                <div className="flex items-center gap-2">
                  {[0, 30, 50, 60, 70].map(v => (
                    <button
                      key={v}
                      onClick={() => setMinMargin(v)}
                      className={`px-2.5 py-1 rounded-md text-xs font-medium border transition-all ${
                        minMargin === v ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      {v === 0 ? 'Any' : `${v}%+`}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Daily Picks */}
        {!selectedCategory && minMargin === 0 && !loading && (
          <DailyPicksSection />
        )}

        {/* Results count */}
        <p className="text-xs text-slate-500 mb-4" data-testid="results-count">
          Showing {filteredAndSorted.length} product{filteredAndSorted.length !== 1 ? 's' : ''}
          {selectedCategory && <> in <strong>{selectedCategory}</strong></>}
          {minMargin > 0 && <> with {minMargin}%+ margin</>}
        </p>

        {/* Product Grid */}
        {loading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="bg-white rounded-2xl border border-slate-100 overflow-hidden animate-pulse">
                <div className="h-40 bg-slate-100" />
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-slate-100 rounded w-3/4" />
                  <div className="h-3 bg-slate-100 rounded w-1/2" />
                  <div className="grid grid-cols-3 gap-2 pt-2">
                    <div className="h-10 bg-slate-50 rounded-lg" />
                    <div className="h-10 bg-slate-50 rounded-lg" />
                    <div className="h-10 bg-slate-50 rounded-lg" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : filteredAndSorted.length === 0 && products.length === 0 ? (
          <div className="text-center py-20">
            <Package className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 font-medium">Products are being loaded</p>
            <p className="text-slate-400 text-sm mt-1">Our system is refreshing product data. Check back in a few minutes.</p>
            <button onClick={() => window.location.reload()} className="text-indigo-600 text-sm font-medium mt-3 hover:underline">
              Refresh page
            </button>
          </div>
        ) : filteredAndSorted.length === 0 ? (
          <div className="text-center py-20">
            <Package className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 font-medium">No products match your filters</p>
            <button onClick={() => { setSelectedCategory(null); setMinMargin(0); }} className="text-indigo-600 text-sm font-medium mt-2 hover:underline">
              Clear all filters
            </button>
          </div>
        ) : (
          <>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4" data-testid="product-grid">
              {(isAuthenticated ? filteredAndSorted : filteredAndSorted.slice(0, 3)).map((product) => (
                <ProductCard key={product.id} product={product} compareIds={compareIds} toggleCompare={toggleCompare} />
              ))}
            </div>
            {!isAuthenticated && filteredAndSorted.length > 3 && (
              <SignupGate
                title={`${filteredAndSorted.length - 3} more products available`}
                description="Create a free account to see all products with launch scores, profit margins, and supplier costs."
              />
            )}
          </>
        )}

        {/* CTA */}
        <div className="text-center mt-16 mb-8">
          <div className="bg-white border border-slate-200 rounded-2xl p-8 max-w-lg mx-auto">
            <Sparkles className="h-8 w-8 text-indigo-500 mx-auto mb-3" />
            <h3 className="font-manrope text-xl font-bold text-slate-900">Want full product intelligence?</h3>
            <p className="mt-2 text-sm text-slate-500">Get supplier data, ad insights, and launch tools with a TrendScout account.</p>
            <Link to="/signup">
              <Button className="mt-5 bg-slate-900 hover:bg-slate-800 rounded-xl font-semibold" data-testid="cta-signup-btn">
                Validate Your First Product <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Floating Compare Bar */}
      {compareIds.length >= 2 && (
        <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-slate-200 shadow-[0_-4px_20px_rgba(0,0,0,0.08)] p-3" data-testid="compare-bar">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ArrowLeftRight className="h-5 w-5 text-indigo-500" />
              <span className="text-sm font-medium text-slate-900">{compareIds.length} products selected</span>
              <div className="flex items-center gap-1">
                {compareIds.map(id => {
                  const p = products.find(x => x.id === id);
                  return (
                    <Badge key={id} variant="outline" className="text-[10px] pl-2 pr-1 gap-1 max-w-[120px]">
                      <span className="truncate">{p?.product_name?.substring(0, 15) || id.slice(0, 8)}</span>
                      <button onClick={(e) => { e.stopPropagation(); toggleCompare(id); }} className="hover:text-red-500 ml-0.5">
                        <X className="h-2.5 w-2.5" />
                      </button>
                    </Badge>
                  );
                })}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCompareIds([])}
                className="text-xs"
                data-testid="clear-compare"
              >
                Clear
              </Button>
              <Button
                size="sm"
                className="bg-indigo-600 hover:bg-indigo-700"
                onClick={() => navigate(`/compare?ids=${compareIds.join(',')}`)}
                data-testid="compare-now-btn"
              >
                <ArrowLeftRight className="h-3.5 w-3.5 mr-1.5" />
                Compare Now
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Enhanced Product Card ── */
function ProductCard({ product, compareIds = [], toggleCompare }) {
  const conf = getConfidence(product.launch_score);
  const CIcon = conf.icon;
  const isSelected = compareIds.includes(product.id);

  return (
    <div className="relative group" data-testid={`product-card-${product.id}`}>
      {/* Compare checkbox */}
      {toggleCompare && (
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggleCompare(product.id); }}
          className={`absolute top-2 right-2 z-10 w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all ${
            isSelected
              ? 'bg-indigo-600 border-indigo-600 text-white shadow-md'
              : 'bg-white/80 border-slate-300 opacity-0 group-hover:opacity-100 hover:border-indigo-400'
          }`}
          data-testid={`compare-check-${product.id}`}
          title={isSelected ? 'Remove from comparison' : 'Add to comparison'}
        >
          {isSelected && <ArrowLeftRight className="h-3 w-3" />}
        </button>
      )}
      <Link
        to={`/trending/${product.slug}`}
        className={`block bg-white rounded-2xl border overflow-hidden hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5 ${
          isSelected ? 'border-indigo-300 ring-2 ring-indigo-100' : 'border-slate-100 hover:border-slate-200'
        }`}
      >
      {/* Image */}
      <div className="relative h-36 bg-gradient-to-br from-slate-50 to-slate-100 overflow-hidden">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Package className="h-10 w-10 text-slate-200" />
          </div>
        )}
        {/* Score badge */}
        <div className="absolute top-2.5 left-2.5 bg-white/95 backdrop-blur-sm rounded-lg px-2 py-1 shadow-sm">
          <span className="font-mono text-sm font-bold text-indigo-600">{product.launch_score}</span>
        </div>
        {/* Confidence badge */}
        <div className="absolute top-2.5 right-2.5">
          <Badge className={`text-[10px] border rounded-full ${conf.color} shadow-sm`}>
            <CIcon className="h-3 w-3 mr-0.5" />
            {conf.label}
          </Badge>
        </div>
        {/* Stage */}
        {product.trend_stage && (
          <div className="absolute bottom-2.5 left-2.5">
            <Badge className={`text-[10px] border rounded-full ${STAGE_COLORS[product.trend_stage] || STAGE_COLORS.Unknown}`}>
              {product.trend_stage}
            </Badge>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-3.5">
        <h3 className="font-semibold text-slate-900 text-sm line-clamp-1 group-hover:text-indigo-600 transition-colors">{product.product_name}</h3>
        {product.category && (
          <p className="text-[11px] text-slate-400 mt-0.5">{product.category}</p>
        )}

        {/* Key metrics */}
        <div className="grid grid-cols-3 gap-1.5 mt-3">
          <MetricCell label="Margin" value={`${product.margin_percent || 0}%`} highlight />
          <MetricCell label="Supplier" value={`£${(product.supplier_cost || 0).toFixed(0)}`} />
          <MetricCell label="Retail" value={`£${(product.retail_price || 0).toFixed(0)}`} />
        </div>

        {/* UK Shipping */}
        {product.uk_shipping && (
          <div className="flex items-center gap-1.5 mt-2.5" data-testid="shipping-info-row">
            <Truck className="h-3 w-3 text-slate-400" />
            <span className="text-[11px] text-slate-500">UK:</span>
            <span className={`inline-flex items-center gap-1 text-[11px] font-semibold ${
              product.uk_shipping.tier === 'green' ? 'text-emerald-600' :
              product.uk_shipping.tier === 'yellow' ? 'text-amber-600' :
              'text-red-500'
            }`}>
              <span className={`h-1.5 w-1.5 rounded-full ${
                product.uk_shipping.tier === 'green' ? 'bg-emerald-500' :
                product.uk_shipping.tier === 'yellow' ? 'bg-amber-500' :
                'bg-red-500'
              }`} />
              {product.uk_shipping.label}
            </span>
          </div>
        )}

        {/* Bottom row */}
        <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-50">
          <span className="text-[10px] text-slate-400 flex items-center gap-1">
            {product.last_updated ? (
              <>
                <Clock className="h-3 w-3" />
                {(() => {
                  const diff = Date.now() - new Date(product.last_updated).getTime();
                  const hours = Math.floor(diff / 3600000);
                  if (hours < 1) return 'Just now';
                  if (hours < 24) return `${hours}h ago`;
                  const days = Math.floor(hours / 24);
                  if (days < 7) return `${days}d ago`;
                  return `${Math.floor(days / 7)}w ago`;
                })()}
              </>
            ) : (
              <>
                <TrendingUp className="h-3 w-3" />
                {product.growth_rate || 0}% growth
              </>
            )}
          </span>
          <span className="text-[11px] text-indigo-500 font-medium group-hover:text-indigo-600 flex items-center gap-0.5">
            Details <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </div>
      </Link>
    </div>
  );
}

function MetricCell({ label, value, highlight }) {
  return (
    <div className={`rounded-lg px-2 py-1.5 text-center ${highlight ? 'bg-emerald-50' : 'bg-slate-50'}`}>
      <p className={`text-xs font-semibold ${highlight ? 'text-emerald-700' : 'text-slate-700'}`}>{value}</p>
      <p className="text-[10px] text-slate-400">{label}</p>
    </div>
  );
}
