import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  BarChart3, TrendingUp, DollarSign, Package, Loader2,
  CheckCircle2, AlertTriangle, XCircle, Clock, ArrowRight,
  RefreshCcw, Lightbulb, Target, ShoppingCart,
} from 'lucide-react';
import { apiGet, apiPost, apiPut } from '@/lib/api';
import { toast } from 'sonner';

const STATUS_CONFIG = {
  success: { label: 'Success', icon: CheckCircle2, color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  moderate: { label: 'Moderate', icon: AlertTriangle, color: 'bg-amber-100 text-amber-700 border-amber-200' },
  failed: { label: 'Failed', icon: XCircle, color: 'bg-red-100 text-red-700 border-red-200' },
  pending: { label: 'Pending', icon: Clock, color: 'bg-slate-100 text-slate-600 border-slate-200' },
};

export default function OutcomesPage() {
  const navigate = useNavigate();
  const [outcomes, setOutcomes] = useState([]);
  const [summary, setSummary] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [outcomesRes, statsRes] = await Promise.all([
        apiGet('/api/outcomes/my'),
        apiGet('/api/outcomes/stats'),
      ]);
      if (outcomesRes.ok) {
        const d = await outcomesRes.json();
        setOutcomes(d.outcomes);
        setSummary(d.summary);
      }
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleAutoLabel = async () => {
    const res = await apiPost('/api/outcomes/auto-label');
    if (res.ok) {
      const d = await res.json();
      toast.success(`Auto-labeled ${d.labeled} of ${d.total_checked} outcomes`);
      fetchData();
    }
  };

  const handleUpdate = async (outcomeId) => {
    const res = await apiPut(`/api/outcomes/${outcomeId}`, editForm);
    if (res.ok) {
      toast.success('Outcome updated');
      setEditingId(null);
      setEditForm({});
      fetchData();
    }
  };

  const filtered = activeTab === 'all' ? outcomes : outcomes.filter((o) => o.outcome_status === activeTab);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC]" data-testid="outcomes-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Product Outcomes</h1>
            <p className="text-sm text-slate-500 mt-1">Track launched products and learn what works</p>
          </div>
          <Button
            onClick={handleAutoLabel}
            variant="outline"
            className="text-sm"
            data-testid="auto-label-btn"
          >
            <RefreshCcw className="h-4 w-4 mr-2" />
            Auto-Label
          </Button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8" data-testid="outcomes-summary">
            <StatCard icon={Target} label="Tracked" value={summary.total} color="text-indigo-600" bg="bg-indigo-50" />
            <StatCard icon={CheckCircle2} label="Success Rate" value={`${summary.success_rate}%`} color="text-emerald-600" bg="bg-emerald-50" />
            <StatCard icon={DollarSign} label="Total Revenue" value={`£${summary.total_revenue.toLocaleString()}`} color="text-teal-600" bg="bg-teal-50" />
            <StatCard icon={ShoppingCart} label="Total Orders" value={summary.total_orders} color="text-amber-600" bg="bg-amber-50" />
          </div>
        )}

        {/* Insights */}
        {stats?.insights?.length > 0 && (
          <Card className="mb-8 border-0 shadow-md bg-gradient-to-r from-indigo-50/80 to-purple-50/60" data-testid="outcome-insights">
            <CardContent className="p-5">
              <p className="text-sm font-semibold text-indigo-700 flex items-center gap-2 mb-3">
                <Lightbulb className="h-4 w-4" /> Learning Insights
              </p>
              <div className="space-y-2">
                {stats.insights.map((ins, i) => (
                  <p key={i} className="text-sm text-slate-700">{ins.text}</p>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Score Comparison */}
        {stats && stats.avg_launch_score_success > 0 && (
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            <Card className="border-0 shadow-sm">
              <CardContent className="p-5 flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-emerald-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Avg Score (Successful)</p>
                  <p className="text-2xl font-bold font-mono text-emerald-600" data-testid="avg-score-success">{stats.avg_launch_score_success}</p>
                </div>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-sm">
              <CardContent className="p-5 flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center">
                  <BarChart3 className="h-6 w-6 text-red-500" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Avg Score (Failed)</p>
                  <p className="text-2xl font-bold font-mono text-red-500" data-testid="avg-score-failed">{stats.avg_launch_score_failed}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Outcomes List */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold">Tracked Products</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="w-full bg-slate-50 mb-4">
                <TabsTrigger value="all" className="flex-1 text-xs">All ({outcomes.length})</TabsTrigger>
                <TabsTrigger value="pending" className="flex-1 text-xs">Pending ({summary?.pending || 0})</TabsTrigger>
                <TabsTrigger value="success" className="flex-1 text-xs">Success ({summary?.success || 0})</TabsTrigger>
                <TabsTrigger value="moderate" className="flex-1 text-xs">Moderate ({summary?.moderate || 0})</TabsTrigger>
                <TabsTrigger value="failed" className="flex-1 text-xs">Failed ({summary?.failed || 0})</TabsTrigger>
              </TabsList>

              {filtered.length === 0 ? (
                <EmptyState navigate={navigate} />
              ) : (
                <div className="space-y-3">
                  {filtered.map((o) => (
                    <OutcomeRow
                      key={o.id}
                      outcome={o}
                      isEditing={editingId === o.id}
                      editForm={editForm}
                      onStartEdit={() => {
                        setEditingId(o.id);
                        setEditForm({
                          revenue: o.metrics?.revenue || 0,
                          orders: o.metrics?.orders || 0,
                          ad_spend: o.metrics?.ad_spend || 0,
                          days_active: o.metrics?.days_active || 0,
                        });
                      }}
                      onCancelEdit={() => { setEditingId(null); setEditForm({}); }}
                      onFormChange={(k, v) => setEditForm((p) => ({ ...p, [k]: v }))}
                      onSave={() => handleUpdate(o.id)}
                      onViewProduct={() => navigate(`/product/${o.product_id}`)}
                    />
                  ))}
                </div>
              )}
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color, bg }) {
  return (
    <Card className="border-0 shadow-sm">
      <CardContent className="p-4 flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg ${bg} flex items-center justify-center flex-shrink-0`}>
          <Icon className={`h-5 w-5 ${color}`} />
        </div>
        <div>
          <p className="text-xs text-slate-500">{label}</p>
          <p className={`text-lg font-bold ${color}`}>{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function OutcomeRow({ outcome, isEditing, editForm, onStartEdit, onCancelEdit, onFormChange, onSave, onViewProduct }) {
  const cfg = STATUS_CONFIG[outcome.outcome_status] || STATUS_CONFIG.pending;
  const StatusIcon = cfg.icon;
  const m = outcome.metrics || {};

  return (
    <div className="p-4 rounded-xl border border-slate-100 hover:border-slate-200 transition-colors" data-testid={`outcome-${outcome.id}`}>
      <div className="flex items-start gap-3">
        {outcome.image_url ? (
          <img src={outcome.image_url} alt="" className="w-14 h-14 rounded-lg object-cover bg-slate-100 flex-shrink-0"  loading="lazy" />
        ) : (
          <div className="w-14 h-14 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
            <Package className="h-6 w-6 text-slate-400" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p
              className="font-semibold text-sm text-slate-900 truncate cursor-pointer hover:text-indigo-600 transition-colors"
              onClick={onViewProduct}
            >
              {outcome.product_name}
            </p>
            <Badge className={`text-[10px] border ${cfg.color}`}>
              <StatusIcon className="h-3 w-3 mr-1" />
              {cfg.label}
            </Badge>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{outcome.category} | Launched {new Date(outcome.launched_at).toLocaleDateString()}</p>

          {/* Metrics row */}
          <div className="flex items-center gap-4 mt-2 text-xs">
            <span className="text-slate-600">Score at launch: <span className="font-mono font-bold text-indigo-600">{outcome.launch_score_at_launch}</span></span>
            <span className="text-slate-600">Revenue: <span className="font-mono font-bold text-emerald-600">£{m.revenue || 0}</span></span>
            <span className="text-slate-600">Orders: <span className="font-mono font-bold">{m.orders || 0}</span></span>
            {m.roi ? <span className="text-slate-600">ROI: <span className="font-mono font-bold text-teal-600">{m.roi}%</span></span> : null}
          </div>

          {outcome.auto_label_reason && (
            <p className="text-[10px] text-slate-400 mt-1">Auto-labeled: {outcome.auto_label_reason}</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex-shrink-0">
          {!isEditing ? (
            <Button size="sm" variant="outline" onClick={onStartEdit} data-testid={`edit-outcome-${outcome.id}`}>
              Update
            </Button>
          ) : null}
        </div>
      </div>

      {/* Edit form */}
      {isEditing && (
        <div className="mt-4 p-4 bg-slate-50 rounded-lg" data-testid={`edit-form-${outcome.id}`}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <Label className="text-xs text-slate-500">Revenue (£)</Label>
              <Input
                type="number"
                value={editForm.revenue}
                onChange={(e) => onFormChange('revenue', parseFloat(e.target.value) || 0)}
                data-testid="edit-revenue"
              />
            </div>
            <div>
              <Label className="text-xs text-slate-500">Orders</Label>
              <Input
                type="number"
                value={editForm.orders}
                onChange={(e) => onFormChange('orders', parseInt(e.target.value) || 0)}
                data-testid="edit-orders"
              />
            </div>
            <div>
              <Label className="text-xs text-slate-500">Ad Spend (£)</Label>
              <Input
                type="number"
                value={editForm.ad_spend}
                onChange={(e) => onFormChange('ad_spend', parseFloat(e.target.value) || 0)}
                data-testid="edit-ad-spend"
              />
            </div>
            <div>
              <Label className="text-xs text-slate-500">Days Active</Label>
              <Input
                type="number"
                value={editForm.days_active}
                onChange={(e) => onFormChange('days_active', parseInt(e.target.value) || 0)}
                data-testid="edit-days-active"
              />
            </div>
          </div>
          <div className="flex gap-2 mt-3">
            <Button size="sm" onClick={onSave} data-testid="save-outcome-btn">Save</Button>
            <Button size="sm" variant="outline" onClick={onCancelEdit}>Cancel</Button>
          </div>
        </div>
      )}
    </div>
  );
}

function EmptyState({ navigate }) {
  return (
    <div className="text-center py-12" data-testid="outcomes-empty">
      <Target className="h-12 w-12 text-slate-300 mx-auto mb-3" />
      <p className="text-lg font-semibold text-slate-700">No products tracked yet</p>
      <p className="text-sm text-slate-500 mt-1 mb-6">
        Launch products through the wizard to start tracking outcomes
      </p>
      <Button onClick={() => navigate('/dashboard')} data-testid="go-to-dashboard-btn">
        Go to Dashboard
        <ArrowRight className="h-4 w-4 ml-2" />
      </Button>
    </div>
  );
}
