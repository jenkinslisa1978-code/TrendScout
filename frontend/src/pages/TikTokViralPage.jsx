import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import PageMeta from '@/components/PageMeta';
import { useAuth } from '@/contexts/AuthContext';
import { apiGet, apiPost } from '@/lib/api';
import { toast } from 'sonner';
import {
  Loader2, Lock, ArrowRight, TrendingUp, Zap, Flame,
  Clock, Eye, Target, Hash, Video, Sparkles, RefreshCw,
  PoundSterling, Users, BarChart3, AlertTriangle,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const URGENCY_CONFIG = {
  high: { color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/25', label: 'Act now' },
  medium: { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/25', label: '24-48h window' },
  low: { color: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-sky-500/25', label: '48-72h window' },
};

const CONFIDENCE_CONFIG = {
  high: { color: 'text-emerald-400', icon: Flame },
  medium: { color: 'text-amber-400', icon: TrendingUp },
  low: { color: 'text-zinc-400', icon: BarChart3 },
};

export default function TikTokViralPage() {
  const [predictions, setPredictions] = useState([]);
  const [totalAvailable, setTotalAvailable] = useState(0);
  const [generatedAt, setGeneratedAt] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { isAuthenticated } = useAuth();

  useEffect(() => { loadPredictions(); }, [isAuthenticated]);

  const loadPredictions = async () => {
    setLoading(true);
    try {
      if (isAuthenticated) {
        const res = await apiGet('/api/viral-predictions');
        if (res.ok) {
          const data = await res.json();
          setPredictions(data.predictions || []);
          setTotalAvailable(data.predictions?.length || 0);
          setGeneratedAt(data.generated_at || '');
        }
      } else {
        const res = await fetch(`${API_URL}/api/public/viral-predictions`);
        if (res.ok) {
          const data = await res.json();
          setPredictions(data.predictions || []);
          setTotalAvailable(data.total_available || 0);
          setGeneratedAt(data.generated_at || '');
        }
      }
    } catch {}
    setLoading(false);
  };

  const refresh = async () => {
    setRefreshing(true);
    try {
      const res = await apiPost('/api/viral-predictions/refresh');
      if (res.ok) {
        const data = await res.json();
        setPredictions(data.predictions || []);
        setGeneratedAt(data.generated_at || '');
        toast.success(`${data.count} new predictions generated`);
      }
    } catch { toast.error('Refresh failed'); }
    setRefreshing(false);
  };

  const freeLimit = isAuthenticated ? predictions.length : 3;
  const lockedCount = totalAvailable - freeLimit;

  return (
    <LandingLayout>
      <PageMeta
        title="TikTok Viral Predictor — Products About to Trend | TrendScout"
        description="AI predicts which products will go viral on TikTok in the next 48-72 hours. Get ahead of trends before your competitors."
      />

      <div className="bg-[#09090b] min-h-screen">
        <div className="mx-auto max-w-5xl px-6 pt-16 pb-20 lg:pt-20" data-testid="viral-predictor-page">
          {/* Header */}
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 rounded-full bg-red-500/10 border border-red-500/20 px-3.5 py-1.5 mb-4">
              <Flame className="h-3.5 w-3.5 text-red-400" />
              <span className="text-xs font-bold text-red-400 tracking-[0.15em] uppercase">AI Trend Predictions</span>
            </div>
            <h1 className="font-manrope text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tighter">
              Products about to <span className="bg-gradient-to-r from-red-400 via-pink-400 to-violet-400 bg-clip-text text-transparent">go viral on TikTok</span>
            </h1>
            <p className="mt-3 text-base text-zinc-500 max-w-xl mx-auto">
              AI analyses product data, TikTok trends, and UK buyer behaviour to predict which products will explode in the next 48-72 hours.
            </p>
            {generatedAt && (
              <p className="mt-2 text-xs text-zinc-600 flex items-center justify-center gap-1.5">
                <Clock className="h-3 w-3" /> Last updated: {new Date(generatedAt).toLocaleString('en-GB')}
                {isAuthenticated && (
                  <button onClick={refresh} disabled={refreshing} className="ml-2 text-emerald-500 hover:text-emerald-400 transition-colors">
                    <RefreshCw className={`h-3 w-3 ${refreshing ? 'animate-spin' : ''}`} />
                  </button>
                )}
              </p>
            )}
          </div>

          {/* Loading */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 gap-4">
              <div className="relative">
                <div className="absolute inset-0 rounded-full bg-red-400/20 animate-ping" />
                <div className="relative w-14 h-14 rounded-full bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center">
                  <Flame className="h-6 w-6 text-white" />
                </div>
              </div>
              <p className="text-sm text-zinc-400">Analysing trends...</p>
            </div>
          )}

          {/* Predictions */}
          {!loading && predictions.length > 0 && (
            <div className="space-y-4">
              {predictions.map((pred, idx) => (
                <PredictionCard key={pred.id || idx} prediction={pred} rank={idx + 1} />
              ))}

              {/* Locked teaser */}
              {!isAuthenticated && lockedCount > 0 && (
                <div className="relative">
                  {/* Blurred preview cards */}
                  {[1, 2].map(i => (
                    <div key={i} className="rounded-xl border border-white/[0.06] bg-[#18181b] p-6 mb-3 blur-sm opacity-40">
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-xl bg-zinc-800" />
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-zinc-800 rounded w-2/3" />
                          <div className="h-3 bg-zinc-800 rounded w-1/3" />
                        </div>
                        <div className="h-10 w-10 rounded-full bg-zinc-800" />
                      </div>
                    </div>
                  ))}

                  {/* Overlay CTA */}
                  <div className="absolute inset-0 flex items-center justify-center" data-testid="viral-upgrade-overlay">
                    <div className="text-center bg-[#09090b]/90 backdrop-blur-sm rounded-2xl border border-emerald-500/20 p-8 max-w-sm">
                      <Lock className="h-8 w-8 text-emerald-400 mx-auto mb-3" />
                      <p className="text-lg font-bold text-white mb-1">{lockedCount} more predictions</p>
                      <p className="text-sm text-zinc-500 mb-5">Get the full list, TikTok ad scripts, hashtags, and alert notifications</p>
                      <Link to="/signup">
                        <Button className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold tracking-wide px-8 rounded-lg shadow-[0_0_20px_rgba(16,185,129,0.35)]" data-testid="viral-signup-cta">
                          Unlock All Predictions <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {!loading && predictions.length === 0 && (
            <div className="text-center py-20">
              <Flame className="h-12 w-12 text-zinc-700 mx-auto mb-4" />
              <p className="text-sm text-zinc-500">No predictions available yet. Check back soon — AI is analysing the latest trends.</p>
            </div>
          )}

          {/* How it works */}
          <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-5">
            {[
              { icon: BarChart3, color: 'text-violet-400', title: 'Data-driven signals', desc: 'AI analyses product scores, pricing, margins, and historical trend velocity across our database.' },
              { icon: Video, color: 'text-pink-400', title: 'TikTok format matching', desc: 'Products are matched to trending TikTok formats: GRWM, hauls, satisfying, life hacks, before/after.' },
              { icon: Target, color: 'text-emerald-400', title: 'UK audience targeting', desc: 'Predictions are tuned for UK buyer behaviour, price sensitivity, and cultural preferences.' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="rounded-xl bg-[#18181b] border border-white/[0.08] p-6 text-center">
                  <Icon className={`h-6 w-6 ${item.color} mx-auto mb-3`} />
                  <h3 className="font-manrope text-sm font-bold text-white mb-1">{item.title}</h3>
                  <p className="text-xs text-zinc-500 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </LandingLayout>
  );
}

function PredictionCard({ prediction: p, rank }) {
  const urgency = URGENCY_CONFIG[p.urgency] || URGENCY_CONFIG.medium;
  const confidence = CONFIDENCE_CONFIG[p.confidence] || CONFIDENCE_CONFIG.medium;
  const ConfIcon = confidence.icon;

  return (
    <div
      className="rounded-xl border border-white/[0.08] bg-[#18181b] p-5 hover:border-white/[0.15] hover:shadow-[0_4px_20px_rgba(255,255,255,0.03)] transition-all group"
      data-testid={`prediction-card-${rank}`}
    >
      <div className="flex items-start gap-4">
        {/* Rank */}
        <div className="flex flex-col items-center gap-1 shrink-0">
          <span className={`text-2xl font-extrabold font-mono ${rank <= 3 ? 'text-red-400' : 'text-zinc-600'}`}>
            #{rank}
          </span>
          <ConfIcon className={`h-4 w-4 ${confidence.color}`} />
        </div>

        {/* Image */}
        {p.image_url ? (
          <img src={p.image_url} alt="" className="h-20 w-20 rounded-xl object-cover border border-white/[0.08] shrink-0" />
        ) : (
          <div className="h-20 w-20 rounded-xl bg-[#121214] border border-white/[0.06] flex items-center justify-center shrink-0">
            <Video className="h-6 w-6 text-zinc-700" />
          </div>
        )}

        {/* Main content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h3 className="text-sm font-bold text-white truncate">{p.product_name}</h3>
            {p.category && <Badge className="bg-white/[0.05] text-zinc-500 border-white/[0.08] text-[10px]">{p.category}</Badge>}
          </div>

          {/* Urgency + confidence */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${urgency.bg} ${urgency.color} border ${urgency.border}`}>
              <Clock className="h-2.5 w-2.5" /> {urgency.label}
            </span>
            <span className={`text-[10px] font-bold ${confidence.color}`}>
              {p.confidence} confidence
            </span>
            {p.estimated_views && (
              <span className="inline-flex items-center gap-1 text-[10px] text-zinc-500">
                <Eye className="h-2.5 w-2.5" /> {p.estimated_views} est. views
              </span>
            )}
          </div>

          {/* Reasoning */}
          <p className="text-xs text-zinc-400 leading-relaxed mb-3">{p.reasoning}</p>

          {/* TikTok details */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {p.tiktok_format && (
              <div className="flex items-start gap-2 text-xs">
                <Video className="h-3.5 w-3.5 text-pink-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-zinc-600">Format:</span>
                  <span className="text-zinc-300 ml-1">{p.tiktok_format}</span>
                </div>
              </div>
            )}
            {p.hook_idea && (
              <div className="flex items-start gap-2 text-xs">
                <Zap className="h-3.5 w-3.5 text-amber-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-zinc-600">Hook:</span>
                  <span className="text-zinc-300 ml-1">"{p.hook_idea}"</span>
                </div>
              </div>
            )}
            {p.target_demographic && (
              <div className="flex items-start gap-2 text-xs">
                <Users className="h-3.5 w-3.5 text-violet-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-zinc-600">Audience:</span>
                  <span className="text-zinc-300 ml-1">{p.target_demographic}</span>
                </div>
              </div>
            )}
            {p.ad_budget_suggestion && (
              <div className="flex items-start gap-2 text-xs">
                <PoundSterling className="h-3.5 w-3.5 text-emerald-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-zinc-600">Budget:</span>
                  <span className="text-zinc-300 ml-1">{p.ad_budget_suggestion}</span>
                </div>
              </div>
            )}
          </div>

          {/* Hashtags */}
          {p.hashtags && p.hashtags.length > 0 && (
            <div className="flex items-center gap-1.5 mt-2 flex-wrap">
              <Hash className="h-3 w-3 text-zinc-600 shrink-0" />
              {p.hashtags.map((tag, i) => (
                <span key={i} className="text-[10px] text-sky-400">{tag}</span>
              ))}
            </div>
          )}
        </div>

        {/* Viral score */}
        <div className="text-center shrink-0">
          <div className={`text-2xl font-extrabold font-mono ${
            p.viral_score >= 80 ? 'text-red-400' : p.viral_score >= 60 ? 'text-amber-400' : 'text-zinc-400'
          }`} data-testid={`viral-score-${rank}`}>
            {p.viral_score}
          </div>
          <p className="text-[10px] text-zinc-600">viral score</p>
        </div>
      </div>
    </div>
  );
}
