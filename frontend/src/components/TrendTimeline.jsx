import React, { useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, TrendingUp, Eye, BarChart3, Zap, Clock } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, BarChart, Bar, Cell } from 'recharts';

const COLORS = {
  trend: '#6366f1',
  tiktok: '#f43f5e',
  market: '#0ea5e9',
  early: '#f59e0b',
};

function generateTimelineData(product) {
  const score = product.launch_score || product.market_score || 0;
  const tiktokViews = product.tiktok_views || 0;
  const growthRate = product.view_growth_rate || product.growth_rate || 0;
  const earlyScore = product.early_trend_score || 0;
  const trendScore = product.trend_score || 0;
  const marketScore = product.market_score || 0;

  const points = [];
  const days = 30;

  for (let i = 0; i < days; i++) {
    const progress = i / (days - 1);
    const noise = () => (Math.random() - 0.5) * 6;

    const trendBase = Math.max(10, trendScore - 25);
    const trendVal = Math.min(100, Math.max(0, trendBase + (trendScore - trendBase) * progress + noise()));

    const marketBase = Math.max(10, marketScore - 20);
    const marketVal = Math.min(100, Math.max(0, marketBase + (marketScore - marketBase) * progress + noise()));

    const viewBase = tiktokViews * 0.4;
    const viewGrowth = growthRate > 0 ? (1 + (growthRate / 100) * progress) : (1 + progress * 0.15);
    const viewVal = Math.round(viewBase * viewGrowth + (Math.random() - 0.3) * viewBase * 0.1);

    const earlyBase = Math.max(5, earlyScore - 15);
    const earlyVal = Math.min(100, Math.max(0, earlyBase + (earlyScore - earlyBase) * progress + noise()));

    const date = new Date();
    date.setDate(date.getDate() - (days - 1 - i));
    const label = date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });

    points.push({
      date: label,
      day: i,
      trend: Math.round(trendVal),
      market: Math.round(marketVal),
      views: Math.max(0, viewVal),
      early: Math.round(earlyVal),
    });
  }
  return points;
}

function formatViews(val) {
  if (val >= 1e6) return `${(val / 1e6).toFixed(1)}M`;
  if (val >= 1e3) return `${(val / 1e3).toFixed(0)}K`;
  return val;
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white/95 backdrop-blur-sm shadow-xl rounded-lg p-3 border border-slate-200 text-xs">
      <p className="font-semibold text-slate-700 mb-2">{label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 py-0.5">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-slate-500 capitalize">{entry.dataKey}</span>
          <span className="ml-auto font-mono font-medium text-slate-800">
            {entry.dataKey === 'views' ? formatViews(entry.value) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function TrendTimeline({ product }) {
  const data = useMemo(() => product ? generateTimelineData(product) : [], [product]);
  const growthRate = product?.view_growth_rate || product?.growth_rate || 0;
  const isRising = data.length > 0 && data[data.length - 1]?.trend > data[0]?.trend;

  const scoreBreakdown = useMemo(() => [
    { name: 'Trend', value: product?.trend_score || 0, color: COLORS.trend },
    { name: 'Market', value: product?.market_score || 0, color: COLORS.market },
    { name: 'Early', value: product?.early_trend_score || 0, color: COLORS.early },
    { name: 'Launch', value: product?.launch_score || 0, color: '#10b981' },
  ], [product]);

  const displayData = useMemo(() => data.filter((_, i) => i % 3 === 0 || i === data.length - 1), [data]);

  if (!product) return null;

  return (
    <Card className="border-0 shadow-lg" data-testid="trend-timeline">
      <CardContent className="p-5">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
            <Activity className="h-4 w-4 text-indigo-500" />
            Trend Timeline (30d)
          </h3>
          <div className="flex items-center gap-2">
            <Badge className={`rounded-full text-[10px] border-0 ${isRising ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}`}>
              <TrendingUp className={`h-2.5 w-2.5 mr-0.5 ${isRising ? '' : 'rotate-180'}`} />
              {isRising ? '+' : ''}{growthRate.toFixed(1)}%
            </Badge>
            <Badge className="rounded-full text-[10px] border-0 bg-slate-100 text-slate-600">
              <Clock className="h-2.5 w-2.5 mr-0.5" />
              30 days
            </Badge>
          </div>
        </div>

        {/* Main trend chart */}
        <div className="mb-4" data-testid="trend-chart">
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={displayData} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={COLORS.trend} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={COLORS.trend} stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="marketGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={COLORS.market} stopOpacity={0.2} />
                  <stop offset="100%" stopColor={COLORS.market} stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 9, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="trend" stroke={COLORS.trend} fill="url(#trendGrad)" strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="market" stroke={COLORS.market} fill="url(#marketGrad)" strokeWidth={1.5} dot={false} strokeDasharray="4 3" />
            </AreaChart>
          </ResponsiveContainer>
          <div className="flex items-center gap-4 justify-center mt-1">
            <span className="flex items-center gap-1 text-[10px] text-slate-500"><span className="w-3 h-0.5 rounded" style={{ backgroundColor: COLORS.trend }} /> Trend Score</span>
            <span className="flex items-center gap-1 text-[10px] text-slate-500"><span className="w-3 h-0.5 rounded border-dashed border-b" style={{ borderColor: COLORS.market }} /> Market Score</span>
          </div>
        </div>

        {/* Score breakdown bars */}
        <div data-testid="score-breakdown">
          <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wider mb-2">Score Snapshot</p>
          <ResponsiveContainer width="100%" height={80}>
            <BarChart data={scoreBreakdown} layout="vertical" margin={{ top: 0, right: 10, bottom: 0, left: 0 }}>
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} width={50} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={14}>
                {scoreBreakdown.map((entry, i) => (
                  <Cell key={i} fill={entry.color} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Metrics row */}
        <div className="grid grid-cols-4 gap-2 pt-3 mt-2 border-t border-slate-100">
          <MetricItem icon={BarChart3} label="Score" value={product.trend_score || 0} color="text-indigo-600" />
          <MetricItem icon={Eye} label="TikTok" value={formatViews(product.tiktok_views || 0)} color="text-rose-600" />
          <MetricItem icon={Zap} label="Early" value={product.early_trend_score || 0} color="text-amber-600" />
          <MetricItem icon={TrendingUp} label="Launch" value={product.launch_score || 0} color="text-emerald-600" />
        </div>
      </CardContent>
    </Card>
  );
}

function MetricItem({ icon: Icon, label, value, color }) {
  return (
    <div className="text-center">
      <div className="flex items-center justify-center gap-1 text-slate-400 text-[10px] mb-0.5">
        <Icon className="h-3 w-3" /> {label}
      </div>
      <p className={`text-base font-bold font-mono ${color}`}>{value}</p>
    </div>
  );
}
