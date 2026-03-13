import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  BarChart3, TrendingUp, Users, Eye, Loader2, ArrowRight,
  MousePointerClick, UserPlus, ShoppingCart, Activity, Flame,
  ChevronDown, Calendar,
} from 'lucide-react';
import api from '@/lib/api';

export default function AnalyticsDashboardPage() {
  const [data, setData] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(7);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get(`/api/analytics/dashboard?days=${days}`).then(r => r.data).catch(() => null),
      api.get(`/api/analytics/funnel?days=${days}`).then(r => r.data).catch(() => null),
    ]).then(([dashData, funnelData]) => {
      setData(dashData);
      setFunnel(funnelData);
      setLoading(false);
    });
  }, [days]);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      </DashboardLayout>
    );
  }

  const eventCounts = data?.event_counts || {};
  const funnelData = funnel?.funnel || {};
  const conversionRates = funnel?.conversion_rates || {};
  const dailyBreakdown = data?.daily_breakdown || {};
  const topPages = data?.top_pages || [];

  const FUNNEL_STEPS = [
    { key: 'page_view', label: 'Landing Visits', icon: Eye, color: 'bg-sky-500' },
    { key: 'signup_click', label: 'Signup Clicks', icon: MousePointerClick, color: 'bg-indigo-500' },
    { key: 'signup_complete', label: 'Signups', icon: UserPlus, color: 'bg-violet-500' },
    { key: 'product_view', label: 'Product Views', icon: Activity, color: 'bg-amber-500' },
    { key: 'upgrade_click', label: 'Upgrade Clicks', icon: ShoppingCart, color: 'bg-emerald-500' },
  ];

  const CONVERSION_LABELS = {
    visit_to_signup_click: 'Visit → Click',
    click_to_complete: 'Click → Signup',
    signup_to_product_view: 'Signup → View',
    view_to_upgrade_click: 'View → Upgrade',
  };

  const sortedDays = Object.keys(dailyBreakdown).sort();

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="analytics-dashboard">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">Analytics Dashboard</h1>
            <p className="mt-1 text-slate-500">Track conversions, engagement, and user behavior</p>
          </div>
          <div className="flex items-center gap-2">
            {[7, 14, 30].map(d => (
              <Button
                key={d}
                size="sm"
                variant={days === d ? 'default' : 'outline'}
                onClick={() => setDays(d)}
                className={days === d ? 'bg-indigo-600' : ''}
                data-testid={`period-${d}d`}
              >
                {d}d
              </Button>
            ))}
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total Events', value: data?.total_events || 0, icon: Activity, color: 'text-indigo-600 bg-indigo-50' },
            { label: 'Unique Sessions', value: data?.unique_sessions || 0, icon: Eye, color: 'text-sky-600 bg-sky-50' },
            { label: 'Unique Users', value: data?.unique_users || 0, icon: Users, color: 'text-violet-600 bg-violet-50' },
            { label: 'Signup Rate', value: conversionRates.visit_to_signup_click ? `${conversionRates.visit_to_signup_click}%` : '—', icon: TrendingUp, color: 'text-emerald-600 bg-emerald-50' },
          ].map(stat => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label} className="border-slate-200 shadow-sm">
                <CardContent className="p-5">
                  <div className="flex items-center gap-3">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${stat.color}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-slate-900">{typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}</p>
                      <p className="text-xs text-slate-500">{stat.label}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Conversion Funnel */}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Flame className="h-5 w-5 text-amber-500" />
              Conversion Funnel
            </CardTitle>
            <CardDescription>User journey from landing page to upgrade ({days}-day period)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3" data-testid="conversion-funnel">
              {FUNNEL_STEPS.map((step, i) => {
                const Icon = step.icon;
                const count = funnelData[step.key] || 0;
                const maxCount = Math.max(...FUNNEL_STEPS.map(s => funnelData[s.key] || 1));
                const widthPct = Math.max(5, (count / maxCount) * 100);

                return (
                  <div key={step.key} data-testid={`funnel-step-${step.key}`}>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4 text-slate-500" />
                        <span className="text-sm font-medium text-slate-700">{step.label}</span>
                      </div>
                      <span className="font-mono text-sm font-bold text-slate-900">{count.toLocaleString()}</span>
                    </div>
                    <div className="h-7 bg-slate-50 rounded-lg overflow-hidden">
                      <div
                        className={`h-full ${step.color} rounded-lg transition-all duration-700 flex items-center justify-end pr-2`}
                        style={{ width: `${widthPct}%` }}
                      >
                        {i > 0 && Object.values(conversionRates)[i - 1] && (
                          <span className="text-white text-xs font-medium">
                            {Object.values(conversionRates)[i - 1]}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Conversion Rate Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-4 border-t">
              {Object.entries(CONVERSION_LABELS).map(([key, label]) => (
                <div key={key} className="bg-slate-50 rounded-xl p-3 text-center">
                  <p className="font-mono text-xl font-bold text-indigo-600">{conversionRates[key] ? `${conversionRates[key]}%` : '—'}</p>
                  <p className="text-xs text-slate-500 mt-1">{label}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Event Breakdown */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-indigo-500" />
                Event Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2" data-testid="event-breakdown">
                {Object.entries(eventCounts)
                  .sort(([, a], [, b]) => b - a)
                  .map(([event, count]) => {
                    const maxEvt = Math.max(...Object.values(eventCounts));
                    const pct = Math.max(3, (count / maxEvt) * 100);
                    return (
                      <div key={event} className="flex items-center gap-3">
                        <span className="text-xs text-slate-600 w-32 truncate font-mono">{event}</span>
                        <div className="flex-1 h-5 bg-slate-50 rounded overflow-hidden">
                          <div className="h-full bg-indigo-100 rounded" style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-xs font-bold text-slate-700 w-12 text-right">{count}</span>
                      </div>
                    );
                  })}
                {Object.keys(eventCounts).length === 0 && (
                  <p className="text-sm text-slate-400 text-center py-4">No events recorded yet</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Top Pages */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Eye className="h-5 w-5 text-sky-500" />
                Top Pages
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2" data-testid="top-pages">
                {topPages.map((p, i) => {
                  const maxPV = topPages[0]?.views || 1;
                  const pct = Math.max(3, (p.views / maxPV) * 100);
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-xs text-slate-600 w-40 truncate font-mono">{p.page || '/'}</span>
                      <div className="flex-1 h-5 bg-slate-50 rounded overflow-hidden">
                        <div className="h-full bg-sky-100 rounded" style={{ width: `${pct}%` }} />
                      </div>
                      <span className="text-xs font-bold text-slate-700 w-12 text-right">{p.views}</span>
                    </div>
                  );
                })}
                {topPages.length === 0 && (
                  <p className="text-sm text-slate-400 text-center py-4">No page views yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Daily Breakdown */}
        {sortedDays.length > 0 && (
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Calendar className="h-5 w-5 text-violet-500" />
                Daily Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto" data-testid="daily-breakdown">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-slate-50">
                      <th className="text-left p-3 font-medium text-slate-700">Date</th>
                      <th className="text-center p-3 font-medium text-slate-700">Page Views</th>
                      <th className="text-center p-3 font-medium text-slate-700">Signup Clicks</th>
                      <th className="text-center p-3 font-medium text-slate-700">Signups</th>
                      <th className="text-center p-3 font-medium text-slate-700">Product Views</th>
                      <th className="text-center p-3 font-medium text-slate-700">Upgrades</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedDays.map(day => {
                      const d = dailyBreakdown[day] || {};
                      return (
                        <tr key={day} className="border-b last:border-0 hover:bg-slate-50">
                          <td className="p-3 font-mono text-slate-700">{day}</td>
                          <td className="p-3 text-center">{d.page_view || 0}</td>
                          <td className="p-3 text-center">{d.signup_click || 0}</td>
                          <td className="p-3 text-center font-semibold text-indigo-600">{d.signup_complete || 0}</td>
                          <td className="p-3 text-center">{d.product_view || 0}</td>
                          <td className="p-3 text-center font-semibold text-emerald-600">{d.upgrade_click || 0}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
