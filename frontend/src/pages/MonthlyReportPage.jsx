/**
 * Monthly Market Trends Report Page
 * 
 * Full report view with category insights and market predictions
 */

import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  TrendingUp,
  TrendingDown,
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
  Calendar,
  Layers,
  Eye,
  Flame,
  Activity,
  Scale
} from 'lucide-react';
import { getMonthlyReport, getReportBySlug } from '@/services/reportsService';
import { useAuth } from '@/contexts/AuthContext';

export default function MonthlyReportPage() {
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
        data = await getMonthlyReport();
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

  const getHealthColor = (status) => {
    switch (status) {
      case 'excellent': return 'bg-green-100 text-green-700 border-green-200';
      case 'good': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'moderate': return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'challenging': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!report) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <BarChart3 className="h-16 w-16 text-purple-300 mx-auto mb-4" />
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

  const marketHealth = summary.market_health || {};

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-7xl mx-auto" data-testid="monthly-report-page">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div>
            <Link to="/reports" className="text-sm text-purple-600 hover:text-purple-700 flex items-center gap-1 mb-2">
              <ChevronLeft className="h-4 w-4" />
              Back to Reports
            </Link>
            <h1 className="font-manrope text-2xl lg:text-3xl font-bold text-slate-900 flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
                <BarChart3 className="h-7 w-7 text-purple-600" />
              </div>
              {metadata.title}
            </h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                {formatDate(metadata.generated_at)}
              </span>
              <span className="flex items-center gap-1">
                <Layers className="h-4 w-4" />
                {summary.total_categories || 0} categories analyzed
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge className="bg-purple-100 text-purple-700 border border-purple-200 px-3 py-1 capitalize">
              {userPlan} Plan
            </Badge>
            <Button variant="outline" className="border-purple-300 text-purple-700" disabled>
              <Download className="h-4 w-4 mr-2" />
              PDF (Coming Soon)
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className={`border-2 ${getHealthColor(marketHealth.status)}`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium">Market Health</p>
                  <p className="text-2xl font-bold capitalize">{marketHealth.status || 'N/A'}</p>
                </div>
                <Activity className="h-8 w-8 opacity-40" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-green-600 font-medium">Growing Categories</p>
                  <p className="text-2xl font-bold text-green-700">{marketHealth.growing_categories || 0}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-blue-600 font-medium">Emerging</p>
                  <p className="text-2xl font-bold text-blue-700">{summary.emerging_categories_count || 0}</p>
                </div>
                <Flame className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-amber-50 border-orange-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-orange-600 font-medium">Saturating</p>
                  <p className="text-2xl font-bold text-orange-700">{summary.saturating_categories_count || 0}</p>
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
                        isActive ? 'bg-purple-50 border-l-4 border-purple-500' : 'hover:bg-slate-50'
                      } ${isLocked ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
                    >
                      <div className="flex-1 min-w-0">
                        <p className={`font-medium truncate ${isActive ? 'text-purple-700' : 'text-slate-700'}`}>
                          {section.title}
                        </p>
                        <p className="text-xs text-slate-500 mt-0.5 truncate">
                          {section.description}
                        </p>
                      </div>
                      {isLocked ? (
                        <Lock className="h-4 w-4 text-slate-400 flex-shrink-0 ml-2" />
                      ) : (
                        <ChevronRight className={`h-4 w-4 flex-shrink-0 ml-2 ${isActive ? 'text-purple-500' : 'text-slate-400'}`} />
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
                  <BarChart3 className="h-5 w-5 text-purple-500" />
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
                    <Button className="mt-4 bg-purple-600 hover:bg-purple-700">
                      Upgrade Now
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              ) : (
                <MonthlySectionContent section={sections[activeSection]} />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Upgrade CTA for Free Users */}
        {userPlan === 'free' && (
          <Card className="bg-gradient-to-r from-purple-500 to-indigo-600 border-0 text-white">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <h3 className="text-xl font-bold">Unlock Full Market Analysis</h3>
                  <p className="text-purple-100 mt-1">
                    Get category predictions, demand analysis, and saturation warnings with Pro or Elite
                  </p>
                </div>
                <Link to="/pricing">
                  <Button size="lg" className="bg-white text-purple-600 hover:bg-purple-50">
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
 * Monthly Section Content Renderer
 */
function MonthlySectionContent({ section }) {
  const data = section?.data || {};
  const title = section?.title || '';

  // Emerging Categories
  if (title.includes('Emerging')) {
    const categories = data.categories || [];
    const insights = data.insights || [];
    
    return (
      <div className="space-y-4">
        {insights.length > 0 && (
          <div className="bg-green-50 rounded-lg p-4 mb-4">
            <h4 className="font-medium text-green-800 mb-2">Key Insights</h4>
            <ul className="space-y-1">
              {insights.map((insight, i) => (
                <li key={i} className="text-sm text-green-700 flex items-start gap-2">
                  <Zap className="h-4 w-4 flex-shrink-0 mt-0.5" />
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="space-y-3">
          {categories.map((cat, index) => (
            <div key={cat.category || index} className="p-4 bg-slate-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    index < 3 ? 'bg-green-500 text-white' : 'bg-slate-200 text-slate-600'
                  }`}>
                    {index + 1}
                  </div>
                  <h4 className="font-medium text-slate-900">{cat.category}</h4>
                </div>
                <Badge className={cat.signal_strength === 'strong' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}>
                  {cat.signal_strength} signal
                </Badge>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm ml-10">
                <div>
                  <p className="text-slate-500">Products</p>
                  <p className="font-semibold">{cat.product_count}</p>
                </div>
                <div>
                  <p className="text-slate-500">Emergence Score</p>
                  <p className="font-semibold text-green-600">{cat.emergence_score}</p>
                </div>
                <div>
                  <p className="text-slate-500">Growth</p>
                  <p className={`font-semibold ${cat.growth_momentum > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {cat.growth_momentum > 0 ? '+' : ''}{cat.growth_momentum?.toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {categories.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            <Layers className="h-12 w-12 mx-auto mb-3 text-slate-300" />
            <p>No emerging categories detected</p>
          </div>
        )}
      </div>
    );
  }

  // Market Opportunity Clusters
  if (title.includes('Cluster') || title.includes('Opportunity')) {
    const clusters = data.clusters || [];
    
    return (
      <div className="space-y-3">
        {clusters.map((cluster, index) => (
          <div key={cluster.category || index} className="p-4 bg-slate-50 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-slate-900">{cluster.category}</h4>
              <Badge variant="outline" className="capitalize">
                {cluster.dominant_trend_stage}
              </Badge>
            </div>
            <div className="grid grid-cols-4 gap-4 text-sm mb-3">
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
              <div>
                <p className="text-slate-500">Trend</p>
                <p className="font-semibold capitalize">{cluster.dominant_trend_stage}</p>
              </div>
            </div>
            
            {cluster.top_products?.length > 0 && (
              <div className="border-t border-slate-200 pt-3 mt-3">
                <p className="text-xs text-slate-500 mb-2">Top Products:</p>
                <div className="flex flex-wrap gap-2">
                  {cluster.top_products.map((p, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {p.name} ({p.success_probability}%)
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        
        {clusters.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            <Layers className="h-12 w-12 mx-auto mb-3 text-slate-300" />
            <p>No cluster data available</p>
          </div>
        )}
      </div>
    );
  }

  // Demand vs Competition
  if (title.includes('Demand') || title.includes('Competition')) {
    const favorable = data.high_demand_low_competition || [];
    const balanced = data.balanced_markets || [];
    const saturated = data.saturated_markets || [];
    const insights = data.insights || [];
    
    return (
      <div className="space-y-6">
        {insights.length > 0 && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">Market Insights</h4>
            <ul className="space-y-1">
              {insights.map((insight, i) => (
                <li key={i} className="text-sm text-blue-700 flex items-start gap-2">
                  <Scale className="h-4 w-4 flex-shrink-0 mt-0.5" />
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}

        {favorable.length > 0 && (
          <div>
            <h4 className="font-medium text-green-700 flex items-center gap-2 mb-3">
              <CheckCircle className="h-5 w-5" />
              Favorable Markets ({favorable.length})
            </h4>
            <div className="space-y-2">
              {favorable.slice(0, 5).map((cat, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-medium text-slate-900">{cat.category}</span>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-green-600">Demand: {cat.demand_score}</span>
                    <span className="text-slate-500">Competition: {cat.competition_score}</span>
                    <Badge className="bg-green-100 text-green-700">+{cat.opportunity_gap} gap</Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {saturated.length > 0 && (
          <div>
            <h4 className="font-medium text-orange-700 flex items-center gap-2 mb-3">
              <AlertTriangle className="h-5 w-5" />
              Saturated Markets ({saturated.length})
            </h4>
            <div className="space-y-2">
              {saturated.slice(0, 5).map((cat, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                  <span className="font-medium text-slate-900">{cat.category}</span>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-slate-500">Demand: {cat.demand_score}</span>
                    <span className="text-orange-600">Competition: {cat.competition_score}</span>
                    <Badge className="bg-orange-100 text-orange-700">-{cat.saturation_gap} gap</Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Fastest Growing
  if (title.includes('Fastest') || title.includes('Growing')) {
    const growing = data.top_growing || [];
    const metrics = data.growth_metrics || {};
    
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <Card className="bg-green-50 border-green-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-green-700">{metrics.avg_growth || 0}%</p>
              <p className="text-xs text-green-600">Avg Growth</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-blue-700">{metrics.max_growth || 0}%</p>
              <p className="text-xs text-blue-600">Max Growth</p>
            </CardContent>
          </Card>
          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-purple-700">{metrics.rapid_growth_count || 0}</p>
              <p className="text-xs text-purple-600">Rapid Growth (50%+)</p>
            </CardContent>
          </Card>
        </div>
        
        <div className="space-y-2">
          {growing.map((cat, index) => (
            <div key={cat.category || index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                  index < 3 ? 'bg-green-500 text-white' : 'bg-slate-200 text-slate-600'
                }`}>
                  {index + 1}
                </div>
                <div>
                  <p className="font-medium text-slate-900">{cat.category}</p>
                  <p className="text-xs text-slate-500">{cat.product_count} products</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="font-bold text-green-600">+{cat.growth_momentum?.toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Categories to Watch
  if (title.includes('Watch')) {
    const watchList = data.watch_list || [];
    const predictions = data.predictions || [];
    
    return (
      <div className="space-y-4">
        {predictions.length > 0 && (
          <div className="bg-purple-50 rounded-lg p-4 mb-4">
            <h4 className="font-medium text-purple-800 mb-2">Predictions</h4>
            <ul className="space-y-1">
              {predictions.map((pred, i) => (
                <li key={i} className="text-sm text-purple-700 flex items-start gap-2">
                  <Eye className="h-4 w-4 flex-shrink-0 mt-0.5" />
                  {pred}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="space-y-3">
          {watchList.map((cat, index) => (
            <div key={cat.category || index} className="p-4 bg-slate-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-slate-900">{cat.category}</h4>
                <Badge className={cat.confidence === 'high' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}>
                  {cat.confidence} confidence
                </Badge>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-slate-500">Current Stage</p>
                  <p className="font-semibold capitalize">{cat.current_stage}</p>
                </div>
                <div>
                  <p className="text-slate-500">Prediction Score</p>
                  <p className="font-semibold text-purple-600">{cat.prediction_score}</p>
                </div>
                <div>
                  <p className="text-slate-500">Trajectory</p>
                  <p className="font-semibold text-green-600">{cat.expected_trajectory}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Saturation Warnings
  if (title.includes('Saturation') || title.includes('Warning')) {
    const categories = data.saturating_categories || [];
    const warningLevel = data.warning_level || 'low';
    
    return (
      <div className="space-y-4">
        <div className={`rounded-lg p-4 ${
          warningLevel === 'high' ? 'bg-red-50 border border-red-200' :
          warningLevel === 'moderate' ? 'bg-orange-50 border border-orange-200' :
          'bg-amber-50 border border-amber-200'
        }`}>
          <div className="flex items-center gap-2">
            <AlertTriangle className={`h-5 w-5 ${
              warningLevel === 'high' ? 'text-red-600' :
              warningLevel === 'moderate' ? 'text-orange-600' : 'text-amber-600'
            }`} />
            <span className="font-medium capitalize">{warningLevel} market saturation alert</span>
          </div>
          <p className="text-sm mt-1 opacity-80">
            {warningLevel === 'high' 
              ? 'Multiple categories showing significant saturation. Exercise caution with new entries.'
              : warningLevel === 'moderate'
              ? 'Some categories approaching saturation. Monitor competition closely.'
              : 'Early saturation signals detected. Good time to monitor trends.'}
          </p>
        </div>
        
        <div className="space-y-3">
          {categories.map((cat, index) => (
            <div key={cat.category || index} className="p-4 bg-red-50 rounded-lg border border-red-100">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                  <h4 className="font-medium text-slate-900">{cat.category}</h4>
                </div>
                <Badge className={cat.warning_level === 'high' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}>
                  {cat.warning_level}
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-slate-500">Saturation Score</p>
                  <p className="font-semibold text-red-600">{cat.saturation_score}</p>
                </div>
                <div>
                  <p className="text-slate-500">Recommendation</p>
                  <p className="font-medium text-slate-700">{cat.recommendation}</p>
                </div>
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
