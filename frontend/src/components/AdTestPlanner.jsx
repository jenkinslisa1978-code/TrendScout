import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Loader2, Sparkles, Play, Trophy, BarChart3, Clock,
  Target, DollarSign, MousePointer, ChevronRight, CheckCircle2,
} from 'lucide-react';
import { apiGet, apiPost, apiPut } from '@/lib/api';
import { toast } from 'sonner';

export default function AdTestPlanner({ productId }) {
  const [data, setData] = useState(null);
  const [activeTest, setActiveTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [varRes, testsRes] = await Promise.all([
        apiGet(`/api/ad-tests/variations/${productId}`),
        apiGet('/api/ad-tests/my?status=active'),
      ]);
      if (varRes.ok) setData(await varRes.json());
      if (testsRes.ok) {
        const t = await testsRes.json();
        const existing = t.tests?.find((te) => te.product_id === productId);
        if (existing) setActiveTest(existing);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [productId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreateTest = async () => {
    setCreating(true);
    try {
      const res = await apiPost('/api/ad-tests/create', { product_id: productId });
      if (res.ok) {
        const d = await res.json();
        setActiveTest(d.test);
        toast.success('Ad test created! Start running your ads.');
      }
    } catch (e) { toast.error('Failed to create test'); }
    finally { setCreating(false); }
  };

  if (loading) {
    return (
      <Card className="border-0 shadow-lg">
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-400" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="ad-test-planner">
      <CardHeader className="bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 text-white py-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Target className="h-5 w-5 text-white" />
          Ad A/B Test Planner
          {activeTest && (
            <Badge className="ml-auto bg-white/20 text-white border-white/30 text-[10px]">
              Test Active
            </Badge>
          )}
        </CardTitle>
        <p className="text-xs text-amber-100 mt-1">
          Test {data.variations.length} ad variations to find what converts best
        </p>
      </CardHeader>

      <CardContent className="p-5">
        <Tabs defaultValue="variations">
          <TabsList className="w-full bg-slate-50 mb-4">
            <TabsTrigger value="variations" className="flex-1 text-xs">Variations</TabsTrigger>
            <TabsTrigger value="test-plan" className="flex-1 text-xs">Test Plan</TabsTrigger>
            {activeTest && <TabsTrigger value="results" className="flex-1 text-xs">Results</TabsTrigger>}
          </TabsList>

          {/* Variations Tab */}
          <TabsContent value="variations" className="mt-0 space-y-3">
            {data.variations.map((v, i) => (
              <VariationCard key={v.variation_id} variation={v} index={i} />
            ))}
            {!activeTest && (
              <Button
                onClick={handleCreateTest}
                disabled={creating}
                className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 rounded-xl mt-2"
                data-testid="start-test-btn"
              >
                {creating ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                Start A/B Test
              </Button>
            )}
          </TabsContent>

          {/* Test Plan Tab */}
          <TabsContent value="test-plan" className="mt-0">
            <TestPlanView plan={data.test_plan} />
          </TabsContent>

          {/* Results Tab */}
          {activeTest && (
            <TabsContent value="results" className="mt-0">
              <ResultsTracker test={activeTest} onUpdate={fetchData} />
            </TabsContent>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
}

function VariationCard({ variation, index }) {
  const [expanded, setExpanded] = useState(false);
  const colors = ['border-rose-200 bg-rose-50/40', 'border-indigo-200 bg-indigo-50/40', 'border-emerald-200 bg-emerald-50/40'];
  const dotColors = ['bg-rose-500', 'bg-indigo-500', 'bg-emerald-500'];

  return (
    <div className={`rounded-xl border p-4 ${colors[index % 3]}`} data-testid={`variation-${variation.variation_id}`}>
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-full ${dotColors[index % 3]} text-white text-xs font-bold flex items-center justify-center flex-shrink-0`}>
          {variation.label.split(' ')[1]}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-800">{variation.label} — {variation.hook_type}</p>
          <p className="text-xs text-slate-500">{variation.video_structure} &middot; {variation.recommended_length}</p>
        </div>
        <Badge className="bg-white/80 text-slate-600 border-slate-200 text-[10px]">
          {variation.effectiveness_estimate}% eff.
        </Badge>
      </div>

      <p className="text-xs text-slate-600 mt-2 italic">"{variation.hook_line}"</p>
      <p className="text-xs text-slate-500 mt-1">CTA: {variation.cta}</p>

      <button onClick={() => setExpanded(!expanded)} className="text-xs text-indigo-600 hover:underline mt-2 flex items-center gap-1">
        <ChevronRight className={`h-3 w-3 transition-transform ${expanded ? 'rotate-90' : ''}`} />
        {expanded ? 'Hide' : 'View'} Script
      </button>

      {expanded && (
        <div className="mt-2 space-y-1.5 bg-white/60 rounded-lg p-3" data-testid={`script-${variation.variation_id}`}>
          {variation.script.map((s, i) => (
            <div key={i} className="flex gap-2 text-xs">
              <span className="font-mono text-slate-400 w-12 flex-shrink-0">{s.time}</span>
              <div>
                <p className="text-slate-700">{s.action}</p>
                <p className="text-slate-400">{s.audio}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function TestPlanView({ plan }) {
  return (
    <div className="space-y-4" data-testid="test-plan">
      <div className="flex items-center gap-4 text-sm">
        <span className="flex items-center gap-1 text-slate-500"><DollarSign className="h-3.5 w-3.5" /> Budget: <strong className="text-slate-800">{plan.total_budget}</strong></span>
        <span className="flex items-center gap-1 text-slate-500"><Clock className="h-3.5 w-3.5" /> Duration: <strong className="text-slate-800">{plan.duration}</strong></span>
      </div>

      <div className="space-y-2">
        {plan.steps.map((s) => (
          <div key={s.step} className="flex gap-3 p-3 bg-slate-50 rounded-xl">
            <div className="w-7 h-7 rounded-full bg-indigo-100 text-indigo-600 text-xs font-bold flex items-center justify-center flex-shrink-0">
              {s.step}
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">{s.title}</p>
              <p className="text-xs text-slate-500 mt-0.5">{s.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <p className="text-xs font-semibold text-slate-700 mb-2">Metrics to Evaluate</p>
        <div className="grid grid-cols-2 gap-2">
          {plan.metrics_to_track.map((m) => (
            <div key={m.metric} className="bg-slate-50 rounded-lg p-2.5">
              <p className="text-xs font-bold text-slate-800">{m.metric}</p>
              <p className="text-[10px] text-slate-500">{m.description}</p>
              <div className="flex gap-2 mt-1 text-[10px]">
                <span className="text-emerald-600">Good: {m.good}</span>
                <span className="text-slate-400">|</span>
                <span className="text-red-500">Poor: {m.poor}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ResultsTracker({ test, onUpdate }) {
  const [editVar, setEditVar] = useState(null);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [completing, setCompleting] = useState(false);

  const handleSave = async () => {
    if (!editVar) return;
    setSaving(true);
    try {
      const res = await apiPut(`/api/ad-tests/${test.id}/results`, {
        variation_id: editVar,
        ...form,
      });
      if (res.ok) {
        toast.success('Results saved');
        setEditVar(null);
        onUpdate();
      }
    } catch (e) { toast.error('Failed to save'); }
    finally { setSaving(false); }
  };

  const handleComplete = async () => {
    setCompleting(true);
    try {
      const res = await apiPost(`/api/ad-tests/${test.id}/complete`);
      if (res.ok) {
        toast.success('Test completed! Results saved to learning system.');
        onUpdate();
      }
    } catch (e) { toast.error('Failed to complete'); }
    finally { setCompleting(false); }
  };

  return (
    <div className="space-y-3" data-testid="results-tracker">
      {/* Winner banner */}
      {test.winner && (
        <div className="p-3 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl" data-testid="winner-banner">
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            <div>
              <p className="text-sm font-bold text-amber-800">{test.winner.label} performing best</p>
              <p className="text-xs text-amber-600">
                CTR {test.winner.ctr}% vs {(test.winner.ctr - test.winner.vs_average).toFixed(2)}% average (+{test.winner.vs_average}%)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Variations */}
      {test.variations.map((v) => {
        const r = v.results;
        const isEditing = editVar === v.variation_id;
        return (
          <div key={v.variation_id} className="border border-slate-100 rounded-xl p-3" data-testid={`result-${v.variation_id}`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-800">{v.label}</span>
                <Badge className="text-[10px] bg-slate-100 text-slate-600">{v.hook_type}</Badge>
                {test.winner?.variation_id === v.variation_id && (
                  <Trophy className="h-3.5 w-3.5 text-amber-500" />
                )}
              </div>
              {!isEditing && (
                <Button size="sm" variant="outline" className="text-xs h-7" onClick={() => {
                  setEditVar(v.variation_id);
                  setForm({ spend: r.spend, clicks: r.clicks, ctr: r.ctr, add_to_cart: r.add_to_cart, purchases: r.purchases });
                }} data-testid={`edit-result-${v.variation_id}`}>
                  Record
                </Button>
              )}
            </div>

            {/* Current results */}
            <div className="grid grid-cols-5 gap-2 text-center text-xs">
              <div><p className="font-mono font-bold text-slate-800">£{r.spend}</p><p className="text-slate-400">Spend</p></div>
              <div><p className="font-mono font-bold text-slate-800">{r.clicks}</p><p className="text-slate-400">Clicks</p></div>
              <div><p className="font-mono font-bold text-indigo-600">{r.ctr}%</p><p className="text-slate-400">CTR</p></div>
              <div><p className="font-mono font-bold text-slate-800">{r.add_to_cart}</p><p className="text-slate-400">ATC</p></div>
              <div><p className="font-mono font-bold text-emerald-600">{r.purchases}</p><p className="text-slate-400">Sales</p></div>
            </div>

            {/* Edit form */}
            {isEditing && (
              <div className="mt-3 p-3 bg-slate-50 rounded-lg space-y-2" data-testid={`edit-form-${v.variation_id}`}>
                <div className="grid grid-cols-5 gap-2">
                  {[
                    ['spend', 'Spend (£)'],
                    ['clicks', 'Clicks'],
                    ['ctr', 'CTR %'],
                    ['add_to_cart', 'ATC'],
                    ['purchases', 'Sales'],
                  ].map(([key, label]) => (
                    <div key={key}>
                      <Label className="text-[10px] text-slate-500">{label}</Label>
                      <Input
                        type="number"
                        step="any"
                        value={form[key] || 0}
                        onChange={(e) => setForm((p) => ({ ...p, [key]: parseFloat(e.target.value) || 0 }))}
                        className="h-8 text-xs"
                        data-testid={`input-${key}`}
                      />
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={handleSave} disabled={saving} className="text-xs h-7" data-testid="save-results-btn">
                    {saving ? <Loader2 className="h-3 w-3 animate-spin" /> : 'Save'}
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setEditVar(null)} className="text-xs h-7">Cancel</Button>
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Complete test */}
      {test.status === 'active' && (
        <Button
          onClick={handleComplete}
          disabled={completing}
          variant="outline"
          className="w-full text-xs border-amber-200 text-amber-700 hover:bg-amber-50"
          data-testid="complete-test-btn"
        >
          {completing ? <Loader2 className="h-3 w-3 animate-spin mr-2" /> : <CheckCircle2 className="h-3 w-3 mr-2" />}
          Complete Test & Save Learnings
        </Button>
      )}
    </div>
  );
}
