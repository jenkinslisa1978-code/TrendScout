import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Target, Trophy, Loader2, Package, Play, CheckCircle2, BarChart3,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

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
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Ad A/B Tests</h1>
            <p className="text-sm text-slate-500 mt-1">Track and compare ad variations to find winners</p>
          </div>
          <div className="flex gap-4 text-sm">
            <span className="text-slate-500">Active: <strong className="text-indigo-600">{active.length}</strong></span>
            <span className="text-slate-500">Completed: <strong className="text-emerald-600">{completed.length}</strong></span>
          </div>
        </div>

        {tests.length === 0 ? (
          <Card className="border-0 shadow-md">
            <CardContent className="text-center py-12">
              <Target className="h-12 w-12 text-slate-300 mx-auto mb-3" />
              <p className="text-lg font-semibold text-slate-700">No A/B tests yet</p>
              <p className="text-sm text-slate-500 mt-1 mb-6">Start an A/B test from any product page</p>
              <Button onClick={() => navigate('/discover')} data-testid="go-discover-btn">Browse Products</Button>
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
                  <BarChart3 className="h-5 w-5 text-slate-300 flex-shrink-0" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
