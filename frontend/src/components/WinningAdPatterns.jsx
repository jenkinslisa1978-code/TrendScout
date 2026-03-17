import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Loader2, Sparkles, Eye, Video, Users, Megaphone,
  Music, MousePointer, BarChart3, Shield,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const CONFIDENCE_COLORS = {
  High: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  Medium: 'bg-amber-100 text-amber-700 border-amber-200',
  Low: 'bg-slate-100 text-slate-600 border-slate-200',
};

export default function WinningAdPatterns({ productId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await apiGet(`/api/ad-engine/patterns/${productId}`);
        if (res.ok) setData(await res.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, [productId]);

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

  const p = data.patterns;

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="winning-ad-patterns">
      <CardHeader className="bg-gradient-to-r from-rose-600 via-pink-600 to-violet-600 text-white py-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-amber-300" />
          Winning Ad Patterns
          <Badge className="ml-auto bg-white/20 text-white border-white/30 text-[10px]">
            {data.overall_confidence}% confidence
          </Badge>
        </CardTitle>
        <p className="text-xs text-rose-200 mt-1">
          Based on {data.total_ads_analysed} ads analysed &middot; Source: {data.data_source === 'ad_discovery' ? 'Real ad data' : 'Product signals'}
        </p>
      </CardHeader>

      <CardContent className="p-5">
        <Tabs defaultValue="patterns">
          <TabsList className="w-full bg-slate-50 mb-4">
            <TabsTrigger value="patterns" className="flex-1 text-xs">Patterns</TabsTrigger>
            <TabsTrigger value="engagement" className="flex-1 text-xs">Engagement</TabsTrigger>
            <TabsTrigger value="platforms" className="flex-1 text-xs">Platforms</TabsTrigger>
          </TabsList>

          <TabsContent value="patterns" className="space-y-3 mt-0">
            {/* Hook Type */}
            <PatternRow
              icon={Eye}
              label="Hook Type"
              value={p.hook_type.primary.name}
              detail={p.hook_type.primary.description}
              frequency={p.hook_type.primary.pattern_frequency}
              strength={p.hook_type.primary.pattern_strength}
              confidence={p.hook_type.primary.confidence_level}
            />
            <PatternRow
              icon={Eye}
              label="Alt Hook"
              value={p.hook_type.secondary.name}
              detail={p.hook_type.secondary.description}
              frequency={p.hook_type.secondary.pattern_frequency}
              strength={p.hook_type.secondary.pattern_strength}
              confidence={p.hook_type.secondary.confidence_level}
              secondary
            />
            {/* Video Length */}
            <PatternRow
              icon={Video}
              label="Video Length"
              value={p.video_length.dominant_range}
              detail={`${p.video_length.platform} — ${p.video_length.best_for}`}
              frequency={p.video_length.pattern_frequency}
              confidence={p.video_length.confidence_level}
            />
            {/* Content Format */}
            <PatternRow
              icon={Users}
              label="Content Format"
              value={`${p.content_format.dominant} (${p.content_format.ugc_ratio}%)`}
              detail={`UGC: ${p.content_format.ugc_ratio}% | Studio: ${p.content_format.studio_ratio}%`}
              confidence={p.content_format.confidence_level}
            />
            {/* CTA Style */}
            <PatternRow
              icon={MousePointer}
              label="CTA Style"
              value={p.cta_style.name}
              detail={p.cta_style.example}
              strength={p.cta_style.pattern_strength}
              confidence={p.cta_style.confidence_level}
            />
            {/* Music */}
            <PatternRow
              icon={Music}
              label="Music / Sound"
              value={p.music_sound.dominant_type}
              confidence={p.music_sound.confidence_level}
            />
          </TabsContent>

          <TabsContent value="engagement" className="mt-0">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-sm text-slate-600 flex items-center gap-2"><BarChart3 className="h-4 w-4 text-indigo-400" /> Avg Engagement Rate</span>
                <span className="font-mono font-bold text-indigo-600" data-testid="avg-engagement">{p.engagement_indicators.avg_engagement_rate}%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-sm text-slate-600 flex items-center gap-2"><Users className="h-4 w-4 text-emerald-400" /> Comment Sentiment</span>
                <Badge className={p.engagement_indicators.comment_sentiment === 'Positive' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}>
                  {p.engagement_indicators.comment_sentiment}
                </Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-sm text-slate-600 flex items-center gap-2"><Shield className="h-4 w-4 text-violet-400" /> Save Rate</span>
                <Badge className={p.engagement_indicators.save_rate === 'High' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}>
                  {p.engagement_indicators.save_rate}
                </Badge>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="platforms" className="mt-0">
            <div className="space-y-2">
              {Object.entries(data.platforms).map(([plat, count]) => (
                <div key={plat} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                  <span className="text-sm text-slate-600 capitalize flex items-center gap-2">
                    <Megaphone className="h-4 w-4 text-rose-400" />
                    {plat.replace('_', ' ')}
                  </span>
                  <span className="font-mono font-bold text-slate-800">{count} ads</span>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

function PatternRow({ icon: Icon, label, value, detail, frequency, strength, confidence, secondary }) {
  const confColor = CONFIDENCE_COLORS[confidence] || CONFIDENCE_COLORS.Medium;
  return (
    <div className={`p-3 rounded-xl ${secondary ? 'bg-slate-50/50 border border-slate-100' : 'bg-slate-50'}`} data-testid={`pattern-${label.toLowerCase().replace(/\s/g, '-')}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          <Icon className={`h-4 w-4 flex-shrink-0 ${secondary ? 'text-slate-400' : 'text-rose-500'}`} />
          <span className="text-xs text-slate-500 flex-shrink-0">{label}</span>
          <span className={`text-sm font-semibold ${secondary ? 'text-slate-600' : 'text-slate-900'}`}>{value}</span>
        </div>
        <Badge className={`text-[10px] border ${confColor}`}>{confidence}</Badge>
      </div>
      {detail && <p className="text-xs text-slate-500 mt-1 ml-6">{detail}</p>}
      {(frequency || strength) && (
        <div className="flex gap-4 mt-1.5 ml-6 text-[10px] text-slate-400">
          {frequency && <span>Frequency: {frequency}%</span>}
          {strength && <span>Strength: {strength}%</span>}
        </div>
      )}
    </div>
  );
}
