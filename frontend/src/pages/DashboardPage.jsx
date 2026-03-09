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
      gradient: 'from-indigo-500 to-indigo-600',
      bgGradient: 'from-indigo-50 to-indigo-100/50',
      iconBg: 'bg-indigo-100',
      iconColor: 'text-indigo-600'
    },
    {
      title: 'Avg Trend Score',
      value: stats?.avgTrendScore || 0,
      change: '+5.2%',
      changeType: 'positive',
      icon: TrendingUp,
      gradient: 'from-emerald-500 to-emerald-600',
      bgGradient: 'from-emerald-50 to-emerald-100/50',
      iconBg: 'bg-emerald-100',
      iconColor: 'text-emerald-600'
    },
    {
      title: 'High Opportunity',
      value: stats?.highOpportunityCount || 0,
      change: '+8',
      changeType: 'positive',
      icon: Target,
      gradient: 'from-amber-500 to-amber-600',
      bgGradient: 'from-amber-50 to-amber-100/50',
      iconBg: 'bg-amber-100',
      iconColor: 'text-amber-600'
    },
    {
      title: 'Rising Trends',
      value: stats?.risingProducts || 0,
      change: '+3',
      changeType: 'positive',
      icon: Flame,
      gradient: 'from-rose-500 to-rose-600',
      bgGradient: 'from-rose-50 to-rose-100/50',
      iconBg: 'bg-rose-100',
      iconColor: 'text-rose-600'
    }
  ];

  const secondaryStats = [
    { title: 'Avg Margin', value: formatCurrency(avgMargin), icon: DollarSign, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { title: 'Early Stage', value: earlyStageCount, icon: Zap, color: 'text-purple-600', bg: 'bg-purple-50' },
    { title: 'Ads Tracked', value: formatNumber(totalAdCount), icon: BarChart3, color: 'text-blue-600', bg: 'bg-blue-50' },
    { title: 'TikTok Views', value: formatNumber(stats?.totalTikTokViews || 0), icon: Eye, color: 'text-pink-600', bg: 'bg-pink-50' }
  ];

  const recentActivity = [
    { action: 'New trending product detected', product: 'Portable Neck Fan', time: '2 mins ago', type: 'new' },
    { action: 'Trend score increased', product: 'Sunset Lamp', time: '15 mins ago', type: 'up' },
    { action: 'Competition level changed', product: 'Smart Bottle', time: '1 hour ago', type: 'alert' },
    { action: 'New supplier found', product: 'Mini Projector', time: '2 hours ago', type: 'new' },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Premium Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="font-manrope text-3xl font-extrabold text-slate-900 tracking-tight">Dashboard</h1>
            <p className="mt-1 text-slate-500">Your product research command center</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-[150px] h-10 bg-white border-slate-200 shadow-sm" data-testid="time-range-select">
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
            <Button variant="outline" size="icon" className="h-10 w-10 shadow-sm" data-testid="refresh-btn">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Premium Stats Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4" data-testid="stats-grid">
          {statCards.map((stat, index) => (
            <Card 
              key={stat.title} 
              className="relative overflow-hidden border-0 shadow-card hover:shadow-card-hover transition-all duration-300 card-premium stat-card-shine"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Gradient accent line */}
              <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${stat.gradient}`} />
              
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-3">
                    <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">{stat.title}</p>
                    <p className="font-mono text-4xl font-bold text-slate-900 number-display">
                      {loading ? (
                        <span className="inline-block w-16 h-10 bg-slate-100 animate-pulse rounded-lg" />
                      ) : (
                        formatNumber(stat.value)
                      )}
                    </p>
                    <div className="flex items-center gap-1.5 text-sm">
                      <span className="flex items-center gap-0.5 text-emerald-600 font-semibold">
                        <ArrowUpRight className="h-4 w-4" />
                        {stat.change}
                      </span>
                      <span className="text-slate-400">vs last period</span>
                    </div>
                  </div>
                  <div className={`flex h-14 w-14 items-center justify-center rounded-2xl ${stat.iconBg} transition-transform duration-300 group-hover:scale-110`}>
                    <stat.icon className={`h-7 w-7 ${stat.iconColor}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trend Chart */}
          <Card className="border-0 shadow-card lg:col-span-2">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="font-manrope text-lg font-bold text-slate-900">
                    Trend Activity
                  </CardTitle>
                  <p className="text-sm text-slate-500 mt-1">Products & opportunities over time</p>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-indigo-500 shadow-sm" />
                    <span className="text-slate-600 font-medium">Products</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm" />
                    <span className="text-slate-600 font-medium">Opportunities</span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-2">
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorProducts" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.15}/>
                        <stop offset="95%" stopColor="#4F46E5" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorOpportunities" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.15}/>
                        <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                    <XAxis 
                      dataKey="day" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: '#94A3B8', fontSize: 12, fontWeight: 500 }}
                    />
                    <YAxis 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: '#94A3B8', fontSize: 12 }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: 'none',
                        borderRadius: '12px',
                        boxShadow: '0 10px 40px -10px rgba(0,0,0,0.2)',
                        padding: '12px 16px'
                      }}
                      labelStyle={{ fontWeight: 600, color: '#0F172A' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="products" 
                      stroke="#4F46E5" 
                      strokeWidth={2.5}
                      fillOpacity={1} 
                      fill="url(#colorProducts)" 
                    />
                    <Area 
                      type="monotone" 
                      dataKey="opportunities" 
                      stroke="#10B981" 
                      strokeWidth={2.5}
                      fillOpacity={1} 
                      fill="url(#colorOpportunities)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Category Distribution */}
          <Card className="border-0 shadow-card">
            <CardHeader className="pb-2">
              <CardTitle className="font-manrope text-lg font-bold text-slate-900">
                Category Mix
              </CardTitle>
              <p className="text-sm text-slate-500 mt-1">Products by category</p>
            </CardHeader>
            <CardContent className="pt-2">
              <div className="h-[220px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={85}
                      paddingAngle={3}
                      dataKey="value"
                      strokeWidth={0}
                    >
                      {categoryData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={CHART_COLORS[index % CHART_COLORS.length]} 
                        />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: 'none',
                        borderRadius: '12px',
                        boxShadow: '0 10px 40px -10px rgba(0,0,0,0.2)'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap gap-3 mt-4 justify-center">
                {categoryData.slice(0, 4).map((cat, i) => (
                  <div key={cat.name} className="flex items-center gap-2 text-xs bg-slate-50 px-3 py-1.5 rounded-full">
                    <div 
                      className="w-2.5 h-2.5 rounded-full" 
                      style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }}
                    />
                    <span className="text-slate-700 font-medium">{cat.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Secondary Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {secondaryStats.map((stat) => (
            <div
              key={stat.title}
              className="flex items-center gap-4 p-5 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-all duration-200"
            >
              <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${stat.bg}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{stat.title}</p>
                <p className="font-mono text-xl font-bold text-slate-900 mt-0.5">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Top Products */}
          <Card className="border-0 shadow-card lg:col-span-2">
            <CardHeader className="border-b border-slate-100 pb-5">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="font-manrope text-lg font-bold text-slate-900">
                    Top Trending Products
                  </CardTitle>
                  <p className="text-sm text-slate-500 mt-1">Highest performing products this week</p>
                </div>
                <Link 
                  to="/discover" 
                  className="flex items-center gap-1.5 text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
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
                    <div className="inline-block w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                  </div>
                ) : topProducts.length === 0 ? (
                  <div className="p-8 text-center text-slate-500">No products found</div>
                ) : (
                  topProducts.map((product, index) => (
                    <Link
                      key={product.id}
                      to={`/product/${product.id}`}
                      className="flex items-center justify-between p-5 hover:bg-slate-50/80 transition-colors group"
                      data-testid={`product-row-${product.id}`}
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-slate-100 to-slate-50 font-mono text-sm font-bold text-slate-500 border border-slate-200/50">
                          {String(index + 1).padStart(2, '0')}
                        </div>
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-50 to-slate-50 group-hover:from-indigo-100 transition-colors">
                          <Package className="h-6 w-6 text-indigo-500" />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
                            {product.product_name}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-sm text-slate-500">{product.category}</span>
                            <span className="text-slate-300">•</span>
                            <span className="text-sm font-medium text-emerald-600">{formatCurrency(product.estimated_margin)} margin</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className={`font-mono text-2xl font-bold ${getTrendScoreColor(product.trend_score)}`}>
                            {product.trend_score}
                          </p>
                        </div>
                        <Badge className={`${getTrendStageColor(product.trend_stage)} border px-3 py-1 text-xs font-bold uppercase tracking-wider`}>
                          {product.trend_stage}
                        </Badge>
                        <Badge className={`${getOpportunityColor(product.opportunity_rating)} border px-3 py-1 text-xs font-bold uppercase tracking-wider hidden sm:inline-flex`}>
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
          <Card className="border-0 shadow-card">
            <CardHeader className="border-b border-slate-100 pb-5">
              <div className="flex items-center justify-between">
                <CardTitle className="font-manrope text-lg font-bold text-slate-900 flex items-center gap-2">
                  <Activity className="h-5 w-5 text-indigo-600" />
                  Recent Activity
                </CardTitle>
                <Badge className="bg-emerald-100 text-emerald-700 border-0 text-xs font-semibold px-2.5">
                  Live
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                {recentActivity.map((activity, index) => (
                  <div 
                    key={index}
                    className="flex items-start gap-4 p-5 hover:bg-slate-50/80 transition-colors"
                  >
                    <div className={`flex-shrink-0 mt-0.5 h-10 w-10 rounded-xl flex items-center justify-center ${
                      activity.type === 'new' ? 'bg-emerald-100' :
                      activity.type === 'up' ? 'bg-blue-100' :
                      activity.type === 'warning' ? 'bg-amber-100' :
                      'bg-slate-100'
                    }`}>
                      {activity.type === 'new' ? (
                        <Sparkles className="h-5 w-5 text-emerald-600" />
                      ) : activity.type === 'up' ? (
                        <TrendingUp className="h-5 w-5 text-blue-600" />
                      ) : activity.type === 'warning' ? (
                        <Activity className="h-5 w-5 text-amber-600" />
                      ) : (
                        <Zap className="h-5 w-5 text-slate-600" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-600">{activity.action}</p>
                      <p className="text-sm font-semibold text-slate-900 truncate mt-0.5">{activity.product}</p>
                      <p className="text-xs text-slate-400 mt-1.5">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions CTA */}
        <Card className="border-0 shadow-card bg-gradient-to-r from-indigo-600 via-indigo-600 to-purple-600 overflow-hidden">
          <CardContent className="p-8 relative">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/3" />
            <div className="absolute bottom-0 left-1/4 w-64 h-64 bg-white/5 rounded-full translate-y-1/2" />
            
            <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
              <div className="flex items-center gap-5">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm">
                  <Zap className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="font-manrope text-xl font-bold text-white">
                    Ready to find your next winner?
                  </h3>
                  <p className="text-indigo-100 mt-1">Explore trending products across all categories</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Link to="/saved">
                  <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20 backdrop-blur-sm" data-testid="view-saved-btn">
                    View Saved
                  </Button>
                </Link>
                <Link to="/discover">
                  <Button className="bg-white text-indigo-600 hover:bg-white/90 shadow-lg font-semibold" data-testid="discover-btn">
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
