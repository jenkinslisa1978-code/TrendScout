import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
  Rocket, Store, Megaphone, ArrowRight, ArrowLeft,
  CheckCircle2, Sparkles, ChevronRight,
} from 'lucide-react';

const COLOR_MAP = {
  indigo: {
    gradient: 'bg-gradient-to-br from-indigo-600 to-indigo-700',
    btn: 'bg-indigo-600 hover:bg-indigo-700',
  },
  emerald: {
    gradient: 'bg-gradient-to-br from-emerald-600 to-emerald-700',
    btn: 'bg-emerald-600 hover:bg-emerald-700',
  },
  purple: {
    gradient: 'bg-gradient-to-br from-purple-600 to-purple-700',
    btn: 'bg-purple-600 hover:bg-purple-700',
  },
};

const STEPS = [
  {
    id: 'welcome',
    icon: Sparkles,
    title: 'Welcome to TrendScout',
    subtitle: 'Your AI-powered e-commerce launchpad',
    body: 'TrendScout finds winning products, sets up your shop, and creates professional ads — all at the touch of a button.',
    bullets: [
      'AI scans thousands of products to find the best ones to sell',
      'One click to publish products to your Shopify or WooCommerce store',
      'Professional ad campaigns created and posted automatically',
    ],
    color: 'indigo',
  },
  {
    id: 'connect-store',
    icon: Store,
    title: 'Step 1: Connect Your Store',
    subtitle: 'Link your online shop so we can publish products for you',
    body: "If you have a Shopify, WooCommerce, Etsy, or BigCommerce store, connect it now. Don't have one yet? Shopify offers a free trial — you can set one up in minutes.",
    bullets: [
      'Go to Connections in the sidebar',
      'Click "Connect" on your platform (e.g., Shopify)',
      'Enter your store URL and API access token',
      'That\'s it — products will auto-publish to your store',
    ],
    action: '/settings/connections',
    actionLabel: 'Connect My Store',
    color: 'emerald',
  },
  {
    id: 'connect-ads',
    icon: Megaphone,
    title: 'Step 2: Connect Your Ad Accounts (Optional)',
    subtitle: 'Link your ad platforms to auto-post campaigns',
    body: 'Connect your Meta (Facebook/Instagram), TikTok, or Google ad accounts. TrendScout will create high-quality ad campaigns and post them for you. Or skip this — you can always create your own ads.',
    bullets: [
      'Meta: Need a Business account and ad account ID',
      'TikTok: Need a TikTok for Business account',
      'Google: Need a Google Ads account',
      'All campaigns start PAUSED so you review before spending',
    ],
    action: '/settings/connections',
    actionLabel: 'Connect Ad Accounts',
    color: 'purple',
  },
  {
    id: 'quick-launch',
    icon: Rocket,
    title: 'Step 3: Launch in 3 Clicks',
    subtitle: 'Pick a product, set up shop, create ads — done',
    body: "Your dashboard shows a 'Quick Launch' widget with our #1 recommended product. Just click through the 3 steps and you're live.",
    bullets: [
      'Click "Pick This" on the recommended product',
      'Click "Create Shop" — publishes to your connected store',
      'Click "Make Ads" — creates campaigns on your connected platforms',
      'Or click "Skip, I\'ll do my own" if you prefer to create ads yourself',
    ],
    action: '/dashboard',
    actionLabel: 'Go to Dashboard',
    color: 'indigo',
  },
];

export default function OnboardingWalkthrough({ onComplete }) {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [open, setOpen] = useState(true);

  const step = STEPS[currentStep];
  const colors = COLOR_MAP[step.color] || COLOR_MAP.indigo;
  const isLast = currentStep === STEPS.length - 1;
  const isFirst = currentStep === 0;
  const StepIcon = step.icon;

  const handleNext = () => {
    if (isLast) {
      setOpen(false);
      localStorage.setItem('trendscout_onboarding_complete', 'true');
      if (onComplete) onComplete();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleAction = () => {
    setOpen(false);
    localStorage.setItem('trendscout_onboarding_complete', 'true');
    if (onComplete) onComplete();
    if (step.action) navigate(step.action);
  };

  const handleSkip = () => {
    setOpen(false);
    localStorage.setItem('trendscout_onboarding_complete', 'true');
    if (onComplete) onComplete();
  };

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) handleSkip(); }}>
      <DialogContent className="sm:max-w-lg p-0 overflow-hidden" data-testid="onboarding-walkthrough">
        <DialogTitle className="sr-only">{step.title}</DialogTitle>
        {/* Header with gradient */}
        <div className={`${colors.gradient} p-6 text-white`}>
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
              <StepIcon className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold font-manrope">{step.title}</h2>
              <p className="text-sm text-white/80">{step.subtitle}</p>
            </div>
          </div>
          {/* Progress dots */}
          <div className="flex gap-1.5 mt-4">
            {STEPS.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 rounded-full flex-1 transition-all ${
                  i <= currentStep ? 'bg-white' : 'bg-white/30'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Body */}
        <div className="p-6">
          <p className="text-sm text-slate-600 mb-4 leading-relaxed">{step.body}</p>

          <ul className="space-y-2 mb-6">
            {step.bullets.map((bullet, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                <span className="text-slate-700">{bullet}</span>
              </li>
            ))}
          </ul>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              {!isFirst && (
                <Button variant="ghost" size="sm" onClick={() => setCurrentStep(currentStep - 1)} data-testid="onboarding-back">
                  <ArrowLeft className="h-4 w-4 mr-1" /> Back
                </Button>
              )}
            </div>
            <div className="flex gap-2">
              {step.action && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAction}
                  data-testid="onboarding-action"
                >
                  {step.actionLabel}
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              )}
              <Button
                size="sm"
                onClick={handleNext}
                className={colors.btn}
                data-testid="onboarding-next"
              >
                {isLast ? "Let's Go!" : 'Next'}
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>

          {/* Skip link */}
          <button
            onClick={handleSkip}
            className="text-xs text-slate-400 hover:text-slate-600 mt-4 block mx-auto"
            data-testid="onboarding-skip"
          >
            Skip walkthrough
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
