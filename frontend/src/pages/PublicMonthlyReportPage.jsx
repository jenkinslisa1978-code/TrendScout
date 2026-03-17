/**
 * Public Monthly Report Page
 * 
 * SEO-optimised public preview of monthly market trends report
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  BarChart3, 
  TrendingUp,
  TrendingDown,
  Lock,
  ArrowRight,
  Loader2,
  CheckCircle,
  Layers,
  Calendar,
  Flame
} from 'lucide-react';
import { getPublicMonthlyReport } from '@/services/reportsService';

export default function PublicMonthlyReportPage() {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      const data = await getPublicMonthlyReport();
      setReportData(data);
      setLoading(false);
    };
    
    fetchReport();
  }, []);

  const report = reportData?.report;
  const cta = reportData?.cta;
  const preview = report?.public_preview || {};
  const metadata = report?.metadata || {};
  const summary = report?.summary || {};

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <LandingLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
        </div>
      </LandingLayout>
    );
  }

  const marketSnapshot = preview.market_snapshot || {};
  const demandCompetition = preview.demand_competition_summary || {};

  return (
    <LandingLayout>
      <div className="max-w-4xl mx-auto px-4 py-12" data-testid="public-monthly-report">
        {/* SEO Header */}
        <header className="text-center mb-12">
          <Badge className="bg-purple-100 text-purple-700 mb-4">Free Monthly Report</Badge>
          <h1 className="font-manrope text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            {metadata.title || 'Monthly Market Trends Report'}
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            {metadata.description || 'Comprehensive ecommerce market analysis with emerging categories, demand insights, and growth predictions.'}
          </p>
          <div className="flex items-center justify-center gap-4 mt-4 text-sm text-slate-500">
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              {formatDate(metadata.generated_at)}
            </span>
            <span className="flex items-center gap-1">
              <Layers className="h-4 w-4" />
              {summary.total_categories || 0} categories analysed
            </span>
          </div>
        </header>

        {/* Market Snapshot */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <Card className="bg-slate-50 border-slate-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-slate-700">{marketSnapshot.total_categories || 0}</p>
              <p className="text-xs text-slate-600">Total Categories</p>
            </CardContent>
          </Card>
          <Card className="bg-green-50 border-green-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-green-700">{marketSnapshot.growing_categories || 0}</p>
              <p className="text-xs text-green-600">Growing</p>
            </CardContent>
          </Card>
          <Card className="bg-red-50 border-red-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-red-700">{marketSnapshot.declining_categories || 0}</p>
              <p className="text-xs text-red-600">Declining</p>
            </CardContent>
          </Card>
        </div>

        {/* Top Emerging Categories */}
        <Card className="border-2 border-purple-200 mb-8">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-purple-200">
            <CardTitle className="flex items-center gap-2">
              <Flame className="h-5 w-5 text-purple-500" />
              Top 3 Emerging Categories
            </CardTitle>
            <p className="text-sm text-purple-700">Categories showing strongest early trend signals</p>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100">
              {preview.top_3_emerging?.map((category, index) => (
                <div key={category.category || index} className="flex items-center gap-4 p-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                    index === 0 ? 'bg-purple-500 text-white' : 
                    index === 1 ? 'bg-purple-400 text-white' : 
                    'bg-purple-200 text-purple-700'
                  }`}>
                    {index + 1}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-900">{category.category}</p>
                    <p className="text-xs text-slate-500">{category.product_count} products tracked</p>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    <span className="font-bold text-green-600">+{category.growth_momentum?.toFixed(0)}%</span>
                  </div>
                </div>
              ))}
              
              {(!preview.top_3_emerging || preview.top_3_emerging.length === 0) && (
                <div className="p-8 text-center text-slate-500">
                  <Layers className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                  <p>No emerging category data available</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Demand vs Competition */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              Demand vs Competition
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <TrendingUp className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <p className="text-3xl font-bold text-green-700">{demandCompetition.favorable_markets || 0}</p>
                <p className="text-sm text-green-600">Favorable Markets</p>
                <p className="text-xs text-green-500 mt-1">High demand, low competition</p>
              </div>
              <div className="text-center p-6 bg-orange-50 rounded-lg">
                <TrendingDown className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                <p className="text-3xl font-bold text-orange-700">{demandCompetition.saturated_markets || 0}</p>
                <p className="text-sm text-orange-600">Saturated Markets</p>
                <p className="text-xs text-orange-500 mt-1">High competition, lower demand</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Locked Content Teaser */}
        <Card className="border-2 border-dashed border-slate-300 bg-slate-50 mb-8">
          <CardContent className="p-8 text-center">
            <Lock className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-700 mb-2">
              Unlock the Full Market Analysis
            </h3>
            <p className="text-slate-500 mb-4 max-w-md mx-auto">
              {preview.teaser_message || cta?.message}
            </p>
            <ul className="text-sm text-slate-600 space-y-2 mb-6 max-w-sm mx-auto">
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                All {summary.total_categories || 0} category analyses
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Fastest growing niches with data
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Categories to watch next month
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Saturation warnings and risk analysis
              </li>
            </ul>
            <Link to="/signup">
              <Button size="lg" className="bg-purple-600 hover:bg-purple-700">
                {cta?.action || 'Sign up for free'}
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* CTA Footer */}
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-2">Stay Ahead of Market Trends</h2>
          <p className="text-purple-100 mb-6">
            Get monthly insights on emerging categories and market opportunities.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" className="bg-white text-purple-600 hover:bg-purple-50">
                Get Started Free
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
            <Link to="/reports">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                Browse All Reports
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </LandingLayout>
  );
}
