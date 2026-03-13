import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Loader2, Video, Sparkles, Play, Clock, Music, BarChart3,
  ChevronDown, ChevronUp, Wand2, Clapperboard,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const TYPE_CONFIG = {
  'Unboxing': { color: 'from-violet-500 to-indigo-500', icon: '📦' },
  'Problem/Solution': { color: 'from-rose-500 to-pink-500', icon: '💡' },
  'Curiosity Hook': { color: 'from-amber-500 to-orange-500', icon: '🔮' },
  'Transformation': { color: 'from-emerald-500 to-teal-500', icon: '✨' },
};

export default function AdCreativeGenerator({ productId, productName }) {
  const [creatives, setCreatives] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(null);

  const generate = async () => {
    if (creatives) { setCreatives(null); return; }
    setLoading(true);
    try {
      const res = await apiGet(`/api/ad-tests/ad-creatives/${productId}`);
      if (res.ok) {
        const data = await res.json();
        setCreatives(data.creatives || []);
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="ad-creative-generator">
      <CardHeader className="bg-gradient-to-r from-rose-600 via-pink-600 to-violet-600 text-white py-4">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Video className="h-5 w-5 text-rose-200" />
          AI Ad Creative Generator
        </CardTitle>
        <p className="text-xs text-rose-200 mt-1">
          GPT 5.2 generates 3 viral TikTok ad scripts for this product
        </p>
      </CardHeader>

      <CardContent className="p-5">
        <Button
          onClick={generate}
          disabled={loading}
          className="w-full bg-gradient-to-r from-rose-600 to-violet-600 hover:from-rose-700 hover:to-violet-700 text-white rounded-xl h-10 font-semibold"
          data-testid="generate-ads-btn"
        >
          {loading ? (
            <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Generating Ad Scripts...</>
          ) : creatives ? (
            <><ChevronUp className="h-4 w-4 mr-2" /> Hide Ad Scripts</>
          ) : (
            <><Wand2 className="h-4 w-4 mr-2" /> Generate 3 TikTok Ad Concepts</>
          )}
        </Button>

        {creatives && creatives.length > 0 && (
          <div className="mt-4 space-y-3 animate-in fade-in slide-in-from-bottom-2 duration-500" data-testid="ad-creatives-list">
            {creatives.map((ad, i) => {
              const cfg = TYPE_CONFIG[ad.type] || TYPE_CONFIG['Curiosity Hook'];
              const isExpanded = expanded === i;

              return (
                <div
                  key={i}
                  className="rounded-xl border border-slate-200 overflow-hidden hover:border-indigo-200 transition-colors"
                  data-testid={`ad-creative-${i}`}
                >
                  {/* Header */}
                  <button
                    onClick={() => setExpanded(isExpanded ? null : i)}
                    className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition-colors"
                  >
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${cfg.color} flex items-center justify-center flex-shrink-0 text-lg`}>
                      {cfg.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-900 text-sm">{ad.type}</span>
                        {ad.estimated_engagement && (
                          <Badge className={`text-[10px] rounded-full border-0 ${
                            ad.estimated_engagement === 'high' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                          }`}>
                            <BarChart3 className="h-2.5 w-2.5 mr-0.5" />{ad.estimated_engagement}
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 truncate mt-0.5">"{ad.hook}"</p>
                    </div>
                    {isExpanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
                  </button>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="px-4 pb-4 space-y-3 border-t border-slate-100 pt-3 animate-in slide-in-from-top-1 duration-200">
                      {/* Hook */}
                      <div className="p-3 bg-gradient-to-r from-indigo-50 to-violet-50 rounded-lg">
                        <p className="text-xs font-semibold text-indigo-700 mb-1 flex items-center gap-1">
                          <Sparkles className="h-3 w-3" /> Opening Hook
                        </p>
                        <p className="text-sm text-slate-800 font-medium italic">"{ad.hook}"</p>
                      </div>

                      {/* Scenes */}
                      <div className="space-y-2">
                        {(ad.scenes || []).map((scene) => (
                          <div key={scene.scene} className="flex items-start gap-3 p-2.5 bg-slate-50 rounded-lg">
                            <div className="w-7 h-7 rounded-full bg-white border border-slate-200 flex items-center justify-center flex-shrink-0">
                              <Play className="h-3 w-3 text-indigo-500" />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-semibold text-slate-600">Scene {scene.scene}</span>
                                <Badge className="text-[9px] bg-slate-100 text-slate-500 border-0 rounded-full">
                                  <Clock className="h-2 w-2 mr-0.5" />{scene.duration}
                                </Badge>
                              </div>
                              <p className="text-xs text-slate-700 mt-0.5">{scene.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Music */}
                      {ad.music_style && (
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                          <Music className="h-3.5 w-3.5" />
                          Music: <span className="text-slate-700 font-medium">{ad.music_style}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
