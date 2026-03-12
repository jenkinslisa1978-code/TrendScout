import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Target, TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import { apiGet } from '@/lib/api';

export default function PredictionAccuracyCard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiGet('/api/outcomes/prediction-accuracy');
        if (res.ok) setData(await res.json());
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <Card className="border-0 shadow-lg">
        <CardContent className="flex items-center justify-center py-10">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-400" />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.insufficient_data) {
    return (
      <Card className="border-0 shadow-md" data-testid="prediction-accuracy">
        <CardContent className="p-5">
          <div className="flex items-center gap-2 mb-3">
            <Target className="h-5 w-5 text-indigo-600" />
            <p className="text-sm font-semibold text-slate-900">Prediction Accuracy</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Info className="h-4 w-4 text-slate-400" />
            <span>Track more product outcomes to see accuracy data. Need at least 3 resolved outcomes.</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const accColor = data.accuracy_pct >= 60 ? 'text-emerald-600' : data.accuracy_pct >= 40 ? 'text-amber-600' : 'text-red-500';

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="prediction-accuracy">
      <CardContent className="p-0">
        {/* Header */}
        <div className="p-5 bg-gradient-to-r from-violet-50/80 to-indigo-50/60 border-b border-slate-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-violet-600" />
              <p className="text-sm font-semibold text-slate-900">Prediction Accuracy</p>
            </div>
            <Badge className="bg-violet-100 text-violet-700 border-violet-200 text-[10px]">
              {data.sample_size} products tracked
            </Badge>
          </div>
        </div>

        {/* Main stat */}
        <div className="p-5">
          <div className="flex items-center gap-6">
            <div className="text-center">
              <p className={`text-4xl font-bold font-mono ${accColor}`} data-testid="accuracy-pct">
                {data.accuracy_pct}%
              </p>
              <p className="text-xs text-slate-500 mt-1">Accuracy</p>
            </div>
            <div className="flex-1 grid grid-cols-2 gap-3">
              <div className="bg-emerald-50 rounded-lg p-3 text-center">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 mx-auto mb-1" />
                <p className="text-lg font-bold font-mono text-emerald-600" data-testid="correct-predictions">{data.successful_predictions}</p>
                <p className="text-[10px] text-emerald-600">Correct</p>
              </div>
              <div className="bg-red-50 rounded-lg p-3 text-center">
                <AlertTriangle className="h-4 w-4 text-red-400 mx-auto mb-1" />
                <p className="text-lg font-bold font-mono text-red-500" data-testid="failed-predictions">{data.failed_predictions}</p>
                <p className="text-[10px] text-red-500">Incorrect</p>
              </div>
            </div>
          </div>

          {/* Score buckets */}
          {data.score_buckets?.length > 0 && (
            <div className="mt-4 space-y-2">
              {data.score_buckets.map((b) => (
                <div key={b.range} className="flex items-center gap-3 text-xs" data-testid={`bucket-${b.range}`}>
                  <span className="w-12 text-slate-500 font-mono">{b.range}</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full ${b.success_rate >= 60 ? 'bg-emerald-500' : b.success_rate >= 30 ? 'bg-amber-400' : 'bg-red-400'}`}
                      style={{ width: `${b.success_rate}%` }}
                    />
                  </div>
                  <span className="w-20 text-right text-slate-600">{b.success_rate}% success</span>
                </div>
              ))}
            </div>
          )}

          {/* Insights */}
          {data.insights?.length > 0 && (
            <div className="mt-4 space-y-1.5">
              {data.insights.filter(i => i.bucket !== 'info').slice(0, 3).map((ins, i) => (
                <p key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                  <TrendingUp className="h-3 w-3 text-indigo-400 mt-0.5 flex-shrink-0" />
                  {ins.text}
                </p>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
