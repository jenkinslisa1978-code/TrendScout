import React, { useState } from 'react';
import { Bell, X, Check, AlertTriangle, Loader2, Activity, Wifi, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';

const JOB_LABELS = {
  full_pipeline: 'Full Automation',
  trend_scoring: 'Trend Scoring',
  opportunity_rating: 'Opportunity Rating',
  ai_summary: 'AI Summaries',
  alert_generation: 'Alert Generation',
  tiktok_import: 'TikTok Import',
  amazon_import: 'Amazon Import',
  supplier_import: 'Supplier Import',
  full_data_sync: 'Full Data Sync',
};

const formatTime = (ts) => {
  if (!ts) return '';
  const d = new Date(ts);
  const now = new Date();
  const diff = (now - d) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return d.toLocaleDateString();
};

function NotificationItem({ notification }) {
  const label = JOB_LABELS[notification.job_type] || notification.job_type;
  const source = notification.source ? ` (${notification.source})` : '';

  if (notification.type === 'job_started') {
    return (
      <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-50/80 border border-blue-100" data-testid={`notification-started-${notification.job_type}`}>
        <Loader2 className="h-4 w-4 text-blue-500 animate-spin mt-0.5 shrink-0" />
        <div className="min-w-0">
          <p className="text-sm font-medium text-blue-800">{label} started{source}</p>
          <p className="text-xs text-blue-500">{formatTime(notification.timestamp)}</p>
        </div>
      </div>
    );
  }

  if (notification.type === 'job_progress') {
    const pct = notification.total > 0 ? Math.round((notification.current / notification.total) * 100) : 0;
    return (
      <div className="flex items-start gap-3 p-3 rounded-lg bg-indigo-50/80 border border-indigo-100" data-testid={`notification-progress-${notification.job_type}`}>
        <Activity className="h-4 w-4 text-indigo-500 mt-0.5 shrink-0" />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-indigo-800">{label}{source}</p>
          <div className="mt-1 w-full bg-indigo-200 rounded-full h-1.5">
            <div className="bg-indigo-500 h-1.5 rounded-full transition-all" style={{ width: `${pct}%` }} />
          </div>
          <p className="text-xs text-indigo-500 mt-1">{notification.detail || `${notification.current}/${notification.total}`}</p>
        </div>
      </div>
    );
  }

  if (notification.type === 'job_completed') {
    const result = notification.result || {};
    const detail = result.processed
      ? `${result.processed} products, ${result.alerts_generated || 0} alerts`
      : result.inserted !== undefined
      ? `${result.inserted} new, ${result.updated || 0} updated`
      : result.total_imported !== undefined
      ? `${result.total_imported} imported, ${result.total_alerts || 0} alerts`
      : 'Done';
    return (
      <div className="flex items-start gap-3 p-3 rounded-lg bg-emerald-50/80 border border-emerald-100" data-testid={`notification-completed-${notification.job_type}`}>
        <Check className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
        <div className="min-w-0">
          <p className="text-sm font-medium text-emerald-800">{label} completed{source}</p>
          <p className="text-xs text-emerald-600">{detail}</p>
          <p className="text-xs text-emerald-400">{formatTime(notification.timestamp)}</p>
        </div>
      </div>
    );
  }

  if (notification.type === 'job_failed') {
    return (
      <div className="flex items-start gap-3 p-3 rounded-lg bg-red-50/80 border border-red-100" data-testid={`notification-failed-${notification.job_type}`}>
        <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />
        <div className="min-w-0">
          <p className="text-sm font-medium text-red-800">{label} failed{source}</p>
          <p className="text-xs text-red-500 truncate">{notification.error}</p>
          <p className="text-xs text-red-400">{formatTime(notification.timestamp)}</p>
        </div>
      </div>
    );
  }

  return null;
}

export default function NotificationFeed({ notifications, connected, activeJobs, onClear }) {
  const [open, setOpen] = useState(false);
  const unreadCount = notifications.filter(
    (n) => n.type === 'job_completed' || n.type === 'job_failed'
  ).length;
  const activeCount = Object.keys(activeJobs || {}).length;

  return (
    <div className="relative" data-testid="notification-feed">
      <Button
        variant="ghost"
        size="sm"
        className="relative p-2"
        onClick={() => setOpen(!open)}
        data-testid="notification-bell"
      >
        <Bell className="h-5 w-5 text-slate-600" />
        {(unreadCount > 0 || activeCount > 0) && (
          <span className="absolute -top-0.5 -right-0.5 h-4 min-w-[1rem] px-1 flex items-center justify-center bg-indigo-500 text-white text-[10px] font-bold rounded-full">
            {activeCount > 0 ? activeCount : unreadCount}
          </span>
        )}
        {activeCount > 0 && (
          <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 bg-emerald-400 rounded-full animate-pulse" />
        )}
      </Button>

      {open && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />

          {/* Dropdown */}
          <div className="absolute right-0 top-full mt-2 w-[380px] max-h-[480px] bg-white rounded-xl shadow-2xl border border-slate-200 z-50 overflow-hidden" data-testid="notification-dropdown">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50/50">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-slate-800">Live Activity</h3>
                {connected ? (
                  <span className="flex items-center gap-1 text-[10px] text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full">
                    <Wifi className="h-2.5 w-2.5" /> Live
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-[10px] text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded-full">
                    <WifiOff className="h-2.5 w-2.5" /> Reconnecting
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1">
                {notifications.length > 0 && (
                  <Button variant="ghost" size="sm" className="h-7 text-xs text-slate-500" onClick={onClear} data-testid="clear-notifications">
                    Clear
                  </Button>
                )}
                <Button variant="ghost" size="sm" className="h-7 p-1" onClick={() => setOpen(false)}>
                  <X className="h-4 w-4 text-slate-400" />
                </Button>
              </div>
            </div>

            {/* Active Jobs */}
            {activeCount > 0 && (
              <div className="px-3 py-2 border-b border-slate-100 bg-indigo-50/30">
                <p className="text-[10px] font-semibold text-indigo-600 uppercase tracking-wider mb-1.5">Running Now</p>
                <div className="space-y-1.5">
                  {Object.entries(activeJobs).map(([key, job]) => (
                    <div key={key} className="flex items-center gap-2 text-xs text-indigo-700">
                      <Loader2 className="h-3 w-3 animate-spin shrink-0" />
                      <span className="font-medium">{JOB_LABELS[key] || key}</span>
                      {job.current && job.total && (
                        <span className="text-indigo-500 ml-auto">{Math.round((job.current / job.total) * 100)}%</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Notification List */}
            <div className="overflow-y-auto max-h-[360px] p-2 space-y-1.5">
              {notifications.length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                  <Bell className="h-8 w-8 mx-auto mb-2 opacity-40" />
                  <p className="text-sm">No notifications yet</p>
                  <p className="text-xs mt-1">Activity will appear here in real-time</p>
                </div>
              ) : (
                notifications.map((n, i) => <NotificationItem key={`${n.timestamp}-${i}`} notification={n} />)
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
