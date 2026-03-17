import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Brain, TrendingUp, Pause, XCircle, Clock, ArrowRight,
  Loader2, Settings2, Zap, Shield, Rocket, ChevronDown,
  Bell, Check, RefreshCw, ArrowLeft,
} from 'lucide-react';
import { apiGet, apiPost } from '@/lib/api';
import { toast } from 'sonner';

const ACTION_CONFIG = {
  increase_budget: { icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', label: 'Scale' },
  pause: { icon: Pause, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', label: 'Pause' },
  kill: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', label: 'Kill' },
  maintain: { icon: Clock, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', label: 'Monitor' },
  needs_more_data: { icon: Clock, color: 'text-slate-500', bg: 'bg-slate-50', border: 'border-slate-200', label: 'Collecting' },
};

const PRESET_CONFIG = {
  beginner: { icon: Shield, color: 'text-blue-600', bg: 'bg-blue-50', desc: 'Conservative. Smaller steps. Prioritise safety.' },
  balanced: { icon: Brain, color: 'text-indigo-600', bg: 'bg-indigo-50', desc: 'Standard thresholds. Good for most users.' },
  aggressive: { icon: Rocket, color: 'text-red-600', bg: 'bg-red-50', desc: 'Loose thresholds. Faster scaling. Higher risk.' },
};

export default function OptimizationPage() {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [settings, setSettings] = useState({ preset: 'balanced', auto_recommend_enabled: false });
  const [timeline, setTimeline] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [presets, setPresets] = useState({});
  const [loading, setLoading] = useState(true);
  const [showPresets, setShowPresets] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [settingsRes, presetsRes, alertsRes] = await Promise.all([
        apiGet('/api/optimization/settings'),
        apiGet('/api/optimization/presets'),
        apiGet('/api/optimization/alerts?limit=20'),
      ]);
      if (settingsRes.ok) setSettings(await settingsRes.json());
      if (presetsRes.ok) { const d = await presetsRes.json(); setPresets(d.presets || {}); }
      if (alertsRes.ok) { const d = await alertsRes.json(); setAlerts(d.alerts || []); }

      if (testId) {
        const timelineRes = await apiGet(`/api/optimization/timeline/${testId}`);
        if (timelineRes.ok) { const d = await timelineRes.json(); setTimeline(d.events || []); }
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [testId]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleSetPreset = async (preset) => {
    try {
      const res = await apiPost('/api/optimization/set-preset', { preset });
      if (res.ok) {
        setSettings(prev => ({ ...prev, preset }));
        toast.success(`Preset changed to ${preset}`);
        setShowPresets(false);
      }
    } catch { toast.error('Failed to set preset'); }
  };

  const handleToggleAutoRecommend = async (enabled) => {
    try {
      const res = await apiPost('/api/optimization/toggle-auto-recommend', { enabled });
      if (res.ok) {
        setSettings(prev => ({ ...prev, auto_recommend_enabled: enabled }));
        toast.success(enabled ? 'Auto-recommend enabled' : 'Auto-recommend disabled');
      }
    } catch { toast.error('Failed to toggle auto-recommend'); }
  };

  const handleMarkAlertsRead = async () => {
    try {
      await apiPost('/api/optimization/alerts/mark-read');
      setAlerts(prev => prev.map(a => ({ ...a, read: true })));
      toast.success('Alerts marked as read');
    } catch { /* silent */ }
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

  const currentPreset = PRESET_CONFIG[settings.preset] || PRESET_CONFIG.balanced;
  const CurrentPresetIcon = currentPreset.icon;
  const unreadAlerts = alerts.filter(a => !a.read).length;

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-6" data-testid="optimization-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="text-slate-400">
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900 font-manrope">Smart Budget Optimiser</h1>
                <p className="text-sm text-slate-500">Manage your ad test optimisation strategy</p>
              </div>
            </div>
          </div>
        </div>

        {/* Settings Row */}
        <div className="grid md:grid-cols-2 gap-4">
          {/* Preset Selector */}
          <Card className="border-0 shadow-md" data-testid="preset-selector-card">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Settings2 className="h-4 w-4 text-slate-400" />
                  <span className="text-sm font-semibold text-slate-700">Strategy Preset</span>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setShowPresets(!showPresets)} className="text-xs text-indigo-600" data-testid="change-preset-btn">
                  Change <ChevronDown className="h-3 w-3 ml-1" />
                </Button>
              </div>
              <div className={`flex items-center gap-3 p-3 rounded-xl ${currentPreset.bg}`}>
                <CurrentPresetIcon className={`h-5 w-5 ${currentPreset.color}`} />
                <div>
                  <p className={`font-semibold text-sm ${currentPreset.color}`}>{settings.preset.charAt(0).toUpperCase() + settings.preset.slice(1)}</p>
                  <p className="text-xs text-slate-500">{currentPreset.desc}</p>
                </div>
              </div>
              {showPresets && (
                <div className="mt-3 space-y-2" data-testid="preset-options">
                  {Object.entries(PRESET_CONFIG).map(([key, cfg]) => {
                    const Icon = cfg.icon;
                    const isActive = key === settings.preset;
                    return (
                      <button
                        key={key}
                        onClick={() => handleSetPreset(key)}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl border-2 transition-all text-left ${
                          isActive ? `${cfg.bg} border-current ${cfg.color}` : 'border-slate-100 hover:border-slate-200'
                        }`}
                        data-testid={`preset-${key}`}
                      >
                        <Icon className={`h-4 w-4 ${cfg.color}`} />
                        <div className="flex-1">
                          <p className="font-medium text-sm text-slate-800">{key.charAt(0).toUpperCase() + key.slice(1)}</p>
                          <p className="text-xs text-slate-500">{cfg.desc}</p>
                        </div>
                        {isActive && <Check className={`h-4 w-4 ${cfg.color}`} />}
                      </button>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Auto-Recommend Toggle */}
          <Card className="border-0 shadow-md" data-testid="auto-recommend-card">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-semibold text-slate-700">Auto-Recommend</span>
                </div>
                <Switch
                  checked={settings.auto_recommend_enabled}
                  onCheckedChange={handleToggleAutoRecommend}
                  data-testid="auto-recommend-toggle"
                />
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                {settings.auto_recommend_enabled
                  ? 'TrendScout will continuously analyse your ad performance and generate optimisation recommendations automatically.'
                  : 'Enable to let TrendScout automatically generate recommendations based on live ad performance.'}
              </p>
              {settings.auto_recommend_enabled && (
                <div className="mt-3 flex items-center gap-2 text-xs text-emerald-600 bg-emerald-50 rounded-lg px-3 py-2">
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                  Auto-recommend active — monitoring your ad tests
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Optimiser Alerts */}
        <Card className="border-0 shadow-md" data-testid="optimiser-alerts-card">
          <CardHeader className="py-3 px-5">
            <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <Bell className="h-4 w-4 text-indigo-500" />
              Optimiser Alerts
              {unreadAlerts > 0 && (
                <Badge className="bg-red-100 text-red-700 border-red-200 text-[10px] ml-1">{unreadAlerts} new</Badge>
              )}
              {unreadAlerts > 0 && (
                <Button variant="ghost" size="sm" onClick={handleMarkAlertsRead} className="ml-auto text-xs text-slate-500">
                  Mark all read
                </Button>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="px-5 pb-5">
            {alerts.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-6">No optimiser alerts yet. Run recommendations on your ad tests to generate alerts.</p>
            ) : (
              <div className="space-y-2 max-h-[300px] overflow-y-auto">
                {alerts.map((alert, i) => {
                  const cfg = ACTION_CONFIG[alert.action] || ACTION_CONFIG.maintain;
                  const Icon = cfg.icon;
                  return (
                    <div
                      key={alert.id || i}
                      className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                        !alert.read ? `${cfg.bg} ${cfg.border}` : 'bg-white border-slate-100'
                      }`}
                      data-testid={`optimiser-alert-${i}`}
                    >
                      <Icon className={`h-4 w-4 ${cfg.color} flex-shrink-0`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-800 truncate">{alert.label || 'Ad Variation'}</p>
                        <p className="text-xs text-slate-500 truncate">{(alert.reasoning || [])[0] || alert.alert_type}</p>
                      </div>
                      <Badge className={`text-[10px] ${cfg.bg} ${cfg.color} border ${cfg.border}`}>{cfg.label}</Badge>
                      {!alert.read && <div className="h-2 w-2 rounded-full bg-indigo-500 flex-shrink-0" />}
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Optimization Timeline */}
        {testId && (
          <Card className="border-0 shadow-md" data-testid="optimization-timeline-card">
            <CardHeader className="py-3 px-5">
              <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                <RefreshCw className="h-4 w-4 text-indigo-500" />
                Optimization Timeline
                <Badge className="bg-indigo-50 text-indigo-600 border-indigo-100 text-[10px] ml-1">{timeline.length} events</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="px-5 pb-5">
              {timeline.length === 0 ? (
                <p className="text-sm text-slate-400 text-center py-6">No optimization events yet for this test.</p>
              ) : (
                <div className="relative pl-6" data-testid="timeline-events">
                  {/* Timeline line */}
                  <div className="absolute left-2.5 top-0 bottom-0 w-px bg-slate-200" />

                  {timeline.map((event, i) => {
                    const cfg = ACTION_CONFIG[event.recommendation_action] || ACTION_CONFIG.needs_more_data;
                    const Icon = cfg.icon;
                    const date = new Date(event.timestamp);
                    const dayNum = timeline.length - i;
                    return (
                      <div key={event.id || i} className="relative mb-4 last:mb-0" data-testid={`timeline-event-${i}`}>
                        {/* Dot */}
                        <div className={`absolute -left-3.5 w-5 h-5 rounded-full ${cfg.bg} border-2 ${cfg.border} flex items-center justify-center`}>
                          <Icon className={`h-2.5 w-2.5 ${cfg.color}`} />
                        </div>
                        {/* Content */}
                        <div className="ml-4 bg-slate-50 rounded-xl p-3">
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-semibold text-slate-400">Day {dayNum}</span>
                              <Badge className={`text-[9px] ${cfg.bg} ${cfg.color} border ${cfg.border}`}>{cfg.label}</Badge>
                            </div>
                            <span className="text-[10px] text-slate-400">{date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}</span>
                          </div>
                          <p className="text-sm text-slate-700">{event.variation_id && <span className="font-medium">{event.variation_id}: </span>}{(event.reason_codes || [])[0] || 'Recommendation generated'}</p>
                          {event.recommended_budget > 0 && (
                            <p className="text-xs text-indigo-600 mt-1 font-medium">Recommended budget: £{event.recommended_budget}</p>
                          )}
                          <div className="flex items-center gap-3 mt-1.5 text-[10px] text-slate-400">
                            <span>CTR: {event.metrics_snapshot?.ctr || 0}%</span>
                            <span>CPC: £{event.metrics_snapshot?.cpc || 0}</span>
                            <span>Spend: £{event.metrics_snapshot?.spend || 0}</span>
                            <span>Confidence: {Math.round((event.confidence || 0) * 100)}%</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Quick navigation */}
        {!testId && (
          <Card className="border-0 shadow-md">
            <CardContent className="p-5 text-center">
              <p className="text-sm text-slate-500 mb-3">Select an ad test to view its optimization timeline</p>
              <Button onClick={() => navigate('/ad-tests')} className="bg-indigo-600 hover:bg-indigo-700" data-testid="go-to-ad-tests-btn">
                View Ad Tests <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
