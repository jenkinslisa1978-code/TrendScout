import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Sparkles, Clock, Target, Video, Store, Layers,
  Calculator, ArrowRight, X, Zap, Gift, CheckCircle2,
} from 'lucide-react';
import api from '@/lib/api';
import { useSubscription } from '@/hooks/useSubscription';
import { toast } from 'sonner';

const FEATURE_OPTIONS = [
  { id: 'ad_intelligence', label: 'Ad Intelligence', icon: Target, desc: 'Search & analyze competitor ads', color: 'from-blue-500 to-indigo-600' },
  { id: 'tiktok_intel', label: 'TikTok Intelligence', icon: Video, desc: 'Full viral rankings & patterns', color: 'from-pink-500 to-rose-600' },
  { id: 'competitor_intel', label: 'Competitor Intel', icon: Store, desc: 'Deep-analyse Shopify stores', color: 'from-emerald-500 to-teal-600' },
  { id: 'product_deep_dive', label: 'Product Deep Dive', icon: Layers, desc: 'Saturation, ad patterns & more', color: 'from-violet-500 to-purple-600' },
  { id: 'profit_simulator', label: 'Profit Simulator', icon: Calculator, desc: 'Unlimited profit simulations', color: 'from-amber-500 to-orange-600' },
];

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export default function TrialBanner() {
  const { isFree, trial, hasActiveTrial, refresh } = useSubscription();
  const navigate = useNavigate();
  const [trialStatus, setTrialStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activating, setActivating] = useState(false);
  const [showPicker, setShowPicker] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const [countdown, setCountdown] = useState(0);

  const fetchTrialStatus = useCallback(async () => {
    try {
      const res = await api.get('/api/trial/status');
      if (res.data) setTrialStatus(res.data);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => {
    if (isFree) fetchTrialStatus();
    else setLoading(false);
  }, [isFree, fetchTrialStatus]);

  // Countdown timer for active trial
  useEffect(() => {
    if (!trialStatus?.active_trial?.remaining_seconds) return;
    setCountdown(trialStatus.active_trial.remaining_seconds);
    const interval = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) { clearInterval(interval); return 0; }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [trialStatus]);

  const activateTrial = async (featureId) => {
    setActivating(true);
    try {
      const res = await api.post('/api/trial/activate', { feature: featureId });
      if (res.ok && res.data.success) {
        toast.success(res.data.message);
        setShowPicker(false);
        await fetchTrialStatus();
        await refresh(); // Refresh subscription to pick up trial unlocks
      } else {
        toast.error(res.data?.detail || 'Could not activate trial');
      }
    } catch (e) {
      toast.error('Failed to activate trial');
    }
    setActivating(false);
  };

  if (!isFree || loading || dismissed) return null;

  // Trial expired
  if (trialStatus?.reason === 'trial_expired') {
    return (
      <Card className="border-0 shadow-lg bg-gradient-to-r from-slate-800 to-slate-900 text-white relative overflow-hidden" data-testid="trial-expired-banner">
        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full -translate-y-8 translate-x-8" />
        <CardContent className="py-4 flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
            <Gift className="h-5 w-5 text-indigo-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-sm">Your free trial has ended</p>
            <p className="text-xs text-slate-400">Upgrade now to keep access to premium features.</p>
          </div>
          <Button onClick={() => navigate('/pricing')} size="sm" className="bg-indigo-600 hover:bg-indigo-500 text-white flex-shrink-0">
            View Plans <ArrowRight className="h-3.5 w-3.5 ml-1" />
          </Button>
          <button onClick={() => setDismissed(true)} className="text-slate-500 hover:text-slate-300 p-1">
            <X className="h-4 w-4" />
          </button>
        </CardContent>
      </Card>
    );
  }

  // Active trial
  if (trialStatus?.reason === 'trial_active' && trialStatus.active_trial) {
    const t = trialStatus.active_trial;
    return (
      <Card className="border-0 shadow-lg bg-gradient-to-r from-indigo-600 to-violet-600 text-white relative overflow-hidden" data-testid="trial-active-banner">
        <div className="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full -translate-y-12 translate-x-12" />
        <CardContent className="py-4 flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-white/15 flex items-center justify-center flex-shrink-0 animate-pulse">
            <Zap className="h-5 w-5 text-amber-300" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <p className="font-bold text-sm">Trial Active</p>
              <Badge className="bg-white/20 text-white border-0 text-[10px]">
                {t.feature_label}
              </Badge>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-indigo-200 flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {countdown > 0 ? formatTime(countdown) : 'Expiring...'} remaining
              </span>
              <span className="text-xs text-indigo-200 flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" />
                Full access unlocked
              </span>
            </div>
          </div>
          <Button onClick={() => navigate('/pricing')} size="sm" variant="secondary" className="bg-white/15 hover:bg-white/25 text-white border-0 flex-shrink-0">
            Upgrade to Keep <ArrowRight className="h-3.5 w-3.5 ml-1" />
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Eligible — never used trial
  if (trialStatus?.eligible) {
    return (
      <>
        <Card className="border-0 shadow-lg bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 text-white relative overflow-hidden cursor-pointer group" onClick={() => setShowPicker(true)} data-testid="trial-eligible-banner">
          <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 rounded-full -translate-y-16 translate-x-16 group-hover:scale-110 transition-transform" />
          <CardContent className="py-4 flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
              <Gift className="h-5 w-5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm">Unlock a Premium Feature — Free for 24 Hours</p>
              <p className="text-xs text-white/80">Choose one feature to try at full power. No card required.</p>
            </div>
            <Button size="sm" className="bg-white text-orange-600 hover:bg-orange-50 font-semibold flex-shrink-0">
              <Sparkles className="h-3.5 w-3.5 mr-1" /> Choose Feature
            </Button>
          </CardContent>
        </Card>

        {/* Feature picker modal */}
        {showPicker && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowPicker(false)}>
            <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 relative" onClick={e => e.stopPropagation()} data-testid="trial-feature-picker">
              <button onClick={() => setShowPicker(false)} className="absolute top-3 right-3 text-slate-400 hover:text-slate-600">
                <X className="h-5 w-5" />
              </button>
              <div className="text-center mb-5">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-amber-400 to-rose-400 flex items-center justify-center mx-auto mb-3">
                  <Gift className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-lg font-bold text-slate-900">Choose Your Free Trial Feature</h2>
                <p className="text-sm text-slate-500 mt-1">Pick one premium feature to unlock for 24 hours.</p>
              </div>
              <div className="space-y-2">
                {FEATURE_OPTIONS.map(opt => {
                  const Icon = opt.icon;
                  return (
                    <button
                      key={opt.id}
                      onClick={() => !activating && activateTrial(opt.id)}
                      disabled={activating}
                      className="w-full flex items-center gap-3 p-3 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 transition-all group text-left disabled:opacity-50"
                      data-testid={`trial-option-${opt.id}`}
                    >
                      <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${opt.color} flex items-center justify-center flex-shrink-0`}>
                        <Icon className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-slate-800 group-hover:text-indigo-600 transition-colors">{opt.label}</p>
                        <p className="text-xs text-slate-500">{opt.desc}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-indigo-500 transition-colors flex-shrink-0" />
                    </button>
                  );
                })}
              </div>
              <p className="text-[10px] text-slate-400 text-center mt-4">
                One trial per account. Feature unlocks for 24 hours from activation.
              </p>
            </div>
          </div>
        )}
      </>
    );
  }

  return null;
}
