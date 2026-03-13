import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, BarChart3, Eye, Activity } from 'lucide-react';

export default function TrendTimeline({ product }) {
  if (!product) return null;

  const score = product.launch_score || product.market_score || 0;
  const tiktokViews = product.tiktok_views || 0;
  const googleTrend = product.google_trend_score || 0;
  const growthRate = product.growth_rate || product.trend_velocity || 0;

  // Generate a synthetic 7-day trend line from available data
  const generateTrendData = () => {
    const base = Math.max(10, score - 20);
    const points = [];
    for (let i = 0; i < 7; i++) {
      const dayGrowth = growthRate > 0 ? (growthRate / 100) * (i / 7) : (Math.random() * 0.3 - 0.1);
      const noise = (Math.random() - 0.5) * 8;
      const value = Math.min(100, Math.max(0, base + (score - base) * (i / 6) + noise));
      points.push({ day: i, value: Math.round(value) });
    }
    return points;
  };

  const trendData = generateTrendData();
  const maxVal = Math.max(...trendData.map(d => d.value));
  const minVal = Math.min(...trendData.map(d => d.value));
  const range = maxVal - minVal || 1;

  // Create SVG path
  const width = 280;
  const height = 60;
  const padding = 4;
  const pathPoints = trendData.map((d, i) => {
    const x = padding + (i / 6) * (width - padding * 2);
    const y = height - padding - ((d.value - minVal) / range) * (height - padding * 2);
    return { x, y };
  });

  const linePath = pathPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaPath = linePath + ` L ${pathPoints[pathPoints.length - 1].x} ${height} L ${pathPoints[0].x} ${height} Z`;

  const isRising = trendData[trendData.length - 1].value > trendData[0].value;
  const color = isRising ? '#10b981' : '#ef4444';
  const bgColor = isRising ? '#10b98120' : '#ef444420';

  const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  return (
    <Card className="border-0 shadow-lg" data-testid="trend-timeline">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
            <Activity className="h-4 w-4 text-indigo-500" />
            Trend Timeline
          </h3>
          <Badge className={`rounded-full text-[10px] border-0 ${isRising ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}`}>
            <TrendingUp className={`h-2.5 w-2.5 mr-0.5 ${isRising ? '' : 'rotate-180'}`} />
            {isRising ? '+' : ''}{growthRate.toFixed(1)}% / 7d
          </Badge>
        </div>

        {/* Chart */}
        <div className="relative mb-3">
          <svg width="100%" viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
            <defs>
              <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity="0.3" />
                <stop offset="100%" stopColor={color} stopOpacity="0.02" />
              </linearGradient>
            </defs>
            {/* Grid lines */}
            {[0, 1, 2].map(i => (
              <line key={i} x1={padding} x2={width - padding} y1={padding + i * ((height - padding * 2) / 2)} y2={padding + i * ((height - padding * 2) / 2)} stroke="#e2e8f0" strokeWidth="0.5" strokeDasharray="4 4" />
            ))}
            {/* Area */}
            <path d={areaPath} fill="url(#trendGradient)" />
            {/* Line */}
            <path d={linePath} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            {/* Points */}
            {pathPoints.map((p, i) => (
              <circle key={i} cx={p.x} cy={p.y} r="3" fill="white" stroke={color} strokeWidth="1.5" />
            ))}
          </svg>
          {/* Day labels */}
          <div className="flex justify-between px-1 mt-1">
            {dayLabels.map(d => <span key={d} className="text-[9px] text-slate-400">{d}</span>)}
          </div>
        </div>

        {/* Metrics row */}
        <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-100">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-slate-400 text-[10px] mb-0.5">
              <BarChart3 className="h-3 w-3" /> Score
            </div>
            <p className="text-lg font-bold text-indigo-600 font-mono">{score}</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-slate-400 text-[10px] mb-0.5">
              <Eye className="h-3 w-3" /> TikTok
            </div>
            <p className="text-lg font-bold text-rose-600 font-mono">
              {tiktokViews >= 1e6 ? `${(tiktokViews / 1e6).toFixed(1)}M` : tiktokViews >= 1e3 ? `${(tiktokViews / 1e3).toFixed(0)}K` : tiktokViews}
            </p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-slate-400 text-[10px] mb-0.5">
              <TrendingUp className="h-3 w-3" /> Google
            </div>
            <p className="text-lg font-bold text-amber-600 font-mono">{googleTrend}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
