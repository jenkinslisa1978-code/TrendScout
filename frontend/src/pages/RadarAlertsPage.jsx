import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Radio, Plus, Trash2, Bell, BellOff, TrendingUp,
  Loader2, Zap, Eye, Shield, Truck, Megaphone,
  Activity, Clock, AlertTriangle, ChevronRight, Target,
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

const WATCH_TYPES = [
  { id: 'product_score', label: 'Score Alert', desc: 'Alert when a product score crosses a threshold', icon: Target },
  { id: 'category_trend', label: 'Category Trend', desc: 'Alert when a category starts trending', icon: TrendingUp },
  { id: 'competitor_new_products', label: 'Competitor Activity', desc: 'Alert when competitors add new products', icon: Eye },
];

const EVENT_ICONS = {
  trend_spike: TrendingUp,
  new_ads: Megaphone,
  supplier_demand: Truck,
  competition_drop: Shield,
};

const EVENT_COLORS = {
  trend_spike: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  new_ads: 'bg-purple-50 text-purple-700 border-purple-200',
  supplier_demand: 'bg-amber-50 text-amber-700 border-amber-200',
  competition_drop: 'bg-blue-50 text-blue-700 border-blue-200',
};

export default function RadarAlertsPage() {
  const [liveEvents, setLiveEvents] = useState([]);
  const [watches, setWatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [evRes, wRes] = await Promise.all([
        api.get('/api/radar/live-events?limit=15'),
        api.get('/api/radar/watches'),
      ]);
      if (evRes.ok) setLiveEvents(evRes.data.events || []);
      if (wRes.ok) setWatches(wRes.data.watches || []);
    } catch {}
    setLoading(false);
  };

  const deleteWatch = async (id) => {
    try {
      await api.delete(`/api/radar/watches/${id}`);
      setWatches(prev => prev.filter(w => w.id !== id));
      toast.success('Watch removed');
    } catch { toast.error('Failed to remove'); }
  };

  const toggleWatch = async (watch) => {
    try {
      const res = await api.put(`/api/radar/watches/${watch.id}`, { active: !watch.active });
      if (res.ok) {
        setWatches(prev => prev.map(w => w.id === watch.id ? { ...w, active: !w.active } : w));
        toast.success(watch.active ? 'Watch paused' : 'Watch activated');
      }
    } catch { toast.error('Failed to update'); }
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6 space-y-6" data-testid="radar-alerts-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Radar Alerts</h1>
            <p className="text-sm text-slate-500 mt-1">Real-time signals, custom watches, and market alerts.</p>
          </div>
          <Button onClick={() => setShowCreate(true)} className="bg-indigo-600 hover:bg-indigo-700" data-testid="create-watch-btn">
            <Plus className="h-4 w-4 mr-1.5" /> New Watch
          </Button>
        </div>

        {/* Active Watches */}
        <Card className="border-0 shadow-lg" data-testid="watches-section">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <Bell className="h-4 w-4 text-indigo-600" /> Your Watches ({watches.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {watches.length === 0 ? (
              <p className="text-sm text-slate-400 py-4 text-center">No watches yet. Create one to get alerted on market changes.</p>
            ) : (
              <div className="space-y-2">
                {watches.map(w => (
                  <div key={w.id} className={`flex items-center justify-between p-3 rounded-lg border ${w.active ? 'bg-white border-slate-200' : 'bg-slate-50 border-slate-100'}`} data-testid="watch-item">
                    <div className="flex items-center gap-3">
                      <div className={`h-2 w-2 rounded-full ${w.active ? 'bg-emerald-500' : 'bg-slate-300'}`} />
                      <div>
                        <p className="text-sm font-semibold text-slate-800">{w.name}</p>
                        <p className="text-xs text-slate-400">
                          {w.watch_type.replace(/_/g, ' ')} &middot; Triggered {w.triggered_count || 0}x
                          {w.notify_email && ' · Email'}{w.notify_in_app && ' · In-app'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => toggleWatch(w)} className="text-slate-400 hover:text-slate-600" data-testid={`toggle-watch-${w.id}`}>
                        {w.active ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
                      </button>
                      <button onClick={() => deleteWatch(w.id)} className="text-slate-400 hover:text-red-500" data-testid={`delete-watch-${w.id}`}>
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Live Signal Feed */}
        <Card className="border-0 shadow-lg" data-testid="live-events-feed">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-bold flex items-center gap-2">
                <Zap className="h-4 w-4 text-amber-500" /> Live Signal Feed
              </CardTitle>
              <Button variant="ghost" size="sm" onClick={fetchData} className="text-xs" data-testid="refresh-feed">
                <Activity className="h-3 w-3 mr-1" /> Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-10">
                <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
              </div>
            ) : liveEvents.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No live signals at the moment. Check back later.</p>
            ) : (
              <div className="space-y-2">
                {liveEvents.map((ev, idx) => {
                  const Icon = EVENT_ICONS[ev.type] || Activity;
                  const color = EVENT_COLORS[ev.type] || 'bg-slate-50 text-slate-600 border-slate-200';
                  return (
                    <a
                      key={idx}
                      href={ev.product_id ? `/product/${ev.product_id}` : '#'}
                      className="flex items-center gap-3 p-3 rounded-lg border border-slate-100 hover:border-slate-200 hover:bg-slate-50/50 transition-colors group"
                      data-testid="signal-event"
                    >
                      <div className={`h-9 w-9 rounded-lg flex items-center justify-center border ${color}`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      {ev.image_url && (
                        <img src={ev.image_url} alt="" className="h-9 w-9 rounded-lg object-cover"  loading="lazy" /> 
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-800 truncate">{ev.title}</p>
                        <p className="text-xs text-slate-400">{ev.detail}</p>
                      </div>
                      {ev.launch_score > 0 && (
                        <Badge className="bg-indigo-50 text-indigo-600 border-indigo-200 text-[10px]">
                          {ev.launch_score}
                        </Badge>
                      )}
                      <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-slate-500" />
                    </a>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create Watch Modal */}
      {showCreate && (
        <CreateWatchModal
          onClose={() => setShowCreate(false)}
          onCreated={(w) => { setWatches(prev => [w, ...prev]); setShowCreate(false); }}
        />
      )}
    </DashboardLayout>
  );
}

function CreateWatchModal({ onClose, onCreated }) {
  const [name, setName] = useState('');
  const [type, setType] = useState('product_score');
  const [threshold, setThreshold] = useState(60);
  const [operator, setOperator] = useState('below');
  const [email, setEmail] = useState(true);
  const [inApp, setInApp] = useState(true);
  const [creating, setCreating] = useState(false);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    try {
      const res = await api.post('/api/radar/watches', {
        name: name.trim(),
        watch_type: type,
        condition: { operator, value: threshold },
        notify_email: email,
        notify_in_app: inApp,
      });
      if (res.ok) {
        toast.success('Watch created');
        onCreated(res.data.watch);
      }
    } catch { toast.error('Failed to create watch'); }
    setCreating(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose} data-testid="create-watch-modal">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4" onClick={e => e.stopPropagation()}>
        <div className="p-6 space-y-4">
          <h2 className="text-lg font-bold text-slate-900">Create Radar Watch</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Watch Name</label>
              <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g., Score drop under 60" data-testid="watch-name-input" />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Watch Type</label>
              <div className="space-y-2">
                {WATCH_TYPES.map(wt => (
                  <button
                    key={wt.id}
                    type="button"
                    onClick={() => setType(wt.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border text-left transition-colors ${type === wt.id ? 'bg-indigo-50 border-indigo-300' : 'bg-white border-slate-200 hover:border-slate-300'}`}
                    data-testid={`watch-type-${wt.id}`}
                  >
                    <wt.icon className={`h-4 w-4 ${type === wt.id ? 'text-indigo-600' : 'text-slate-400'}`} />
                    <div>
                      <p className="text-sm font-medium text-slate-800">{wt.label}</p>
                      <p className="text-xs text-slate-400">{wt.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Condition</label>
                <select value={operator} onChange={e => setOperator(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" data-testid="watch-operator">
                  <option value="below">Drops below</option>
                  <option value="above">Rises above</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Threshold</label>
                <Input type="number" value={threshold} onChange={e => setThreshold(Number(e.target.value))} data-testid="watch-threshold" />
              </div>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
                <input type="checkbox" checked={email} onChange={e => setEmail(e.target.checked)} className="rounded" /> Email
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
                <input type="checkbox" checked={inApp} onChange={e => setInApp(e.target.checked)} className="rounded" /> In-app
              </label>
            </div>
            <div className="flex gap-2 pt-2">
              <Button type="button" variant="outline" onClick={onClose} className="flex-1">Cancel</Button>
              <Button type="submit" disabled={creating || !name.trim()} className="flex-1 bg-indigo-600 hover:bg-indigo-700" data-testid="submit-watch-btn">
                {creating ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
                Create Watch
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
