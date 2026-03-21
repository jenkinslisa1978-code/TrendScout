import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  PoundSterling, Users, Target, Mail, TrendingUp, BarChart3,
  Shield, Zap, Activity, Image, Wifi, Package, Loader2,
  CheckCircle2, AlertTriangle, Clock, ArrowRight, Eye,
  FileText, Bell, Search, Calendar, Server,
} from 'lucide-react';
import api from '@/lib/api';

function QuickStat({ label, value, sub, icon: Icon, color }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-white border border-slate-100">
      <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${color}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="min-w-0">
        <p className="text-lg font-bold text-slate-900 leading-tight">{value}</p>
        <p className="text-xs text-slate-500 truncate">{label}</p>
      </div>
    </div>
  );
}

function AdminLink({ href, icon: Icon, title, desc, badge, onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex items-start gap-3 p-4 rounded-xl border border-slate-100 bg-white hover:border-indigo-200 hover:shadow-sm transition-all text-left w-full group"
      data-testid={`admin-link-${href.replace(/\//g, '-')}`}
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-50 group-hover:bg-indigo-50 transition-colors">
        <Icon className="h-5 w-5 text-slate-500 group-hover:text-indigo-600" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="font-semibold text-slate-800 text-sm">{title}</p>
          {badge && <Badge variant="secondary" className="text-[10px] px-1.5 py-0">{badge}</Badge>}
        </div>
        <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
      </div>
      <ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-indigo-400 mt-1 shrink-0" />
    </button>
  );
}

function ChecklistItem({ done, label, action, onAction }) {
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-slate-50 last:border-0">
      {done ? (
        <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
      ) : (
        <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0" />
      )}
      <span className={`text-sm flex-1 ${done ? 'text-slate-500' : 'text-slate-800 font-medium'}`}>{label}</span>
      {action && !done && (
        <Button size="sm" variant="outline" className="text-xs h-7" onClick={onAction}>{action}</Button>
      )}
    </div>
  );
}

export default function AdminHubPage() {
  const navigate = useNavigate();
  const [growth, setGrowth] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/api/analytics/growth?days=7').then(r => r.data).catch(() => null),
      api.get('/api/system-health/overview').then(r => r.data).catch(() => null),
    ]).then(([g, h]) => {
      setGrowth(g);
      setHealth(h);
      setLoading(false);
    });
  }, []);

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
  const users = growth?.users || {};
  const drip = growth?.email_drip || {};
  const totalDripSent = (drip.viability_result_sent || 0) + (drip.trending_products_sent || 0) + (drip.trial_prompt_sent || 0);

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="admin-hub">
        {/* Header */}
        <div>
          <h1 className="font-manrope text-2xl font-bold text-slate-900">Admin Command Center</h1>
          <p className="mt-1 text-sm text-slate-500">Everything you need to run TrendScout at a glance</p>
        </div>

        {/* Quick Stats Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" data-testid="quick-stats">
          <QuickStat label="MRR" value={`\u00A3${rev.mrr || 0}`} icon={PoundSterling} color="text-emerald-600 bg-emerald-50" />
          <QuickStat label="Paid Subs" value={rev.total_paid_subscribers || 0} icon={TrendingUp} color="text-indigo-600 bg-indigo-50" />
          <QuickStat label="Leads (7d)" value={leads.period || 0} icon={Target} color="text-amber-600 bg-amber-50" />
          <QuickStat label="Signups (7d)" value={users.period_signups || 0} icon={Users} color="text-violet-600 bg-violet-50" />
          <QuickStat label="Emails Sent" value={totalDripSent} icon={Mail} color="text-sky-600 bg-sky-50" />
          <QuickStat label="Total Users" value={users.total || 0} icon={Users} color="text-slate-600 bg-slate-50" />
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Admin Checklist */}
          <div className="lg:col-span-2 space-y-6">
            {/* Setup & Health Checklist */}
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Shield className="h-5 w-5 text-indigo-500" />
                  Admin Checklist
                </CardTitle>
                <CardDescription>Key setup items and things to monitor</CardDescription>
              </CardHeader>
              <CardContent data-testid="admin-checklist">
                <div className="space-y-1">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Setup & Configuration</p>
                  <ChecklistItem done={true} label="MongoDB Atlas connected (production database)" />
                  <ChecklistItem done={true} label="Resend email service configured (drip campaigns)" />
                  <ChecklistItem done={true} label="Stripe payment integration active" />
                  <ChecklistItem done={true} label="Emergent LLM Key configured (AI viability search)" />
                  <ChecklistItem done={true} label="3-email drip sequence deployed (instant + day 2 + day 5)" />
                  <ChecklistItem
                    done={false}
                    label="Google Analytics 4 tracking ID not set"
                    action="Set up"
                    onAction={() => window.open('https://analytics.google.com/', '_blank')}
                  />
                  <ChecklistItem
                    done={false}
                    label="A/B test hook not wired to hero CTA yet"
                  />
                </div>

                <div className="space-y-1 mt-5">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Daily Monitoring</p>
                  <ChecklistItem done={true} label="Check revenue & new subscribers" action="View" onAction={() => navigate('/admin/analytics')} />
                  <ChecklistItem done={true} label="Monitor lead capture volume" action="View" onAction={() => navigate('/admin/analytics')} />
                  <ChecklistItem done={true} label="Review email drip delivery rates" action="View" onAction={() => navigate('/admin/analytics')} />
                  <ChecklistItem done={true} label="Check system health & background jobs" action="View" onAction={() => navigate('/admin/health')} />
                </div>

                <div className="space-y-1 mt-5">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Weekly Tasks</p>
                  <ChecklistItem done={true} label="Review top product searches (spot new niches)" action="View" onAction={() => navigate('/admin/analytics')} />
                  <ChecklistItem done={true} label="Check blog auto-generation ran on Monday" action="Blog" onAction={() => navigate('/admin/automation')} />
                  <ChecklistItem done={true} label="Review image quality for new products" action="Review" onAction={() => navigate('/admin/image-review')} />
                  <ChecklistItem done={true} label="Monitor prediction accuracy scores" action="Accuracy" onAction={() => navigate('/accuracy')} />
                  <ChecklistItem done={true} label="Check conversion funnel drop-off points" action="Funnel" onAction={() => navigate('/admin/analytics')} />
                </div>
              </CardContent>
            </Card>

            {/* What to Watch For */}
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Eye className="h-5 w-5 text-amber-500" />
                  What to Keep an Eye On
                </CardTitle>
              </CardHeader>
              <CardContent data-testid="watch-list">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100">
                    <p className="font-semibold text-emerald-800 text-sm flex items-center gap-2"><PoundSterling className="h-4 w-4" /> Revenue Health</p>
                    <ul className="mt-2 space-y-1.5 text-xs text-emerald-700">
                      <li>- MRR trend: is it growing month over month?</li>
                      <li>- New subscriber count vs churned subscribers</li>
                      <li>- Which plan (Pro vs Elite) converts more?</li>
                      <li>- Failed payments in Stripe dashboard</li>
                    </ul>
                  </div>
                  <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100">
                    <p className="font-semibold text-indigo-800 text-sm flex items-center gap-2"><Target className="h-4 w-4" /> Lead Quality</p>
                    <ul className="mt-2 space-y-1.5 text-xs text-indigo-700">
                      <li>- Lead-to-signup conversion rate</li>
                      <li>- Which product searches get most interest?</li>
                      <li>- Email gate completion rate (search {'->'} email)</li>
                      <li>- Source breakdown (viability tool vs newsletter)</li>
                    </ul>
                  </div>
                  <div className="p-4 rounded-xl bg-violet-50 border border-violet-100">
                    <p className="font-semibold text-violet-800 text-sm flex items-center gap-2"><Mail className="h-4 w-4" /> Email Performance</p>
                    <ul className="mt-2 space-y-1.5 text-xs text-violet-700">
                      <li>- Drip step completion: do leads get all 3 emails?</li>
                      <li>- If Day 2/5 emails stay at 0, check the cron job</li>
                      <li>- Resend dashboard for bounce/spam rates</li>
                      <li>- Weekly digest delivery to subscribers</li>
                    </ul>
                  </div>
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
                    <p className="font-semibold text-amber-800 text-sm flex items-center gap-2"><Server className="h-4 w-4" /> System Health</p>
                    <ul className="mt-2 space-y-1.5 text-xs text-amber-700">
                      <li>- Background job failures (check /admin/health)</li>
                      <li>- Blog auto-generation running every Monday</li>
                      <li>- Product data freshness (ingestion every 4h)</li>
                      <li>- Prediction accuracy trending above 60%</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Technical Reference */}
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <FileText className="h-5 w-5 text-slate-500" />
                  Technical Reference
                </CardTitle>
                <CardDescription>Environment & service configuration</CardDescription>
              </CardHeader>
              <CardContent data-testid="tech-reference">
                <div className="space-y-4">
                  <div>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Environment Variables (Production)</p>
                    <div className="bg-slate-900 rounded-xl p-4 font-mono text-xs text-slate-300 space-y-1.5 overflow-x-auto">
                      <p><span className="text-emerald-400">MONGO_URL</span> = your MongoDB Atlas connection string</p>
                      <p><span className="text-emerald-400">DB_NAME</span> = trendscout</p>
                      <p><span className="text-emerald-400">RESEND_API_KEY</span> = re_xxxx (Resend dashboard {'>'} API Keys)</p>
                      <p><span className="text-emerald-400">STRIPE_SECRET_KEY</span> = sk_live_xxxx (Stripe dashboard {'>'} Developers)</p>
                      <p><span className="text-emerald-400">STRIPE_WEBHOOK_SECRET</span> = whsec_xxxx (Stripe {'>'} Webhooks)</p>
                      <p><span className="text-emerald-400">EMERGENT_LLM_KEY</span> = Emergent universal key (Profile {'>'} Universal Key)</p>
                      <p><span className="text-emerald-400">PEXELS_API_KEY</span> = your Pexels API key</p>
                      <p><span className="text-emerald-400">REACT_APP_GA4_ID</span> = G-XXXXXXX (Google Analytics)</p>
                      <p><span className="text-slate-500"># Frontend</span></p>
                      <p><span className="text-emerald-400">REACT_APP_BACKEND_URL</span> = auto-set by Emergent on deploy</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Automated Scheduled Tasks</p>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs">
                        <thead><tr className="border-b bg-slate-50">
                          <th className="text-left p-2 font-medium text-slate-600">Task</th>
                          <th className="text-left p-2 font-medium text-slate-600">Schedule</th>
                          <th className="text-left p-2 font-medium text-slate-600">What It Does</th>
                        </tr></thead>
                        <tbody className="text-slate-700">
                          <tr className="border-b"><td className="p-2 font-mono">send_lead_drip_emails</td><td className="p-2">Daily 9 AM</td><td className="p-2">Day 2 trending + Day 5 trial emails to leads</td></tr>
                          <tr className="border-b"><td className="p-2 font-mono">review_prediction_accuracy</td><td className="p-2">Daily 6 AM</td><td className="p-2">Snapshot and score prediction accuracy</td></tr>
                          <tr className="border-b"><td className="p-2 font-mono">ingest_trending_products</td><td className="p-2">Every 4h</td><td className="p-2">Pull fresh product data from sources</td></tr>
                          <tr className="border-b"><td className="p-2 font-mono">weekly_blog_generation</td><td className="p-2">Monday 8 AM</td><td className="p-2">AI-generated blog posts</td></tr>
                          <tr className="border-b"><td className="p-2 font-mono">send_weekly_email_digest</td><td className="p-2">Monday 10 AM</td><td className="p-2">Weekly digest to registered users</td></tr>
                          <tr className="border-b"><td className="p-2 font-mono">send_trial_expiry_notifications</td><td className="p-2">Every 2h</td><td className="p-2">Notify users whose trial is expiring</td></tr>
                          <tr className="border-b"><td className="p-2 font-mono">enrich_product_images</td><td className="p-2">Every 8h</td><td className="p-2">Find/improve product images</td></tr>
                          <tr><td className="p-2 font-mono">cleanup_stale_jobs</td><td className="p-2">Every 15m</td><td className="p-2">Remove stuck background jobs</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">External Service Dashboards</p>
                    <div className="flex flex-wrap gap-2">
                      {[
                        { name: 'Stripe', url: 'https://dashboard.stripe.com' },
                        { name: 'Resend', url: 'https://resend.com/emails' },
                        { name: 'MongoDB Atlas', url: 'https://cloud.mongodb.com' },
                        { name: 'Google Analytics', url: 'https://analytics.google.com' },
                        { name: 'Sentry (Errors)', url: 'https://sentry.io' },
                        { name: 'Emergent (Deploy)', url: 'https://app.emergent.sh' },
                      ].map(s => (
                        <a
                          key={s.name}
                          href={s.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 transition-colors"
                        >
                          {s.name} <ArrowRight className="h-3 w-3" />
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Quick Links */}
          <div className="space-y-6">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">Admin Tools</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2" data-testid="admin-tools">
                <AdminLink href="/admin/analytics" icon={BarChart3} title="Growth & Revenue" desc="Revenue, leads, email drip, conversion funnel" onClick={() => navigate('/admin/analytics')} />
                <AdminLink href="/admin/products" icon={Package} title="Product Management" desc="Add, edit, delete products in the catalogue" onClick={() => navigate('/admin')} badge="CRUD" />
                <AdminLink href="/admin/automation" icon={Zap} title="Automation & Jobs" desc="Background tasks, cron schedules, job history" onClick={() => navigate('/admin/automation')} />
                <AdminLink href="/admin/health" icon={Activity} title="System Health" desc="Server status, DB connections, error rates" onClick={() => navigate('/admin/health')} />
                <AdminLink href="/admin/image-review" icon={Image} title="Image Review" desc="QA product images, approve/reject/replace" onClick={() => navigate('/admin/image-review')} />
                <AdminLink href="/admin/integrations" icon={Wifi} title="Integrations" desc="Stripe, Resend, Shopify connection status" onClick={() => navigate('/admin/integrations')} />
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start text-xs" onClick={() => navigate('/admin')}>
                  <Package className="h-3.5 w-3.5 mr-2" /> Add New Product
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start text-xs" onClick={() => navigate('/blog')}>
                  <FileText className="h-3.5 w-3.5 mr-2" /> View Blog Posts
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start text-xs" onClick={() => navigate('/admin/automation')}>
                  <Zap className="h-3.5 w-3.5 mr-2" /> Run Manual Job
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start text-xs" onClick={() => navigate('/accuracy')}>
                  <TrendingUp className="h-3.5 w-3.5 mr-2" /> Prediction Accuracy
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
