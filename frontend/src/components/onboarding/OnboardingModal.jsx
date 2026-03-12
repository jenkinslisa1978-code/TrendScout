/**
 * OnboardingModal Component
 * 
 * A 4-step interactive onboarding flow for new users.
 * Steps: Experience level → Niche preferences → First opportunity → First analysis
 * Goal: first value within 60 seconds.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  Trophy,
  Store,
  ChevronRight,
  ChevronLeft,
  X,
  Sparkles,
  Rocket,
  Package,
  Zap,
  Check
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { apiGet } from '@/lib/api';

const EXPERIENCE_LEVELS = [
  { id: 'beginner', label: 'Beginner', desc: "I'm new to dropshipping/ecommerce", icon: '🌱' },
  { id: 'intermediate', label: 'Intermediate', desc: "I've sold products before", icon: '📦' },
  { id: 'advanced', label: 'Advanced', desc: 'I run multiple stores', icon: '🚀' },
];

const NICHES = [
  'Health & Beauty', 'Home & Garden', 'Electronics', 'Fashion',
  'Sports & Outdoors', 'Pets', 'Kitchen', 'Baby & Kids',
  'Automotive', 'Office & School', 'Toys & Games', 'Jewellery',
];

export default function OnboardingModal({ isOpen, onClose }) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [step, setStep] = useState(0);
  const [experience, setExperience] = useState(null);
  const [selectedNiches, setSelectedNiches] = useState([]);
  const [featuredProduct, setFeaturedProduct] = useState(null);
  const [loadingProduct, setLoadingProduct] = useState(false);

  const totalSteps = 4;
  const progress = ((step + 1) / totalSteps) * 100;

  // Fetch a featured product for step 3
  useEffect(() => {
    if (step === 2 && !featuredProduct) {
      setLoadingProduct(true);
      (async () => {
        try {
          const res = await apiGet('/api/products?sortBy=launch_score&sortOrder=desc&limit=5');
          if (res.ok) {
            const data = await res.json();
            const products = data.data || [];
            // Pick one matching selected niches if possible
            const matched = products.find(p =>
              selectedNiches.some(n => (p.category || '').toLowerCase().includes(n.toLowerCase()))
            );
            setFeaturedProduct(matched || products[0] || null);
          }
        } catch { /* silent */ }
        setLoadingProduct(false);
      })();
    }
  }, [step]);

  const handleNext = () => {
    if (step < totalSteps - 1) setStep(s => s + 1);
    else completeOnboarding();
  };

  const handlePrev = () => {
    if (step > 0) setStep(s => s - 1);
  };

  const toggleNiche = (niche) => {
    setSelectedNiches(prev =>
      prev.includes(niche) ? prev.filter(n => n !== niche) : [...prev, niche]
    );
  };

  const completeOnboarding = async () => {
    try {
      await api.post('/api/user/complete-onboarding', {
        experience_level: experience,
        preferred_niches: selectedNiches,
      });
    } catch { /* silent */ }
    onClose();
  };

  const goToAnalysis = () => {
    completeOnboarding();
    if (featuredProduct) navigate(`/product/${featuredProduct.id}`);
    else navigate('/discover');
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent
        className="sm:max-w-lg p-0 gap-0 overflow-hidden"
        data-testid="onboarding-modal"
        onPointerDownOutside={(e) => e.preventDefault()}
        onEscapeKeyDown={(e) => e.preventDefault()}
      >
        <DialogTitle className="sr-only">TrendScout Onboarding</DialogTitle>
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-50 via-violet-50 to-fuchsia-50 px-6 pt-5 pb-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-indigo-600" />
              <span className="text-sm font-medium text-slate-600">
                Step {step + 1} of {totalSteps}
              </span>
            </div>
            <Button variant="ghost" size="sm" onClick={completeOnboarding} className="text-slate-400 hover:text-slate-600 h-8 px-2" data-testid="onboarding-skip-btn">
              Skip <X className="h-4 w-4 ml-1" />
            </Button>
          </div>
          <div className="h-1.5 bg-white/50 rounded-full overflow-hidden">
            <div className="h-full bg-indigo-600 transition-all duration-300 rounded-full" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {/* Step content */}
        <div className="px-6 py-6">
          {step === 0 && (
            <div data-testid="onboarding-step-experience">
              <div className="w-14 h-14 rounded-2xl bg-indigo-100 flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-7 w-7 text-indigo-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 text-center mb-1">Welcome to TrendScout</h2>
              <p className="text-sm text-slate-500 text-center mb-6">What's your ecommerce experience level?</p>
              <div className="space-y-2">
                {EXPERIENCE_LEVELS.map(lvl => (
                  <button
                    key={lvl.id}
                    onClick={() => setExperience(lvl.id)}
                    className={`w-full flex items-center gap-3 p-4 rounded-xl border-2 transition-all text-left ${
                      experience === lvl.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-slate-100 hover:border-slate-200 bg-white'
                    }`}
                    data-testid={`exp-${lvl.id}`}
                  >
                    <span className="text-2xl">{lvl.icon}</span>
                    <div>
                      <p className="font-semibold text-slate-800 text-sm">{lvl.label}</p>
                      <p className="text-xs text-slate-500">{lvl.desc}</p>
                    </div>
                    {experience === lvl.id && <Check className="h-5 w-5 text-indigo-600 ml-auto" />}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 1 && (
            <div data-testid="onboarding-step-niches">
              <div className="w-14 h-14 rounded-2xl bg-violet-100 flex items-center justify-center mx-auto mb-4">
                <Package className="h-7 w-7 text-violet-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 text-center mb-1">Pick your niches</h2>
              <p className="text-sm text-slate-500 text-center mb-5">Select categories you're interested in (pick 1-3)</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {NICHES.map(niche => (
                  <button
                    key={niche}
                    onClick={() => toggleNiche(niche)}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
                      selectedNiches.includes(niche)
                        ? 'bg-violet-600 text-white border-violet-600'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-violet-300'
                    }`}
                    data-testid={`niche-${niche.replace(/\s+/g, '-').toLowerCase()}`}
                  >
                    {niche}
                  </button>
                ))}
              </div>
              {selectedNiches.length > 0 && (
                <p className="text-xs text-violet-600 text-center mt-3 font-medium">
                  {selectedNiches.length} selected — we'll prioritise these in your feed
                </p>
              )}
            </div>
          )}

          {step === 2 && (
            <div data-testid="onboarding-step-opportunity">
              <div className="w-14 h-14 rounded-2xl bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                <Trophy className="h-7 w-7 text-emerald-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 text-center mb-1">Your first opportunity</h2>
              <p className="text-sm text-slate-500 text-center mb-5">TrendScout already found this for you</p>
              {loadingProduct ? (
                <div className="p-8 text-center">
                  <div className="inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : featuredProduct ? (
                <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                  <div className="flex items-start gap-3">
                    <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-100 to-violet-100 flex items-center justify-center flex-shrink-0">
                      {featuredProduct.image_url ? (
                        <img src={featuredProduct.image_url} alt="" className="w-full h-full rounded-xl object-cover" onError={(e) => { e.target.style.display = 'none'; }} />
                      ) : (
                        <Package className="h-6 w-6 text-indigo-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-slate-900 text-sm truncate">{featuredProduct.product_name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-[10px]">{featuredProduct.category}</Badge>
                        <Badge className="bg-amber-100 text-amber-700 border-amber-200 text-[10px]">{featuredProduct.early_trend_label || featuredProduct.trend_stage}</Badge>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 mt-4">
                    <div className="bg-white rounded-xl p-2.5 text-center">
                      <p className="text-lg font-bold text-indigo-600 font-mono">{featuredProduct.launch_score || featuredProduct.trend_score || '—'}</p>
                      <p className="text-[10px] text-slate-400">Launch Score</p>
                    </div>
                    <div className="bg-white rounded-xl p-2.5 text-center">
                      <p className="text-lg font-bold text-emerald-600 font-mono">{featuredProduct.success_probability || '—'}%</p>
                      <p className="text-[10px] text-slate-400">Success</p>
                    </div>
                    <div className="bg-white rounded-xl p-2.5 text-center">
                      <p className="text-lg font-bold text-amber-600 font-mono">£{(featuredProduct.estimated_margin || 0).toFixed(0)}</p>
                      <p className="text-[10px] text-slate-400">Margin</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400">
                  <Package className="h-12 w-12 mx-auto mb-2 opacity-30" />
                  <p className="text-sm">Products are being loaded...</p>
                </div>
              )}
            </div>
          )}

          {step === 3 && (
            <div data-testid="onboarding-step-analyze">
              <div className="w-14 h-14 rounded-2xl bg-rose-100 flex items-center justify-center mx-auto mb-4">
                <Zap className="h-7 w-7 text-rose-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 text-center mb-1">Run your first analysis</h2>
              <p className="text-sm text-slate-500 text-center mb-5">Click below to dive deep into this product's potential</p>
              <div className="space-y-3">
                {[
                  { label: 'View detailed product intelligence', icon: TrendingUp },
                  { label: 'See supplier costs and profit margins', icon: Store },
                  { label: 'Generate ad creatives with AI', icon: Sparkles },
                ].map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <div key={i} className="flex items-center gap-3 bg-slate-50 rounded-lg px-4 py-2.5">
                      <div className="w-7 h-7 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
                        <Icon className="h-3.5 w-3.5 text-indigo-600" />
                      </div>
                      <span className="text-sm text-slate-700">{item.label}</span>
                    </div>
                  );
                })}
              </div>
              <Button onClick={goToAnalysis} className="w-full mt-6 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700" data-testid="onboarding-analyze-btn">
                <Rocket className="mr-2 h-4 w-4" />
                {featuredProduct ? 'Analyze This Product' : 'Browse Products'}
              </Button>
            </div>
          )}
        </div>

        {/* Footer navigation */}
        <div className="px-6 pb-5 flex items-center justify-between">
          <Button variant="outline" onClick={handlePrev} disabled={step === 0} className={step === 0 ? 'invisible' : ''} data-testid="onboarding-prev-btn">
            <ChevronLeft className="h-4 w-4 mr-1" /> Back
          </Button>
          {step < 3 && (
            <Button onClick={handleNext} className="bg-indigo-600 hover:bg-indigo-700 text-white min-w-[100px]" disabled={step === 0 && !experience} data-testid="onboarding-next-btn">
              Next <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          )}
        </div>

        {/* Step dots */}
        <div className="flex justify-center gap-1.5 pb-4">
          {Array.from({ length: totalSteps }).map((_, idx) => (
            <div key={idx} className={`h-2 rounded-full transition-all ${idx === step ? 'w-6 bg-indigo-600' : 'w-2 bg-slate-200'}`} data-testid={`onboarding-dot-${idx}`} />
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
