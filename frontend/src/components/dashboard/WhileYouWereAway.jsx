import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { TrendingUp, Flame, BarChart3, Sparkles } from 'lucide-react';
import { apiGet } from '@/lib/api';

export default function WhileYouWereAway() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiGet('/api/products?sortBy=trend_score&sortOrder=desc&limit=50');
        if (res.ok) {
          const data = await res.json();
          const products = data.data || [];
          const exploding = products.filter(p => p.early_trend_label === 'exploding').length;
          const emerging = products.filter(p => p.early_trend_label === 'emerging' || p.early_trend_label === 'rising').length;
          const highMargin = products.filter(p => {
            const cost = p.supplier_cost || 0;
            const retail = p.estimated_retail_price || p.recommended_price || 0;
            return cost > 0 && retail > 0 && ((retail - cost) / retail) > 0.6;
          }).length;

          if (exploding + emerging + highMargin > 0) {
            setStats({ exploding, emerging, highMargin, total: products.length });
          }
        }
      } catch (e) { /* silent */ }
    })();
  }, []);

  if (!stats) return null;

  const items = [
    { count: stats.exploding, label: 'Exploding Trends', icon: Flame, color: 'text-red-600', bg: 'bg-red-50' },
    { count: stats.emerging, label: 'Emerging Products', icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { count: stats.highMargin, label: 'High Margin Opportunities', icon: BarChart3, color: 'text-amber-600', bg: 'bg-amber-50' },
  ].filter(i => i.count > 0);

  if (items.length === 0) return null;

  return (
    <Card className="border-0 shadow-md bg-gradient-to-r from-indigo-50/80 via-violet-50/60 to-fuchsia-50/40" data-testid="while-you-were-away">
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="h-4 w-4 text-indigo-600" />
          <p className="text-sm font-semibold text-indigo-900">While you were away, TrendScout detected:</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {items.map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className={`flex items-center gap-2 ${item.bg} rounded-lg px-3 py-2`}>
                <Icon className={`h-4 w-4 ${item.color}`} />
                <span className={`text-sm font-bold ${item.color}`}>{item.count}</span>
                <span className="text-xs text-slate-600">{item.label}</span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
