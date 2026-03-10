/**
 * Public Weekly Report Page
 * 
 * SEO-optimized public preview of weekly winning products report
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Trophy, 
  TrendingUp,
  Package,
  Lock,
  ArrowRight,
  Loader2,
  CheckCircle,
  Zap,
  ChevronRight,
  Calendar,
  Users,
  Download
} from 'lucide-react';
import { getPublicWeeklyReport, downloadReportPDF } from '@/services/reportsService';
import { toast } from 'sonner';

export default function PublicWeeklyReportPage() {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPDF, setDownloadingPDF] = useState(false);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      const data = await getPublicWeeklyReport();
      setReportData(data);
      setLoading(false);
    };
    
    fetchReport();
  }, []);

  const handleDownloadPDF = async () => {
    setDownloadingPDF(true);
    try {
      await downloadReportPDF('weekly', true);
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to download PDF');
    } finally {
      setDownloadingPDF(false);
    }
  };

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

  const getTrendColor = (stage) => {
    switch (stage) {
      case 'exploding': return 'bg-red-100 text-red-700';
      case 'rising': return 'bg-green-100 text-green-700';
      case 'early': return 'bg-blue-100 text-blue-700';
      default: return 'bg-slate-100 text-slate-600';
    }
  };

  if (loading) {
    return (
      <LandingLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-amber-600" />
        </div>
      </LandingLayout>
    );
  }

  return (
    <LandingLayout>
      <div className="max-w-4xl mx-auto px-4 py-12" data-testid="public-weekly-report">
        {/* SEO Header */}
        <header className="text-center mb-12">
          <Badge className="bg-amber-100 text-amber-700 mb-4">Free Weekly Report</Badge>
          <h1 className="font-manrope text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            {metadata.title || 'Weekly Winning Products Report'}
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            {metadata.description || 'Discover the top dropshipping products ranked by success probability, trend velocity, and margin potential.'}
          </p>
          <div className="flex items-center justify-center gap-4 mt-4 text-sm text-slate-500">
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              {formatDate(metadata.generated_at)}
            </span>
            <span className="flex items-center gap-1">
              <Package className="h-4 w-4" />
              {preview.total_products || 20} products analyzed
            </span>
          </div>
          {/* Download PDF Button */}
          <div className="mt-6">
            <Button 
              variant="outline" 
              className="border-amber-300 text-amber-700 hover:bg-amber-100"
              onClick={handleDownloadPDF}
              disabled={downloadingPDF}
              data-testid="download-public-weekly-pdf"
            >
              {downloadingPDF ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              Download Preview PDF
            </Button>
          </div>
        </header>

        {/* Preview Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <Card className="bg-green-50 border-green-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-green-700">{summary.avg_success_probability || 0}%</p>
              <p className="text-xs text-green-600">Avg Success Rate</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-blue-700">{summary.low_competition_opportunities || 0}</p>
              <p className="text-xs text-blue-600">Low Competition</p>
            </CardContent>
          </Card>
          <Card className="bg-amber-50 border-amber-200">
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-amber-700">{preview.top_categories?.length || 0}</p>
              <p className="text-xs text-amber-600">Hot Categories</p>
            </CardContent>
          </Card>
        </div>

        {/* Top 5 Products Preview */}
        <Card className="border-2 border-amber-200 mb-8">
          <CardHeader className="bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-200">
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-amber-500" />
              Top 5 Winning Products
            </CardTitle>
            <p className="text-sm text-amber-700">Preview of this week's highest opportunity products</p>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100">
              {preview.top_5_products?.map((product, index) => (
                <div key={product.id || index} className="flex items-center gap-4 p-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    index < 3 ? 'bg-amber-500 text-white' : 'bg-slate-200 text-slate-600'
                  }`}>
                    {index + 1}
                  </div>
                  
                  <div className="w-12 h-12 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
                    <Package className="h-6 w-6 text-slate-400" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-900 truncate">{product.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className={`text-xs ${getTrendColor(product.trend_stage)}`}>
                        {product.trend_stage}
                      </Badge>
                      <span className="text-xs text-slate-500 capitalize">{product.competition_level} competition</span>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <p className="font-bold text-green-600">{product.success_probability}%</p>
                    <p className="text-xs text-slate-500">Success</p>
                  </div>
                  
                  <div className="text-right">
                    <p className="font-medium text-slate-400">{product.estimated_margin}</p>
                    <p className="text-xs text-slate-500">Margin</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Trend Distribution */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              Trend Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {Object.entries(preview.trend_distribution || {}).map(([stage, count]) => (
                <Badge key={stage} variant="outline" className={`${getTrendColor(stage)} px-3 py-1`}>
                  {stage}: {count} products
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Competition Snapshot */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Competition Snapshot</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-700">{preview.competition_snapshot?.low || 0}</p>
                <p className="text-sm text-green-600">Low Competition</p>
              </div>
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <p className="text-2xl font-bold text-amber-700">{preview.competition_snapshot?.medium || 0}</p>
                <p className="text-sm text-amber-600">Medium Competition</p>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <p className="text-2xl font-bold text-red-700">{preview.competition_snapshot?.high || 0}</p>
                <p className="text-sm text-red-600">High Competition</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Locked Content Teaser */}
        <Card className="border-2 border-dashed border-slate-300 bg-slate-50 mb-8">
          <CardContent className="p-8 text-center">
            <Lock className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-700 mb-2">
              Unlock the Full Report
            </h3>
            <p className="text-slate-500 mb-4 max-w-md mx-auto">
              {preview.teaser_message || cta?.message}
            </p>
            <ul className="text-sm text-slate-600 space-y-2 mb-6 max-w-sm mx-auto">
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                All 20 winning products with full details
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Supplier costs and margin analysis
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Opportunity clusters and predictions
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Saturation warnings to avoid losses
              </li>
            </ul>
            <Link to="/signup">
              <Button size="lg" className="bg-amber-600 hover:bg-amber-700">
                {cta?.action || 'Sign up for free'}
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* CTA Footer */}
        <div className="bg-gradient-to-r from-amber-500 to-orange-500 rounded-2xl p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-2">Ready to Find Your Winning Product?</h2>
          <p className="text-amber-100 mb-6">
            Join thousands of dropshippers using ViralScout to discover profitable products.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" className="bg-white text-amber-600 hover:bg-amber-50">
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
