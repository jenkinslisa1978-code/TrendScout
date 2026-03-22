import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  BarChart3, TrendingUp, Users, Eye, Loader2, ArrowUpRight, ArrowDownRight,
  MousePointerClick, UserPlus, ShoppingCart, Activity, Flame,
  Calendar, PoundSterling, Mail, Target, Search, Zap,
} from 'lucide-react';
import api from '@/lib/api';

function StatCard({ label, value, subtitle, icon: Icon, color, trend, testId }) {
  const isUp = trend > 0;
  return (
    <Card className="border-slate-200 shadow-sm" data-testid={testId}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${color}`}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
        {trend !== undefined && trend !== null && (
          <div className={`flex items-center gap-1 mt-2 text-xs font-medium ${isUp ? 'text-emerald-600' : trend < 0 ? 'text-red-500' : 'text-slate-400'}`}>
            {isUp ? <ArrowUpRight className="h-3 w-3" /> : trend < 0 ? <ArrowDownRight className="h-3 w-3" /> : null}
            {trend !== 0 ? `${Math.abs(trend)}% vs prev period` : 'No change'}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function DripStep({ label, count, total, color }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div className="flex items-center gap-4">
      <div className="w-36 text-sm font-medium text-slate-700">{label}</div>
      <div className="flex-1 h-8 bg-slate-50 rounded-lg overflow-hidden relative">
        <div
          className={`h-full ${color} rounded-lg transition-all duration-700 flex items-center justify-end pr-3`}
          style={{ width: `${Math.max(5, pct)}%` }}
        >
          <span className="text-white text-xs font-bold">{count}</span>
        </div>
      </div>
      <span className="w-12 text-right text-xs font-mono text-slate-500">{pct}%</span>
    </div>
  );
}

function pctChange(current, previous) {
  if (!previous || previous === 0) return current > 0 ? 100 : 0;
  return Math.round(((current - previous) / previous) * 100);
}

export default function AnalyticsDashboardPage() {
  const [data, setData] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [growth, setGrowth] = useState(null);
  const [emailStats, setEmailStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get(`/api/analytics/dashboard?days=${days}`).then(r => r.data).catch(() => null),
      api.get(`/api/analytics/funnel?days=${days}`).then(r => r.data).catch(() => null),
      api.get(`/api/analytics/growth?days=${days}`).then(r => r.data).catch(() => null),
      api.get('/api/webhooks/resend/stats').then(r => r.data).catch(() => null),
    ]).then(([dashData, funnelData, growthData, emailData]) => {
      setData(dashData);
      setFunnel(funnelData);
      setGrowth(growthData);
      setEmailStats(emailData);
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

  const rev = growth?.revenue || {};
  const leads = growth?.leads || {};
  const drip = growth?.email_drip || {};
  const users = growth?.users || {};
  const planDist = users.plan_distribution || {};
  const topSearches = leads.top_searches || [];
  const leadSources = leads.sources || {};

  const eventCounts = data?.event_counts || {};
  const funnelData = funnel?.funnel || {};
  const conversionRates = funnel?.conversion_rates || {};
  const dailyBreakdown = data?.daily_breakdown || {};
  const topPages = data?.top_pages || [];

  const FUNNEL_STEPS = [
    { key: 'page_view', label: 'Visits', icon: Eye, color: 'bg-sky-500' },
    { key: 'signup_click', label: 'Signup Clicks', icon: MousePointerClick, color: 'bg-indigo-500' },
    { key: 'signup_complete', label: 'Signups', icon: UserPlus, color: 'bg-violet-500' },
    { key: 'product_view', label: 'Product Views', icon: Activity, color: 'bg-amber-500' },
    { key: 'upgrade_click', label: 'Upgrade Clicks', icon: ShoppingCart, color: 'bg-emerald-500' },
  ];

  const sortedDays = Object.keys(dailyBreakdown).sort();

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="analytics-dashboard">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">Growth & Revenue</h1>
            <p className="mt-1 text-sm text-slate-500">Track leads, conversions, email performance, and revenue</p>
          </div>
          <div className="flex items-center gap-2">
            {[7, 14, 30, 90].map(d => (
              <Button
                key={d}
                size="sm"
                variant={days === d ? 'default' : 'outline'}
                onClick={() => setDays(d)}
                className={days === d ? 'bg-indigo-600 hover:bg-indigo-700' : ''}
                data-testid={`period-${d}d`}
              >
                {d}d
              </Button>
            ))}
          </div>
        </div>

        {/* Revenue KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" data-testid="revenue-kpis">
          <StatCard
            label="Monthly Recurring Revenue"
            value={`\u00A3${(rev.mrr || 0).toLocaleString()}`}
            subtitle={`${rev.total_paid_subscribers || 0} paid subscribers`}
            icon={PoundSterling}
            color="text-emerald-600 bg-emerald-50"
            testId="stat-mrr"
          />
          <StatCard
            label={`New Revenue (${days}d)`}
            value={`\u00A3${(rev.new_revenue_period || 0).toLocaleString()}`}
            subtitle={`${rev.new_subscribers_period || 0} new subscribers`}
            icon={TrendingUp}
            color="text-indigo-600 bg-indigo-50"
            trend={pctChange(rev.new_revenue_period, rev.prev_revenue_period)}
            testId="stat-new-revenue"
          />
          <StatCard
            label={`Leads Captured (${days}d)`}
            value={leads.period || 0}
            subtitle={`${leads.total || 0} total`}
            icon={Target}
            color="text-amber-600 bg-amber-50"
            trend={pctChange(leads.period, leads.prev_period)}
            testId="stat-leads"
          />
          <StatCard
            label={`New Signups (${days}d)`}
            value={users.period_signups || 0}
            subtitle={`${users.total || 0} total users`}
            icon={Users}
            color="text-violet-600 bg-violet-50"
            testId="stat-signups"
          />
        </div>

        {/* Email Drip + Lead Sources */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Email Drip Performance */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Mail className="h-5 w-5 text-indigo-500" />
                Email Drip Performance
              </CardTitle>
              <CardDescription>3-email nurture sequence delivery</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3" data-testid="drip-performance">
              <DripStep label="Instant Result" count={drip.viability_result_sent || 0} total={leads.total || 1} color="bg-indigo-500" />
              <DripStep label="Day 2: Trending" count={drip.trending_products_sent || 0} total={leads.total || 1} color="bg-violet-500" />
              <DripStep label="Day 5: Trial CTA" count={drip.trial_prompt_sent || 0} total={leads.total || 1} color="bg-emerald-500" />
              <div className="border-t pt-3 mt-3 flex items-center justify-between text-sm">
                <span className="text-slate-500">Total Emails Sent</span>
                <span className="font-bold text-slate-900">
                  {(drip.viability_result_sent || 0) + (drip.trending_products_sent || 0) + (drip.trial_prompt_sent || 0)}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Email Engagement (from Resend webhooks) */}
          {emailStats && (
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Mail className="h-5 w-5 text-emerald-500" />
                Email Engagement
              </CardTitle>
              <CardDescription>Open & click rates from Resend</CardDescription>
            </CardHeader>
            <CardContent data-testid="email-engagement">
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-emerald-50 rounded-xl p-3 text-center">
                  <p className="font-mono text-2xl font-bold text-emerald-600">{emailStats.open_rate || 0}%</p>
                  <p className="text-xs text-slate-500">Open Rate</p>
                </div>
                <div className="bg-indigo-50 rounded-xl p-3 text-center">
                  <p className="font-mono text-2xl font-bold text-indigo-600">{emailStats.click_rate || 0}%</p>
                  <p className="text-xs text-slate-500">Click Rate</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                {[
                  { label: 'Delivered', value: emailStats.total_delivered, color: 'text-slate-700' },
                  { label: 'Opened', value: emailStats.total_opened, color: 'text-emerald-600' },
                  { label: 'Clicked', value: emailStats.total_clicked, color: 'text-indigo-600' },
                  { label: 'Bounced', value: emailStats.total_bounced, color: 'text-red-500' },
                ].map(row => (
                  <div key={row.label} className="flex justify-between items-center py-1 border-b border-slate-50 last:border-0">
                    <span className="text-slate-500">{row.label}</span>
                    <span className={`font-bold font-mono ${row.color}`}>{row.value || 0}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          )}

          {/* Lead Sources + Top Searches */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Search className="h-5 w-5 text-amber-500" />
                Top Product Searches
              </CardTitle>
              <CardDescription>What leads are searching for</CardDescription>
            </CardHeader>
            <CardContent data-testid="top-searches">
              {topSearches.length > 0 ? (
                <div className="space-y-2">
                  {topSearches.map((s, i) => (
                    <div key={i} className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-400 w-5">{i + 1}</span>
                        <span className="text-sm text-slate-700 capitalize">{s.term}</span>
                      </div>
                      <span className="text-xs font-mono font-bold text-slate-500">{s.count}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400 text-center py-6">No searches yet</p>
              )}
              {Object.keys(leadSources).length > 0 && (
                <div className="border-t pt-3 mt-4">
                  <p className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wide">Lead Sources</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(leadSources).map(([src, count]) => (
                      <span key={src} className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-100 rounded-full text-xs font-medium text-slate-600">
                        {(src || 'direct').replace(/_/g, ' ')} <span className="text-slate-400">({count})</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Plan Distribution + Conversion Funnel */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Plan Distribution */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Zap className="h-5 w-5 text-amber-500" />
                User Plan Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent data-testid="plan-distribution">
              {Object.keys(planDist).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(planDist)
                    .sort(([, a], [, b]) => b - a)
                    .map(([plan, count]) => {
                      const total = Object.values(planDist).reduce((a, b) => a + b, 0);
                      const pct = Math.round((count / total) * 100);
                      const colors = { elite: 'bg-amber-500', pro: 'bg-indigo-500', free: 'bg-slate-400', none: 'bg-slate-200' };
                      return (
                        <div key={plan}>
                          <div className="flex justify-between mb-1">
                            <span className="text-sm font-medium text-slate-700 capitalize">{plan === 'none' ? 'No plan' : plan}</span>
                            <span className="text-sm text-slate-500">{count} ({pct}%)</span>
                          </div>
                          <div className="h-3 bg-slate-50 rounded-full overflow-hidden">
                            <div className={`h-full ${colors[plan] || 'bg-slate-300'} rounded-full`} style={{ width: `${pct}%` }} />
                          </div>
                        </div>
                      );
                    })}
                </div>
              ) : (
                <p className="text-sm text-slate-400 text-center py-6">No user data</p>
              )}
            </CardContent>
          </Card>

          {/* Conversion Funnel */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Flame className="h-5 w-5 text-amber-500" />
                Conversion Funnel
              </CardTitle>
              <CardDescription>User journey ({days}-day period)</CardDescription>
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
                      <div className="h-6 bg-slate-50 rounded-lg overflow-hidden">
                        <div className={`h-full ${step.color} rounded-lg transition-all duration-700`} style={{ width: `${widthPct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="grid grid-cols-2 gap-3 mt-4 pt-3 border-t">
                {Object.entries(conversionRates).map(([key, val]) => {
                  const labels = { visit_to_signup_click: 'Visit to Click', click_to_complete: 'Click to Signup', signup_to_product_view: 'Signup to View', view_to_upgrade_click: 'View to Upgrade' };
                  return (
                    <div key={key} className="bg-slate-50 rounded-xl p-2.5 text-center">
                      <p className="font-mono text-lg font-bold text-indigo-600">{val}%</p>
                      <p className="text-[10px] text-slate-500">{labels[key] || key}</p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Event Breakdown + Top Pages */}
        <div className="grid md:grid-cols-2 gap-6">
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
                  .slice(0, 12)
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

        {/* Daily Activity Table */}
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
                      <th className="text-center p-3 font-medium text-slate-700">Visits</th>
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
