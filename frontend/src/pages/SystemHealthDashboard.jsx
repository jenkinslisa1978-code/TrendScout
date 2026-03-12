import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Activity, RefreshCw, Database, Wifi, Server, Zap,
  CheckCircle2, AlertTriangle, XCircle, Clock, Loader2,
  ChevronDown, ChevronUp, Shield,
} from 'lucide-react';
import { apiGet } from '@/lib/api';
import { toast } from 'sonner';

const STATUS_CONFIG = {
  healthy: { icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', badge: 'bg-emerald-100 text-emerald-700 border-emerald-200', dot: 'bg-emerald-500' },
  warning: { icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', badge: 'bg-amber-100 text-amber-700 border-amber-200', dot: 'bg-amber-500' },
  error:   { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', badge: 'bg-red-100 text-red-700 border-red-200', dot: 'bg-red-500' },
};

const CATEGORY_META = {
  data_ingestion:   { label: 'Data Ingestion', icon: Database, color: 'text-blue-600' },
  api_integrations: { label: 'API Integrations', icon: Wifi, color: 'text-violet-600' },
  core_systems:     { label: 'Core Systems', icon: Zap, color: 'text-amber-600' },
  infrastructure:   { label: 'Infrastructure', icon: Server, color: 'text-slate-700' },
};

function StatusDot({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.error;
  return <span className={`inline-block w-2 h-2 rounded-full ${cfg.dot}`} />;
}

function OverallBanner({ data }) {
  const cfg = STATUS_CONFIG[data.overall_status] || STATUS_CONFIG.error;
  const Icon = cfg.icon;
  return (
    <div className={`rounded-2xl border ${cfg.border} ${cfg.bg} p-6`} data-testid="overall-banner">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-xl bg-white/80 flex items-center justify-center shadow-sm">
            <Icon className={`h-7 w-7 ${cfg.color}`} />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Platform Status</h2>
            <p className="text-sm text-slate-600 mt-0.5">
              {data.healthy} healthy, {data.warnings} warnings, {data.errors} errors
            </p>
          </div>
        </div>
        <div className="text-right">
          <Badge className={`${cfg.badge} text-sm px-3 py-1`} data-testid="overall-status-badge">
            {data.overall_status.charAt(0).toUpperCase() + data.overall_status.slice(1)}
          </Badge>
          <p className="text-xs text-slate-400 mt-2">Avg uptime: {data.avg_uptime}%</p>
        </div>
      </div>
      {/* Stats row */}
      <div className="grid grid-cols-4 gap-4 mt-5">
        <StatCard label="Total Checks" value={data.total_checks} />
        <StatCard label="Healthy" value={data.healthy} color="text-emerald-700" />
        <StatCard label="Warnings" value={data.warnings} color="text-amber-700" />
        <StatCard label="Errors" value={data.errors} color="text-red-700" />
      </div>
    </div>
  );
}

function StatCard({ label, value, color = 'text-slate-900' }) {
  return (
    <div className="bg-white/60 rounded-xl p-3 text-center">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-[11px] text-slate-500 mt-0.5">{label}</p>
    </div>
  );
}

function ServiceRow({ check }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = STATUS_CONFIG[check.status] || STATUS_CONFIG.error;
  const Icon = cfg.icon;

  const lastSuccess = check.last_success
    ? new Date(check.last_success).toLocaleString()
    : 'Never';

  return (
    <div
      className={`rounded-xl border ${cfg.border} ${cfg.bg} transition-all`}
      data-testid={`service-${check.name.toLowerCase().replace(/\s+/g, '-')}`}
    >
      <div
        className="flex items-center gap-3 p-3 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="w-8 h-8 rounded-lg bg-white/80 flex items-center justify-center flex-shrink-0">
          <Icon className={`h-4 w-4 ${cfg.color}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-800">{check.name}</span>
            <Badge className={`text-[10px] ${cfg.badge}`}>{check.status}</Badge>
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5 truncate">{check.message}</p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="w-20">
            <Progress value={check.uptime || 0} className="h-1.5" />
            <p className="text-[10px] text-slate-400 text-center mt-0.5">{check.uptime}%</p>
          </div>
          {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
        </div>
      </div>
      {expanded && (
        <div className="px-3 pb-3 ml-11 space-y-1.5 text-xs">
          <div className="flex gap-6">
            <span className="text-slate-500">Last Success:</span>
            <span className="font-medium text-slate-700">{lastSuccess}</span>
          </div>
          <div className="flex gap-6">
            <span className="text-slate-500">Status:</span>
            <span className={`font-medium ${cfg.color}`}>{check.status}</span>
          </div>
          <div className="flex gap-6">
            <span className="text-slate-500">Message:</span>
            <span className="text-slate-700">{check.message}</span>
          </div>
          {check.extra?.jobs && (
            <div className="mt-2 space-y-1">
              <p className="text-[11px] font-semibold text-slate-600">Scheduled Jobs:</p>
              {check.extra.jobs.map((j, i) => (
                <div key={i} className="flex items-center gap-2 text-[10px] text-slate-500 bg-white/60 rounded px-2 py-1">
                  <StatusDot status="healthy" />
                  <span className="flex-1 truncate">{j.name}</span>
                  {j.next_run && <span className="text-slate-400">Next: {j.next_run.slice(0, 16)}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CategorySection({ categoryKey, checks }) {
  const meta = CATEGORY_META[categoryKey] || { label: categoryKey, icon: Server, color: 'text-slate-600' };
  const Icon = meta.icon;
  const healthyCount = checks.filter(c => c.status === 'healthy').length;

  return (
    <Card className="border-0 shadow-md overflow-hidden" data-testid={`category-${categoryKey}`}>
      <CardHeader className="py-3 px-4 bg-white border-b border-slate-100">
        <CardTitle className="text-sm font-semibold text-slate-800 flex items-center gap-2">
          <Icon className={`h-4 w-4 ${meta.color}`} />
          {meta.label}
          <Badge className="ml-auto bg-slate-100 text-slate-600 border-slate-200 text-[10px]">
            {healthyCount}/{checks.length} healthy
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-3 space-y-2">
        {checks.map((check, i) => (
          <ServiceRow key={i} check={check} />
        ))}
      </CardContent>
    </Card>
  );
}

export default function SystemHealthDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchHealth = useCallback(async (showToast = false) => {
    try {
      const res = await apiGet('/api/system-health');
      if (res.ok) {
        setData(await res.json());
        if (showToast) toast.success('Health data refreshed');
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || 'Failed to load health data');
      }
    } catch (e) {
      toast.error('Network error');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchHealth(); }, [fetchHealth]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchHealth(true);
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </DashboardLayout>
    );
  }

  if (!data) {
    return (
      <DashboardLayout>
        <div className="max-w-3xl mx-auto text-center py-20">
          <Shield className="h-12 w-12 text-slate-300 mx-auto mb-4" />
          <p className="text-lg font-semibold text-slate-700">Unable to load system health</p>
          <p className="text-sm text-slate-500 mt-1">Admin access is required to view this page.</p>
          <Button onClick={handleRefresh} className="mt-4" data-testid="retry-btn">Retry</Button>
        </div>
      </DashboardLayout>
    );
  }

  const categoryOrder = ['data_ingestion', 'api_integrations', 'core_systems', 'infrastructure'];

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-6" data-testid="system-health-dashboard">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <Activity className="h-6 w-6 text-indigo-600" />
              System Health
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Platform operational overview
              {data.checked_at && (
                <span className="text-slate-400 ml-2">
                  &middot; Checked {new Date(data.checked_at).toLocaleTimeString()}
                </span>
              )}
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
            data-testid="refresh-health-btn"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Overall banner */}
        <OverallBanner data={data} />

        {/* Category sections */}
        <div className="grid md:grid-cols-2 gap-6">
          {categoryOrder.map((catKey) => {
            const checks = data.categories?.[catKey];
            if (!checks || checks.length === 0) return null;
            return <CategorySection key={catKey} categoryKey={catKey} checks={checks} />;
          })}
        </div>
      </div>
    </DashboardLayout>
  );
}
