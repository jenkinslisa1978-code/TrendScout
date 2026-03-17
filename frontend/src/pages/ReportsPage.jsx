/**
 * Reports Page
 * 
 * Main page listing available market intelligence reports
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  Trophy,
  TrendingUp,
  Calendar,
  Clock,
  ChevronRight,
  Download,
  Lock,
  Sparkles,
  BarChart3,
  Loader2
} from 'lucide-react';
import { getReportsList, getReportHistory, downloadReportPDF } from '@/services/reportsService';
import { useAuth } from '@/contexts/AuthContext';
import { useSubscription } from '@/hooks/useSubscription';
import { ReportUpgradePrompt, LockedContent, UpgradeBadge } from '@/components/common/UpgradePrompts';
import { toast } from 'sonner';

export default function ReportsPage() {
  const { profile } = useAuth();
  const { canAccessFullReports, canExportPdf, isFree, plan } = useSubscription();
  const [reportsData, setReportsData] = useState({ reports: [], latest: {} });
  const [weeklyHistory, setWeeklyHistory] = useState([]);
  const [monthlyHistory, setMonthlyHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloadingPDF, setDownloadingPDF] = useState(null);
  
  const userPlan = profile?.plan || 'free';

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      const [listData, weeklyData, monthlyData] = await Promise.all([
        getReportsList(),
        getReportHistory('weekly_winning_products', 10),
        getReportHistory('monthly_market_trends', 10)
      ]);
      
      setReportsData(listData);
      setWeeklyHistory(weeklyData.reports || []);
      setMonthlyHistory(monthlyData.reports || []);
      setLoading(false);
    };
    
    fetchData();
  }, []);

  const handleDownloadPDF = async (reportType) => {
    if (!canExportPdf) {
      toast.error('Upgrade to Pro to export PDF reports');
      return;
    }
    setDownloadingPDF(reportType);
    try {
      await downloadReportPDF(reportType);
      toast.success('PDF downloaded successfully');
    } catch (error) {
      if (error?.response?.status === 403) {
        toast.error('Upgrade to Pro to export PDF reports');
      } else {
        toast.error('Failed to download PDF');
      }
      console.error('PDF download error:', error);
    } finally {
      setDownloadingPDF(null);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const getPlanBadge = (plan) => {
    switch (plan) {
      case 'elite':
        return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'pro':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8 max-w-7xl mx-auto" data-testid="reports-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900 flex items-center gap-2">
              <FileText className="h-7 w-7 text-indigo-500" />
              Market Intelligence Reports
            </h1>
            <p className="text-slate-500 mt-1">Automated ecommerce trend reports and market analysis</p>
          </div>
          <Badge className={`${getPlanBadge(userPlan)} border px-3 py-1 capitalize`}>
            {userPlan} Plan
          </Badge>
        </div>

        {/* Upgrade Prompt for Free Users */}
        {isFree && (
          <ReportUpgradePrompt />
        )}

        {/* Latest Reports */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Weekly Report Card */}
          <Card className="border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-bold text-amber-900 flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-amber-500" />
                  Weekly Winning Products
                </CardTitle>
                <Badge className="bg-amber-500 text-white">Latest</Badge>
              </div>
            </CardHeader>
            <CardContent>
              {reportsData.latest?.weekly ? (
                <>
                  <p className="text-amber-800 font-medium">
                    {reportsData.latest.weekly.metadata?.title}
                  </p>
                  <p className="text-sm text-amber-600 mt-1">
                    Top 20 products ranked by launch potential
                  </p>
                  <div className="flex items-center gap-2 mt-4">
                    <Link to="/reports/weekly-winning-products" className="flex-1">
                      <Button className="w-full bg-amber-600 hover:bg-amber-700">
                        View Report
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Button>
                    </Link>
                    <Button 
                      variant="outline" 
                      className={`border-amber-300 ${canExportPdf ? 'text-amber-700 hover:bg-amber-100' : 'text-slate-400 cursor-not-allowed'}`}
                      onClick={() => handleDownloadPDF('weekly')}
                      disabled={downloadingPDF === 'weekly' || !canExportPdf}
                      data-testid="download-weekly-pdf"
                      title={canExportPdf ? 'Download PDF' : 'Upgrade to Pro for PDF export'}
                    >
                      {downloadingPDF === 'weekly' ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : !canExportPdf ? (
                        <Lock className="h-4 w-4" />
                      ) : (
                        <Download className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </>
              ) : (
                <div className="text-center py-4">
                  <Trophy className="h-10 w-10 text-amber-300 mx-auto" />
                  <p className="text-amber-700 mt-2">Generating first report...</p>
                  <Link to="/reports/weekly-winning-products">
                    <Button className="mt-3 bg-amber-600 hover:bg-amber-700">
                      Generate Now
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Monthly Report Card */}
          <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-bold text-purple-900 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-purple-500" />
                  Monthly Market Trends
                </CardTitle>
                <Badge className="bg-purple-500 text-white">Latest</Badge>
              </div>
            </CardHeader>
            <CardContent>
              {reportsData.latest?.monthly ? (
                <>
                  <p className="text-purple-800 font-medium">
                    {reportsData.latest.monthly.metadata?.title}
                  </p>
                  <p className="text-sm text-purple-600 mt-1">
                    Category insights and market predictions
                  </p>
                  <div className="flex items-center gap-2 mt-4">
                    <Link to="/reports/monthly-market-trends" className="flex-1">
                      <Button className="w-full bg-purple-600 hover:bg-purple-700">
                        View Report
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Button>
                    </Link>
                    <Button 
                      variant="outline" 
                      className={`border-purple-300 ${canExportPdf ? 'text-purple-700 hover:bg-purple-100' : 'text-slate-400 cursor-not-allowed'}`}
                      onClick={() => handleDownloadPDF('monthly')}
                      disabled={downloadingPDF === 'monthly' || !canExportPdf}
                      data-testid="download-monthly-pdf"
                      title={canExportPdf ? 'Download PDF' : 'Upgrade to Pro for PDF export'}
                    >
                      {downloadingPDF === 'monthly' ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : !canExportPdf ? (
                        <Lock className="h-4 w-4" />
                      ) : (
                        <Download className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </>
              ) : (
                <div className="text-center py-4">
                  <BarChart3 className="h-10 w-10 text-purple-300 mx-auto" />
                  <p className="text-purple-700 mt-2">Generating first report...</p>
                  <Link to="/reports/monthly-market-trends">
                    <Button className="mt-3 bg-purple-600 hover:bg-purple-700">
                      Generate Now
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Report Archive */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="border-b border-slate-100">
            <CardTitle className="font-manrope text-xl font-bold text-slate-900 flex items-center gap-2">
              <Calendar className="h-6 w-6 text-slate-500" />
              Report Archive
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Tabs defaultValue="weekly" className="w-full">
              <TabsList className="w-full justify-start border-b rounded-none bg-transparent h-auto p-0">
                <TabsTrigger 
                  value="weekly" 
                  className="data-[state=active]:border-b-2 data-[state=active]:border-amber-500 rounded-none px-6 py-3"
                >
                  <Trophy className="h-4 w-4 mr-2 text-amber-500" />
                  Weekly Reports
                </TabsTrigger>
                <TabsTrigger 
                  value="monthly"
                  className="data-[state=active]:border-b-2 data-[state=active]:border-purple-500 rounded-none px-6 py-3"
                >
                  <BarChart3 className="h-4 w-4 mr-2 text-purple-500" />
                  Monthly Reports
                </TabsTrigger>
              </TabsList>

              <TabsContent value="weekly" className="p-0">
                <div className="divide-y divide-slate-100">
                  {weeklyHistory.length > 0 ? (
                    weeklyHistory.map((report, index) => (
                      <Link
                        key={report.metadata?.id || index}
                        to={`/reports/weekly/${report.metadata?.slug}`}
                        className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                            <Trophy className="h-5 w-5 text-amber-600" />
                          </div>
                          <div>
                            <p className="font-medium text-slate-900">{report.metadata?.title}</p>
                            <p className="text-sm text-slate-500 flex items-center gap-2">
                              <Clock className="h-3 w-3" />
                              {formatDate(report.metadata?.generated_at)}
                              <span className="text-slate-300">•</span>
                              {report.summary?.total_products_analysed || 0} products
                            </p>
                          </div>
                        </div>
                        <ChevronRight className="h-5 w-5 text-slate-400" />
                      </Link>
                    ))
                  ) : (
                    <div className="p-8 text-center text-slate-500">
                      <Trophy className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                      <p>No weekly reports available yet</p>
                    </div>
                  )}
                </div>
                
                {userPlan === 'free' && weeklyHistory.length > 0 && (
                  <div className="p-4 bg-amber-50 border-t border-amber-100">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-amber-700">
                        <Lock className="h-4 w-4" />
                        <span className="text-sm">Upgrade to Pro for full archive access</span>
                      </div>
                      <Link to="/pricing">
                        <Button size="sm" variant="outline" className="border-amber-300 text-amber-700">
                          Upgrade
                        </Button>
                      </Link>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="monthly" className="p-0">
                <div className="divide-y divide-slate-100">
                  {monthlyHistory.length > 0 ? (
                    monthlyHistory.map((report, index) => (
                      <Link
                        key={report.metadata?.id || index}
                        to={`/reports/monthly/${report.metadata?.slug}`}
                        className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                            <BarChart3 className="h-5 w-5 text-purple-600" />
                          </div>
                          <div>
                            <p className="font-medium text-slate-900">{report.metadata?.title}</p>
                            <p className="text-sm text-slate-500 flex items-center gap-2">
                              <Clock className="h-3 w-3" />
                              {formatDate(report.metadata?.generated_at)}
                              <span className="text-slate-300">•</span>
                              {report.summary?.total_categories || 0} categories
                            </p>
                          </div>
                        </div>
                        <ChevronRight className="h-5 w-5 text-slate-400" />
                      </Link>
                    ))
                  ) : (
                    <div className="p-8 text-center text-slate-500">
                      <BarChart3 className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                      <p>No monthly reports available yet</p>
                    </div>
                  )}
                </div>
                
                {userPlan !== 'elite' && monthlyHistory.length > 0 && (
                  <div className="p-4 bg-purple-50 border-t border-purple-100">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-purple-700">
                        <Lock className="h-4 w-4" />
                        <span className="text-sm">Upgrade to Elite for full archive access</span>
                      </div>
                      <Link to="/pricing">
                        <Button size="sm" variant="outline" className="border-purple-300 text-purple-700">
                          Upgrade
                        </Button>
                      </Link>
                    </div>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Features Info */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="h-8 w-8" />
            <h2 className="font-manrope text-2xl font-bold">Automated Intelligence</h2>
          </div>
          <p className="text-indigo-100 mb-6 max-w-2xl">
            Reports are generated automatically using aggregated platform data. 
            Weekly reports publish every Monday, monthly reports on the first of each month.
          </p>
          <div className="grid sm:grid-cols-3 gap-4">
            <div className="bg-white/10 rounded-lg p-4">
              <h3 className="font-semibold mb-1">Weekly Reports</h3>
              <p className="text-sm text-indigo-200">Top 20 winning products, margin analysis, saturation warnings</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <h3 className="font-semibold mb-1">Monthly Reports</h3>
              <p className="text-sm text-indigo-200">Emerging categories, market predictions, demand analysis</p>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <h3 className="font-semibold mb-1">PDF Downloads</h3>
              <p className="text-sm text-indigo-200">Export and share reports with your team</p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
