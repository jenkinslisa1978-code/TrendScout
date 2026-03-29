import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import ProGate from '@/components/ProGate';
import {
  Bell, Plus, Trash2, Mail, Clock, ChevronDown,
  Loader2, Check, X, Zap, Filter,
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function ProductAlertsPage() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [history, setHistory] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [subsRes, histRes, catRes] = await Promise.all([
        api.get('/api/product-alerts/subscriptions'),
        api.get('/api/product-alerts/history?limit=20'),
        api.get('/api/product-alerts/categories'),
      ]);
      setSubscriptions(subsRes.data?.subscriptions || []);
      setHistory(histRes.data?.alerts || []);
      setCategories(catRes.data?.categories || []);
    } catch (err) {
      if (err?.response?.status === 403) {
        // Expected for free users — ProGate will handle
      } else {
        toast.error('Failed to load alert data');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleToggle = async (subId) => {
    try {
      const res = await api.put(`/api/product-alerts/subscriptions/${subId}/toggle`);
      setSubscriptions(prev => prev.map(s =>
        s.id === subId ? { ...s, active: res.data.active } : s
      ));
      toast.success(res.data.active ? 'Alert enabled' : 'Alert paused');
    } catch { toast.error('Failed to toggle alert'); }
  };

  const handleDelete = async (subId) => {
    try {
      await api.delete(`/api/product-alerts/subscriptions/${subId}`);
      setSubscriptions(prev => prev.filter(s => s.id !== subId));
      toast.success('Alert deleted');
    } catch { toast.error('Failed to delete alert'); }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6" data-testid="product-alerts-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900" data-testid="product-alerts-title">
              Product Alerts
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Get instant email alerts when new products matching your criteria are detected.
            </p>
          </div>
          <Button
            onClick={() => setShowCreate(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white gap-2"
            data-testid="create-alert-btn"
          >
            <Plus className="h-4 w-4" /> New Alert
          </Button>
        </div>

        <ProGate requiredPlan="starter" feature="Product Alerts">
          {/* Create form */}
          {showCreate && (
            <CreateAlertForm
              categories={categories}
              onCreated={(sub) => {
                setSubscriptions(prev => [sub, ...prev]);
                setShowCreate(false);
              }}
              onCancel={() => setShowCreate(false)}
            />
          )}

          {/* Active subscriptions */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Bell className="h-4 w-4 text-indigo-600" />
                Active Alerts ({subscriptions.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
                </div>
              ) : subscriptions.length === 0 ? (
                <div className="text-center py-8 text-slate-400" data-testid="no-alerts-message">
                  <Bell className="h-8 w-8 mx-auto mb-2 opacity-40" />
                  <p className="text-sm">No alerts yet. Create one to get started.</p>
                </div>
              ) : (
                <div className="space-y-3" data-testid="subscriptions-list">
                  {subscriptions.map(sub => (
                    <div
                      key={sub.id}
                      className="flex items-center gap-4 p-3 rounded-lg border border-slate-100 hover:border-slate-200 transition-colors"
                      data-testid={`subscription-${sub.id}`}
                    >
                      <Switch
                        checked={sub.active}
                        onCheckedChange={() => handleToggle(sub.id)}
                        data-testid={`toggle-${sub.id}`}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900 truncate">
                          {sub.label || sub.categories?.join(', ')}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                          {sub.categories?.slice(0, 3).map(cat => (
                            <Badge key={cat} variant="secondary" className="text-[10px] px-1.5 py-0">
                              {cat}
                            </Badge>
                          ))}
                          {sub.categories?.length > 3 && (
                            <span className="text-[10px] text-slate-400">+{sub.categories.length - 3}</span>
                          )}
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-xs font-mono font-bold text-indigo-600">
                          {sub.min_score}+
                        </span>
                        <p className="text-[10px] text-slate-400">min score</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(sub.id)}
                        className="text-slate-400 hover:text-red-500 shrink-0"
                        data-testid={`delete-${sub.id}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Alert history */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4 text-slate-500" />
                Recent Alerts Sent
              </CardTitle>
            </CardHeader>
            <CardContent>
              {history.length === 0 ? (
                <p className="text-sm text-slate-400 text-center py-6" data-testid="no-history">
                  No alerts sent yet. They'll appear here once products match your criteria.
                </p>
              ) : (
                <div className="space-y-2" data-testid="alert-history-list">
                  {history.map(h => (
                    <div
                      key={h.id}
                      className="flex items-center gap-3 p-2.5 rounded-lg bg-slate-50 text-sm"
                      data-testid={`history-${h.id}`}
                    >
                      <Mail className="h-4 w-4 text-indigo-500 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <span className="font-medium text-slate-800 truncate block">
                          {h.product_name}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          {h.category} &middot; Score {h.score}
                        </span>
                      </div>
                      <Badge
                        variant={h.email_status === 'success' ? 'default' : 'destructive'}
                        className="text-[10px] shrink-0"
                      >
                        {h.email_status === 'success' ? 'Sent' : 'Failed'}
                      </Badge>
                      <span className="text-[10px] text-slate-400 shrink-0">
                        {h.sent_at ? new Date(h.sent_at).toLocaleDateString() : ''}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </ProGate>
      </div>
    </DashboardLayout>
  );
}


function CreateAlertForm({ categories, onCreated, onCancel }) {
  const [selected, setSelected] = useState([]);
  const [minScore, setMinScore] = useState(50);
  const [label, setLabel] = useState('');
  const [saving, setSaving] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [search, setSearch] = useState('');

  const filtered = categories.filter(c =>
    c.toLowerCase().includes(search.toLowerCase())
  );

  const toggleCategory = (cat) => {
    setSelected(prev =>
      prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]
    );
  };

  const handleSubmit = async () => {
    if (selected.length === 0) {
      toast.error('Select at least one category');
      return;
    }
    setSaving(true);
    try {
      const res = await api.post('/api/product-alerts/subscriptions', {
        categories: selected,
        min_score: minScore,
        label: label || undefined,
      });
      onCreated(res.data.subscription);
      toast.success('Alert created');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to create alert');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card className="border-indigo-200 bg-indigo-50/30" data-testid="create-alert-form">
      <CardContent className="pt-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
            <Zap className="h-4 w-4 text-indigo-600" /> New Alert Subscription
          </h3>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Label */}
        <div>
          <label className="text-xs font-medium text-slate-600 mb-1 block">Alert Name (optional)</label>
          <Input
            placeholder="e.g. Beauty trending alerts"
            value={label}
            onChange={e => setLabel(e.target.value)}
            data-testid="alert-label-input"
          />
        </div>

        {/* Category selector */}
        <div>
          <label className="text-xs font-medium text-slate-600 mb-1 block">
            Categories <span className="text-slate-400">({selected.length} selected)</span>
          </label>
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="w-full flex items-center justify-between px-3 py-2 rounded-md border border-slate-200 bg-white text-sm text-slate-700 hover:border-slate-300"
              data-testid="category-dropdown-btn"
            >
              <span className="truncate">
                {selected.length === 0
                  ? 'Select categories...'
                  : selected.slice(0, 3).join(', ') + (selected.length > 3 ? ` +${selected.length - 3}` : '')}
              </span>
              <ChevronDown className="h-4 w-4 text-slate-400 shrink-0" />
            </button>

            {dropdownOpen && (
              <div className="absolute z-20 mt-1 w-full bg-white border border-slate-200 rounded-lg shadow-lg max-h-60 overflow-auto" data-testid="category-dropdown-list">
                <div className="p-2 sticky top-0 bg-white border-b border-slate-100">
                  <Input
                    placeholder="Search categories..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="h-8 text-sm"
                    data-testid="category-search-input"
                  />
                </div>
                {filtered.length === 0 ? (
                  <p className="text-xs text-slate-400 p-3 text-center">No categories found</p>
                ) : (
                  filtered.map(cat => (
                    <button
                      key={cat}
                      onClick={() => toggleCategory(cat)}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-50 text-left"
                      data-testid={`category-option-${cat}`}
                    >
                      <div className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 ${
                        selected.includes(cat)
                          ? 'bg-indigo-600 border-indigo-600'
                          : 'border-slate-300'
                      }`}>
                        {selected.includes(cat) && <Check className="h-3 w-3 text-white" />}
                      </div>
                      <span className="text-slate-700">{cat}</span>
                    </button>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Selected tags */}
          {selected.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {selected.map(cat => (
                <Badge
                  key={cat}
                  variant="secondary"
                  className="text-xs pl-2 pr-1 py-0.5 cursor-pointer hover:bg-slate-200"
                  onClick={() => toggleCategory(cat)}
                >
                  {cat}
                  <X className="h-3 w-3 ml-1" />
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Score threshold */}
        <div>
          <label className="text-xs font-medium text-slate-600 mb-1 block">
            Minimum Score: <span className="font-bold text-indigo-600">{minScore}</span>
          </label>
          <Slider
            value={[minScore]}
            onValueChange={v => setMinScore(v[0])}
            min={1}
            max={100}
            step={5}
            className="mt-2"
            data-testid="score-slider"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>1 (all products)</span>
            <span>50 (emerging+)</span>
            <span>100 (top only)</span>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="outline" size="sm" onClick={onCancel}>Cancel</Button>
          <Button
            size="sm"
            className="bg-indigo-600 hover:bg-indigo-700 text-white gap-1.5"
            onClick={handleSubmit}
            disabled={saving || selected.length === 0}
            data-testid="save-alert-btn"
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bell className="h-4 w-4" />}
            Create Alert
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
