import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Loader2, Rocket, TrendingUp, DollarSign, ShoppingCart,
  AlertTriangle, CheckCircle2, Clock, Target, BarChart3, Info,
  Brain, Users, Zap, Calendar, ChevronDown, ChevronUp,
  Sparkles, Shield,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const POTENTIAL_CONFIG = {
  High: { color: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: Rocket, barColor: 'bg-emerald-500' },
  Moderate: { color: 'bg-amber-100 text-amber-700 border-amber-200', icon: TrendingUp, barColor: 'bg-amber-500' },
  Risky: { color: 'bg-red-100 text-red-700 border-red-200', icon: AlertTriangle, barColor: 'bg-red-500' },
};

export default function LaunchSimulator({ productId }) {
  const [data, setData] = useState(null);
  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [showAi, setShowAi] = useState(false);
  const [showPhases, setShowPhases] = useState(false);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await apiGet(`/api/ad-tests/simulate/${productId}`);
        if (res.ok) setData(await res.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, [productId]);

  const loadAiAnalysis = async () => {
    if (aiData) { setShowAi(!showAi); return; }
    setAiLoading(true);
    setShowAi(true);
    try {
      const res = await apiGet(`/api/ad-tests/ai-simulate/${productId}`);
      if (res.ok) {
        const result = await res.json();
        setAiData(result.ai_analysis);
      }
    } catch (e) { console.error(e); }
    setAiLoading(false);
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

  const sim = data.simulation;
  const cfg = POTENTIAL_CONFIG[data.potential] || POTENTIAL_CONFIG.Moderate;
  const PotentialIcon = cfg.icon;

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="launch-simulator">
      <CardHeader className="bg-gradient-to-r from-teal-600 via-emerald-600 to-green-600 text-white py-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Rocket className="h-5 w-5 text-amber-300" />
          AI Launch Simulator
          <Badge className={`ml-auto text-[10px] border ${cfg.color}`}>
            <PotentialIcon className="h-3 w-3 mr-1" />
            {data.potential} Potential
          </Badge>
        </CardTitle>
        <p className="text-xs text-emerald-200 mt-1">
          Powered by TrendScout AI — projected outcomes based on product signals and market data
        </p>
      </CardHeader>

      <CardContent className="p-5">
        {/* Key projections grid */}
        <div className="grid grid-cols-2 gap-3 mb-5" data-testid="sim-projections">
          <ProjectionCard icon={DollarSign} label="Profit per Sale" value={`£${sim.profit_per_sale}`} color="text-emerald-600" bg="bg-emerald-50" />
          <ProjectionCard icon={Target} label="Est. Conversion" value={`${sim.estimated_cvr}%`} color="text-indigo-600" bg="bg-indigo-50" />
          <ProjectionCard icon={BarChart3} label="Break-even Ad Cost" value={`£${sim.breakeven_ad_cost}`} color="text-amber-600" bg="bg-amber-50" />
          <ProjectionCard icon={ShoppingCart} label="Daily Sales Range" value={`${sim.daily_sales_range.low}–${sim.daily_sales_range.high}`} sub="units/day" color="text-teal-600" bg="bg-teal-50" />
        </div>

        {/* Detailed metrics */}
        <div className="space-y-2 mb-4">
          <MetricRow label="Estimated CPC" value={`£${sim.estimated_cpc}`} />
          <MetricRow label="Estimated CPA" value={`£${sim.estimated_cpa}`} />
          <MetricRow label="Daily Profit Range" value={`£${sim.daily_profit_range.low} – £${sim.daily_profit_range.high}`} highlight={sim.daily_profit_range.high > 0} />
          {sim.breakeven_days && <MetricRow label="Break-even Timeline" value={`~${sim.breakeven_days} days`} />}
        </div>

        {/* Risks */}
        {data.risks.length > 0 && (
          <div className="mb-4" data-testid="sim-risks">
            <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-500" /> Risk Factors
            </p>
            <div className="space-y-1.5">
              {data.risks.map((r, i) => (
                <p key={i} className="text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-1.5 border border-amber-100">{r}</p>
              ))}
            </div>
          </div>
        )}

        {/* Beginner Guidance */}
        <div className="p-3.5 bg-gradient-to-r from-indigo-50/80 to-violet-50/60 rounded-xl border border-indigo-100 mb-4" data-testid="sim-guidance">
          <div className="flex items-start gap-2">
            <Info className="h-4 w-4 text-indigo-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-indigo-700 leading-relaxed">{data.guidance}</p>
          </div>
        </div>

        {/* AI Analysis Button */}
        <Button
          onClick={loadAiAnalysis}
          disabled={aiLoading}
          className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white rounded-xl h-10 font-semibold"
          data-testid="ai-analysis-btn"
        >
          {aiLoading ? (
            <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Generating AI Strategy...</>
          ) : showAi ? (
            <><ChevronUp className="h-4 w-4 mr-2" /> Hide AI Strategy</>
          ) : (
            <><Brain className="h-4 w-4 mr-2" /> Generate AI Launch Strategy</>
          )}
        </Button>

        {/* AI Analysis Section */}
        {showAi && aiData && !aiData.error && (
          <div className="mt-4 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500" data-testid="ai-analysis-section">
            {/* AI Verdict */}
            <div className="p-4 bg-gradient-to-r from-violet-50 to-indigo-50 rounded-xl border border-violet-200">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-violet-600" />
                <span className="text-xs font-bold text-violet-700">AI VERDICT</span>
                {aiData.confidence_score && (
                  <Badge className="ml-auto bg-violet-100 text-violet-700 border-0 text-xs rounded-full">
                    {aiData.confidence_score}% confidence
                  </Badge>
                )}
              </div>
              <p className="text-sm text-slate-800 font-medium">{aiData.verdict}</p>
            </div>

            {/* Launch Strategy Phases */}
            {aiData.strategy && (
              <div>
                <button
                  onClick={() => setShowPhases(!showPhases)}
                  className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2 hover:text-indigo-600 transition-colors"
                >
                  <Calendar className="h-4 w-4 text-indigo-500" />
                  Launch Strategy Phases
                  {showPhases ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                </button>
                {showPhases && (
                  <div className="space-y-3">
                    {['phase_1', 'phase_2', 'phase_3'].map((phase) => {
                      const p = aiData.strategy[phase];
                      if (!p) return null;
                      return (
                        <div key={phase} className="p-3.5 rounded-xl bg-slate-50 border border-slate-100" data-testid={`ai-${phase}`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-slate-800 text-sm">{p.name}</span>
                            <div className="flex items-center gap-2">
                              <Badge className="bg-slate-100 text-slate-600 border-0 text-[10px] rounded-full">{p.duration}</Badge>
                              <Badge className="bg-indigo-100 text-indigo-700 border-0 text-[10px] rounded-full">£{p.daily_budget}/day</Badge>
                            </div>
                          </div>
                          <ul className="space-y-1">
                            {(p.actions || []).map((a, i) => (
                              <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                                <CheckCircle2 className="h-3 w-3 text-emerald-500 mt-0.5 flex-shrink-0" />
                                {a}
                              </li>
                            ))}
                          </ul>
                          <p className="text-[10px] text-indigo-600 mt-2 font-medium">Success: {p.success_criteria}</p>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* Target Audience */}
            {aiData.target_audience && (
              <div className="p-3.5 rounded-xl bg-sky-50 border border-sky-100">
                <p className="text-xs font-semibold text-sky-700 mb-2 flex items-center gap-1.5">
                  <Users className="h-3.5 w-3.5" /> Target Audience
                </p>
                <p className="text-sm text-slate-700 mb-1"><strong>Primary:</strong> {aiData.target_audience.primary}</p>
                <p className="text-sm text-slate-700 mb-1"><strong>Secondary:</strong> {aiData.target_audience.secondary}</p>
                {aiData.target_audience.platforms && (
                  <div className="flex gap-1.5 mt-2">
                    {aiData.target_audience.platforms.map(p => (
                      <Badge key={p} className="bg-sky-100 text-sky-700 border-0 text-[10px] rounded-full">{p}</Badge>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Revenue Projection */}
            {aiData.revenue_projection && (
              <div>
                <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1.5">
                  <TrendingUp className="h-3.5 w-3.5 text-emerald-500" /> Revenue Projection
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {['month_1', 'month_3', 'month_6'].map(m => {
                    const d = aiData.revenue_projection[m];
                    if (!d) return null;
                    const label = m === 'month_1' ? 'Month 1' : m === 'month_3' ? 'Month 3' : 'Month 6';
                    return (
                      <div key={m} className="p-3 rounded-xl bg-emerald-50 text-center border border-emerald-100" data-testid={`revenue-${m}`}>
                        <p className="text-[10px] text-emerald-600 font-medium">{label}</p>
                        <p className="text-sm font-bold text-emerald-700 mt-1">£{(d.revenue || 0).toLocaleString()}</p>
                        <p className="text-[10px] text-emerald-500">£{(d.profit || 0).toLocaleString()} profit</p>
                        <p className="text-[10px] text-slate-500">{d.orders} orders</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Creative Angles */}
            {aiData.creative_angles && aiData.creative_angles.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-amber-500" /> Ad Creative Angles
                </p>
                <div className="space-y-1.5">
                  {aiData.creative_angles.map((angle, i) => (
                    <div key={i} className="text-xs bg-amber-50 rounded-lg px-3 py-2 border border-amber-100 flex items-start gap-2">
                      <Zap className="h-3 w-3 text-amber-500 mt-0.5 flex-shrink-0" />
                      <span className="text-amber-800">{angle}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Risk Assessment */}
            {aiData.risk_assessment && aiData.risk_assessment.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1.5">
                  <Shield className="h-3.5 w-3.5 text-slate-500" /> AI Risk Assessment
                </p>
                <div className="space-y-1.5">
                  {aiData.risk_assessment.map((r, i) => (
                    <p key={i} className="text-xs text-slate-600 bg-slate-50 rounded-lg px-3 py-2 border border-slate-100">{r}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Competitive Edge */}
            {aiData.competitive_edge && (
              <div className="p-3.5 rounded-xl bg-gradient-to-r from-indigo-50 to-violet-50 border border-indigo-100">
                <p className="text-xs font-semibold text-indigo-700 mb-1 flex items-center gap-1.5">
                  <Target className="h-3.5 w-3.5" /> Competitive Edge
                </p>
                <p className="text-sm text-slate-700">{aiData.competitive_edge}</p>
              </div>
            )}
          </div>
        )}

        {/* AI Error */}
        {showAi && aiData?.error && (
          <div className="mt-4 p-3 bg-amber-50 rounded-xl border border-amber-200 text-sm text-amber-700">
            AI analysis could not be generated. The base simulation is still accurate.
          </div>
        )}

        {/* Inputs used */}
        <details className="mt-3">
          <summary className="text-[10px] text-slate-400 cursor-pointer hover:text-slate-600">View simulation inputs</summary>
          <div className="mt-2 grid grid-cols-3 gap-2 text-[10px]">
            {Object.entries(data.inputs_used).map(([k, v]) => (
              <div key={k} className="bg-slate-50 rounded-lg p-1.5 text-center">
                <p className="text-slate-400 capitalize">{k.replace('_', ' ')}</p>
                <p className="font-mono font-bold text-slate-700">{v}</p>
              </div>
            ))}
          </div>
        </details>
      </CardContent>
    </Card>
  );
}

function ProjectionCard({ icon: Icon, label, value, sub, color, bg }) {
  return (
    <div className={`${bg} rounded-xl p-3.5 text-center`}>
      <Icon className={`h-4 w-4 ${color} mx-auto mb-1.5`} />
      <p className={`text-xl font-bold font-mono ${color}`}>{value}</p>
      {sub && <p className={`text-[10px] ${color} opacity-70`}>{sub}</p>}
      <p className="text-[10px] text-slate-500 mt-0.5">{label}</p>
    </div>
  );
}

function MetricRow({ label, value, highlight }) {
  return (
    <div className="flex items-center justify-between text-sm py-1 border-b border-slate-50 last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className={`font-mono font-medium ${highlight ? 'text-emerald-600' : 'text-slate-800'}`}>{value}</span>
    </div>
  );
}
