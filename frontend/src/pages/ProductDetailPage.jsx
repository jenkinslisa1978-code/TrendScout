import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, 
  Bookmark, 
  BookmarkCheck, 
  ExternalLink,
  TrendingUp,
  DollarSign,
  Eye,
  BarChart3,
  Target,
  Sparkles,
  Package,
  Loader2,
  Store,
  Plus
} from 'lucide-react';
import { getProductById } from '@/services/productService';
import { toggleSaveProduct, isProductSaved } from '@/services/savedProductService';
import { useAuth } from '@/contexts/AuthContext';
import { 
  formatCurrency, 
  formatNumber, 
  getTrendStageColor, 
  getOpportunityColor, 
  getCompetitionColor,
  getTrendScoreColor 
} from '@/lib/utils';
import { toast } from 'sonner';
import StoreBuilderModal from '@/components/store/StoreBuilderModal';

export default function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
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
      label: 'Trend Score',
      value: product.trend_score,
      icon: TrendingUp,
      color: getTrendScoreColor(product.trend_score)
    },
    {
      label: 'Est. Margin',
      value: formatCurrency(product.estimated_margin),
      icon: DollarSign,
      color: 'text-emerald-600'
    },
    {
      label: 'TikTok Views',
      value: formatNumber(product.tiktok_views),
      icon: Eye,
      color: 'text-blue-600'
    },
    {
      label: 'Ad Count',
      value: product.ad_count,
      icon: BarChart3,
      color: 'text-purple-600'
    }
  ];

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
                <h4 className="text-sm font-medium text-slate-500 uppercase tracking-wider">Opportunity Rating</h4>
                <p className="mt-2 text-lg font-semibold text-slate-900 capitalize">{product.opportunity_rating}</p>
                <p className="mt-1 text-sm text-slate-500">
                  Based on trend score and competition analysis
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
