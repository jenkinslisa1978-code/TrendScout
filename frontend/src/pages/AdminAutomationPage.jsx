import React, { useState, useRef } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { 
  Upload, 
  FileSpreadsheet,
  Wand2,
  Bell,
  Calculator,
  Sparkles,
  Play,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Download,
  Plus,
  RefreshCw,
  ArrowRight,
  Zap,
  History,
  Database
} from 'lucide-react';
import { parseCSV, processImportedProducts, generateImportReport, ImportSources } from '@/lib/automation/product-import';
import { createProduct, runAutomationOnAllProducts, bulkImportProducts, getAllProductsRaw } from '@/services/productService';
import { createAlertsForProducts } from '@/services/alertService';
import { createAutomationLog, updateAutomationLog, AutomationJobTypes, AutomationStatus } from '@/services/automationLogService';
import AutomationLogs from '@/components/automation/AutomationLogs';
import DataIngestionPanel from '@/components/automation/DataIngestionPanel';
import { toast } from 'sonner';

const INITIAL_PRODUCT = {
  product_name: '',
  category: '',
  short_description: '',
  supplier_cost: '',
  estimated_retail_price: '',
  tiktok_views: '',
  ad_count: '',
  competition_level: 'medium',
  supplier_link: '',
  is_premium: false
};

export default function AdminAutomationPage() {
  const [activeTab, setActiveTab] = useState('sources');
  const [loading, setLoading] = useState({});
  const [formData, setFormData] = useState(INITIAL_PRODUCT);
  const [csvContent, setCsvContent] = useState('');
  const [importResults, setImportResults] = useState(null);
  const [automationResults, setAutomationResults] = useState(null);
  const fileInputRef = useRef(null);

  // Manual product entry
  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setLoading(prev => ({ ...prev, manual: true }));

    try {
      const productData = {
        product_name: formData.product_name,
        category: formData.category || 'General',
        short_description: formData.short_description,
        supplier_cost: parseFloat(formData.supplier_cost) || 0,
        estimated_retail_price: parseFloat(formData.estimated_retail_price) || 0,
        tiktok_views: parseInt(formData.tiktok_views) || 0,
        ad_count: parseInt(formData.ad_count) || 0,
        competition_level: formData.competition_level,
        supplier_link: formData.supplier_link,
        is_premium: formData.is_premium,
      };

      const { data, error, alert } = await createProduct(productData, true);

      if (error) {
        toast.error('Failed to create product');
      } else {
        toast.success(`Product created with trend score: ${data.trend_score}`);
        if (alert) {
          toast.info('Alert generated for this high-opportunity product!');
        }
        setFormData(INITIAL_PRODUCT);
      }
    } catch (err) {
      toast.error('Error creating product');
    }

    setLoading(prev => ({ ...prev, manual: false }));
  };

  // CSV file upload
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      setCsvContent(event.target?.result);
    };
    reader.readAsText(file);
  };

  // Process CSV
  const handleCSVImport = async () => {
    if (!csvContent.trim()) {
      toast.error('Please upload or paste CSV content');
      return;
    }

    setLoading(prev => ({ ...prev, csv: true }));

    try {
      // Parse CSV
      const parseResult = parseCSV(csvContent);
      
      if (parseResult.errors.length > 0) {
        parseResult.errors.forEach(err => toast.error(err));
        setLoading(prev => ({ ...prev, csv: false }));
        return;
      }

      // Process with automation
      const processedProducts = processImportedProducts(parseResult.products);
      
      // Import to database
      const { data, alerts, summary, error } = await bulkImportProducts(processedProducts);

      if (error) {
        toast.error('Failed to import products');
      } else {
        const report = generateImportReport(
          parseResult.products.length,
          processedProducts,
          parseResult.errors,
          parseResult.warnings
        );
        
        setImportResults(report);
        toast.success(`Imported ${processedProducts.length} products with automation`);
        
        if (alerts?.length > 0) {
          toast.info(`${alerts.length} alerts generated for high-opportunity products`);
        }
      }
    } catch (err) {
      toast.error('Error processing CSV');
    }

    setLoading(prev => ({ ...prev, csv: false }));
  };

  // Run trend scoring on all products
  const handleRunTrendScoring = async () => {
    setLoading(prev => ({ ...prev, scoring: true }));

    // Create log entry
    const { data: log } = await createAutomationLog({
      job_type: AutomationJobTypes.TREND_SCORING,
      status: AutomationStatus.RUNNING,
    });

    try {
      const { data, alerts, summary, error } = await runAutomationOnAllProducts();

      if (error) {
        await updateAutomationLog(log.id, { status: AutomationStatus.FAILED, error_message: error });
        toast.error('Failed to run trend scoring');
      } else {
        await updateAutomationLog(log.id, { 
          status: AutomationStatus.COMPLETED, 
          products_processed: summary.processed,
          alerts_generated: summary.alertsGenerated || 0,
        });
        setAutomationResults({
          type: 'scoring',
          ...summary,
          products: data,
        });
        toast.success(`Updated ${summary.processed} products`);
      }
    } catch (err) {
      await updateAutomationLog(log.id, { status: AutomationStatus.FAILED, error_message: err.message });
      toast.error('Error running trend scoring');
    }

    setLoading(prev => ({ ...prev, scoring: false }));
  };

  // Generate AI summaries
  const handleGenerateSummaries = async () => {
    setLoading(prev => ({ ...prev, summaries: true }));

    const { data: log } = await createAutomationLog({
      job_type: AutomationJobTypes.AI_SUMMARY,
      status: AutomationStatus.RUNNING,
    });

    try {
      const { data, summary, error } = await runAutomationOnAllProducts();

      if (error) {
        await updateAutomationLog(log.id, { status: AutomationStatus.FAILED, error_message: error });
        toast.error('Failed to generate summaries');
      } else {
        await updateAutomationLog(log.id, { 
          status: AutomationStatus.COMPLETED, 
          products_processed: summary.processed,
        });
        setAutomationResults({
          type: 'summaries',
          ...summary,
        });
        toast.success(`Generated AI summaries for ${summary.processed} products`);
      }
    } catch (err) {
      await updateAutomationLog(log.id, { status: AutomationStatus.FAILED, error_message: err.message });
      toast.error('Error generating summaries');
    }

    setLoading(prev => ({ ...prev, summaries: false }));
  };

  // Generate alerts
  const handleGenerateAlerts = async () => {
    setLoading(prev => ({ ...prev, alerts: true }));

    const { data: log } = await createAutomationLog({
      job_type: AutomationJobTypes.ALERT_GENERATION,
      status: AutomationStatus.RUNNING,
    });

    try {
      const { data: products } = await getAllProductsRaw();
      const { data: alerts, count, error } = await createAlertsForProducts(products);

      if (error) {
        await updateAutomationLog(log.id, { status: AutomationStatus.FAILED, error_message: error });
        toast.error('Failed to generate alerts');
      } else {
        await updateAutomationLog(log.id, { 
          status: AutomationStatus.COMPLETED, 
          products_processed: products.length,
          alerts_generated: count,
        });
        setAutomationResults({
          type: 'alerts',
          alertsGenerated: count,
          alerts,
        });
        toast.success(`Generated ${count} new alerts`);
      }
    } catch (err) {
      await updateAutomationLog(log.id, { status: AutomationStatus.FAILED, error_message: err.message });
      toast.error('Error generating alerts');
    }

    setLoading(prev => ({ ...prev, alerts: false }));
  };

  // Download CSV template
  const handleDownloadTemplate = () => {
    const template = `product_name,category,short_description,supplier_cost,estimated_retail_price,tiktok_views,ad_count,competition_level,supplier_link,is_premium
"Portable Neck Fan","Electronics","Hands-free personal cooling device",8.50,29.99,15000000,234,medium,"https://alibaba.com/example",false
"LED Strip Lights","Home Decor","App-controlled RGB LED strips",5.40,19.99,45000000,412,high,"https://alibaba.com/example",false`;
    
    const blob = new Blob([template], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'trendscout_import_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="font-manrope text-2xl font-bold text-slate-900">Automation Center</h1>
          <p className="mt-1 text-slate-500">Import products and run automated analysis</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-slate-200 hover:border-indigo-200 hover:shadow-md transition-all cursor-pointer" onClick={handleRunTrendScoring}>
            <CardContent className="p-5 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50">
                <Calculator className="h-6 w-6 text-indigo-600" />
              </div>
              <div>
                <p className="font-semibold text-slate-900">Run Scoring</p>
                <p className="text-sm text-slate-500">Update all trend scores</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200 hover:border-purple-200 hover:shadow-md transition-all cursor-pointer" onClick={handleGenerateSummaries}>
            <CardContent className="p-5 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50">
                <Sparkles className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="font-semibold text-slate-900">AI Summaries</p>
                <p className="text-sm text-slate-500">Generate product insights</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200 hover:border-amber-200 hover:shadow-md transition-all cursor-pointer" onClick={handleGenerateAlerts}>
            <CardContent className="p-5 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50">
                <Bell className="h-6 w-6 text-amber-600" />
              </div>
              <div>
                <p className="font-semibold text-slate-900">Generate Alerts</p>
                <p className="text-sm text-slate-500">Check for opportunities</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200 hover:border-emerald-200 hover:shadow-md transition-all cursor-pointer" onClick={() => setActiveTab('import')}>
            <CardContent className="p-5 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50">
                <Upload className="h-6 w-6 text-emerald-600" />
              </div>
              <div>
                <p className="font-semibold text-slate-900">Import Products</p>
                <p className="text-sm text-slate-500">CSV or manual entry</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Automation Results */}
        {automationResults && (
          <Card className="border-emerald-200 bg-emerald-50/50">
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                <div>
                  <p className="font-semibold text-emerald-900">
                    Automation Complete
                  </p>
                  <p className="text-sm text-emerald-700">
                    {automationResults.type === 'scoring' && `Processed ${automationResults.processed} products`}
                    {automationResults.type === 'summaries' && `Generated summaries for ${automationResults.processed} products`}
                    {automationResults.type === 'alerts' && `Generated ${automationResults.alertsGenerated} new alerts`}
                    {automationResults.alertsGenerated > 0 && ` • ${automationResults.alertsGenerated} alerts created`}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-slate-100">
            <TabsTrigger value="sources" className="data-[state=active]:bg-white" data-testid="tab-sources">
              <Database className="mr-2 h-4 w-4" />
              Data Sources
            </TabsTrigger>
            <TabsTrigger value="import" className="data-[state=active]:bg-white" data-testid="tab-import">
              <Upload className="mr-2 h-4 w-4" />
              CSV Import
            </TabsTrigger>
            <TabsTrigger value="manual" className="data-[state=active]:bg-white" data-testid="tab-manual">
              <Plus className="mr-2 h-4 w-4" />
              Manual Entry
            </TabsTrigger>
            <TabsTrigger value="pipeline" className="data-[state=active]:bg-white" data-testid="tab-pipeline">
              <Wand2 className="mr-2 h-4 w-4" />
              Automation
            </TabsTrigger>
            <TabsTrigger value="logs" className="data-[state=active]:bg-white" data-testid="tab-logs">
              <History className="mr-2 h-4 w-4" />
              Logs
            </TabsTrigger>
          </TabsList>

          {/* Data Sources Tab */}
          <TabsContent value="sources">
            <DataIngestionPanel />
          </TabsContent>

          {/* CSV Import Tab */}
          <TabsContent value="import">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Upload Section */}
              <Card className="border-slate-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileSpreadsheet className="h-5 w-5 text-indigo-600" />
                    CSV Upload
                  </CardTitle>
                  <CardDescription>
                    Upload a CSV file or paste content directly
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* File upload */}
                  <div 
                    className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center hover:border-indigo-300 transition-colors cursor-pointer"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv"
                      className="hidden"
                      onChange={handleFileUpload}
                      data-testid="csv-file-input"
                    />
                    <Upload className="h-10 w-10 text-slate-400 mx-auto mb-3" />
                    <p className="font-medium text-slate-700">Click to upload CSV</p>
                    <p className="text-sm text-slate-500 mt-1">or drag and drop</p>
                  </div>

                  {/* Paste CSV */}
                  <div className="space-y-2">
                    <Label>Or paste CSV content:</Label>
                    <Textarea
                      placeholder="product_name,category,supplier_cost,estimated_retail_price..."
                      value={csvContent}
                      onChange={(e) => setCsvContent(e.target.value)}
                      rows={6}
                      className="font-mono text-sm"
                      data-testid="csv-paste-input"
                    />
                  </div>

                  <div className="flex gap-3">
                    <Button
                      onClick={handleCSVImport}
                      disabled={loading.csv || !csvContent.trim()}
                      className="flex-1 bg-indigo-600 hover:bg-indigo-700"
                      data-testid="import-csv-btn"
                    >
                      {loading.csv ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Play className="mr-2 h-4 w-4" />
                          Import & Analyze
                        </>
                      )}
                    </Button>
                    <Button variant="outline" onClick={handleDownloadTemplate} data-testid="download-template-btn">
                      <Download className="mr-2 h-4 w-4" />
                      Template
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Results Section */}
              <Card className="border-slate-200">
                <CardHeader>
                  <CardTitle>Import Results</CardTitle>
                  <CardDescription>
                    Preview of imported products with calculated scores
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {importResults ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="p-3 bg-emerald-50 rounded-lg text-center">
                          <p className="text-2xl font-bold text-emerald-700">{importResults.summary.successfullyImported}</p>
                          <p className="text-xs text-emerald-600">Imported</p>
                        </div>
                        <div className="p-3 bg-amber-50 rounded-lg text-center">
                          <p className="text-2xl font-bold text-amber-700">{importResults.summary.warnings}</p>
                          <p className="text-xs text-amber-600">Warnings</p>
                        </div>
                        <div className="p-3 bg-red-50 rounded-lg text-center">
                          <p className="text-2xl font-bold text-red-700">{importResults.summary.errors}</p>
                          <p className="text-xs text-red-600">Errors</p>
                        </div>
                      </div>

                      {importResults.products.length > 0 && (
                        <div className="max-h-64 overflow-y-auto">
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Product</TableHead>
                                <TableHead>Score</TableHead>
                                <TableHead>Stage</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {importResults.products.slice(0, 10).map((p, i) => (
                                <TableRow key={i}>
                                  <TableCell className="font-medium">{p.name}</TableCell>
                                  <TableCell className="font-mono">{p.trend_score}</TableCell>
                                  <TableCell>
                                    <Badge variant="outline" className="capitalize">{p.trend_stage}</Badge>
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </div>
                      )}

                      {importResults.warnings.length > 0 && (
                        <div className="p-3 bg-amber-50 rounded-lg">
                          <p className="text-sm font-medium text-amber-800 mb-2">Warnings:</p>
                          <ul className="text-xs text-amber-700 space-y-1">
                            {importResults.warnings.slice(0, 5).map((w, i) => (
                              <li key={i}>• {w}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-slate-400">
                      <FileSpreadsheet className="h-12 w-12 mx-auto mb-3" />
                      <p>Import results will appear here</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Manual Entry Tab */}
          <TabsContent value="manual">
            <Card className="border-slate-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Plus className="h-5 w-5 text-indigo-600" />
                  Add New Product
                </CardTitle>
                <CardDescription>
                  Enter product details manually. Trend score, opportunity rating, and AI summary will be generated automatically.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleManualSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="product_name">Product Name *</Label>
                      <Input
                        id="product_name"
                        value={formData.product_name}
                        onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                        placeholder="Portable Neck Fan"
                        required
                        data-testid="manual-product-name"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="category">Category</Label>
                      <Input
                        id="category"
                        value={formData.category}
                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                        placeholder="Electronics"
                        data-testid="manual-category"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="supplier_cost">Supplier Cost (£) *</Label>
                      <Input
                        id="supplier_cost"
                        type="number"
                        step="0.01"
                        value={formData.supplier_cost}
                        onChange={(e) => setFormData({ ...formData, supplier_cost: e.target.value })}
                        placeholder="8.50"
                        required
                        data-testid="manual-supplier-cost"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="estimated_retail_price">Retail Price (£) *</Label>
                      <Input
                        id="estimated_retail_price"
                        type="number"
                        step="0.01"
                        value={formData.estimated_retail_price}
                        onChange={(e) => setFormData({ ...formData, estimated_retail_price: e.target.value })}
                        placeholder="29.99"
                        required
                        data-testid="manual-retail-price"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="tiktok_views">TikTok Views</Label>
                      <Input
                        id="tiktok_views"
                        type="number"
                        value={formData.tiktok_views}
                        onChange={(e) => setFormData({ ...formData, tiktok_views: e.target.value })}
                        placeholder="15000000"
                        data-testid="manual-tiktok-views"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="ad_count">Active Ad Count</Label>
                      <Input
                        id="ad_count"
                        type="number"
                        value={formData.ad_count}
                        onChange={(e) => setFormData({ ...formData, ad_count: e.target.value })}
                        placeholder="234"
                        data-testid="manual-ad-count"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Competition Level</Label>
                      <Select 
                        value={formData.competition_level} 
                        onValueChange={(v) => setFormData({ ...formData, competition_level: v })}
                      >
                        <SelectTrigger data-testid="manual-competition">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="supplier_link">Supplier Link</Label>
                      <Input
                        id="supplier_link"
                        value={formData.supplier_link}
                        onChange={(e) => setFormData({ ...formData, supplier_link: e.target.value })}
                        placeholder="https://alibaba.com/..."
                        data-testid="manual-supplier-link"
                      />
                    </div>

                    <div className="md:col-span-2 space-y-2">
                      <Label htmlFor="short_description">Description</Label>
                      <Textarea
                        id="short_description"
                        value={formData.short_description}
                        onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
                        placeholder="Brief product description..."
                        rows={2}
                        data-testid="manual-description"
                      />
                    </div>

                    <div className="md:col-span-2 flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="is_premium"
                        checked={formData.is_premium}
                        onChange={(e) => setFormData({ ...formData, is_premium: e.target.checked })}
                        className="h-4 w-4 rounded border-slate-300"
                        data-testid="manual-is-premium"
                      />
                      <Label htmlFor="is_premium">Premium Product (Pro/Elite only)</Label>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 pt-4 border-t border-slate-200">
                    <Button
                      type="submit"
                      disabled={loading.manual}
                      className="bg-indigo-600 hover:bg-indigo-700"
                      data-testid="manual-submit-btn"
                    >
                      {loading.manual ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Creating...
                        </>
                      ) : (
                        <>
                          <Wand2 className="mr-2 h-4 w-4" />
                          Create & Auto-Analyze
                        </>
                      )}
                    </Button>
                    <p className="text-sm text-slate-500">
                      Trend score, opportunity rating, and AI summary will be generated automatically
                    </p>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Automation Pipeline Tab */}
          <TabsContent value="pipeline">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Pipeline Steps */}
              <Card className="border-slate-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-indigo-600" />
                    Automation Pipeline
                  </CardTitle>
                  <CardDescription>
                    Run individual automation steps or the full pipeline
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Step 1: Trend Scoring */}
                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-600 font-bold text-sm">1</div>
                      <div>
                        <p className="font-medium text-slate-900">Calculate Trend Scores</p>
                        <p className="text-sm text-slate-500">Based on views, ads, competition, margin</p>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={handleRunTrendScoring}
                      disabled={loading.scoring}
                      data-testid="run-scoring-btn"
                    >
                      {loading.scoring ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                    </Button>
                  </div>

                  {/* Step 2: Opportunity Rating */}
                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 font-bold text-sm">2</div>
                      <div>
                        <p className="font-medium text-slate-900">Calculate Opportunity Ratings</p>
                        <p className="text-sm text-slate-500">Low, medium, high, very high</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-xs">Included in scoring</Badge>
                  </div>

                  {/* Step 3: Trend Stage */}
                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100 text-amber-600 font-bold text-sm">3</div>
                      <div>
                        <p className="font-medium text-slate-900">Classify Trend Stages</p>
                        <p className="text-sm text-slate-500">Early, rising, peak, saturated</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-xs">Included in scoring</Badge>
                  </div>

                  {/* Step 4: AI Summaries */}
                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100 text-purple-600 font-bold text-sm">4</div>
                      <div>
                        <p className="font-medium text-slate-900">Generate AI Summaries</p>
                        <p className="text-sm text-slate-500">Product insights and recommendations</p>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={handleGenerateSummaries}
                      disabled={loading.summaries}
                      data-testid="run-summaries-btn"
                    >
                      {loading.summaries ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                    </Button>
                  </div>

                  {/* Step 5: Alerts */}
                  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-rose-100 text-rose-600 font-bold text-sm">5</div>
                      <div>
                        <p className="font-medium text-slate-900">Generate Trend Alerts</p>
                        <p className="text-sm text-slate-500">For high-opportunity products</p>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={handleGenerateAlerts}
                      disabled={loading.alerts}
                      data-testid="run-alerts-btn"
                    >
                      {loading.alerts ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bell className="h-4 w-4" />}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Future Integrations */}
              <Card className="border-slate-200">
                <CardHeader>
                  <CardTitle>Future Integrations</CardTitle>
                  <CardDescription>
                    Upcoming automated data sources (placeholders)
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { name: 'TikTok Creative Center API', status: 'planned', desc: 'Auto-import trending products' },
                    { name: 'Amazon Product API', status: 'planned', desc: 'Price & competition data' },
                    { name: 'AliExpress API', status: 'planned', desc: 'Supplier sourcing automation' },
                    { name: 'OpenAI GPT-4', status: 'ready', desc: 'Enhanced AI summaries' },
                    { name: 'Scheduled Jobs', status: 'ready', desc: 'Cron-based automation' },
                    { name: 'Webhook Triggers', status: 'planned', desc: 'Real-time data updates' },
                  ].map((integration) => (
                    <div key={integration.name} className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
                      <div>
                        <p className="font-medium text-slate-900">{integration.name}</p>
                        <p className="text-sm text-slate-500">{integration.desc}</p>
                      </div>
                      <Badge 
                        variant="outline" 
                        className={integration.status === 'ready' ? 'border-emerald-200 text-emerald-700' : 'border-slate-200 text-slate-500'}
                      >
                        {integration.status}
                      </Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs">
            <AutomationLogs />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
