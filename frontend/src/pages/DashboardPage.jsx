import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  Package, 
  TrendingUp, 
  Target, 
  Flame,
  Eye,
  ArrowUpRight,
  ArrowDownRight,
  ArrowRight,
  Zap,
  Clock,
  DollarSign,
  BarChart3,
  Activity,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import { getProducts, getDashboardStats } from '@/services/productService';
import { formatNumber, formatCurrency, getTrendStageColor, getOpportunityColor, getTrendScoreColor } from '@/lib/utils';

// Mock trend data for charts
const generateTrendData = () => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days.map((day, i) => ({
    day,
    products: Math.floor(Math.random() * 20) + 30 + i * 2,
    views: Math.floor(Math.random() * 500000) + 1000000 + i * 100000,
    opportunities: Math.floor(Math.random() * 10) + 5 + i,
  }));
};

const generateCategoryData = (products) => {
  const categories = {};
  products.forEach(p => {
    categories[p.category] = (categories[p.category] || 0) + 1;
  });
  return Object.entries(categories).map(([name, value]) => ({ name, value }));
};

const CHART_COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');
  const [trendData] = useState(generateTrendData());

  useEffect(() => {
    const fetchData = async () => {
      const [statsResult, productsResult] = await Promise.all([
        getDashboardStats(),
        getProducts({ sortBy: 'trend_score', sortOrder: 'desc' })
      ]);

      if (statsResult.data) setStats(statsResult.data);
      if (productsResult.data) {
        setProducts(productsResult.data);
        setTopProducts(productsResult.data.slice(0, 5));
      }
      setLoading(false);
    };

    fetchData();
  }, []);

  const categoryData = generateCategoryData(products);

  // Calculate additional stats
  const avgMargin = products.length > 0 
    ? products.reduce((sum, p) => sum + (p.estimated_margin || 0), 0) / products.length 
    : 0;
  
  const earlyStageCount = products.filter(p => p.trend_stage === 'early').length;
  const totalAdCount = products.reduce((sum, p) => sum + (p.ad_count || 0), 0);

  const statCards = [
    {
      title: 'Total Products',
      value: stats?.totalProducts || 0,
      change: '+12%',
      changeType: 'positive',
      icon: Package,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      borderColor: 'border-indigo-100'
    },
    {
      title: 'Avg Trend Score',
      value: stats?.avgTrendScore || 0,
      change: '+5.2%',
      changeType: 'positive',
      icon: TrendingUp,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-100'
    },
    {
      title: 'High Opportunity',
      value: stats?.highOpportunityCount || 0,
      change: '+8',
      changeType: 'positive',
      icon: Target,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-100'
    },
    {
      title: 'Rising Trends',
      value: stats?.risingProducts || 0,
      change: '+3',
      changeType: 'positive',
      icon: Flame,
      color: 'text-rose-600',
      bgColor: 'bg-rose-50',
      borderColor: 'border-rose-100'
    }
  ];

  const secondaryStats = [
    {
      title: 'Avg Margin',
      value: formatCurrency(avgMargin),
      icon: DollarSign,
      color: 'text-emerald-600'
    },
    {
      title: 'Early Stage',
      value: earlyStageCount,
      icon: Zap,
      color: 'text-purple-600'
    },
    {
      title: 'Total Ads Tracked',
      value: formatNumber(totalAdCount),
      icon: BarChart3,
      color: 'text-blue-600'
    },
    {
      title: 'TikTok Views',
      value: formatNumber(stats?.totalTikTokViews || 0),
      icon: Eye,
      color: 'text-pink-600'
    }
  ];

  const recentActivity = [
    { action: 'New trending product detected', product: 'Portable Neck Fan', time: '2 mins ago', type: 'new' },
    { action: 'Trend score increased', product: 'Sunset Lamp', time: '15 mins ago', type: 'up' },
    { action: 'Competition level changed', product: 'Smart Bottle', time: '1 hour ago', type: 'alert' },
    { action: 'New supplier found', product: 'Mini Projector', time: '2 hours ago', type: 'new' },
    { action: 'Market saturation warning', product: 'LED Strips', time: '3 hours ago', type: 'warning' },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="mt-1 text-slate-500">Your product research command center</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-[140px] h-9 bg-white" data-testid="time-range-select">
                <Clock className="mr-2 h-4 w-4 text-slate-400" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24h">Last 24 hours</SelectItem>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm" className="h-9" data-testid="refresh-btn">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Primary Stats Grid */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4" data-testid="stats-grid">
          {statCards.map((stat) => (
            <Card 
              key={stat.title} 
              className={`border ${stat.borderColor} shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden group`}
            >
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                    <p className="font-mono text-3xl font-bold text-slate-900">
                      {loading ? (
                        <span className="inline-block w-16 h-8 bg-slate-100 animate-pulse rounded" />
                      ) : (
                        formatNumber(stat.value)
                      )}
                    </p>
                    <div className={`flex items-center gap-1 text-sm ${
                      stat.changeType === 'positive' ? 'text-emerald-600' : 'text-rose-600'
                    }`}>
                      {stat.changeType === 'positive' ? (
                        <ArrowUpRight className="h-4 w-4" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4" />
                      )}
                      <span className="font-medium">{stat.change}</span>
                      <span className="text-slate-400">vs last period</span>
                    </div>
                  </div>
                  <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${stat.bgColor} group-hover:scale-110 transition-transform duration-300`}>
                    <stat.icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trend Chart - Takes 2 columns */}
          <Card className="border-slate-200 shadow-sm lg:col-span-2">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="font-manrope text-base font-semibold text-slate-900">
                    Trend Activity
                  </CardTitle>
                  <p className="text-sm text-slate-500 mt-0.5">Products & opportunities over time</p>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-indigo-500" />
                    <span className="text-slate-500">Products</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-emerald-500" />
                    <span className="text-slate-500">Opportunities</span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorProducts" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#4F46E5" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorOpportunities" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                    <XAxis 
                      dataKey="day" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: '#94A3B8', fontSize: 12 }}
                    />
                    <YAxis 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: '#94A3B8', fontSize: 12 }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #E2E8F0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                      }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="products" 
                      stroke="#4F46E5" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorProducts)" 
                    />
                    <Area 
                      type="monotone" 
                      dataKey="opportunities" 
                      stroke="#10B981" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorOpportunities)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Category Distribution */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="font-manrope text-base font-semibold text-slate-900">
                Category Distribution
              </CardTitle>
              <p className="text-sm text-slate-500 mt-0.5">Products by category</p>
            </CardHeader>
            <CardContent className="pt-2">
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #E2E8F0',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap gap-2 mt-2 justify-center">
                {categoryData.slice(0, 4).map((cat, i) => (
                  <div key={cat.name} className="flex items-center gap-1.5 text-xs">
                    <div 
                      className="w-2.5 h-2.5 rounded-full" 
                      style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }}
                    />
                    <span className="text-slate-600">{cat.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Secondary Stats Bar */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {secondaryStats.map((stat) => (
            <div
              key={stat.title}
              className="flex items-center gap-3 p-4 rounded-xl bg-white border border-slate-200 hover:border-slate-300 transition-colors"
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-slate-50`}>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{stat.title}</p>
                <p className="font-mono text-lg font-bold text-slate-900">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Row - Products & Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Top Products - Takes 2 columns */}
          <Card className="border-slate-200 shadow-sm lg:col-span-2">
            <CardHeader className="border-b border-slate-100 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="font-manrope text-base font-semibold text-slate-900">
                    Top Trending Products
                  </CardTitle>
                  <p className="text-sm text-slate-500 mt-0.5">Highest performing products this week</p>
                </div>
                <Link 
                  to="/discover" 
                  className="flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
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
                  <div className="p-8 text-center text-slate-500">
                    <div className="inline-block w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                  </div>
                ) : topProducts.length === 0 ? (
                  <div className="p-8 text-center text-slate-500">No products found</div>
                ) : (
                  topProducts.map((product, index) => (
                    <Link
                      key={product.id}
                      to={`/product/${product.id}`}
                      className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors group"
                      data-testid={`product-row-${product.id}`}
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 font-mono text-sm font-bold text-slate-400">
                          {index + 1}
                        </div>
                        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-slate-100 to-slate-50 group-hover:from-indigo-50 group-hover:to-slate-50 transition-colors">
                          <Package className="h-5 w-5 text-slate-400 group-hover:text-indigo-500 transition-colors" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-900 group-hover:text-indigo-600 transition-colors">
                            {product.product_name}
                          </p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-sm text-slate-500">{product.category}</span>
                            <span className="text-slate-300">•</span>
                            <span className="text-sm text-slate-500">{formatCurrency(product.estimated_margin)} margin</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right mr-2">
                          <p className={`font-mono text-xl font-bold ${getTrendScoreColor(product.trend_score)}`}>
                            {product.trend_score}
                          </p>
                        </div>
                        <Badge 
                          className={`${getTrendStageColor(product.trend_stage)} border px-2 py-0.5 text-xs font-semibold uppercase tracking-wider`}
                        >
                          {product.trend_stage}
                        </Badge>
                        <Badge 
                          className={`${getOpportunityColor(product.opportunity_rating)} border px-2 py-0.5 text-xs font-semibold uppercase tracking-wider hidden sm:inline-flex`}
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

          {/* Activity Feed */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="border-b border-slate-100 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="font-manrope text-base font-semibold text-slate-900 flex items-center gap-2">
                    <Activity className="h-4 w-4 text-indigo-600" />
                    Recent Activity
                  </CardTitle>
                </div>
                <Badge variant="outline" className="text-xs">Live</Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                {recentActivity.map((activity, index) => (
                  <div 
                    key={index}
                    className="flex items-start gap-3 p-4 hover:bg-slate-50 transition-colors"
                  >
                    <div className={`flex-shrink-0 mt-0.5 h-8 w-8 rounded-full flex items-center justify-center ${
                      activity.type === 'new' ? 'bg-emerald-50' :
                      activity.type === 'up' ? 'bg-blue-50' :
                      activity.type === 'warning' ? 'bg-amber-50' :
                      'bg-slate-50'
                    }`}>
                      {activity.type === 'new' ? (
                        <Sparkles className="h-4 w-4 text-emerald-600" />
                      ) : activity.type === 'up' ? (
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                      ) : activity.type === 'warning' ? (
                        <Activity className="h-4 w-4 text-amber-600" />
                      ) : (
                        <Zap className="h-4 w-4 text-slate-600" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-600">{activity.action}</p>
                      <p className="text-sm font-medium text-slate-900 truncate">{activity.product}</p>
                      <p className="text-xs text-slate-400 mt-1">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="border-slate-200 shadow-sm bg-gradient-to-r from-indigo-50/50 to-purple-50/50">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-200">
                  <Zap className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="font-manrope text-lg font-semibold text-slate-900">
                    Ready to find your next winner?
                  </h3>
                  <p className="text-slate-500">Explore trending products across all categories</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Link to="/saved">
                  <Button variant="outline" data-testid="view-saved-btn">
                    View Saved
                  </Button>
                </Link>
                <Link to="/discover">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-200" data-testid="discover-btn">
                    Discover Products
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
