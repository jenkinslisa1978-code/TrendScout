import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Loader2, Film, Clock, Camera, Lightbulb, Volume2, Target, ChevronRight,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

export default function AdBlueprint({ productId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const res = await apiGet(`/api/ad-engine/blueprint/${productId}`);
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

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="ad-blueprint">
      <CardHeader className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 text-white py-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Film className="h-5 w-5 text-amber-300" />
          Ad Blueprint
          <Badge className="ml-auto bg-white/20 text-white border-white/30 text-[10px]">
            {data.optimal_length} &middot; {data.content_style}
          </Badge>
        </CardTitle>
        <p className="text-xs text-indigo-200 mt-1">
          Filming plan for {data.target_platforms.join(', ')}
        </p>
      </CardHeader>

      <CardContent className="p-5">
        {/* Timeline */}
        <div className="space-y-0 relative">
          <div className="absolute left-[18px] top-4 bottom-4 w-px bg-gradient-to-b from-rose-300 via-violet-300 to-indigo-300" />
          {data.scenes.map((scene, i) => (
            <SceneCard key={i} scene={scene} index={i} total={data.scenes.length} />
          ))}
        </div>

        {/* Hook Variations */}
        {data.hook_variations?.length > 0 && (
          <div className="mt-6" data-testid="hook-variations">
            <p className="text-sm font-semibold text-slate-800 mb-3 flex items-center gap-2">
              <Target className="h-4 w-4 text-rose-500" />
              Hook Variations to Test
            </p>
            <div className="space-y-2">
              {data.hook_variations.map((hv, i) => (
                <div key={i} className="flex items-start gap-2 p-2.5 bg-slate-50 rounded-lg">
                  <ChevronRight className="h-3.5 w-3.5 text-rose-400 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-slate-700">{hv.hook_type} <span className="text-slate-400">({hv.effectiveness}% eff.)</span></p>
                    <p className="text-xs text-slate-500 mt-0.5">{hv.opening_line}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Filming Tips */}
        {data.filming_tips?.length > 0 && (
          <div className="mt-5" data-testid="filming-tips">
            <p className="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-amber-500" />
              Filming Tips
            </p>
            <ul className="space-y-1.5">
              {data.filming_tips.map((tip, i) => (
                <li key={i} className="text-xs text-slate-600 flex items-start gap-2">
                  <span className="text-indigo-400 mt-0.5">&#x2022;</span>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        )}

        <p className="text-[10px] text-slate-400 mt-4 text-center">
          Generated using winning ad patterns
        </p>
      </CardContent>
    </Card>
  );
}

function SceneCard({ scene, index, total }) {
  const sceneColors = [
    'border-rose-200 bg-rose-50/50',
    'border-indigo-200 bg-indigo-50/50',
    'border-violet-200 bg-violet-50/50',
    'border-amber-200 bg-amber-50/50',
    'border-emerald-200 bg-emerald-50/50',
  ];
  const dotColors = ['bg-rose-500', 'bg-indigo-500', 'bg-violet-500', 'bg-amber-500', 'bg-emerald-500'];
  const colorIdx = index % sceneColors.length;

  return (
    <div className="flex gap-3 relative pl-1" data-testid={`scene-${index}`}>
      {/* Timeline dot */}
      <div className={`relative z-10 flex h-9 w-9 items-center justify-center rounded-full ${dotColors[colorIdx]} text-white text-xs font-bold flex-shrink-0 shadow-sm`}>
        {index + 1}
      </div>
      {/* Content */}
      <div className={`flex-1 border rounded-xl p-3 mb-2 ${sceneColors[colorIdx]}`}>
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-semibold text-slate-800">{scene.scene}</span>
          <Badge className="bg-white/80 text-slate-600 border-slate-200 text-[10px]">
            <Clock className="h-2.5 w-2.5 mr-1" />
            {scene.timing}
          </Badge>
        </div>
        <p className="text-xs text-slate-600">{scene.visual}</p>
        {scene.text_overlay && (
          <p className="text-[10px] text-slate-400 mt-1 flex items-center gap-1">
            <Camera className="h-2.5 w-2.5" /> Text: "{scene.text_overlay}"
          </p>
        )}
        {scene.audio && (
          <p className="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1">
            <Volume2 className="h-2.5 w-2.5" /> {scene.audio}
          </p>
        )}
        <p className="text-[10px] text-indigo-500 mt-1 italic">{scene.purpose}</p>
      </div>
    </div>
  );
}
