import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Target, Trophy, Loader2, Package, Play, CheckCircle2, BarChart3,
  Lightbulb, ArrowRight, Zap, Clock, PoundSterling, TrendingUp,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const HOW_IT_WORKS = [
  { step: 1, icon: Target, title: 'Choose a Product', desc: 'Pick any product from your discovery feed. We generate 3 ad variations with proven hook styles.' },
  { step: 2, icon: Play, title: 'Run Your Ads', desc: 'Launch all 3 variations on TikTok or Meta with identical budgets and audiences (£10-20 each).' },
  { step: 3, icon: BarChart3, title: 'Log Your Results', desc: 'Enter your real spend, clicks, CTR, and purchases for each variation after 24-48 hours.' },
  { step: 4, icon: Trophy, title: 'Find Your Winner', desc: 'We identify the best-performing hook. Scale the winner and cut the losers.' },
];

export default function AdTestsPage() {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTests = useCallback(async () => {
    try {
      const res = await apiGet('/api/ad-tests/my');
      if (res.ok) {
        const d = await res.json();
        setTests(d.tests || []);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchTests(); }, [fetchTests]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  const active = tests.filter((t) => t.status === 'active');
  const completed = tests.filter((t) => t.status === 'completed');

  return (
    <div className="min-h-screen bg-[#F8FAFC]" data-testid="ad-tests-page">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Ad Creative Testing</h1>
            <p className="text-sm text-slate-500 mt-1">Test different ad hooks before scaling your budget</p>
          </div>
          <div className="flex gap-4 text-sm">
            <span className="text-slate-500">Active: <strong className="text-indigo-600">{active.length}</strong></span>
            <span className="text-slate-500">Completed: <strong className="text-emerald-600">{completed.length}</strong></span>
          </div>
        </div>

        {/* How It Works */}
        <Card className="border-0 shadow-sm mb-6 bg-gradient-to-r from-indigo-50 to-slate-50" data-testid="how-it-works">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="h-4 w-4 text-indigo-600" />
              <h2 className="text-sm font-semibold text-slate-900">How Ad Testing Works</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {HOW_IT_WORKS.map(({ step, icon: Icon, title, desc }) => (
                <div key={step} className="flex gap-3">
                  <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                    <Icon className="h-3.5 w-3.5 text-indigo-600" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-900">{step}. {title}</p>
                    <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Key Metrics Reference */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {[
            { label: 'Good CTR', value: '> 2%', icon: TrendingUp, color: 'text-emerald-600 bg-emerald-50' },
            { label: 'Good CPC', value: '< £0.50', icon: PoundSterling, color: 'text-blue-600 bg-blue-50' },
            { label: 'Test Duration', value: '24-48h', icon: Clock, color: 'text-amber-600 bg-amber-50' },
            { label: 'Min Budget', value: '£30-60', icon: Zap, color: 'text-purple-600 bg-purple-50' },
          ].map(m => (
            <Card key={m.label} className="border-0 shadow-sm">
              <CardContent className="p-3 flex items-center gap-2.5">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${m.color}`}>
                  <m.icon className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs text-slate-400">{m.label}</p>
                  <p className="text-sm font-bold text-slate-900">{m.value}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Tests List */}
        {tests.length === 0 ? (
          <Card className="border-0 shadow-md" data-testid="empty-state">
            <CardContent className="text-center py-12">
              <Target className="h-12 w-12 text-slate-300 mx-auto mb-3" />
              <p className="text-lg font-semibold text-slate-700">No ad tests yet</p>
              <p className="text-sm text-slate-500 mt-1 mb-2 max-w-md mx-auto">
                Go to any product page and click <strong>"Create Ad Test"</strong> to generate 3 ad variations with proven hook styles (Transformation, Social Proof, Curiosity, etc.)
              </p>
              <p className="text-xs text-slate-400 mb-6">
                Each variation comes with a scene-by-scene script, recommended CTA, and testing plan
              </p>
              <Button onClick={() => navigate('/discover')} data-testid="go-discover-btn" className="gap-2">
                Browse Products <ArrowRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {tests.map((t) => (
              <Card
                key={t.id}
                className="border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/product/${t.product_id}`)}
                data-testid={`ad-test-${t.id}`}
              >
                <CardContent className="p-4 flex items-center gap-4">
                  {t.image_url ? (
                    <img src={t.image_url} alt="" className="w-14 h-14 rounded-xl object-cover bg-slate-100 flex-shrink-0" />
                  ) : (
                    <div className="w-14 h-14 rounded-xl bg-slate-100 flex items-center justify-center flex-shrink-0">
                      <Package className="h-6 w-6 text-slate-400" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-slate-900 truncate">{t.product_name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={t.status === 'active' ? 'bg-indigo-100 text-indigo-700 border-indigo-200' : 'bg-emerald-100 text-emerald-700 border-emerald-200'}>
                        {t.status === 'active' ? <Play className="h-2.5 w-2.5 mr-1" /> : <CheckCircle2 className="h-2.5 w-2.5 mr-1" />}
                        {t.status}
                      </Badge>
                      <span className="text-xs text-slate-400">{t.variations?.length || 3} variations</span>
                      {t.scripts && (
                        <span className="text-xs text-slate-400">
                          Hooks: {t.scripts.map(s => s.hook_type).join(', ')}
                        </span>
                      )}
                    </div>
                  </div>
                  {t.winner && (
                    <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2">
                      <Trophy className="h-4 w-4 text-amber-500" />
                      <div>
                        <p className="text-xs font-semibold text-amber-800">{t.winner.label}</p>
                        <p className="text-[10px] text-amber-600">CTR {t.winner.ctr}%</p>
                      </div>
                    </div>
                  )}
                  <ArrowRight className="h-5 w-5 text-slate-300 flex-shrink-0" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Data Transparency */}
        <div className="mt-8 p-4 bg-slate-100 rounded-lg" data-testid="data-transparency">
          <p className="text-xs text-slate-500">
            <strong className="text-slate-700">How this works:</strong> We generate ad variations using proven hook frameworks (Transformation, Social Proof, Curiosity, etc.) based on the product's category and attributes. The scripts provide a starting point — customise them for your brand voice. Results tracking is manual: run the ads on your platform, then log the real performance data here to find your winner.
          </p>
        </div>
      </div>
    </div>
  );
}
