import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import {
  Radar, Bell, BellRing, Mail, Smartphone, ChevronDown, ChevronUp,
  Loader2, Save, Check
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function ThresholdSubscriptionCard() {
  const [sub, setSub] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [categories, setCategories] = useState([]);
  const [draft, setDraft] = useState({
    enabled: false,
    score_threshold: 75,
    categories: [],
    email_alerts: true,
    in_app_alerts: true,
  });

  useEffect(() => {
    Promise.all([
      api.get('/api/notifications/threshold-subscription'),
      fetch(`${API_URL}/api/public/categories`).then(r => r.json()),
    ]).then(([subRes, cats]) => {
      const s = subRes.data;
      setSub(s);
      setDraft({
        enabled: s.enabled ?? false,
        score_threshold: s.score_threshold ?? 75,
        categories: s.categories ?? [],
        email_alerts: s.email_alerts ?? true,
        in_app_alerts: s.in_app_alerts ?? true,
      });
      setCategories(Array.isArray(cats) ? cats : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await api.put('/api/notifications/threshold-subscription', draft);
      setSub(res.data);
      toast.success(draft.enabled ? 'Alert subscription activated' : 'Alert subscription paused');
    } catch {
      toast.error('Failed to update subscription');
    }
    setSaving(false);
  };

  const toggleCategory = (name) => {
    setDraft(prev => ({
      ...prev,
      categories: prev.categories.includes(name)
        ? prev.categories.filter(c => c !== name)
        : [...prev.categories, name],
    }));
  };

  if (loading) {
    return (
      <Card className="border-slate-200">
        <CardContent className="p-6 flex items-center justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-indigo-500" />
        </CardContent>
      </Card>
    );
  }

  const scoreLabel = draft.score_threshold >= 85 ? 'Strict (fewer, stronger signals)'
    : draft.score_threshold >= 65 ? 'Balanced (recommended)'
    : 'Broad (more alerts, more noise)';

  return (
    <Card className={`border transition-all duration-300 ${draft.enabled ? 'border-indigo-200 bg-indigo-50/30' : 'border-slate-200'}`} data-testid="threshold-subscription-card">
      <CardContent className="p-5">
        {/* Header Row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-xl ${draft.enabled ? 'bg-indigo-100' : 'bg-slate-100'}`}>
              <Radar className={`h-5 w-5 ${draft.enabled ? 'text-indigo-600' : 'text-slate-400'}`} />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-sm">Score Threshold Alerts</h3>
              <p className="text-xs text-slate-500">Get notified when products cross your score threshold</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Switch
              checked={draft.enabled}
              onCheckedChange={(v) => setDraft(prev => ({ ...prev, enabled: v }))}
              data-testid="threshold-enabled-switch"
            />
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1 rounded-lg hover:bg-slate-100 transition-colors"
              data-testid="threshold-expand-btn"
            >
              {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
            </button>
          </div>
        </div>

        {/* Quick Status */}
        {!expanded && draft.enabled && (
          <div className="mt-3 flex items-center gap-2 text-xs">
            <Badge className="bg-indigo-100 text-indigo-700 border-0 rounded-full">Score {draft.score_threshold}+</Badge>
            {draft.email_alerts && <Badge className="bg-slate-100 text-slate-600 border-0 rounded-full"><Mail className="h-3 w-3 mr-1" />Email</Badge>}
            {draft.in_app_alerts && <Badge className="bg-slate-100 text-slate-600 border-0 rounded-full"><BellRing className="h-3 w-3 mr-1" />In-App</Badge>}
            {draft.categories.length > 0 && (
              <Badge className="bg-slate-100 text-slate-600 border-0 rounded-full">{draft.categories.length} categories</Badge>
            )}
          </div>
        )}

        {/* Expanded Settings */}
        {expanded && (
          <div className="mt-5 space-y-5 pt-4 border-t border-slate-200/80">
            {/* Score Threshold Slider */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-slate-700">Minimum Launch Score</label>
                <span className="text-sm font-bold text-indigo-600 font-mono">{draft.score_threshold}</span>
              </div>
              <Slider
                value={[draft.score_threshold]}
                onValueChange={([v]) => setDraft(prev => ({ ...prev, score_threshold: v }))}
                min={30}
                max={95}
                step={5}
                className="mt-2"
                data-testid="threshold-slider"
              />
              <p className="text-xs text-slate-400 mt-1.5">{scoreLabel}</p>
            </div>

            {/* Category Filters */}
            <div>
              <label className="text-sm font-medium text-slate-700 block mb-2">Categories (empty = all)</label>
              <div className="flex flex-wrap gap-1.5">
                {categories.map(cat => (
                  <button
                    key={cat.name}
                    onClick={() => toggleCategory(cat.name)}
                    className={`text-xs px-2.5 py-1 rounded-full border transition-all ${
                      draft.categories.includes(cat.name)
                        ? 'bg-indigo-600 text-white border-indigo-600'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300'
                    }`}
                    data-testid={`category-filter-${cat.slug}`}
                  >
                    {cat.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Channels */}
            <div className="flex items-center gap-6">
              <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  checked={draft.email_alerts}
                  onChange={(e) => setDraft(prev => ({ ...prev, email_alerts: e.target.checked }))}
                  data-testid="email-alerts-checkbox"
                />
                <Mail className="h-4 w-4 text-slate-400" />
                Email
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  checked={draft.in_app_alerts}
                  onChange={(e) => setDraft(prev => ({ ...prev, in_app_alerts: e.target.checked }))}
                  data-testid="inapp-alerts-checkbox"
                />
                <Smartphone className="h-4 w-4 text-slate-400" />
                In-App
              </label>
            </div>

            {/* Save Button */}
            <Button
              onClick={handleSave}
              disabled={saving}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white h-9 rounded-lg font-semibold"
              data-testid="save-threshold-btn"
            >
              {saving ? (
                <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Saving...</>
              ) : (
                <><Save className="h-4 w-4 mr-2" /> Save Alert Settings</>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
