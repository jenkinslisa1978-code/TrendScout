import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Sparkles, Video, Facebook, Instagram, Target, Type, 
  Film, Camera, Mic, Loader2, RefreshCw, Copy, Check, ChevronDown, ChevronUp
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={handleCopy} className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-600 transition-colors" title="Copy">
      {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
    </button>
  );
}

function Collapsible({ title, icon: Icon, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-slate-200 rounded-lg">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between p-3 hover:bg-slate-50 transition-colors">
        <span className="flex items-center gap-2 text-sm font-semibold text-slate-800">
          {Icon && <Icon className="h-4 w-4 text-indigo-500" />}
          {title}
        </span>
        {open ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
      </button>
      {open && <div className="p-3 pt-0 border-t border-slate-100">{children}</div>}
    </div>
  );
}

export default function AdCreativeSection({ productId }) {
  const [creatives, setCreatives] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const fetchCreatives = useCallback(async () => {
    try {
      const token = localStorage.getItem('trendscout_token');
      const res = await fetch(`${API_URL}/api/ad-creatives/${productId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.creatives && data.success !== false) {
        setCreatives(data);
      }
    } catch (err) {
      console.error('Failed to fetch creatives:', err);
    }
  }, [productId]);

  useEffect(() => { fetchCreatives(); }, [fetchCreatives]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const token = localStorage.getItem('trendscout_token');
      const res = await fetch(`${API_URL}/api/ad-creatives/generate/${productId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setCreatives(data);
        toast.success('Ad creatives generated!');
      } else {
        toast.error(data.error || 'Generation failed');
      }
    } catch (err) {
      toast.error('Failed to generate creatives');
    } finally {
      setGenerating(false);
    }
  };

  const c = creatives?.creatives;

  if (!c) {
    return (
      <Card className="border-slate-200 shadow-sm" data-testid="ad-creative-section">
        <CardContent className="p-8 text-center">
          <Sparkles className="h-8 w-8 mx-auto mb-3 text-indigo-400" />
          <h3 className="text-base font-semibold text-slate-900 mb-1">AI Ad Creatives</h3>
          <p className="text-sm text-slate-500 mb-4">Generate TikTok scripts, Facebook ads, Instagram captions, and more</p>
          <Button onClick={handleGenerate} disabled={generating} data-testid="generate-creatives-btn" className="bg-indigo-600 hover:bg-indigo-700 text-white">
            {generating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Generating...</> : <><Sparkles className="mr-2 h-4 w-4" />Generate Ad Creatives</>}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-200 shadow-sm" data-testid="ad-creative-section">
      <CardHeader className="border-b border-slate-100 pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="font-manrope text-lg font-semibold text-slate-900 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-500" />
            AI Ad Creatives
            <Badge variant="outline" className="text-xs text-emerald-600 border-emerald-200">Generated</Badge>
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={handleGenerate} disabled={generating} data-testid="regenerate-creatives-btn">
            {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            <span className="ml-1">Regenerate</span>
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <Tabs defaultValue="tiktok" className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-4">
            <TabsTrigger value="tiktok" className="text-xs" data-testid="tab-tiktok"><Video className="h-3.5 w-3.5 mr-1" />TikTok</TabsTrigger>
            <TabsTrigger value="facebook" className="text-xs" data-testid="tab-facebook"><Facebook className="h-3.5 w-3.5 mr-1" />Facebook</TabsTrigger>
            <TabsTrigger value="instagram" className="text-xs" data-testid="tab-instagram"><Instagram className="h-3.5 w-3.5 mr-1" />Instagram</TabsTrigger>
            <TabsTrigger value="video" className="text-xs" data-testid="tab-video"><Film className="h-3.5 w-3.5 mr-1" />Video</TabsTrigger>
            <TabsTrigger value="strategy" className="text-xs" data-testid="tab-strategy"><Target className="h-3.5 w-3.5 mr-1" />Strategy</TabsTrigger>
          </TabsList>

          {/* TikTok Tab */}
          <TabsContent value="tiktok" className="space-y-3" data-testid="tiktok-content">
            {(c.tiktok_scripts || []).map((script, i) => (
              <div key={i} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-slate-900">{script.title || `Script ${i + 1}`}</h4>
                  <CopyButton text={`Hook: ${script.hook}\n\n${script.script}\n\nCTA: ${script.cta}`} />
                </div>
                <div className="space-y-2">
                  <div>
                    <span className="text-xs font-medium text-rose-600 uppercase">Hook (first 3 seconds)</span>
                    <p className="text-sm text-slate-800 mt-0.5 font-medium">{script.hook}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-slate-500 uppercase">Script</span>
                    <p className="text-sm text-slate-700 mt-0.5 whitespace-pre-line">{script.script}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-emerald-600 uppercase">CTA</span>
                    <p className="text-sm text-slate-800 mt-0.5 font-medium">{script.cta}</p>
                  </div>
                </div>
              </div>
            ))}
          </TabsContent>

          {/* Facebook Tab */}
          <TabsContent value="facebook" className="space-y-3" data-testid="facebook-content">
            {(c.facebook_ads || []).map((ad, i) => (
              <div key={i} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-slate-900">{ad.headline}</h4>
                  <CopyButton text={`${ad.headline}\n\n${ad.primary_text}\n\n${ad.description}`} />
                </div>
                <p className="text-sm text-slate-700 whitespace-pre-line mb-2">{ad.primary_text}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="outline" className="text-xs">{ad.description}</Badge>
                  <Badge className="bg-blue-600 text-white text-xs">{ad.cta_button}</Badge>
                </div>
              </div>
            ))}
          </TabsContent>

          {/* Instagram Tab */}
          <TabsContent value="instagram" className="space-y-3" data-testid="instagram-content">
            {(c.instagram_captions || []).map((cap, i) => (
              <div key={i} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                <div className="flex items-end justify-between mb-1">
                  <span className="text-xs font-medium text-purple-600 uppercase">Caption {i + 1}</span>
                  <CopyButton text={cap.caption} />
                </div>
                <p className="text-sm text-slate-700 whitespace-pre-line">{cap.caption}</p>
                {cap.hashtags && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {cap.hashtags.map((tag, j) => (
                      <Badge key={j} variant="outline" className="text-xs text-blue-600">#{tag}</Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </TabsContent>

          {/* Video Tab */}
          <TabsContent value="video" className="space-y-3" data-testid="video-content">
            <Collapsible title="Video Storyboard" icon={Film} defaultOpen={true}>
              <div className="space-y-2 mt-2">
                {(c.video_storyboard || []).map((scene, i) => (
                  <div key={i} className="flex gap-3 p-2 rounded bg-white border border-slate-100">
                    <div className="flex-shrink-0 w-16 text-center">
                      <div className="text-xs font-bold text-indigo-600">Scene {scene.scene}</div>
                      <div className="text-xs text-slate-400">{scene.duration}</div>
                    </div>
                    <div className="flex-1 text-xs text-slate-700">
                      <p><span className="font-medium">Visual:</span> {scene.visual}</p>
                      {scene.text_overlay && <p><span className="font-medium">Text:</span> {scene.text_overlay}</p>}
                      {scene.audio && <p><span className="font-medium">Audio:</span> {scene.audio}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </Collapsible>

            <Collapsible title="Shot List" icon={Camera}>
              <div className="space-y-2 mt-2">
                {(c.shot_list || []).map((shot, i) => (
                  <div key={i} className="flex gap-3 p-2 rounded bg-white border border-slate-100">
                    <Badge variant="outline" className="text-xs flex-shrink-0">{shot.type}</Badge>
                    <div className="text-xs text-slate-700">
                      <p className="font-medium">{shot.description}</p>
                      <p className="text-slate-400 mt-0.5">{shot.purpose}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Collapsible>

            <Collapsible title="Voiceover Script" icon={Mic}>
              <div className="mt-2 p-3 bg-white border border-slate-100 rounded">
                <div className="flex justify-end mb-1"><CopyButton text={c.voiceover_script || ''} /></div>
                <p className="text-sm text-slate-700 whitespace-pre-line">{c.voiceover_script}</p>
              </div>
            </Collapsible>
          </TabsContent>

          {/* Strategy Tab */}
          <TabsContent value="strategy" className="space-y-3" data-testid="strategy-content">
            <div>
              <h4 className="text-sm font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <Target className="h-4 w-4 text-indigo-500" /> Product Angles
              </h4>
              <div className="space-y-2">
                {(c.product_angles || []).map((angle, i) => (
                  <div key={i} className="border border-slate-200 rounded-lg p-3 bg-slate-50">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-slate-900">{angle.angle}</span>
                      <Badge variant="outline" className="text-xs">{angle.target_audience}</Badge>
                    </div>
                    <p className="text-xs text-slate-600 mt-1">{angle.hook}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <Type className="h-4 w-4 text-indigo-500" /> Headline Variations
              </h4>
              <div className="space-y-1">
                {(c.headlines || []).map((h, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-100">
                    <span className="text-sm text-slate-800">{h}</span>
                    <CopyButton text={h} />
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
