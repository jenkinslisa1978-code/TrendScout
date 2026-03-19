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
  Activity,
  Gauge,
  Rocket,
  AlertTriangle,
  XCircle,
  Info,
  Share2,
  ShoppingBag,
  Truck,
} from 'lucide-react';
import { getProductById, getProductCompetitors } from '@/services/productService';
import { getCompleteAnalysis } from '@/services/intelligenceService';
import { toggleSaveProduct, isProductSaved } from '@/services/savedProductService';
import { useAuth } from '@/contexts/AuthContext';
import { useSubscription } from '@/hooks/useSubscription';
import { LockedContent, UpgradeBadge } from '@/components/common/UpgradePrompts';
import { UpgradeModal } from '@/components/common/UpgradeModal';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import SupplierSection from '@/components/SupplierSection';
import AdCreativeSection from '@/components/AdCreativeSection';
import AdDiscoverySection from '@/components/AdDiscoverySection';
import SaturationRadar from '@/components/SaturationRadar';
import CompetitorIntelligence from '@/components/CompetitorIntelligence';
import WinningAdPatterns from '@/components/WinningAdPatterns';
import AdBlueprint from '@/components/AdBlueprint';
import AdPerformanceIndicator from '@/components/AdPerformanceIndicator';
import AdTestPlanner from '@/components/AdTestPlanner';
import LaunchSimulator from '@/components/LaunchSimulator';
import AdCreativeGenerator from '@/components/AdCreativeGenerator';
import TrendTimeline from '@/components/TrendTimeline';
import ProductProfitCalculator from '@/components/ProductProfitCalculator';
import ShareableProductCard from '@/components/ShareableProductCard';
import ScoringMethodology from '@/components/ScoringMethodology';
import ProfitabilityCalculator from '@/components/ProfitabilityCalculator';
import WinningProductIndicator from '@/components/WinningProductIndicator';
import ProductLaunchPlaybook from '@/components/ProductLaunchPlaybook';
import SimilarProducts from '@/components/SimilarProducts';
import { DataFreshnessBadge, DataFreshnessCard } from '@/components/DataFreshness';
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
  getMarketSaturationLabel,
  getLaunchScoreInfo,
  getLaunchScoreLabel
} from '@/lib/utils';
import { toast } from 'sonner';
import StoreBuilderModal from '@/components/store/StoreBuilderModal';
import { 
  ConfidenceBadge, 
  DataSourceBadge,
  DataIntegrityWarning,
  DataIntegritySummary 
} from '@/components/data-integrity';
import { SourceTrustBadge, SourceDot, FreshnessIndicator } from '@/components/SourceTrustBadge';
import {
  ProductValidationCard,
  SuccessPredictionCard,
  TrendAnalysisCard,
  LaunchRecommendationBadge,
  QuickValidationSummary
} from '@/components/intelligence';
import { ExplainScoreButton } from '@/components/LaunchScoreExplainerModal';
import ScoreBreakdownPanel from '@/components/product/ScoreBreakdownPanel';
import ShareSnippet from '@/components/product/ShareSnippet';

export default function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { isFree, isStarter, canAccessFullInsights, canAccessEarlyTrends, canDirectPublish, isStarterOrAbove, isProOrAbove, isTrialFeature } = useSubscription();
  const hasDeepDive = isStarterOrAbove || isTrialFeature('saturation') || isTrialFeature('ad_patterns');
  const [product, setProduct] = useState(null);
  const [competitorData, setCompetitorData] = useState(null);
  const [dataIntegrity, setDataIntegrity] = useState(null);
  const [intelligenceData, setIntelligenceData] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [showStoreBuilder, setShowStoreBuilder] = useState(false);
  const [launching, setLaunching] = useState(false);
  const [pushingToShopify, setPushingToShopify] = useState(false);
  const [showShareCard, setShowShareCard] = useState(false);
  const [upgradeModal, setUpgradeModal] = useState({ open: false, feature: 'insights' });

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      // Fetch product WITH data integrity info
      const { data, dataIntegrity: integrity, warnings: productWarnings, error } = await getProductById(id, true);
      
      if (error || !data) {
        toast.error('Product not found');
        navigate('/discover');
        return;
      }

      setProduct(data);
      setDataIntegrity(integrity);
      setWarnings(productWarnings || []);

      // Track insight usage for freemium gating
      try {
        const token = localStorage.getItem('trendscout_token');
        if (token) {
          await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/track-insight`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
          });
        }
      } catch {}
      
      // Fetch competitor data
      const { data: competitors } = await getProductCompetitors(id);
      if (competitors) {
        setCompetitorData(competitors);
      }
      
      // Fetch intelligence analysis (validation + prediction)
      const { data: analysis } = await getCompleteAnalysis(id);
      if (analysis) {
        setIntelligenceData(analysis);
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

  const handleLaunchStore = async () => {
    setLaunching(true);
    try {
      const token = localStorage.getItem('trendscout_token');
      const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/stores/launch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ product_id: id }),
      });
      const data = await res.json();
      if (data.success) {
        toast.success('Store launched successfully!');
        navigate(`/stores/${data.store.id}`);
      } else {
        toast.error(data.detail || 'Failed to launch store');
      }
    } catch (err) {
      toast.error('Failed to launch store');
    } finally {
      setLaunching(false);
    }
  };

  const handlePushToShopify = async () => {
    setPushingToShopify(true);
    try {
      const token = localStorage.getItem('trendscout_token');
      const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/shopify/push-product`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ product_id: id }),
      });
      const data = await res.json();
      if (data.success) {
        toast.success(`Product pushed to Shopify as draft! View it in your store admin.`);
      } else {
        toast.error(data.error || 'Failed to push to Shopify');
      }
    } catch {
      toast.error('Failed to push to Shopify');
    } finally {
      setPushingToShopify(false);
    }
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

  // Get launch score info
  const launchInfo = getLaunchScoreInfo(product.launch_score || 0, product.launch_score_label);
  const LaunchIcon = product.launch_score >= 80 ? Rocket : 
                     product.launch_score >= 60 ? TrendingUp : 
                     product.launch_score >= 40 ? AlertTriangle : XCircle;

  const stats = [
    {
      label: 'Launch Score',
      value: product.launch_score || 0,
      icon: LaunchIcon,
      color: launchInfo.textColor,
      isPrimary: true,
      showExplain: true,
      tooltip: 'How ready this product is to sell. Higher = better chance of success. Based on trend, profit margin, competition, and demand.'
    },
    {
      label: 'Trend Score',
      value: product.trend_score,
      icon: TrendingUp,
      color: getTrendScoreColor(product.trend_score),
      tooltip: 'How popular this product is right now. Higher = more people are searching for and buying it.'
    },
    {
      label: 'Est. Margin',
      value: formatCurrency(product.estimated_margin),
      icon: PoundSterling,
      color: 'text-emerald-600',
      tooltip: 'How much profit you could make per sale after paying the supplier. Higher = more money in your pocket.'
    },
    {
      label: 'Competitors',
      value: product.active_competitor_stores || 0,
      icon: Users,
      color: 'text-purple-600',
      tooltip: 'How many other shops are already selling this product. Lower = less competition for you.'
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

        {/* Data Integrity Warnings */}
        {warnings && warnings.length > 0 && (
          <DataIntegrityWarning warnings={warnings} />
        )}

        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
          <div className="flex items-start gap-6">
            {/* Product image */}
            <div className="flex-shrink-0 h-32 w-32 rounded-xl bg-slate-100 overflow-hidden">
              {product.image_url ? (
                <img 
                  src={product.image_url} 
                  alt={product.product_name}
                  className="w-full h-full object-cover"
                  onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                />
              ) : null}
              <div className={`${product.image_url ? 'hidden' : 'flex'} w-full h-full items-center justify-center`}>
                <Package className="h-12 w-12 text-slate-300" />
              </div>
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
              {product.data_source === 'cj_dropshipping' && (
                <Badge className="mt-1 bg-emerald-50 text-emerald-700 border-emerald-200 text-xs" data-testid="cj-source-badge">
                  <Truck className="h-3 w-3 mr-1" /> Sourced from CJ Dropshipping
                </Badge>
              )}
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
                {/* Data integrity badges */}
                <ConfidenceBadge 
                  confidence={product.confidence_score || 0} 
                  level={dataIntegrity?.confidence_level}
                  showScore={true}
                />
                <DataSourceBadge 
                  source={product.data_source} 
                  isSimulated={product.data_source === 'simulated'} 
                />
                {product.data_confidence && (
                  <SourceTrustBadge confidence={product.data_confidence} />
                )}
                {product.enrichment_last_run && (
                  <FreshnessIndicator timestamp={product.enrichment_last_run} />
                )}
              </div>
              {/* Data Freshness */}
              <div className="mt-2">
                <DataFreshnessBadge 
                  lastUpdated={product.last_updated || product.updated_at || product.scores_updated_at}
                  dataSource={product.data_source}
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Button
              onClick={handleLaunchStore}
              disabled={launching}
              data-testid="launch-store-btn"
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
            >
              {launching ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Launching...</>
              ) : (
                <><Rocket className="mr-2 h-4 w-4" /> Launch Store</>
              )}
            </Button>
            <Button
              onClick={handlePushToShopify}
              disabled={pushingToShopify}
              data-testid="push-to-shopify-btn"
              variant="outline"
              className="border-green-200 text-green-700 hover:bg-green-50"
            >
              {pushingToShopify ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Pushing...</>
              ) : (
                <><ShoppingBag className="mr-2 h-4 w-4" /> Push to Shopify</>
              )}
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowStoreBuilder(true)}
              data-testid="build-shop-btn"
            >
              <Store className="mr-2 h-4 w-4" />
              Customize
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
            <Button
              variant="outline"
              onClick={() => setShowShareCard(true)}
              data-testid="share-product-btn"
            >
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
          </div>
        </div>

        {/* Winning Product Indicator (Part 5) */}
        <WinningProductIndicator product={product} />

        {/* Launch Recommendation - KEY DECISION CARD */}
        {intelligenceData && (
          <Card className="border-2 border-indigo-200 bg-indigo-50/30 shadow-sm" data-testid="launch-recommendation">
            <CardContent className="p-6">
              <div className="flex items-start justify-between gap-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <Gauge className="h-6 w-6 text-indigo-600" />
                    <h3 className="text-lg font-semibold text-slate-900">Should You Launch This Product?</h3>
                  </div>
                  <p className="text-slate-600 mb-4">{intelligenceData.validation_summary}</p>
                  <div className="flex flex-wrap gap-3">
                    <LaunchRecommendationBadge 
                      recommendation={intelligenceData.recommendation} 
                      label={intelligenceData.recommendation_label} 
                    />
                    <Badge variant="outline" className="bg-white">
                      <Target className="h-3 w-3 mr-1" />
                      {product.launch_score}/100 Launch Score
                    </Badge>
                    <Badge variant="outline" className="bg-white">
                      <Sparkles className="h-3 w-3 mr-1" />
                      {intelligenceData.confidence}% Confidence
                    </Badge>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-indigo-600">
                    {product.launch_score}
                  </div>
                  <div className="text-sm text-slate-500">Launch Score</div>
                  <div className="text-xs text-slate-400 mt-1">
                    {intelligenceData.confidence}% data confidence
                  </div>
                </div>
              </div>
              
              {/* Quick Insights */}
              {(intelligenceData.strengths?.length > 0 || intelligenceData.weaknesses?.length > 0) && (
                <div className="mt-4 pt-4 border-t border-indigo-200 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {intelligenceData.strengths?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-green-700 mb-2">✓ Strengths</h4>
                      <ul className="text-sm text-slate-600 space-y-1">
                        {intelligenceData.strengths.slice(0, 2).map((s, i) => (
                          <li key={i}>• {s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {intelligenceData.weaknesses?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-red-700 mb-2">⚠ Concerns</h4>
                      <ul className="text-sm text-slate-600 space-y-1">
                        {intelligenceData.weaknesses.slice(0, 2).map((w, i) => (
                          <li key={i}>• {w}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4" data-testid="product-stats">
          <TooltipProvider delayDuration={200}>
          {stats.map((stat) => (
            <Card key={stat.label} className={`border-slate-200 shadow-sm ${stat.isPrimary ? 'ring-2 ring-indigo-100' : ''}`}>
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-slate-500">{stat.label}</p>
                      {stat.tooltip && (
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Info className="h-3.5 w-3.5 text-slate-300 hover:text-slate-500 cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent side="top" className="max-w-[220px] text-xs">
                            <p>{stat.tooltip}</p>
                          </TooltipContent>
                        </Tooltip>
                      )}
                      {stat.showExplain && (
                        <ExplainScoreButton 
                          productId={product.id}
                          productName={product.product_name}
                          launchScore={product.launch_score || 0}
                          variant="icon"
                        />
                      )}
                    </div>
                    <p className={`mt-1 font-mono text-2xl font-bold ${stat.color}`}>
                      {stat.value}
                    </p>
                    {stat.isPrimary && (
                      <Badge className={`${getLaunchScoreInfo(product.launch_score || 0).color} border text-xs mt-1`}>
                        {getLaunchScoreLabel(product.launch_score || 0)}
                      </Badge>
                    )}
                  </div>
                  <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${stat.isPrimary ? getLaunchScoreInfo(product.launch_score || 0).bgColor : 'bg-slate-50'}`}>
                    <stat.icon className={`h-5 w-5 ${stat.isPrimary ? 'text-white' : 'text-slate-400'}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
          </TooltipProvider>
        </div>

        {/* 7-Signal Score Breakdown */}
        {isFree ? (
          <LockedContent feature="7-Signal Score Breakdown" requiredPlan="Pro" blurIntensity="medium">
            <ScoreBreakdownPanel productId={id} />
          </LockedContent>
        ) : (
          <ScoreBreakdownPanel productId={id} />
        )}

        {/* Social Share */}
        {product.product_name && (
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400">Share this product's score</p>
            <ShareSnippet
              productName={product.product_name}
              score={product.launch_score || 0}
              category={product.category}
              productId={id}
            />
          </div>
        )}

        {/* Supplier Section */}
        {isStarterOrAbove ? (
          <SupplierSection productId={id} productName={product.product_name} />
        ) : (
          <div className="relative cursor-pointer" onClick={() => setUpgradeModal({ open: true, feature: 'supplier' })} data-testid="supplier-locked">
            <LockedContent feature="Supplier Intelligence" requiredPlan="Starter" blurIntensity="medium">
              <SupplierSection productId={id} productName={product.product_name} />
            </LockedContent>
          </div>
        )}

        {/* How Our Scores Work — Transparency */}
        <ScoringMethodology />

        {/* Profitability Calculator */}
        <ProfitabilityCalculator productId={id} productName={product?.product_name} />

        {/* Launch Playbook */}
        <ProductLaunchPlaybook productId={id} />

        {/* Saturation Radar + Competitor Intelligence — side by side */}
        {hasDeepDive ? (
          <div className="grid lg:grid-cols-2 gap-6">
            <SaturationRadar productId={id} />
            <CompetitorIntelligence productId={id} />
          </div>
        ) : (
          <LockedContent feature="Saturation & Competitor Intelligence" requiredPlan="Starter" blurIntensity="heavy">
            <div className="grid lg:grid-cols-2 gap-6">
              <SaturationRadar productId={id} />
              <CompetitorIntelligence productId={id} />
            </div>
          </LockedContent>
        )}

        {/* Ad Winning Engine — Patterns + Blueprint + Performance */}
        {hasDeepDive ? (
          <div className="grid lg:grid-cols-2 gap-6">
            <WinningAdPatterns productId={id} />
            <AdBlueprint productId={id} />
          </div>
        ) : (
          <LockedContent feature="Winning Ad Patterns & Blueprints" requiredPlan="Starter" blurIntensity="heavy">
            <div className="grid lg:grid-cols-2 gap-6">
              <WinningAdPatterns productId={id} />
              <AdBlueprint productId={id} />
            </div>
          </LockedContent>
        )}

        {/* Ad Performance Indicator */}
        {hasDeepDive ? (
          <AdPerformanceIndicator productId={id} />
        ) : (
          <LockedContent feature="Ad Performance Insights" requiredPlan="Starter" blurIntensity="medium">
            <AdPerformanceIndicator productId={id} />
          </LockedContent>
        )}

        {/* Ad A/B Test Planner */}
        <AdTestPlanner productId={id} />

        {/* Launch Simulator */}
        <LaunchSimulator productId={id} />

        {/* AI Ad Creative Generator */}
        {isStarterOrAbove ? (
          <AdCreativeGenerator productId={id} productName={product.product_name} />
        ) : (
          <div className="relative cursor-pointer" onClick={() => setUpgradeModal({ open: true, feature: 'ads' })} data-testid="ad-generator-locked">
            <LockedContent feature="AI Ad Generator" requiredPlan="Starter" blurIntensity="medium">
              <AdCreativeGenerator productId={id} productName={product.product_name} />
            </LockedContent>
          </div>
        )}

        {/* Trend Timeline */}
        <TrendTimeline product={product} />

        {/* Profit Calculator */}
        <ProductProfitCalculator product={product} />

        {/* AI Ad Creatives */}
        {isStarterOrAbove ? (
          <AdCreativeSection productId={id} />
        ) : (
          <div className="relative cursor-pointer" onClick={() => setUpgradeModal({ open: true, feature: 'ads' })} data-testid="ads-locked">
            <LockedContent feature="Ad Intelligence" requiredPlan="Starter" blurIntensity="medium">
              <AdCreativeSection productId={id} />
            </LockedContent>
          </div>
        )}

        {/* Ad Discovery */}
        <AdDiscoverySection productId={id} />

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
        {isFree ? (
          <LockedContent feature="Market Intelligence" requiredPlan="Pro" blurIntensity="medium">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader><CardTitle className="text-lg flex items-center gap-2"><PieChart className="h-5 w-5 text-indigo-600" /> Market Intelligence</CardTitle></CardHeader>
              <CardContent className="p-6"><div className="h-48 bg-slate-50 rounded-lg" /></CardContent>
            </Card>
          </LockedContent>
        ) : (
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
        )}

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

        {/* Similar Products */}
        <SimilarProducts productId={id} productName={product.product_name} maxItems={isStarterOrAbove ? 6 : 3} />

        {/* Data Freshness Card */}
        <DataFreshnessCard product={product} />

        {/* Data Quality Card */}
        {dataIntegrity && (
          <DataIntegritySummary integrity={dataIntegrity} />
        )}
      </div>

      {/* Store Builder Modal */}
      <StoreBuilderModal
        product={product}
        isOpen={showStoreBuilder}
        onClose={() => setShowStoreBuilder(false)}
      />

      {/* Shareable Product Card Modal */}
      {showShareCard && product && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setShowShareCard(false)}>
          <div className="bg-white rounded-2xl p-6 max-w-md w-full" onClick={(e) => e.stopPropagation()} data-testid="share-card-modal">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-slate-900">Share Product Insight</h3>
              <button onClick={() => setShowShareCard(false)} className="text-slate-400 hover:text-slate-600 text-lg">&times;</button>
            </div>
            <ShareableProductCard product={product} onClose={() => setShowShareCard(false)} />
          </div>
        </div>
      )}

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={upgradeModal.open}
        onClose={() => setUpgradeModal({ open: false, feature: 'insights' })}
        feature={upgradeModal.feature}
      />
    </DashboardLayout>
  );
}
