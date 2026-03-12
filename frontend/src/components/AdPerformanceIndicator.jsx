import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Loader2, Activity, TrendingUp, TrendingDown, Minus,
  Rocket, Megaphone, ShieldAlert, Radio,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const ENGAGEMENT_COLORS = {
  'Very High': { bg: 'bg-red-50', text: 'text-red-600', badge: 'bg-red-100 text-red-700 border-red-200' },
  High: { bg: 'bg-amber-50', text: 'text-amber-600', badge: 'bg-amber-100 text-amber-700 border-amber-200' },
  Medium: { bg: 'bg-sky-50', text: 'text-sky-600', badge: 'bg-sky-100 text-sky-700 border-sky-200' },
  Low: { bg: 'bg-emerald-50', text: 'text-emerald-600', badge: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  None: { bg: 'bg-slate-50', text: 'text-slate-500', badge: 'bg-slate-100 text-slate-600 border-slate-200' },
};

const TREND_ICONS = {
  'rocket': Rocket,
  'trending-up': TrendingUp,
  'trending-down': TrendingDown,
  'minus': Minus,
};

const SATURATION_COLORS = {
  High: 'bg-red-100 text-red-700 border-red-200',
  Medium: 'bg-amber-100 text-amber-700 border-amber-200',
  Low: 'bg-emerald-100 text-emerald-700 border-emerald-200',
};

export default function AdPerformanceIndicator({ productId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await apiGet(`/api/ad-engine/performance/${productId}`);
        if (res.ok) setData(await res.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
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

  const engConfig = ENGAGEMENT_COLORS[data.engagement_level] || ENGAGEMENT_COLORS.Medium;
  const TrendIcon = TREND_ICONS[data.trend_icon] || Minus;
  const satColor = SATURATION_COLORS[data.ad_saturation] || SATURATION_COLORS.Medium;

  return (
    <Card className="border-0 shadow-md" data-testid="ad-performance">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-slate-600" />
            <p className="text-sm font-semibold text-slate-900">Ad Performance</p>
          </div>
          <Badge className={`text-xs border ${engConfig.badge}`} data-testid="engagement-level">
            {data.engagement_level}
          </Badge>
        </div>

        {/* Engagement */}
        <div className={`${engConfig.bg} rounded-xl p-3.5 mb-3`}>
          <div className="flex items-center gap-2 mb-1">
            <Radio className={`h-4 w-4 ${engConfig.text}`} />
            <span className={`text-sm font-semibold ${engConfig.text}`}>Ad Engagement: {data.engagement_level}</span>
          </div>
          <p className="text-xs text-slate-600">{data.engagement_description}</p>
        </div>

        {/* Metrics */}
        <div className="space-y-2.5">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-500 flex items-center gap-2">
              <TrendIcon className="h-3.5 w-3.5 text-slate-400" />
              Activity Trend
            </span>
            <span className="font-medium text-slate-800" data-testid="activity-trend">{data.activity_trend}</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-500 flex items-center gap-2">
              <ShieldAlert className="h-3.5 w-3.5 text-slate-400" />
              Ad Saturation
            </span>
            <Badge className={`text-xs border ${satColor}`} data-testid="ad-saturation">{data.ad_saturation}</Badge>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-500 flex items-center gap-2">
              <Megaphone className="h-3.5 w-3.5 text-slate-400" />
              Ads Detected
            </span>
            <span className="font-mono font-medium text-slate-800">{data.ads_detected}</span>
          </div>

          {data.platforms_active.length > 0 && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Platforms Active</span>
              <div className="flex gap-1">
                {data.platforms_active.map((p) => (
                  <Badge key={p} className="bg-slate-100 text-slate-600 border-slate-200 text-[10px] capitalize">
                    {p.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Advice */}
        <div className="mt-3 p-2.5 bg-indigo-50 rounded-lg text-xs text-indigo-700 border border-indigo-100">
          {data.saturation_advice}
        </div>
      </CardContent>
    </Card>
  );
}
