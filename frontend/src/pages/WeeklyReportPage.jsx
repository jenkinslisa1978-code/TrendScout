/**
 * Weekly Winning Products Report Page
 * 
 * Full report view with interactive sections
 */

import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Trophy, 
  TrendingUp,
  TrendingDown,
  Package,
  Lock,
  Download,
  ChevronRight,
  ChevronLeft,
  ArrowRight,
  Loader2,
  AlertTriangle,
  CheckCircle,
  Target,
  Zap,
  DollarSign,
  Shield,
  BarChart3,
  Calendar,
  Eye
} from 'lucide-react';
import { getWeeklyReport, getReportBySlug } from '@/services/reportsService';
import { useAuth } from '@/contexts/AuthContext';

export default function WeeklyReportPage() {
  const { slug } = useParams();
  const { profile, user } = useAuth();
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState(0);
  
  const userPlan = profile?.plan || 'free';

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      
      let data;
      if (slug) {
        data = await getReportBySlug(slug);
      } else {
        data = await getWeeklyReport();
      }
      
      setReportData(data);
      setLoading(false);
    };
    
    fetchReport();
  }, [slug]);

  const report = reportData?.report;
  const sections = report?.sections || [];
  const summary = report?.summary || {};
  const metadata = report?.metadata || {};

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const getTrendBadge = (stage) => {
    switch (stage) {
      case 'exploding':
        return { color: 'bg-red-100 text-red-700 border-red-200', icon: Zap };
      case 'rising':
        return { color: 'bg-green-100 text-green-700 border-green-200', icon: TrendingUp };
      case 'early':
        return { color: 'bg-blue-100 text-blue-700 border-blue-200', icon: Target };
      case 'stable':
        return { color: 'bg-slate-100 text-slate-600 border-slate-200', icon: BarChart3 };
      case 'saturated':
        return { color: 'bg-orange-100 text-orange-700 border-orange-200', icon: AlertTriangle };
      default:
        return { color: 'bg-slate-100 text-slate-600 border-slate-200', icon: BarChart3 };
    }
  };

  const getCompetitionColor = (level) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-amber-600 bg-amber-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-slate-600 bg-slate-50';
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-amber-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!report) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <Trophy className="h-16 w-16 text-amber-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-700">Report Not Found</h2>
          <p className="text-slate-500 mt-2">This report may not have been generated yet.</p>
          <Link to="/reports">
            <Button className="mt-4">
              <ChevronLeft className="h-4 w-4 mr-1" />
              Back to Reports
            </Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-7xl mx-auto" data-testid="weekly-report-page">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div>
            <Link to="/reports" className="text-sm text-amber-600 hover:text-amber-700 flex items-center gap-1 mb-2">
              <ChevronLeft className="h-4 w-4" />
              Back to Reports
            </Link>
            <h1 className="font-manrope text-2xl lg:text-3xl font-bold text-slate-900 flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
                <Trophy className="h-7 w-7 text-amber-600" />
              </div>
              {metadata.title}
            </h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                {formatDate(metadata.generated_at)}
              </span>
              <span className="flex items-center gap-1">
                <Package className="h-4 w-4" />
                {summary.total_products_analyzed || 0} products analyzed
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge className="bg-amber-100 text-amber-700 border border-amber-200 px-3 py-1 capitalize">
              {userPlan} Plan
            </Badge>
            <Button variant="outline" className="border-amber-300 text-amber-700" disabled>
              <Download className="h-4 w-4 mr-2" />
              PDF (Coming Soon)
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-green-600 font-medium">Avg Success Rate</p>
                  <p className="text-2xl font-bold text-green-700">{summary.avg_success_probability || 0}%</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-blue-600 font-medium">Low Competition</p>
                  <p className="text-2xl font-bold text-blue-700">{summary.low_competition_opportunities || 0}</p>
                </div>
                <Shield className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-violet-50 border-purple-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-purple-600 font-medium">Avg Margin</p>
                  <p className="text-2xl font-bold text-purple-700">£{summary.avg_margin || 0}</p>
                </div>
                <DollarSign className="h-8 w-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-amber-50 border-orange-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-orange-600 font-medium">Saturation Warnings</p>
                  <p className="text-2xl font-bold text-orange-700">{summary.saturation_warnings || 0}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Report Sections */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Section Navigation */}
          <Card className="lg:col-span-1 border-0 shadow-lg">
            <CardHeader className="border-b border-slate-100">
              <CardTitle className="text-lg font-semibold">Report Sections</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                {sections.map((section, index) => {
                  const isLocked = section.locked;
                  const isActive = activeSection === index;
                  
                  return (
                    <button
                      key={index}
                      onClick={() => !isLocked && setActiveSection(index)}
                      disabled={isLocked}
                      className={`w-full p-4 text-left flex items-center justify-between transition-colors ${
                        isActive ? 'bg-amber-50 border-l-4 border-amber-500' : 'hover:bg-slate-50'
                      } ${isLocked ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      <div className="flex-1 min-w-0">
                        <p className={`font-medium truncate ${isActive ? 'text-amber-700' : 'text-slate-700'}`}>
                          {section.title}
                        </p>
                        <p className="text-xs text-slate-500 mt-0.5 truncate">
                          {section.description}
                        </p>
                      </div>
                      {isLocked ? (
                        <Lock className="h-4 w-4 text-slate-400 flex-shrink-0 ml-2" />
                      ) : (
                        <ChevronRight className={`h-4 w-4 flex-shrink-0 ml-2 ${isActive ? 'text-amber-500' : 'text-slate-400'}`} />
                      )}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Section Content */}
          <Card className="lg:col-span-2 border-0 shadow-lg">
            <CardHeader className="border-b border-slate-100">
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                {sections[activeSection]?.locked ? (
                  <Lock className="h-5 w-5 text-slate-400" />
                ) : (
                  <Trophy className="h-5 w-5 text-amber-500" />
                )}
                {sections[activeSection]?.title}
              </CardTitle>
              <p className="text-sm text-slate-500">{sections[activeSection]?.description}</p>
            </CardHeader>
            <CardContent className="p-6">
              {sections[activeSection]?.locked ? (
                <div className="text-center py-12">
                  <Lock className="h-16 w-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-700">
                    {sections[activeSection]?.unlock_message}
                  </h3>
                  <p className="text-slate-500 mt-2 max-w-md mx-auto">
                    This section requires a higher subscription tier to access.
                  </p>
                  <Link to="/pricing">
                    <Button className="mt-4 bg-amber-600 hover:bg-amber-700">
                      Upgrade Now
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              ) : (
                <SectionContent 
                  section={sections[activeSection]} 
                  getTrendBadge={getTrendBadge}
                  getCompetitionColor={getCompetitionColor}
                />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Upgrade CTA for Free Users */}
        {userPlan === 'free' && (
          <Card className="bg-gradient-to-r from-amber-500 to-orange-500 border-0 text-white">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <h3 className="text-xl font-bold">Unlock Full Report Access</h3>
                  <p className="text-amber-100 mt-1">
                    Get detailed margins, opportunity clusters, and saturation warnings with Pro or Elite
                  </p>
                </div>
                <Link to="/pricing">
                  <Button size="lg" className="bg-white text-amber-600 hover:bg-amber-50">
                    View Plans
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}

/**
 * Section Content Renderer
 */
function SectionContent({ section, getTrendBadge, getCompetitionColor }) {
  const data = section?.data || {};
  const title = section?.title || '';

  // Top Products Section
  if (title.includes('Top 20') || title.includes('Winning Products')) {
    const products = data.products || [];
    
    return (
      <div className="space-y-3">
        {products.map((product, index) => {
          const trendStyle = getTrendBadge(product.trend_stage);
          const TrendIcon = trendStyle.icon;
          
          return (
            <div key={product.id || index} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                index < 3 ? 'bg-amber-500 text-white' : 'bg-slate-200 text-slate-600'
              }`}>
                {index + 1}
              </div>
              
              <div className="w-12 h-12 rounded-lg bg-white border border-slate-200 flex items-center justify-center flex-shrink-0">
                <Package className="h-6 w-6 text-slate-400" />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-900 truncate">{product.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="outline" className={`text-xs ${trendStyle.color}`}>
                    <TrendIcon className="h-3 w-3 mr-1" />
                    {product.trend_stage}
                  </Badge>
                  <span className={`text-xs px-2 py-0.5 rounded capitalize ${getCompetitionColor(product.competition_level)}`}>
                    {product.competition_level} comp
                  </span>
                </div>
              </div>
              
              <div className="text-right">
                <p className="font-bold text-green-600">{product.success_probability}%</p>
                <p className="text-xs text-slate-500">Success</p>
              </div>
              
              {product.estimated_margin && typeof product.estimated_margin === 'number' && (
                <div className="text-right">
                  <p className="font-bold text-purple-600">£{product.estimated_margin.toFixed(2)}</p>
                  <p className="text-xs text-slate-500">Margin</p>
                </div>
              )}
              
              <Link to={`/product/${product.id}`}>
                <Button size="sm" variant="ghost" className="text-amber-600">
                  <Eye className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          );
        })}
        
        {products.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            <Package className="h-12 w-12 mx-auto mb-3 text-slate-300" />
            <p>No product data available</p>
          </div>
        )}
      </div>
    );
  }

  // Trend Stage Analysis
  if (title.includes('Trend Stage')) {
    const distribution = data.distribution || {};
    const insights = data.insights || [];
    const total = Object.values(distribution).reduce((a, b) => a + b, 0);
    
    return (
      <div className="space-y-6">
        <div className="space-y-3">
          {Object.entries(distribution).map(([stage, count]) => {
            const percent = total > 0 ? (count / total) * 100 : 0;
            const trendStyle = getTrendBadge(stage);
            
            return (
              <div key={stage} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="capitalize font-medium">{stage}</span>
                  <span className="text-slate-500">{count} products ({percent.toFixed(0)}%)</span>
                </div>
                <Progress value={percent} className="h-2" />
              </div>
            );
          })}
        </div>
        
        {insights.length > 0 && (
          <div className="bg-amber-50 rounded-lg p-4">
            <h4 className="font-medium text-amber-800 mb-2">Key Insights</h4>
            <ul className="space-y-1">
              {insights.map((insight, i) => (
                <li key={i} className="text-sm text-amber-700 flex items-start gap-2">
                  <Zap className="h-4 w-4 flex-shrink-0 mt-0.5" />
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  // Competition Analysis
  if (title.includes('Competition')) {
    const distribution = data.distribution || {};
    const insights = data.insights || [];
    
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(distribution).map(([level, count]) => (
            <Card key={level} className={`border ${getCompetitionColor(level).replace('text', 'border')}`}>
              <CardContent className="p-4 text-center">
                <p className="text-3xl font-bold">{count}</p>
                <p className="text-sm capitalize text-slate-600">{level} Competition</p>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {insights.length > 0 && (
          <div className="space-y-2">
            {insights.map((insight, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-slate-600">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                {insight}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Opportunity Clusters
  if (title.includes('Cluster')) {
    const clusters = data.clusters || [];
    
    return (
      <div className="space-y-3">
        {clusters.map((cluster, index) => (
          <div key={cluster.category || index} className="p-4 bg-slate-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-slate-900">{cluster.category}</h4>
              <Badge variant="outline" className="capitalize">
                {cluster.dominant_trend_stage}
              </Badge>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-slate-500">Products</p>
                <p className="font-semibold">{cluster.product_count}</p>
              </div>
              <div>
                <p className="text-slate-500">Avg Success</p>
                <p className="font-semibold text-green-600">{cluster.avg_success_probability?.toFixed(0)}%</p>
              </div>
              <div>
                <p className="text-slate-500">Growth</p>
                <p className={`font-semibold ${cluster.growth_momentum > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {cluster.growth_momentum > 0 ? '+' : ''}{cluster.growth_momentum?.toFixed(0)}%
                </p>
              </div>
            </div>
          </div>
        ))}
        
        {clusters.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            <BarChart3 className="h-12 w-12 mx-auto mb-3 text-slate-300" />
            <p>No cluster data available</p>
          </div>
        )}
      </div>
    );
  }

  // Margin Analysis
  if (title.includes('Margin')) {
    const ranges = data.margin_ranges || {};
    const topMargin = data.top_margin_products || [];
    
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-green-50 border-green-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-green-700">{ranges.excellent_30_plus || 0}</p>
              <p className="text-xs text-green-600">£30+ margin</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-blue-700">{ranges.good_20_30 || 0}</p>
              <p className="text-xs text-blue-600">£20-30 margin</p>
            </CardContent>
          </Card>
          <Card className="bg-amber-50 border-amber-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-amber-700">{ranges.moderate_10_20 || 0}</p>
              <p className="text-xs text-amber-600">£10-20 margin</p>
            </CardContent>
          </Card>
          <Card className="bg-slate-50 border-slate-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-slate-700">{ranges.low_under_10 || 0}</p>
              <p className="text-xs text-slate-600">Under £10</p>
            </CardContent>
          </Card>
        </div>
        
        {topMargin.length > 0 && (
          <div>
            <h4 className="font-medium text-slate-700 mb-3">Top Margin Products</h4>
            <div className="space-y-2">
              {topMargin.map((p, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div>
                    <p className="font-medium text-slate-900">{p.name}</p>
                    <p className="text-xs text-slate-500">{p.category}</p>
                  </div>
                  <p className="font-bold text-green-600">£{p.margin?.toFixed(2)}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Saturation Warning
  if (title.includes('Saturation')) {
    const products = data.saturating_products || [];
    
    return (
      <div className="space-y-4">
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-orange-700">
            <AlertTriangle className="h-5 w-5" />
            <span className="font-medium">{data.total_saturating || 0} products showing saturation signals</span>
          </div>
          <p className="text-sm text-orange-600 mt-1">
            These products may face increased competition and declining margins. Consider avoiding or proceed with caution.
          </p>
        </div>
        
        <div className="space-y-3">
          {products.map((product, index) => (
            <div key={product.id || index} className="flex items-center gap-4 p-3 bg-red-50 rounded-lg border border-red-100">
              <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-900 truncate">{product.name}</p>
                <p className="text-xs text-slate-500">{product.category}</p>
              </div>
              <div className="text-right">
                <p className="font-bold text-red-600">{product.market_saturation}%</p>
                <p className="text-xs text-slate-500">Saturation</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Default fallback
  return (
    <div className="text-center py-8 text-slate-500">
      <BarChart3 className="h-12 w-12 mx-auto mb-3 text-slate-300" />
      <p>Section content not available</p>
    </div>
  );
}
