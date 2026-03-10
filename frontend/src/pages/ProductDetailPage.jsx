import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  ArrowLeft, 
  Bookmark, 
  BookmarkCheck, 
  ExternalLink,
  TrendingUp,
  PoundSterling,
  Eye,
  BarChart3,
  Target,
  Sparkles,
  Package,
  Loader2,
  Store,
  Plus,
  Users,
  Megaphone,
  PieChart,
  Activity
} from 'lucide-react';
import { getProductById, getProductCompetitors } from '@/services/productService';
import { toggleSaveProduct, isProductSaved } from '@/services/savedProductService';
import { useAuth } from '@/contexts/AuthContext';
import { 
  formatCurrency, 
  formatNumber, 
  getTrendStageColor, 
  getOpportunityColor, 
  getCompetitionColor,
  getTrendScoreColor,
  getMarketOpportunityInfo,
  getMarketScoreColor,
  getMarketSaturationColor,
  getMarketSaturationLabel
} from '@/lib/utils';
import { toast } from 'sonner';
import StoreBuilderModal from '@/components/store/StoreBuilderModal';

export default function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
  const [competitorData, setCompetitorData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [showStoreBuilder, setShowStoreBuilder] = useState(false);

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      const { data, error } = await getProductById(id);
      
      if (error || !data) {
        toast.error('Product not found');
        navigate('/discover');
        return;
      }

      setProduct(data);
      
      // Fetch competitor data
      const { data: competitors } = await getProductCompetitors(id);
      if (competitors) {
        setCompetitorData(competitors);
      }
      
      // Check if saved
      const { data: saved } = await isProductSaved(user?.id || 'demo-user-id', id);
      setIsSaved(saved);
      
      setLoading(false);
    };

    fetchProduct();
  }, [id, user, navigate]);

  const handleSaveToggle = async () => {
    const { error } = await toggleSaveProduct(user?.id || 'demo-user-id', id, product);
    
    if (error) {
      toast.error('Failed to update saved products');
      return;
    }

    setIsSaved(!isSaved);
    toast.success(isSaved ? 'Removed from saved products' : 'Added to saved products');
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!product) return null;

  const stats = [
    {
      label: 'Market Score',
      value: product.market_score || 0,
      icon: PieChart,
      color: getMarketScoreColor(product.market_score || 0)
    },
    {
      label: 'Trend Score',
      value: product.trend_score,
      icon: TrendingUp,
      color: getTrendScoreColor(product.trend_score)
    },
    {
      label: 'Est. Margin',
      value: formatCurrency(product.estimated_margin),
      icon: PoundSterling,
      color: 'text-emerald-600'
    },
    {
      label: 'Competitors',
      value: product.active_competitor_stores || 0,
      icon: Users,
      color: 'text-purple-600'
    }
  ];

  const marketBreakdown = product.market_score_breakdown || {
    trend: 0,
    margin: 0,
    competition: 0,
    ad_activity: 0,
    supplier_demand: 0
  };

  const marketInfo = getMarketOpportunityInfo(product.market_label || 'competitive');

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Back button */}
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="text-slate-600 hover:text-slate-900 -ml-2"
          data-testid="back-btn"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to products
        </Button>

        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
          <div className="flex items-start gap-6">
            {/* Product image placeholder */}
            <div className="flex-shrink-0 h-32 w-32 rounded-xl bg-slate-100 flex items-center justify-center">
              <Package className="h-12 w-12 text-slate-300" />
            </div>
            
            <div>
              <div className="flex items-center gap-3">
                <h1 className="font-manrope text-2xl font-bold text-slate-900">
                  {product.product_name}
                </h1>
                {product.is_premium && (
                  <Badge className="bg-indigo-600 text-white">Premium</Badge>
                )}
              </div>
              <p className="mt-1 text-slate-500">{product.category}</p>
              <p className="mt-3 text-slate-600 max-w-2xl">{product.short_description}</p>
              
              {/* Badges */}
              <div className="mt-4 flex flex-wrap gap-2">
                <Badge className={`${getTrendStageColor(product.trend_stage)} border text-xs uppercase tracking-wider`}>
                  {product.trend_stage}
                </Badge>
                <Badge className={`${getOpportunityColor(product.opportunity_rating)} border text-xs uppercase tracking-wider`}>
                  {product.opportunity_rating} opportunity
                </Badge>
                <Badge className={`${getCompetitionColor(product.competition_level)} border text-xs uppercase tracking-wider`}>
                  {product.competition_level} competition
                </Badge>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Button
              onClick={() => setShowStoreBuilder(true)}
              data-testid="build-shop-btn"
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <Store className="mr-2 h-4 w-4" />
              Build Shop
            </Button>
            <Button
              variant="outline"
              onClick={handleSaveToggle}
              data-testid="save-product-btn"
              className={isSaved ? 'border-indigo-200 bg-indigo-50 text-indigo-600' : ''}
            >
              {isSaved ? (
                <>
                  <BookmarkCheck className="mr-2 h-4 w-4" />
                  Saved
                </>
              ) : (
                <>
                  <Bookmark className="mr-2 h-4 w-4" />
                  Save Product
                </>
              )}
            </Button>
            {product.supplier_link && (
              <a href={product.supplier_link} target="_blank" rel="noopener noreferrer">
                <Button variant="outline" data-testid="supplier-link-btn">
                  View Supplier
                  <ExternalLink className="ml-2 h-4 w-4" />
                </Button>
              </a>
            )}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4" data-testid="product-stats">
          {stats.map((stat) => (
            <Card key={stat.label} className="border-slate-200 shadow-sm">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-500">{stat.label}</p>
                    <p className={`mt-1 font-mono text-2xl font-bold ${stat.color}`}>
                      {stat.value}
                    </p>
                  </div>
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-50">
                    <stat.icon className="h-5 w-5 text-slate-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Pricing */}
          <Card className="border-slate-200 shadow-sm lg:col-span-1">
            <CardHeader className="border-b border-slate-100 pb-4">
              <CardTitle className="font-manrope text-lg font-semibold text-slate-900">
                Pricing Details
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Supplier Cost</span>
                <span className="font-mono font-semibold text-slate-900">
                  {formatCurrency(product.supplier_cost)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Est. Retail Price</span>
                <span className="font-mono font-semibold text-slate-900">
                  {formatCurrency(product.estimated_retail_price)}
                </span>
              </div>
              <div className="border-t border-slate-100 pt-4 flex items-center justify-between">
                <span className="font-medium text-slate-700">Est. Margin</span>
                <span className="font-mono text-xl font-bold text-emerald-600">
                  {formatCurrency(product.estimated_margin)}
                </span>
              </div>
              <div className="pt-2">
                <div className="text-xs text-slate-400">
                  Margin %: {((product.estimated_margin / product.estimated_retail_price) * 100).toFixed(0)}%
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Analysis */}
          <Card className="border-slate-200 shadow-sm lg:col-span-2">
            <CardHeader className="border-b border-slate-100 pb-4">
              <CardTitle className="font-manrope text-lg font-semibold text-slate-900 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-600" />
                AI Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {product.ai_summary ? (
                <p className="text-slate-600 leading-relaxed">{product.ai_summary}</p>
              ) : (
                <p className="text-slate-400 italic">No AI analysis available for this product.</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Market Intelligence Section */}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="font-manrope text-lg font-semibold text-slate-900 flex items-center gap-2">
                <PieChart className="h-5 w-5 text-indigo-600" />
                Market Intelligence
              </CardTitle>
              <Badge className={`${marketInfo.color} border px-3 py-1`}>
                {marketInfo.text}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Market Score Breakdown Chart */}
              <div>
                <h4 className="text-sm font-medium text-slate-700 mb-4">Score Breakdown</h4>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600 flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        Trend Score
                      </span>
                      <span className="text-sm font-semibold text-slate-900">{marketBreakdown.trend}/100</span>
                    </div>
                    <Progress value={marketBreakdown.trend} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600 flex items-center gap-2">
                        <PoundSterling className="h-4 w-4" />
                        Margin Score
                      </span>
                      <span className="text-sm font-semibold text-slate-900">{marketBreakdown.margin}/100</span>
                    </div>
                    <Progress value={marketBreakdown.margin} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600 flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        Competition (higher = less)
                      </span>
                      <span className="text-sm font-semibold text-slate-900">{marketBreakdown.competition}/100</span>
                    </div>
                    <Progress value={marketBreakdown.competition} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600 flex items-center gap-2">
                        <Megaphone className="h-4 w-4" />
                        Ad Validation
                      </span>
                      <span className="text-sm font-semibold text-slate-900">{marketBreakdown.ad_activity}/100</span>
                    </div>
                    <Progress value={marketBreakdown.ad_activity} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600 flex items-center gap-2">
                        <Package className="h-4 w-4" />
                        Supplier Demand
                      </span>
                      <span className="text-sm font-semibold text-slate-900">{marketBreakdown.supplier_demand}/100</span>
                    </div>
                    <Progress value={marketBreakdown.supplier_demand} className="h-2" />
                  </div>
                </div>
                <p className="mt-4 text-xs text-slate-500">{marketInfo.description}</p>
              </div>

              {/* Market Metrics */}
              <div>
                <h4 className="text-sm font-medium text-slate-700 mb-4">Market Metrics</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-50 rounded-lg p-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Active Stores</p>
                    <p className="mt-1 text-2xl font-bold text-slate-900">{product.active_competitor_stores || 0}</p>
                    <p className="text-xs text-slate-500">selling this product</p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Avg. Price</p>
                    <p className="mt-1 text-2xl font-bold text-slate-900">{formatCurrency(product.avg_selling_price || product.estimated_retail_price)}</p>
                    <p className="text-xs text-slate-500">market average</p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Est. Ad Spend</p>
                    <p className="mt-1 text-2xl font-bold text-slate-900">{formatCurrency(product.estimated_monthly_ad_spend || 0)}</p>
                    <p className="text-xs text-slate-500">monthly market</p>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-4">
                    <p className="text-xs text-slate-500 uppercase tracking-wider">Saturation</p>
                    <p className={`mt-1 text-2xl font-bold ${getMarketSaturationColor(product.market_saturation || 0)}`}>
                      {product.market_saturation || 0}%
                    </p>
                    <p className="text-xs text-slate-500">{getMarketSaturationLabel(product.market_saturation || 0)}</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Competitor Stores Section */}
        {competitorData?.competitor_stores && competitorData.competitor_stores.length > 0 && (
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="border-b border-slate-100 pb-4">
              <CardTitle className="font-manrope text-lg font-semibold text-slate-900 flex items-center gap-2">
                <Store className="h-5 w-5 text-indigo-600" />
                Competitor Stores ({competitorData.market_intelligence?.active_competitor_stores || 0} total)
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                {competitorData.competitor_stores.slice(0, 8).map((store, index) => (
                  <div key={store.id} className="flex items-center justify-between p-4 hover:bg-slate-50">
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 font-semibold text-slate-600 text-sm">
                        #{index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-slate-900">{store.name}</p>
                        <div className="flex items-center gap-2 text-sm text-slate-500">
                          <span>★ {store.rating}</span>
                          <span className="text-slate-300">•</span>
                          <span>{store.reviews_count} reviews</span>
                          {store.has_active_ads && (
                            <>
                              <span className="text-slate-300">•</span>
                              <Badge className="bg-amber-50 text-amber-700 border-amber-200 text-xs">Running Ads</Badge>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-mono font-semibold text-slate-900">{formatCurrency(store.price)}</p>
                      <p className="text-xs text-slate-500">~{store.estimated_monthly_sales} sales/mo</p>
                    </div>
                  </div>
                ))}
              </div>
              {competitorData.competitor_stores.length > 8 && (
                <div className="p-4 bg-slate-50 text-center text-sm text-slate-500">
                  + {competitorData.competitor_stores.length - 8} more competitors
                </div>
              )}
              <div className="p-3 bg-slate-50 border-t border-slate-100 text-xs text-slate-400 text-center">
                Data source: {competitorData.data_source} • Updated: {new Date(competitorData.data_freshness).toLocaleDateString()}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Market Overview */}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-4">
            <CardTitle className="font-manrope text-lg font-semibold text-slate-900 flex items-center gap-2">
              <Target className="h-5 w-5 text-indigo-600" />
              Market Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="text-sm font-medium text-slate-500 uppercase tracking-wider">Trend Stage</h4>
                <p className="mt-2 text-lg font-semibold text-slate-900 capitalize">{product.trend_stage}</p>
                <p className="mt-1 text-sm text-slate-500">
                  {product.trend_stage === 'early' && 'New product with growing interest'}
                  {product.trend_stage === 'rising' && 'Rapidly gaining popularity'}
                  {product.trend_stage === 'peak' && 'At maximum popularity'}
                  {product.trend_stage === 'saturated' && 'Market is highly competitive'}
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-slate-500 uppercase tracking-wider">Competition Level</h4>
                <p className="mt-2 text-lg font-semibold text-slate-900 capitalize">{product.competition_level}</p>
                <p className="mt-1 text-sm text-slate-500">
                  {product.ad_count} active ads detected
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-slate-500 uppercase tracking-wider">TikTok Visibility</h4>
                <p className="mt-2 text-lg font-semibold text-slate-900">{formatNumber(product.tiktok_views)} views</p>
                <p className="mt-1 text-sm text-slate-500">
                  Social proof and viral potential
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Store Builder Modal */}
      <StoreBuilderModal
        product={product}
        isOpen={showStoreBuilder}
        onClose={() => setShowStoreBuilder(false)}
      />
    </DashboardLayout>
  );
}
