import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Package, 
  TrendingUp, 
  Target, 
  Flame,
  Eye,
  ArrowUpRight,
  ArrowRight
} from 'lucide-react';
import { getProducts, getDashboardStats } from '@/services/productService';
import { formatNumber, getTrendStageColor, getOpportunityColor, getTrendScoreColor } from '@/lib/utils';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [topProducts, setTopProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const [statsResult, productsResult] = await Promise.all([
        getDashboardStats(),
        getProducts({ sortBy: 'trend_score', sortOrder: 'desc' })
      ]);

      if (statsResult.data) setStats(statsResult.data);
      if (productsResult.data) setTopProducts(productsResult.data.slice(0, 5));
      setLoading(false);
    };

    fetchData();
  }, []);

  const statCards = [
    {
      title: 'Total Products',
      value: stats?.totalProducts || 0,
      icon: Package,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50'
    },
    {
      title: 'Avg Trend Score',
      value: stats?.avgTrendScore || 0,
      icon: TrendingUp,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50'
    },
    {
      title: 'High Opportunity',
      value: stats?.highOpportunityCount || 0,
      icon: Target,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50'
    },
    {
      title: 'Rising Trends',
      value: stats?.risingProducts || 0,
      icon: Flame,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    }
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="font-manrope text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="mt-1 text-slate-500">Overview of your product research</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4" data-testid="stats-grid">
          {statCards.map((stat) => (
            <Card key={stat.title} className="border-slate-200 shadow-sm hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                    <p className="mt-2 font-mono text-3xl font-bold text-slate-900">
                      {loading ? '...' : formatNumber(stat.value)}
                    </p>
                  </div>
                  <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${stat.bgColor}`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* TikTok Views Banner */}
        {stats?.totalTikTokViews > 0 && (
          <Card className="border-indigo-100 bg-gradient-to-r from-indigo-50 to-purple-50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600">
                    <Eye className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-indigo-600">Total TikTok Views Tracked</p>
                    <p className="font-mono text-2xl font-bold text-slate-900">
                      {formatNumber(stats.totalTikTokViews)}
                    </p>
                  </div>
                </div>
                <ArrowUpRight className="h-6 w-6 text-indigo-400" />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Top Products */}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="font-manrope text-lg font-semibold text-slate-900">
                Top Trending Products
              </CardTitle>
              <Link 
                to="/discover" 
                className="flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700"
                data-testid="view-all-products-link"
              >
                View all
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100">
              {loading ? (
                <div className="p-8 text-center text-slate-500">Loading products...</div>
              ) : topProducts.length === 0 ? (
                <div className="p-8 text-center text-slate-500">No products found</div>
              ) : (
                topProducts.map((product) => (
                  <Link
                    key={product.id}
                    to={`/product/${product.id}`}
                    className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
                    data-testid={`product-row-${product.id}`}
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-slate-100">
                        <Package className="h-6 w-6 text-slate-400" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-900">{product.product_name}</p>
                        <p className="text-sm text-slate-500">{product.category}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className={`font-mono text-lg font-semibold ${getTrendScoreColor(product.trend_score)}`}>
                          {product.trend_score}
                        </p>
                        <p className="text-xs text-slate-400">Trend Score</p>
                      </div>
                      <Badge 
                        className={`${getTrendStageColor(product.trend_stage)} border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider`}
                      >
                        {product.trend_stage}
                      </Badge>
                      <Badge 
                        className={`${getOpportunityColor(product.opportunity_rating)} border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider`}
                      >
                        {product.opportunity_rating}
                      </Badge>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
