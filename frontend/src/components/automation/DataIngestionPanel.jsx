import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Play, 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  TrendingUp,
  ShoppingCart,
  Package,
  RefreshCw,
  Database
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const DATA_SOURCES = [
  {
    id: 'tiktok',
    name: 'TikTok Creative Center',
    description: 'Import trending products from TikTok viral content',
    icon: TrendingUp,
    color: 'bg-pink-500',
    endpoint: '/api/ingestion/tiktok',
  },
  {
    id: 'amazon',
    name: 'Amazon Movers & Shakers',
    description: 'Import fast-rising products from Amazon rankings',
    icon: ShoppingCart,
    color: 'bg-amber-500',
    endpoint: '/api/ingestion/amazon',
  },
  {
    id: 'supplier',
    name: 'Supplier Feeds',
    description: 'Import from AliExpress, CJ Dropshipping, etc.',
    icon: Package,
    color: 'bg-blue-500',
    endpoint: '/api/ingestion/supplier',
  },
];

export default function DataIngestionPanel() {
  const [loading, setLoading] = useState({});
  const [results, setResults] = useState({});
  const [productLimit, setProductLimit] = useState('20');
  const [lastSync, setLastSync] = useState(null);

  const runImport = async (source) => {
    setLoading(prev => ({ ...prev, [source.id]: true }));
    setResults(prev => ({ ...prev, [source.id]: null }));

    try {
      const response = await fetch(`${API_URL}${source.endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: parseInt(productLimit) }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setResults(prev => ({
          ...prev,
          [source.id]: {
            success: true,
            fetched: data.fetched,
            inserted: data.inserted,
            updated: data.updated,
            alerts: data.automation?.alerts_generated || 0,
          },
        }));
        toast.success(`Imported ${data.inserted + data.updated} products from ${source.name}`);
      } else {
        setResults(prev => ({
          ...prev,
          [source.id]: { success: false, error: data.detail || 'Import failed' },
        }));
        toast.error(`Failed to import from ${source.name}`);
      }
    } catch (error) {
      setResults(prev => ({
        ...prev,
        [source.id]: { success: false, error: error.message },
      }));
      toast.error(`Error importing from ${source.name}`);
    }

    setLoading(prev => ({ ...prev, [source.id]: false }));
  };

  const runFullSync = async () => {
    setLoading(prev => ({ ...prev, fullSync: true }));
    setResults({});

    try {
      const response = await fetch(`${API_URL}/api/ingestion/full-sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: parseInt(productLimit) }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setResults({
          fullSync: {
            success: true,
            total: data.total_imported,
            alerts: data.total_alerts,
            sources: data.sources,
          },
        });
        setLastSync(new Date().toISOString());
        toast.success(`Full sync complete: ${data.total_imported} products, ${data.total_alerts} alerts`);
      } else {
        toast.error('Full sync failed');
      }
    } catch (error) {
      toast.error(`Sync error: ${error.message}`);
    }

    setLoading(prev => ({ ...prev, fullSync: false }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900">Data Ingestion</h3>
          <p className="text-sm text-slate-500">Import trending products from external sources</p>
        </div>
        <div className="flex items-center gap-3">
          <Select value={productLimit} onValueChange={setProductLimit}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Limit" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10 products</SelectItem>
              <SelectItem value="20">20 products</SelectItem>
              <SelectItem value="50">50 products</SelectItem>
              <SelectItem value="100">100 products</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={runFullSync}
            disabled={loading.fullSync}
            className="bg-indigo-600 hover:bg-indigo-700"
            data-testid="full-sync-btn"
          >
            {loading.fullSync ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Database className="mr-2 h-4 w-4" />
            )}
            Full Data Sync
          </Button>
        </div>
      </div>

      {/* Full Sync Result */}
      {results.fullSync && (
        <Card className="border-emerald-200 bg-emerald-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
              <div>
                <p className="font-semibold text-emerald-900">Full Sync Complete</p>
                <p className="text-sm text-emerald-700">
                  Imported {results.fullSync.total} products • Generated {results.fullSync.alerts} alerts
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Source Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {DATA_SOURCES.map((source) => {
          const Icon = source.icon;
          const result = results[source.id];
          const isLoading = loading[source.id];

          return (
            <Card key={source.id} className="border-slate-200" data-testid={`source-${source.id}`}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${source.color}`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <Badge variant="outline" className="text-xs">
                    Active
                  </Badge>
                </div>
                <CardTitle className="text-base mt-3">{source.name}</CardTitle>
                <CardDescription className="text-xs">
                  {source.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {result && (
                  <div className={`mb-3 p-3 rounded-lg text-sm ${
                    result.success ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
                  }`}>
                    {result.success ? (
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>
                          {result.inserted} new, {result.updated} updated, {result.alerts} alerts
                        </span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <XCircle className="h-4 w-4" />
                        <span>{result.error}</span>
                      </div>
                    )}
                  </div>
                )}
                <Button
                  onClick={() => runImport(source)}
                  disabled={isLoading}
                  variant="outline"
                  className="w-full"
                  data-testid={`import-${source.id}-btn`}
                >
                  {isLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="mr-2 h-4 w-4" />
                  )}
                  Run Import
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Info Banner */}
      <Card className="border-slate-200 bg-slate-50">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <RefreshCw className="h-5 w-5 text-slate-500 mt-0.5" />
            <div className="text-sm text-slate-600">
              <p className="font-medium text-slate-700">Automated Daily Sync</p>
              <p className="mt-1">
                Configure a scheduled job to call <code className="bg-slate-200 px-1 rounded">/api/ingestion/full-sync</code> daily 
                to automatically keep your product database updated with the latest trends.
              </p>
              {lastSync && (
                <p className="mt-2 text-xs text-slate-500">
                  Last sync: {new Date(lastSync).toLocaleString()}
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
