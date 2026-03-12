import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Store, TrendingUp, DollarSign, Megaphone, Clock, ShieldAlert } from 'lucide-react';
import { apiGet } from '@/lib/api';

export default function CompetitorIntelligence({ productId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await apiGet(`/api/products/${productId}/competitor-intelligence`);
        if (res.ok) setData(await res.json());
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, [productId]);

  if (loading) {
    return (
      <Card className="border-0 shadow-md">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 animate-spin text-indigo-400" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const compColor = data.competition_level === 'high' ? 'text-red-600' : data.competition_level === 'low' ? 'text-emerald-600' : 'text-amber-600';
  const compBg = data.competition_level === 'high' ? 'bg-red-100 text-red-700 border-red-200' : data.competition_level === 'low' ? 'bg-emerald-100 text-emerald-700 border-emerald-200' : 'bg-amber-100 text-amber-700 border-amber-200';

  return (
    <Card className="border-0 shadow-md" data-testid="competitor-intelligence">
      <CardContent className="p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-slate-600" />
            <p className="text-sm font-semibold text-slate-900">Competitor Intelligence</p>
          </div>
          <Badge className={`text-xs border capitalize ${compBg}`} data-testid="comp-level">
            {data.competition_level} competition
          </Badge>
        </div>

        {/* Key metrics */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-slate-50 rounded-xl p-3.5">
            <Store className="h-4 w-4 text-indigo-500 mb-1.5" />
            <p className="text-xl font-bold font-mono text-slate-800" data-testid="comp-stores">{data.stores_detected}</p>
            <p className="text-xs text-slate-500">Stores detected</p>
          </div>
          <div className="bg-slate-50 rounded-xl p-3.5">
            <TrendingUp className="h-4 w-4 text-rose-500 mb-1.5" />
            <p className="text-xl font-bold font-mono text-slate-800" data-testid="comp-new-stores">{data.new_stores_7d}</p>
            <p className="text-xs text-slate-500">New stores (7d)</p>
          </div>
        </div>

        {/* Detail rows */}
        <div className="space-y-2.5">
          <DetailRow
            icon={DollarSign}
            label="Estimated price range"
            value={`£${data.price_range.low.toFixed(0)} – £${data.price_range.high.toFixed(0)}`}
          />
          <DetailRow
            icon={Clock}
            label="Avg store age"
            value={`${data.avg_store_age_months} months`}
          />
          <DetailRow
            icon={Megaphone}
            label="Advertising activity"
            value={data.advertising_activity}
          />
          <DetailRow
            icon={Megaphone}
            label="Active ads detected"
            value={data.ads_detected}
          />
        </div>

        {/* Impact note */}
        <div className={`mt-4 p-2.5 rounded-lg text-xs border ${
          data.stores_detected > 50 ? 'bg-red-50 text-red-700 border-red-100' :
          data.stores_detected > 20 ? 'bg-amber-50 text-amber-700 border-amber-100' :
          'bg-emerald-50 text-emerald-700 border-emerald-100'
        }`}>
          {data.competition_impact}
        </div>
      </CardContent>
    </Card>
  );
}

function DetailRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-slate-500 flex items-center gap-2">
        <Icon className="h-3.5 w-3.5 text-slate-400" />
        {label}
      </span>
      <span className="font-medium text-slate-800">{value}</span>
    </div>
  );
}
