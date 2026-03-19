import React, { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { 
  Search, 
  Package, 
  Filter,
  SortAsc,
  SortDesc,
  Bookmark,
  BookmarkCheck,
  Eye,
  Loader2,
  Rocket,
  TrendingUp,
  AlertTriangle,
  XCircle
} from 'lucide-react';
import { getProducts, getCategories } from '@/services/productService';
import { toggleSaveProduct, isProductSaved } from '@/services/savedProductService';
import { useAuth } from '@/contexts/AuthContext';
import { 
  formatCurrency, 
  formatNumber, 
  getTrendStageColor, 
  getCompetitionColor,
  getTrendScoreColor,
  getEarlyTrendInfo,
  getLaunchScoreLabel,
  getLaunchScoreBadgeColor,
  getLaunchScoreInfo
} from '@/lib/utils';
import { toast } from 'sonner';
import StoreBuilderModal from '@/components/store/StoreBuilderModal';
import { ExplainScoreButton } from '@/components/LaunchScoreExplainerModal';
import { useViewMode } from '@/contexts/ViewModeContext';
import ViewModeToggle from '@/components/ViewModeToggle';

export default function DiscoverPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { isBeginner } = useViewMode();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savedProductIds, setSavedProductIds] = useState(new Set());
  
  // Store builder modal
  const [showStoreBuilder, setShowStoreBuilder] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  // Filters
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [trendStage, setTrendStage] = useState('all');
  const [opportunityRating, setOpportunityRating] = useState('all');
  const [earlyTrendFilter, setEarlyTrendFilter] = useState('all');
  const [marketFilter, setMarketFilter] = useState('all');
  const [competitionLevel, setCompetitionLevel] = useState('all');
  const [minTrendScore, setMinTrendScore] = useState('');
  const [maxTrendScore, setMaxTrendScore] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sortBy, setSortBy] = useState('launch_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      const { data } = await getCategories();
      if (data) setCategories(data);
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      const filters = {
        search: search || undefined,
        category: category !== 'all' ? category : undefined,
        trend_stage: trendStage !== 'all' ? trendStage : undefined,
        opportunity_rating: opportunityRating !== 'all' ? opportunityRating : undefined,
        early_trend_label: earlyTrendFilter !== 'all' ? earlyTrendFilter : undefined,
        market_label: marketFilter !== 'all' ? marketFilter : undefined,
        competition_level: competitionLevel !== 'all' ? competitionLevel : undefined,
        min_trend_score: minTrendScore !== '' ? parseInt(minTrendScore) : undefined,
        max_trend_score: maxTrendScore !== '' ? parseInt(maxTrendScore) : undefined,
        min_price: minPrice !== '' ? parseFloat(minPrice) : undefined,
        max_price: maxPrice !== '' ? parseFloat(maxPrice) : undefined,
        sortBy,
        sortOrder
      };
      
      const { data } = await getProducts(filters);
      if (data) setProducts(data);
      setLoading(false);
    };
    
    const debounce = setTimeout(fetchProducts, 300);
    return () => clearTimeout(debounce);
  }, [search, category, trendStage, opportunityRating, earlyTrendFilter, marketFilter, competitionLevel, minTrendScore, maxTrendScore, minPrice, maxPrice, sortBy, sortOrder]);

  const handleSaveToggle = async (product, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const { error } = await toggleSaveProduct(user?.id || 'demo-user-id', product.id, product);
    
    if (error) {
      toast.error('Failed to update saved products');
      return;
    }

    setSavedProductIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(product.id)) {
        newSet.delete(product.id);
        toast.success('Removed from saved products');
      } else {
        newSet.add(product.id);
        toast.success('Added to saved products');
      }
      return newSet;
    });
  };

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc');
  };

  const handleBuildStore = (product) => {
    setSelectedProduct(product);
    setShowStoreBuilder(true);
  };

  const handleStoreCreated = (newStore) => {
    setShowStoreBuilder(false);
    setSelectedProduct(null);
    navigate(`/stores/${newStore.id}`);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">Discover Products</h1>
            <p className="mt-1 text-slate-500">Find winning products and launch your store</p>
          </div>
          <ViewModeToggle />
        </div>

        {/* Filters */}
        <Card className="border-slate-200 shadow-sm">
          <CardContent className="p-4">
            <div className="flex flex-wrap items-center gap-3">
              {/* Search */}
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search products..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10 h-10"
                  data-testid="search-input"
                />
              </div>

              {/* Category filter */}
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="w-[160px] h-10" data-testid="category-filter">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Competition Level filter */}
              <Select value={competitionLevel} onValueChange={setCompetitionLevel}>
                <SelectTrigger className="w-[160px] h-10" data-testid="competition-filter">
                  <SelectValue placeholder="Competition" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>

              {/* Trend Stage filter */}
              <Select value={trendStage} onValueChange={setTrendStage}>
                <SelectTrigger className="w-[140px] h-10" data-testid="trend-stage-filter">
                  <SelectValue placeholder="Trend Stage" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Stages</SelectItem>
                  <SelectItem value="early">Early</SelectItem>
                  <SelectItem value="rising">Rising</SelectItem>
                  <SelectItem value="peak">Peak</SelectItem>
                  <SelectItem value="saturated">Saturated</SelectItem>
                </SelectContent>
              </Select>

              {/* Opportunity filter */}
              <Select value={opportunityRating} onValueChange={setOpportunityRating}>
                <SelectTrigger className="w-[160px] h-10" data-testid="opportunity-filter">
                  <SelectValue placeholder="Opportunity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Ratings</SelectItem>
                  <SelectItem value="very high">Very High</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>

              {/* Sort */}
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-[140px] h-10" data-testid="sort-by-filter">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="launch_score">Launch Score</SelectItem>
                  <SelectItem value="market_score">Market Score</SelectItem>
                  <SelectItem value="trend_score">Trend Score</SelectItem>
                  <SelectItem value="early_trend_score">Early Trend Score</SelectItem>
                  <SelectItem value="success_probability">Success Rate</SelectItem>
                  <SelectItem value="estimated_margin">Margin</SelectItem>
                  <SelectItem value="estimated_retail_price">Price</SelectItem>
                  <SelectItem value="tiktok_views">TikTok Views</SelectItem>
                  <SelectItem value="created_at">Newest</SelectItem>
                </SelectContent>
              </Select>

              <Button
                variant="outline"
                size="icon"
                onClick={toggleSortOrder}
                className="h-10 w-10"
                data-testid="sort-order-btn"
              >
                {sortOrder === 'desc' ? (
                  <SortDesc className="h-4 w-4" />
                ) : (
                  <SortAsc className="h-4 w-4" />
                )}
              </Button>

              {/* Toggle advanced filters */}
              <Button
                variant={showAdvancedFilters ? "secondary" : "outline"}
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className="h-10 gap-2"
                data-testid="toggle-advanced-filters"
              >
                <Filter className="h-4 w-4" />
                Advanced
              </Button>
            </div>

            {/* Advanced Filters Row */}
            {showAdvancedFilters && (
              <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap items-end gap-4">
                {/* Trend Score Range */}
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Trend Score</span>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      min={0}
                      max={100}
                      placeholder="Min"
                      value={minTrendScore}
                      onChange={(e) => setMinTrendScore(e.target.value)}
                      className="w-[80px] h-9 text-sm"
                      data-testid="min-trend-score"
                    />
                    <span className="text-slate-400 text-sm">-</span>
                    <Input
                      type="number"
                      min={0}
                      max={100}
                      placeholder="Max"
                      value={maxTrendScore}
                      onChange={(e) => setMaxTrendScore(e.target.value)}
                      className="w-[80px] h-9 text-sm"
                      data-testid="max-trend-score"
                    />
                  </div>
                </div>

                {/* Price Range */}
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Price Range</span>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      min={0}
                      step={0.01}
                      placeholder="Min"
                      value={minPrice}
                      onChange={(e) => setMinPrice(e.target.value)}
                      className="w-[90px] h-9 text-sm"
                      data-testid="min-price"
                    />
                    <span className="text-slate-400 text-sm">-</span>
                    <Input
                      type="number"
                      min={0}
                      step={0.01}
                      placeholder="Max"
                      value={maxPrice}
                      onChange={(e) => setMaxPrice(e.target.value)}
                      className="w-[90px] h-9 text-sm"
                      data-testid="max-price"
                    />
                  </div>
                </div>

                {/* Early Trend filter */}
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Early Trend</span>
                  <Select value={earlyTrendFilter} onValueChange={setEarlyTrendFilter}>
                    <SelectTrigger className="w-[150px] h-9" data-testid="early-trend-filter">
                      <SelectValue placeholder="Early Trend" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Trends</SelectItem>
                      <SelectItem value="exploding">Exploding</SelectItem>
                      <SelectItem value="rising">Rising</SelectItem>
                      <SelectItem value="early_trend">Early Trend</SelectItem>
                      <SelectItem value="stable">Stable</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Market Opportunity filter */}
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Market Opp.</span>
                  <Select value={marketFilter} onValueChange={setMarketFilter}>
                    <SelectTrigger className="w-[160px] h-9" data-testid="market-filter">
                      <SelectValue placeholder="Market Opp." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Markets</SelectItem>
                      <SelectItem value="massive">Massive Opportunity</SelectItem>
                      <SelectItem value="strong">Strong Opportunity</SelectItem>
                      <SelectItem value="competitive">Competitive</SelectItem>
                      <SelectItem value="saturated">Saturated</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Clear All Filters */}
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-9 text-slate-500 hover:text-red-600"
                  data-testid="clear-filters-btn"
                  onClick={() => {
                    setSearch('');
                    setCategory('all');
                    setTrendStage('all');
                    setOpportunityRating('all');
                    setEarlyTrendFilter('all');
                    setMarketFilter('all');
                    setCompetitionLevel('all');
                    setMinTrendScore('');
                    setMaxTrendScore('');
                    setMinPrice('');
                    setMaxPrice('');
                  }}
                >
                  <XCircle className="h-4 w-4 mr-1" />
                  Clear All
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Products Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-12">
            <Package className="mx-auto h-12 w-12 text-slate-300" />
            <p className="mt-4 text-slate-500">No products found matching your filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {products.map((product) => (
              <Link
                key={product.id}
                to={`/product/${product.id}`}
                data-testid={`product-card-${product.id}`}
              >
                <Card className="group border-slate-200 shadow-sm hover:border-indigo-200 hover:shadow-lg transition-all duration-300 h-full">
                  <CardContent className="p-0">
                    {/* Image */}
                    <div className="relative h-40 bg-slate-100 rounded-t-lg overflow-hidden">
                      {product.image_url ? (
                        <img 
                          src={product.image_url} 
                          alt={product.product_name}
                          className="w-full h-full object-cover"
                          loading="lazy"
                          onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                        />
                      ) : null}
                      <div className={`${product.image_url ? 'hidden' : 'flex'} w-full h-full items-center justify-center`}>
                        <Package className="h-12 w-12 text-slate-300" />
                      </div>
                      {product.is_premium && (
                        <Badge className="absolute top-3 left-3 bg-indigo-600 text-white">
                          Premium
                        </Badge>
                      )}
                      <button
                        onClick={(e) => handleSaveToggle(product, e)}
                        className="absolute top-3 right-3 p-2 rounded-full bg-white/80 hover:bg-white transition-colors"
                        data-testid={`save-btn-${product.id}`}
                      >
                        {savedProductIds.has(product.id) ? (
                          <BookmarkCheck className="h-4 w-4 text-indigo-600" />
                        ) : (
                          <Bookmark className="h-4 w-4 text-slate-400" />
                        )}
                      </button>
                    </div>

                    {/* Content */}
                    <div className="p-4 space-y-3">
                      <div>
                        <h3 className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-1">
                          {product.product_name}
                        </h3>
                        <p className="text-sm text-slate-500 mt-0.5">{product.category}</p>
                      </div>

                      {/* Stats - Launch Score as PRIMARY */}
                      <div className="flex items-center justify-between">
                        {/* Launch Score - PRIMARY METRIC */}
                        <div>
                          <div className="flex items-center gap-1.5">
                            {(() => {
                              const info = getLaunchScoreInfo(product.launch_score || 0, product.launch_score_label);
                              const IconComponent = product.launch_score >= 80 ? Rocket : 
                                                   product.launch_score >= 60 ? TrendingUp : 
                                                   product.launch_score >= 40 ? AlertTriangle : XCircle;
                              return (
                                <>
                                  <div className={`p-1 rounded ${info.bgColor}`}>
                                    <IconComponent className="h-3 w-3 text-white" />
                                  </div>
                                  <p className={`font-mono text-2xl font-bold ${info.textColor}`}>
                                    {product.launch_score || 0}
                                  </p>
                                  {!isBeginner && (
                                    <ExplainScoreButton 
                                      productId={product.id}
                                      productName={product.product_name}
                                      launchScore={product.launch_score || 0}
                                      variant="icon"
                                    />
                                  )}
                                </>
                              );
                            })()}
                          </div>
                          <p className="text-xs text-slate-400">Launch Score</p>
                        </div>
                        {!isBeginner && (
                          <div className="text-center">
                            <p className={`font-mono text-lg font-semibold ${getTrendScoreColor(product.trend_score)}`}>
                              {product.trend_score}
                            </p>
                            <p className="text-xs text-slate-400">Trend</p>
                          </div>
                        )}
                        <div className="text-right">
                          <p className="font-mono text-lg font-semibold text-emerald-600">
                            {formatCurrency(product.estimated_margin)}
                          </p>
                          <p className="text-xs text-slate-400">Est. Profit</p>
                        </div>
                      </div>

                      {/* Advanced: TikTok Views */}
                      {!isBeginner && (
                        <div className="flex items-center gap-2 text-sm text-slate-500">
                          <Eye className="h-4 w-4" />
                          {formatNumber(product.tiktok_views)} TikTok views
                          {product.stores_created > 0 && (
                            <>
                              <span className="text-slate-300">|</span>
                              <span className="text-emerald-600">{product.stores_created} stores built</span>
                            </>
                          )}
                          {product.last_updated && (
                            <>
                              <span className="text-slate-300">|</span>
                              <span className="text-slate-400 text-xs flex items-center gap-0.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
                                {(() => {
                                  const diff = Date.now() - new Date(product.last_updated).getTime();
                                  const hours = Math.floor(diff / 3600000);
                                  if (hours < 1) return 'Just now';
                                  if (hours < 24) return `${hours}h ago`;
                                  const days = Math.floor(hours / 24);
                                  if (days < 7) return `${days}d ago`;
                                  return `${Math.floor(days / 7)}w ago`;
                                })()}
                              </span>
                            </>
                          )}
                        </div>
                      )}

                      {/* Badges - simplified in beginner mode */}
                      <div className="flex flex-wrap gap-2">
                        <Badge 
                          className={`${getLaunchScoreBadgeColor(product.launch_score || 0)} border text-xs font-semibold`}
                          data-testid={`launch-badge-${product.id}`}
                        >
                          {getLaunchScoreLabel(product.launch_score || 0)}
                        </Badge>
                        <Badge className={`${getTrendStageColor(product.trend_stage)} border text-xs`}>
                          {product.trend_stage}
                        </Badge>
                        {!isBeginner && (
                          <>
                            {product.proven_winner && (
                              <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 border text-xs">
                                Proven Winner
                              </Badge>
                            )}
                            {product.early_trend_label && product.early_trend_label !== 'stable' && (
                              <Badge className={`${getEarlyTrendInfo(product.early_trend_label).color} border text-xs`}>
                                {getEarlyTrendInfo(product.early_trend_label).text}
                              </Badge>
                            )}
                            <Badge className={`${getCompetitionColor(product.competition_level)} border text-xs`}>
                              {product.competition_level} comp.
                            </Badge>
                            {product.is_real_data && (
                              <Badge variant="outline" className="text-emerald-600 border-emerald-200 text-xs">
                                Live
                              </Badge>
                            )}
                            {product.confidence_score > 0 && (
                              <Badge variant="outline" className="text-slate-400 border-slate-200 text-xs">
                                {product.confidence_score}% conf.
                              </Badge>
                            )}
                          </>
                        )}
                      </div>

                      {/* Launch Button */}
                      <Button 
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          if (isBeginner) {
                            navigate(`/launch/${product.id}`);
                          } else {
                            handleBuildStore(product);
                          }
                        }}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 mt-2"
                        data-testid={`build-store-btn-${product.id}`}
                      >
                        <Rocket className="mr-2 h-4 w-4" />
                        {isBeginner ? 'Launch Product' : 'Build Store'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Store Builder Modal */}
      {showStoreBuilder && selectedProduct && (
        <StoreBuilderModal
          product={selectedProduct}
          isOpen={showStoreBuilder}
          onClose={() => {
            setShowStoreBuilder(false);
            setSelectedProduct(null);
          }}
          onSuccess={handleStoreCreated}
        />
      )}
    </DashboardLayout>
  );
}
