import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Lock, Sparkles, ArrowRight, Check, Crown, Zap, TrendingUp,
  Package, Eye, Rocket, BarChart3
} from 'lucide-react';

const PLAN_FEATURES = {
  starter: {
    name: 'Starter',
    price: '19',
    color: 'from-sky-500 to-blue-600',
    features: [
      '5 full analyses per day',
      'Supplier intelligence',
      'Ad generator',
      '3 launch simulations',
    ],
  },
  pro: {
    name: 'Pro',
    price: '39',
    color: 'from-indigo-500 to-violet-600',
    features: [
      'Unlimited analysis',
      'Full supplier intel',
      'Ad A/B testing',
      'Unlimited simulations',
      'Advanced filters',
    ],
  },
  elite: {
    name: 'Elite',
    price: '79',
    color: 'from-amber-500 to-orange-600',
    features: [
      'Everything in Pro',
      'Budget Optimiser',
      'Radar alerts',
      'LaunchPad',
      'Priority support',
    ],
  },
};

const FEATURE_CONTEXTS = {
  supplier: {
    icon: Package,
    title: 'Unlock Supplier Intelligence',
    description: 'See verified supplier costs, shipping times, and order volume data to calculate real margins.',
    requiredPlan: 'starter',
  },
  ads: {
    icon: Eye,
    title: 'Unlock Ad Intelligence',
    description: 'Access AI-generated ad creatives, winning ad patterns, and A/B test recommendations.',
    requiredPlan: 'starter',
  },
  insights: {
    icon: BarChart3,
    title: 'Unlock Full Insights',
    description: 'Get complete product analysis with market intelligence, competitor data, and trend predictions.',
    requiredPlan: 'pro',
  },
  daily_limit: {
    icon: Zap,
    title: 'Daily Limit Reached',
    description: "You've used all your free product insights today. Upgrade to keep discovering winning products.",
    requiredPlan: 'starter',
  },
  early_trends: {
    icon: TrendingUp,
    title: 'Unlock Early Trend Detection',
    description: 'Discover products before they go viral with AI-powered early signal detection.',
    requiredPlan: 'elite',
  },
  launch_simulator: {
    icon: Rocket,
    title: 'Unlock Launch Simulator',
    description: 'Simulate product launches with AI to predict revenue, costs, and success probability.',
    requiredPlan: 'starter',
  },
};

export function UpgradeModal({ isOpen, onClose, feature = 'insights', usedCount, dailyLimit }) {
  if (!isOpen) return null;

  const ctx = FEATURE_CONTEXTS[feature] || FEATURE_CONTEXTS.insights;
  const Icon = ctx.icon;
  const plan = PLAN_FEATURES[ctx.requiredPlan] || PLAN_FEATURES.starter;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center" data-testid="upgrade-modal">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className={`bg-gradient-to-r ${plan.color} px-6 py-8 text-white text-center`}>
          <div className="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center mx-auto mb-4">
            <Icon className="h-7 w-7 text-white" />
          </div>
          <h2 className="text-xl font-bold" data-testid="upgrade-modal-title">{ctx.title}</h2>
          <p className="text-white/80 text-sm mt-2 max-w-xs mx-auto">{ctx.description}</p>
          {feature === 'daily_limit' && usedCount !== undefined && (
            <div className="mt-3 inline-flex items-center gap-2 bg-white/15 rounded-full px-4 py-1.5 text-sm">
              <Lock className="h-3.5 w-3.5" />
              {usedCount}/{dailyLimit} insights used today
            </div>
          )}
        </div>

        {/* Plan Details */}
        <div className="px-6 py-6">
          <div className="flex items-baseline gap-1 mb-4">
            <span className="text-3xl font-extrabold text-slate-900">&pound;{plan.price}</span>
            <span className="text-slate-500">/month</span>
            <span className="ml-2 text-sm font-medium text-slate-600">{plan.name} Plan</span>
          </div>

          <ul className="space-y-2.5 mb-6">
            {plan.features.map((f) => (
              <li key={f} className="flex items-center gap-2.5 text-sm text-slate-700">
                <Check className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                {f}
              </li>
            ))}
          </ul>

          <div className="flex flex-col gap-2.5">
            <Link to="/pricing" onClick={onClose}>
              <Button
                className={`w-full h-11 bg-gradient-to-r ${plan.color} text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all`}
                data-testid="upgrade-modal-cta"
              >
                <Crown className="h-4 w-4 mr-2" />
                Upgrade to {plan.name}
              </Button>
            </Link>
            <button
              onClick={onClose}
              className="text-sm text-slate-400 hover:text-slate-600 transition-colors py-1"
              data-testid="upgrade-modal-close"
            >
              Maybe later
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UpgradeModal;
