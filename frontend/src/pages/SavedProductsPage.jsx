import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Bookmark, 
  BookmarkX,
  Package,
  Eye,
  ArrowRight,
  Loader2
} from 'lucide-react';
import { getSavedProducts, unsaveProduct } from '@/services/savedProductService';
import { useAuth } from '@/contexts/AuthContext';
import { 
  formatCurrency, 
  formatNumber, 
  getTrendStageColor, 
  getOpportunityColor,
  getTrendScoreColor 
} from '@/lib/utils';
import { toast } from 'sonner';

export default function SavedProductsPage() {
  const { user } = useAuth();
  const [savedProducts, setSavedProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSavedProducts();
  }, [user]);

  const fetchSavedProducts = async () => {
    setLoading(true);
    const { data, error } = await getSavedProducts(user?.id || 'demo-user-id');
    
    if (data) {
      // Handle both Supabase format and mock format
      const products = data.map(item => item.products || item);
      setSavedProducts(products.filter(Boolean));
    }
    setLoading(false);
  };

  const handleRemove = async (productId, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const { error } = await unsaveProduct(user?.id || 'demo-user-id', productId);
    
    if (error) {
      toast.error('Failed to remove product');
      return;
    }

    setSavedProducts(prev => prev.filter(p => p.id !== productId));
    toast.success('Product removed from saved');
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">Saved Products</h1>
            <p className="mt-1 text-slate-500">Products you've bookmarked for later</p>
          </div>
          <Link to="/discover">
            <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="discover-more-btn">
              Discover More
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : savedProducts.length === 0 ? (
          <Card className="border-slate-200 shadow-sm">
            <CardContent className="py-16 text-center">
              <Bookmark className="mx-auto h-12 w-12 text-slate-300" />
              <h3 className="mt-4 font-manrope text-lg font-semibold text-slate-900">
                No saved products yet
              </h3>
              <p className="mt-2 text-slate-500 max-w-md mx-auto">
                Start exploring products and save the ones you're interested in. They'll appear here for easy access.
              </p>
              <Link to="/discover" className="mt-6 inline-block">
                <Button className="bg-indigo-600 hover:bg-indigo-700">
                  Browse Products
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3" data-testid="saved-products-grid">
            {savedProducts.map((product) => (
              <Link
                key={product.id}
                to={`/product/${product.id}`}
                data-testid={`saved-product-${product.id}`}
              >
                <Card className="group border-slate-200 shadow-sm hover:border-indigo-200 hover:shadow-lg transition-all duration-300 h-full">
                  <CardContent className="p-0">
                    {/* Image */}
                    <div className="relative h-36 bg-slate-100 rounded-t-lg overflow-hidden">
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
                        <Package className="h-10 w-10 text-slate-300" />
                      </div>
                      {product.is_premium && (
                        <Badge className="absolute top-3 left-3 bg-indigo-600 text-white">
                          Premium
                        </Badge>
                      )}
                      <button
                        onClick={(e) => handleRemove(product.id, e)}
                        className="absolute top-3 right-3 p-2 rounded-full bg-white/80 hover:bg-red-50 transition-colors group"
                        data-testid={`remove-btn-${product.id}`}
                      >
                        <BookmarkX className="h-4 w-4 text-slate-400 group-hover:text-red-500" />
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

                      {/* Stats */}
                      <div className="flex items-center justify-between">
                        <div>
                          <p className={`font-mono text-xl font-bold ${getTrendScoreColor(product.trend_score)}`}>
                            {product.trend_score}
                          </p>
                          <p className="text-xs text-slate-400">Trend Score</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-lg font-semibold text-slate-900">
                            {formatCurrency(product.estimated_margin)}
                          </p>
                          <p className="text-xs text-slate-400">Est. Margin</p>
                        </div>
                      </div>

                      {/* TikTok Views */}
                      <div className="flex items-center gap-2 text-sm text-slate-500">
                        <Eye className="h-4 w-4" />
                        {formatNumber(product.tiktok_views)} TikTok views
                      </div>

                      {/* Badges */}
                      <div className="flex flex-wrap gap-2">
                        <Badge className={`${getTrendStageColor(product.trend_stage)} border text-xs`}>
                          {product.trend_stage}
                        </Badge>
                        <Badge className={`${getOpportunityColor(product.opportunity_rating)} border text-xs`}>
                          {product.opportunity_rating}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
