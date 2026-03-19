/**
 * Upgrade Prompt Components
 * 
 * Premium, non-aggressive upgrade prompts for locked features.
 * Displays blurred content with upgrade CTA.
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Lock,
  Crown,
  Rocket,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Store,
  FileText,
  Eye,
  Gift,
} from 'lucide-react';
import { useSubscription } from '@/hooks/useSubscription';
import api from '@/lib/api';
import { toast } from 'sonner';

/**
 * Blurred content overlay with upgrade prompt
 */
export function LockedContent({ 
  children, 
  feature = 'this feature',
  requiredPlan = 'Pro',
  blurIntensity = 'medium',
  className = '',
  trialFeatureId = null,
}) {
  const { isFree, trial, hasActiveTrial, refresh } = useSubscription();
  const [activating, setActivating] = useState(false);
  const blurClasses = {
    light: 'blur-[2px]',
    medium: 'blur-[4px]',
    heavy: 'blur-[8px]'
  };

  // Auto-detect trial feature from the feature name
  const getTrialId = () => {
    if (trialFeatureId) return trialFeatureId;
    const lower = feature.toLowerCase();
    if (lower.includes('ad intel') || lower.includes('ad spy')) return 'ad_intelligence';
    if (lower.includes('tiktok')) return 'tiktok_intel';
    if (lower.includes('competitor') && !lower.includes('saturation')) return 'competitor_intel';
    if (lower.includes('saturation') || lower.includes('ad pattern') || lower.includes('blueprint') || lower.includes('ad performance') || lower.includes('deep dive')) return 'product_deep_dive';
    if (lower.includes('profit') || lower.includes('simulator')) return 'profit_simulator';
    return null;
  };

  const canTrial = isFree && !trial && !hasActiveTrial;
  const detectedTrialId = getTrialId();

  const handleActivateTrial = async () => {
    if (!detectedTrialId) return;
    setActivating(true);
    try {
      const res = await api.post('/api/trial/activate', { feature: detectedTrialId });
      if (res.ok && res.data.success) {
        toast.success(res.data.message);
        await refresh();
        window.location.reload();
      } else {
        toast.error(res.data?.detail || 'Could not activate trial');
      }
    } catch { toast.error('Failed to activate trial'); }
    setActivating(false);
  };
  
  return (
    <div className={`relative ${className}`}>
      {/* Blurred content */}
      <div className={`${blurClasses[blurIntensity]} select-none pointer-events-none`}>
        {children}
      </div>
      
      {/* Overlay */}
      <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] flex items-center justify-center">
        <Card className="bg-white/95 shadow-lg border-indigo-100 max-w-sm mx-4">
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-4">
              <Lock className="h-6 w-6 text-indigo-600" />
            </div>
            <h3 className="font-semibold text-slate-900 mb-2">
              Unlock {feature}
            </h3>
            <p className="text-sm text-slate-600 mb-4">
              Upgrade to {requiredPlan} to access {feature.toLowerCase()}.
            </p>
            <Link to="/pricing">
              <Button className="bg-indigo-600 hover:bg-indigo-700 w-full">
                <Sparkles className="h-4 w-4 mr-2" />
                Upgrade to {requiredPlan}
              </Button>
            </Link>
            {canTrial && detectedTrialId && (
              <button
                onClick={handleActivateTrial}
                disabled={activating}
                className="mt-3 w-full text-center text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center justify-center gap-1 py-1.5 rounded-lg hover:bg-indigo-50 transition-colors disabled:opacity-50"
                data-testid="trial-inline-activate"
              >
                <Gift className="h-3.5 w-3.5" />
                {activating ? 'Activating...' : 'Or try free for 24 hours'}
              </button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

/**
 * Inline upgrade badge for partial access
 */
export function UpgradeBadge({ 
  feature = 'full access',
  requiredPlan = 'Pro',
  size = 'default'
}) {
  const sizeClasses = {
    small: 'text-xs px-2 py-0.5',
    default: 'text-sm px-3 py-1',
    large: 'text-base px-4 py-1.5'
  };
  
  return (
    <Link to="/pricing">
      <Badge 
        className={`bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:from-indigo-600 hover:to-purple-600 cursor-pointer transition-all ${sizeClasses[size]}`}
      >
        <Lock className="h-3 w-3 mr-1" />
        Upgrade for {feature}
      </Badge>
    </Link>
  );
}

/**
 * Card-style upgrade prompt
 */
export function UpgradeCard({
  title = 'Unlock Premium Features',
  description = 'Get access to advanced tools and insights.',
  features = [],
  requiredPlan = 'Pro',
  icon: Icon = Crown,
  variant = 'default'
}) {
  const variants = {
    default: {
      bg: 'bg-gradient-to-br from-indigo-50 to-purple-50',
      border: 'border-indigo-100',
      iconBg: 'bg-indigo-100',
      iconColor: 'text-indigo-600',
      button: 'bg-indigo-600 hover:bg-indigo-700'
    },
    elite: {
      bg: 'bg-gradient-to-br from-amber-50 to-orange-50',
      border: 'border-amber-100',
      iconBg: 'bg-amber-100',
      iconColor: 'text-amber-600',
      button: 'bg-amber-500 hover:bg-amber-600'
    },
    subtle: {
      bg: 'bg-slate-50',
      border: 'border-slate-200',
      iconBg: 'bg-slate-100',
      iconColor: 'text-slate-600',
      button: 'bg-slate-700 hover:bg-slate-800'
    }
  };
  
  const style = variants[variant];
  
  return (
    <Card className={`${style.bg} ${style.border}`} data-testid="upgrade-card">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-xl ${style.iconBg}`}>
            <Icon className={`h-6 w-6 ${style.iconColor}`} />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-slate-900 mb-1">{title}</h3>
            <p className="text-sm text-slate-600 mb-4">{description}</p>
            
            {features.length > 0 && (
              <ul className="space-y-2 mb-4">
                {features.map((feature, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-sm text-slate-700">
                    <Sparkles className="h-3.5 w-3.5 text-indigo-500" />
                    {feature}
                  </li>
                ))}
              </ul>
            )}
            
            <Link to="/pricing">
              <Button className={`${style.button} text-white`}>
                Upgrade to {requiredPlan}
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Store limit upgrade prompt
 */
export function StoreLimitPrompt({ currentCount, maxCount }) {
  return (
    <UpgradeCard
      title="Store Limit Reached"
      description={`You've created ${currentCount} of ${maxCount} stores on your current plan.`}
      features={[
        'Create up to 5 stores with Pro',
        'Unlimited stores with Elite',
        'Full product catalog management'
      ]}
      requiredPlan={currentCount >= 5 ? 'Elite' : 'Pro'}
      icon={Store}
    />
  );
}

/**
 * Report access upgrade prompt
 */
export function ReportUpgradePrompt() {
  return (
    <UpgradeCard
      title="Unlock Full Reports"
      description="Get complete market analysis and winning product insights."
      features={[
        'Full weekly winning products report',
        'Monthly market trend analysis',
        'Category performance breakdowns',
        'Exclusive market predictions'
      ]}
      requiredPlan="Pro"
      icon={FileText}
    />
  );
}

/**
 * Early trend access upgrade prompt
 */
export function EarlyTrendUpgradePrompt() {
  return (
    <UpgradeCard
      title="Unlock Early Trend Detection"
      description="Discover products before they go viral with AI-powered trend analysis."
      features={[
        'Early trend signals & velocity',
        'Advanced opportunity scoring',
        'Automation insights',
        'Priority notifications'
      ]}
      requiredPlan="Elite"
      icon={TrendingUp}
      variant="elite"
    />
  );
}

/**
 * Watchlist/Alerts upgrade prompt
 */
export function WatchlistUpgradePrompt() {
  return (
    <UpgradeCard
      title="Unlock Full Watchlist Access"
      description="Track unlimited products and get real-time opportunity alerts."
      features={[
        'Unlimited watchlist items',
        'Real-time price & trend alerts',
        'Change tracking & notifications',
        'Export watchlist data'
      ]}
      requiredPlan="Pro"
      icon={Eye}
    />
  );
}

/**
 * Simple inline upgrade link
 */
export function UpgradeLink({ 
  text = 'Upgrade to unlock',
  className = ''
}) {
  return (
    <Link 
      to="/pricing" 
      className={`inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-700 text-sm font-medium ${className}`}
    >
      <Lock className="h-3.5 w-3.5" />
      {text}
      <ArrowRight className="h-3.5 w-3.5" />
    </Link>
  );
}

/**
 * Context-aware limit hit banner — shown when Starter users exhaust daily limits
 */
export function LimitHitBanner({ limitType = 'analyses', used = 0, max = 5, upgradeTo = 'Pro' }) {
  if (used < max) return null;

  const messages = {
    analyses: { title: 'Daily analysis limit reached', desc: `You've used all ${max} product analyses today.`, unlock: 'Unlock unlimited analysis' },
    simulations: { title: 'Simulation limit reached', desc: `You've used all ${max} launch simulations today.`, unlock: 'Unlock unlimited simulations' },
    feed: { title: 'Opportunity feed limited', desc: 'Upgrade to see the full opportunity feed.', unlock: 'Unlock full feed' },
    default: { title: 'Feature limit reached', desc: 'Upgrade to unlock more.', unlock: 'Unlock full access' },
  };

  const msg = messages[limitType] || messages.default;

  return (
    <div className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-xl p-4 flex items-center justify-between gap-4" data-testid="limit-hit-banner">
      <div className="flex items-center gap-3 text-white">
        <Lock className="h-5 w-5 flex-shrink-0" />
        <div>
          <p className="font-semibold text-sm">{msg.title}</p>
          <p className="text-indigo-200 text-xs">{msg.desc}</p>
        </div>
      </div>
      <Link to="/pricing">
        <Button size="sm" className="bg-white text-indigo-700 hover:bg-indigo-50 font-semibold whitespace-nowrap" data-testid="limit-upgrade-btn">
          {msg.unlock}
          <ArrowRight className="ml-1 h-3 w-3" />
        </Button>
      </Link>
    </div>
  );
}

/**
 * Inline upgrade nudge for locked insights (appears within content)
 */
export function InsightLockedNudge({ feature = 'full insights', upgradeTo = 'Pro' }) {
  return (
    <div className="flex items-center gap-3 bg-violet-50 border border-violet-100 rounded-lg px-4 py-3" data-testid="insight-locked-nudge">
      <Lock className="h-4 w-4 text-violet-500 flex-shrink-0" />
      <p className="text-sm text-violet-700">
        <span className="font-semibold">Unlock {feature}</span> — Upgrade to {upgradeTo} to enable automation
      </p>
      <Link to="/pricing" className="ml-auto">
        <Button size="sm" variant="ghost" className="text-violet-600 hover:text-violet-700 hover:bg-violet-100 text-xs font-semibold">
          Upgrade
          <ArrowRight className="ml-1 h-3 w-3" />
        </Button>
      </Link>
    </div>
  );
}

export default {
  LockedContent,
  UpgradeBadge,
  UpgradeCard,
  StoreLimitPrompt,
  ReportUpgradePrompt,
  EarlyTrendUpgradePrompt,
  WatchlistUpgradePrompt,
  UpgradeLink,
  LimitHitBanner,
  InsightLockedNudge
};
