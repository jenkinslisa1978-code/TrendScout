import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Activity,
  Loader2,
  AlertTriangle
} from 'lucide-react';
import { getAutomationLogs, getAutomationStats, AutomationStatus } from '@/services/automationLogService';
import { formatDistanceToNow } from 'date-fns';

const JOB_TYPE_LABELS = {
  full_pipeline: 'Full Pipeline',
  trend_scoring: 'Trend Scoring',
  opportunity_rating: 'Opportunity Rating',
  trend_stage: 'Trend Stage',
  ai_summary: 'AI Summary',
  alert_generation: 'Alert Generation',
  product_import: 'Product Import',
  csv_import: 'CSV Import',
  scheduled_daily: 'Scheduled Daily',
  tiktok_import: 'TikTok Import',
  amazon_import: 'Amazon Import',
  supplier_import: 'Supplier Import',
  full_data_sync: 'Full Data Sync',
};

const STATUS_CONFIG = {
  started: { color: 'bg-slate-100 text-slate-700', icon: Clock },
  running: { color: 'bg-blue-100 text-blue-700', icon: Loader2 },
  completed: { color: 'bg-emerald-100 text-emerald-700', icon: CheckCircle2 },
  failed: { color: 'bg-red-100 text-red-700', icon: XCircle },
  partial: { color: 'bg-amber-100 text-amber-700', icon: AlertTriangle },
};

export default function AutomationLogs() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    
    const [logsResult, statsResult] = await Promise.all([
      getAutomationLogs({ limit: 20 }),
      getAutomationStats(),
    ]);

    if (logsResult.data) setLogs(logsResult.data);
    if (statsResult.data) setStats(statsResult.data);
    
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatTime = (timestamp) => {
    if (!timestamp) return '-';
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return timestamp;
    }
  };

  const StatusBadge = ({ status }) => {
    const config = STATUS_CONFIG[status] || STATUS_CONFIG.started;
    const Icon = config.icon;
    
    return (
      <Badge className={`${config.color} border-0 font-semibold capitalize inline-flex items-center gap-1`}>
        <Icon className={`h-3 w-3 ${status === 'running' ? 'animate-spin' : ''}`} />
        {status}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50">
                  <Activity className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900">{stats.totalRuns}</p>
                  <p className="text-xs text-slate-500">Total Runs</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
                  <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900">{stats.successRate}%</p>
                  <p className="text-xs text-slate-500">Success Rate</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-50">
                  <RefreshCw className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900">{stats.productsProcessed}</p>
                  <p className="text-xs text-slate-500">Products Processed</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
                  <AlertTriangle className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900">{stats.alertsGenerated}</p>
                  <p className="text-xs text-slate-500">Alerts Generated</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Logs Table */}
      <Card className="border-slate-200">
        <CardHeader className="border-b border-slate-100 py-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-bold">Automation History</CardTitle>
            <Button variant="outline" size="sm" onClick={fetchData} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Activity className="h-12 w-12 mx-auto mb-3 text-slate-300" />
              <p>No automation logs yet</p>
              <p className="text-sm">Run an automation task to see logs here</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/80">
                  <TableHead className="font-bold text-slate-600 text-xs uppercase">Job Type</TableHead>
                  <TableHead className="font-bold text-slate-600 text-xs uppercase">Status</TableHead>
                  <TableHead className="font-bold text-slate-600 text-xs uppercase text-center">Products</TableHead>
                  <TableHead className="font-bold text-slate-600 text-xs uppercase text-center">Alerts</TableHead>
                  <TableHead className="font-bold text-slate-600 text-xs uppercase">Started</TableHead>
                  <TableHead className="font-bold text-slate-600 text-xs uppercase">Duration</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => {
                  const duration = log.completed_at && log.started_at
                    ? Math.round((new Date(log.completed_at) - new Date(log.started_at)) / 1000)
                    : null;
                  
                  return (
                    <TableRow key={log.id} className="hover:bg-slate-50/50">
                      <TableCell className="font-medium text-slate-900">
                        {JOB_TYPE_LABELS[log.job_type] || log.job_type}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={log.status} />
                      </TableCell>
                      <TableCell className="text-center font-mono">
                        {log.products_processed || 0}
                      </TableCell>
                      <TableCell className="text-center font-mono">
                        {log.alerts_generated || 0}
                      </TableCell>
                      <TableCell className="text-slate-500 text-sm">
                        {formatTime(log.started_at)}
                      </TableCell>
                      <TableCell className="text-slate-500 text-sm font-mono">
                        {duration !== null ? `${duration}s` : '-'}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
