import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Trophy,
  Flame,
  Store,
  ArrowRight,
  Rocket,
  TrendingUp,
  CheckCircle2,
  Package,
  Eye,
  Zap,
  Plus,
  PieChart,
  Users,
  Radar,
  Bell,
  LayoutDashboard
} from 'lucide-react';
import { getProducts, getProvenWinners, getMarketOpportunities } from '@/services/productService';
import { getUserStores } from '@/services/storeService';
import { useAuth } from '@/contexts/AuthContext';
import { formatNumber, formatCurrency, getEarlyTrendInfo, getEarlyTrendScoreColor, getSuccessProbabilityColor, getMarketOpportunityInfo, getMarketScoreColor } from '@/lib/utils';
import StoreBuilderModal from '@/components/store/StoreBuilderModal';
import { DailyWinnersPanel, MarketRadar, OpportunityWatchlist, AlertsPanel } from '@/components/dashboard';

export default function DashboardPage() {
  const { user, profile } = useAuth();
  const navigate = useNavigate();
  const [winningProducts, setWinningProducts] = useState([]);
  const [earlyTrendProducts, setEarlyTrendProducts] = useState([]);
  const [marketOpportunities, setMarketOpportunities] = useState([]);
  const [userStores, setUserStores] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Store builder modal
  const [showStoreBuilder, setShowStoreBuilder] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch winning products (sorted by combined score)
        const [productsResult, winnersResult, marketResult] = await Promise.all([
          getProducts({ sortBy: 'trend_score', sortOrder: 'desc', limit: 50 }),
          getProvenWinners(10),
          getMarketOpportunities(5)
        ]);

        if (productsResult.data) {
          // Calculate win_score for each product
          const productsWithWinScore = productsResult.data.map(p => ({
            ...p,
            win_score: Math.round(
              (p.trend_score || 0) * 0.3 +
              (p.early_trend_score || 0) * 0.3 +
              (p.success_probability || 0) * 0.4
            )
          }));
          
          // Sort by win_score and take top 5
          const sortedByWinScore = [...productsWithWinScore]
            .sort((a, b) => b.win_score - a.win_score)
            .slice(0, 5);
          setWinningProducts(sortedByWinScore);
          
          // Filter early trend opportunities
          const earlyTrends = productsWithWinScore
            .filter(p => p.early_trend_score >= 65 || ['exploding', 'rising'].includes(p.early_trend_label))
            .sort((a, b) => (b.early_trend_score || 0) - (a.early_trend_score || 0))
            .slice(0, 5);
          setEarlyTrendProducts(earlyTrends);
        }

        // Set market opportunities
        if (marketResult.data) {
          setMarketOpportunities(marketResult.data);
        }

        // Fetch user's stores
        if (user?.id) {
          const storesResult = await getUserStores();
          if (storesResult.data) {
            setUserStores(storesResult.data.slice(0, 5));
          }
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  const handleBuildStore = (product) => {
    setSelectedProduct(product);
    setShowStoreBuilder(true);
  };

  const handleStoreCreated = (newStore) => {
    setShowStoreBuilder(false);
    setSelectedProduct(null);
    navigate(`/stores/${newStore.id}`);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'exported': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'ready': return 'bg-amber-50 text-amber-700 border-amber-200';
      default: return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8 max-w-7xl mx-auto" data-testid="dashboard">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">
              Welcome back{profile?.full_name ? `, ${profile.full_name.split(' ')[0]}` : ''}
            </h1>
            <p className="text-slate-500 mt-1">Find winning products and launch your next store</p>
          </div>
          <Link to="/discover">
            <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="browse-products-btn">
              <Package className="mr-2 h-4 w-4" />
              Browse All Products
            </Button>
          </Link>
        </div>

        {/* Section 1: Winning Products Today */}
        <Card className="border-0 shadow-lg overflow-hidden">
          <CardHeader className="border-b border-slate-100 pb-5 bg-gradient-to-r from-amber-50 via-orange-50 to-red-50">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-manrope text-xl font-bold text-slate-900 flex items-center gap-2">
                  <Trophy className="h-6 w-6 text-amber-500" />
                  Winning Products Today
                </CardTitle>
                <p className="text-sm text-slate-600 mt-1">Highest win scores based on trends, momentum, and success data</p>
              </div>
              <Link 
                to="/discover?sort_by=trend_score" 
                className="flex items-center gap-1.5 text-sm font-semibold text-amber-600 hover:text-amber-700 transition-colors"
                data-testid="view-all-winners-link"
              >
                View all
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-12 text-center">
                <div className="inline-block w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : winningProducts.length === 0 ? (
              <div className="p-12 text-center text-slate-500">
                <Trophy className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                <p>No winning products found</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {winningProducts.map((product, index) => (
                  <div 
                    key={product.id}
                    className="flex items-center justify-between p-5 hover:bg-slate-50/80 transition-colors group"
                    data-testid={`winning-product-${product.id}`}
                  >
                    <div className="flex items-center gap-4 flex-1 min-w-0">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-amber-100 to-orange-100 font-bold text-amber-700 text-lg shrink-0">
                        #{index + 1}
                      </div>
                      <div className="min-w-0 flex-1">
                        <Link 
                          to={`/product/${product.id}`}
                          className="font-semibold text-slate-900 group-hover:text-amber-600 transition-colors truncate block"
                        >
                          {product.product_name}
                        </Link>
                        <div className="flex items-center gap-3 mt-1 text-sm text-slate-500">
                          <span>{product.category}</span>
                          <span className="text-slate-300">•</span>
                          <span className="font-medium text-emerald-600">{formatCurrency(product.estimated_margin)} margin</span>
                          {product.stores_created > 0 && (
                            <>
                              <span className="text-slate-300">•</span>
                              <span className="flex items-center gap-1">
                                <Store className="h-3 w-3" />
                                {product.stores_created} stores
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 shrink-0">
                      <div className="text-right hidden sm:block">
                        <p className="font-mono text-2xl font-bold text-amber-600">{product.win_score}</p>
                        <p className="text-xs text-slate-400">Win Score</p>
                      </div>
                      <Button 
                        onClick={() => handleBuildStore(product)}
                        className="bg-indigo-600 hover:bg-indigo-700 shrink-0"
                        data-testid={`build-store-btn-${product.id}`}
                      >
                        <Rocket className="mr-2 h-4 w-4" />
                        Build Store
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Section 2: Early Trend Opportunities */}
        <Card className="border-0 shadow-lg overflow-hidden">
          <CardHeader className="border-b border-slate-100 pb-5 bg-gradient-to-r from-red-50 via-orange-50 to-amber-50">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-manrope text-xl font-bold text-slate-900 flex items-center gap-2">
                  <Flame className="h-6 w-6 text-red-500" />
                  Early Trend Opportunities
                </CardTitle>
                <p className="text-sm text-slate-600 mt-1">Products accelerating fast - get in before saturation</p>
              </div>
              <Link 
                to="/discover?early_trend=rising" 
                className="flex items-center gap-1.5 text-sm font-semibold text-red-600 hover:text-red-700 transition-colors"
                data-testid="view-early-trends-link"
              >
                View all
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-12 text-center">
                <div className="inline-block w-8 h-8 border-4 border-red-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : earlyTrendProducts.length === 0 ? (
              <div className="p-12 text-center text-slate-500">
                <Flame className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                <p>No early trends detected right now</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {earlyTrendProducts.map((product) => {
                  const earlyTrendInfo = getEarlyTrendInfo(product.early_trend_label);
                  return (
                    <div 
                      key={product.id}
                      className="flex items-center justify-between p-5 hover:bg-slate-50/80 transition-colors group"
                      data-testid={`early-trend-${product.id}`}
                    >
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-red-50 to-orange-50 text-2xl shrink-0">
                          {earlyTrendInfo.icon}
                        </div>
                        <div className="min-w-0 flex-1">
                          <Link 
                            to={`/product/${product.id}`}
                            className="font-semibold text-slate-900 group-hover:text-red-600 transition-colors truncate block"
                          >
                            {product.product_name}
                          </Link>
                          <div className="flex items-center gap-3 mt-1 text-sm">
                            <span className="text-slate-500">{product.category}</span>
                            {product.view_growth_rate > 0 && (
                              <>
                                <span className="text-slate-300">•</span>
                                <span className="font-medium text-emerald-600 flex items-center gap-1">
                                  <TrendingUp className="h-3 w-3" />
                                  +{product.view_growth_rate?.toFixed(0)}% growth
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 shrink-0">
                        <Badge className={`${earlyTrendInfo.color} border px-3 py-1 text-xs font-bold uppercase tracking-wider hidden sm:flex`}>
                          {earlyTrendInfo.text}
                        </Badge>
                        <div className="text-right hidden sm:block">
                          <p className={`font-mono text-xl font-bold ${getEarlyTrendScoreColor(product.early_trend_score || 0)}`}>
                            {product.early_trend_score || 0}
                          </p>
                          <p className="text-xs text-slate-400">Early Score</p>
                        </div>
                        <Button 
                          onClick={() => handleBuildStore(product)}
                          className="bg-indigo-600 hover:bg-indigo-700 shrink-0"
                          data-testid={`build-store-early-${product.id}`}
                        >
                          <Rocket className="mr-2 h-4 w-4" />
                          Build Store
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Section 3: Market Opportunities */}
        <Card className="border-0 shadow-lg overflow-hidden">
          <CardHeader className="border-b border-slate-100 pb-5 bg-gradient-to-r from-emerald-50 via-teal-50 to-cyan-50">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-manrope text-xl font-bold text-slate-900 flex items-center gap-2">
                  <PieChart className="h-6 w-6 text-emerald-500" />
                  Market Opportunities
                </CardTitle>
                <p className="text-sm text-slate-600 mt-1">Best balance of demand, margin, and competition</p>
              </div>
              <Link 
                to="/discover?sort_by=market_score" 
                className="flex items-center gap-1.5 text-sm font-semibold text-emerald-600 hover:text-emerald-700 transition-colors"
                data-testid="view-market-opportunities-link"
              >
                View all
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-12 text-center">
                <div className="inline-block w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : marketOpportunities.length === 0 ? (
              <div className="p-12 text-center text-slate-500">
                <PieChart className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                <p>No market opportunities found</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {marketOpportunities.map((product, index) => {
                  const marketInfo = getMarketOpportunityInfo(product.market_label);
                  return (
                    <div 
                      key={product.id}
                      className="flex items-center justify-between p-5 hover:bg-slate-50/80 transition-colors group"
                      data-testid={`market-opportunity-${product.id}`}
                    >
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-100 to-teal-100 font-bold text-emerald-700 text-lg shrink-0">
                          #{index + 1}
                        </div>
                        <div className="min-w-0 flex-1">
                          <Link 
                            to={`/product/${product.id}`}
                            className="font-semibold text-slate-900 group-hover:text-emerald-600 transition-colors truncate block"
                          >
                            {product.product_name}
                          </Link>
                          <div className="flex items-center gap-3 mt-1 text-sm text-slate-500">
                            <span>{product.category}</span>
                            <span className="text-slate-300">•</span>
                            <span className="font-medium text-emerald-600">{formatCurrency(product.estimated_margin)} margin</span>
                            <span className="text-slate-300">•</span>
                            <span className="flex items-center gap-1">
                              <Users className="h-3 w-3" />
                              {product.active_competitor_stores || 0} competitors
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 shrink-0">
                        <Badge className={`${marketInfo.color} border px-3 py-1 text-xs font-bold uppercase tracking-wider hidden sm:flex`}>
                          {marketInfo.shortText}
                        </Badge>
                        <div className="text-right hidden sm:block">
                          <p className={`font-mono text-2xl font-bold ${getMarketScoreColor(product.market_score || 0)}`}>
                            {product.market_score || 0}
                          </p>
                          <p className="text-xs text-slate-400">Market Score</p>
                        </div>
                        <Button 
                          onClick={() => handleBuildStore(product)}
                          className="bg-indigo-600 hover:bg-indigo-700 shrink-0"
                          data-testid={`build-store-market-${product.id}`}
                        >
                          <Rocket className="mr-2 h-4 w-4" />
                          Build Store
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Section 4: Your Stores */}
        <Card className="border-0 shadow-lg overflow-hidden">
          <CardHeader className="border-b border-slate-100 pb-5 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-manrope text-xl font-bold text-slate-900 flex items-center gap-2">
                  <Store className="h-6 w-6 text-indigo-500" />
                  Your Stores
                </CardTitle>
                <p className="text-sm text-slate-600 mt-1">Manage and launch your ecommerce stores</p>
              </div>
              <Link 
                to="/stores" 
                className="flex items-center gap-1.5 text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
                data-testid="view-all-stores-link"
              >
                View all
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-12 text-center">
                <div className="inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : userStores.length === 0 ? (
              <div className="p-12 text-center">
                <Store className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                <p className="text-slate-600 mb-4">You haven't created any stores yet</p>
                <Link to="/discover">
                  <Button className="bg-indigo-600 hover:bg-indigo-700">
                    <Plus className="mr-2 h-4 w-4" />
                    Create Your First Store
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {userStores.map((store) => (
                  <Link
                    key={store.id}
                    to={`/stores/${store.id}`}
                    className="flex items-center justify-between p-5 hover:bg-slate-50/80 transition-colors group"
                    data-testid={`store-row-${store.id}`}
                  >
                    <div className="flex items-center gap-4 flex-1 min-w-0">
                      <div 
                        className="flex h-12 w-12 items-center justify-center rounded-xl shrink-0"
                        style={{ backgroundColor: `${store.branding?.primary_color || '#6366f1'}20` }}
                      >
                        <Store 
                          className="h-6 w-6" 
                          style={{ color: store.branding?.primary_color || '#6366f1' }} 
                        />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors truncate">
                          {store.name}
                        </p>
                        <p className="text-sm text-slate-500 truncate">
                          {store.tagline || 'No tagline set'}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 shrink-0">
                      <Badge className={`${getStatusColor(store.status)} border px-3 py-1 text-xs font-medium capitalize`}>
                        {store.status}
                      </Badge>
                      <ArrowRight className="h-5 w-5 text-slate-400 group-hover:text-indigo-600 transition-colors" />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Intelligence Dashboard Section */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-manrope text-xl font-bold text-slate-900 flex items-center gap-2">
                <LayoutDashboard className="h-6 w-6 text-indigo-500" />
                Intelligence Dashboard
              </h2>
              <p className="text-slate-500 mt-1">Real-time market insights and personalized tracking</p>
            </div>
          </div>

          <Tabs defaultValue="winners" className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-6">
              <TabsTrigger value="winners" className="flex items-center gap-2" data-testid="tab-winners">
                <Trophy className="h-4 w-4" />
                <span className="hidden sm:inline">Winners</span>
              </TabsTrigger>
              <TabsTrigger value="radar" className="flex items-center gap-2" data-testid="tab-radar">
                <Radar className="h-4 w-4" />
                <span className="hidden sm:inline">Radar</span>
              </TabsTrigger>
              <TabsTrigger value="watchlist" className="flex items-center gap-2" data-testid="tab-watchlist">
                <Eye className="h-4 w-4" />
                <span className="hidden sm:inline">Watchlist</span>
              </TabsTrigger>
              <TabsTrigger value="alerts" className="flex items-center gap-2" data-testid="tab-alerts">
                <Bell className="h-4 w-4" />
                <span className="hidden sm:inline">Alerts</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="winners">
              <DailyWinnersPanel limit={5} />
            </TabsContent>

            <TabsContent value="radar">
              <MarketRadar limit={5} />
            </TabsContent>

            <TabsContent value="watchlist">
              <OpportunityWatchlist limit={5} />
            </TabsContent>

            <TabsContent value="alerts">
              <AlertsPanel limit={5} />
            </TabsContent>
          </Tabs>
        </div>

        {/* Quick Action Footer */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-center text-white">
          <h2 className="font-manrope text-2xl font-bold mb-2">Ready to launch your next store?</h2>
          <p className="text-indigo-100 mb-6">Browse winning products and create your Shopify-ready store in minutes</p>
          <Link to="/discover">
            <Button 
              size="lg" 
              className="bg-white text-indigo-600 hover:bg-indigo-50 font-semibold px-8"
              data-testid="cta-browse-products"
            >
              <Zap className="mr-2 h-5 w-5" />
              Find Winning Products
            </Button>
          </Link>
        </div>
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
