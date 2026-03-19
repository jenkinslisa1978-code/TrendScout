import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useSubscription } from '@/hooks/useSubscription';

/**
 * ProGate — Blurred preview overlay with upgrade CTA.
 * 
 * Usage:
 *   <ProGate requiredPlan="starter" feature="Ad Intelligence">
 *     <ExpensiveContent />
 *   </ProGate>
 * 
 * Props:
 *   requiredPlan: 'starter' | 'pro' | 'elite' — minimum plan needed
 *   feature: string — human-readable feature name for the CTA
 *   previewCount: number — how many children items to show before blurring (for lists)
 *   children: ReactNode — the content to gate
 *   compact: boolean — use a smaller overlay style
 */
const PLAN_RANK = { free: 0, starter: 1, pro: 2, elite: 3 };

export default function ProGate({ 
  requiredPlan = 'pro', 
  feature = 'this feature', 
  children, 
  compact = false,
}) {
  const { plan } = useSubscription();
  const navigate = useNavigate();

  const userRank = PLAN_RANK[plan] ?? 0;
  const requiredRank = PLAN_RANK[requiredPlan] ?? 2;

  // User has sufficient plan — render children normally
  if (userRank >= requiredRank) {
    return <>{children}</>;
  }

  const planLabel = requiredPlan.charAt(0).toUpperCase() + requiredPlan.slice(1);

  if (compact) {
    return (
      <div className="relative" data-testid="pro-gate-compact">
        {/* Blurred preview */}
        <div className="blur-[6px] pointer-events-none select-none opacity-60">
          {children}
        </div>
        {/* Overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-white/40 backdrop-blur-[2px] rounded-xl">
          <Button
            onClick={() => navigate('/pricing')}
            size="sm"
            className="bg-indigo-600 hover:bg-indigo-700 text-white gap-1.5 shadow-lg"
            data-testid="pro-gate-upgrade-btn"
          >
            <Lock className="h-3.5 w-3.5" />
            Upgrade to {planLabel}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative" data-testid="pro-gate">
      {/* Blurred preview of the content */}
      <div className="blur-[6px] pointer-events-none select-none opacity-50">
        {children}
      </div>
      {/* Upgrade overlay */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-200 p-6 max-w-sm text-center mx-4">
          <div className="w-12 h-12 rounded-full bg-indigo-50 flex items-center justify-center mx-auto mb-3">
            <Sparkles className="h-6 w-6 text-indigo-600" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-1">
            Unlock {feature}
          </h3>
          <p className="text-sm text-slate-500 mb-4">
            Upgrade to <span className="font-semibold text-indigo-600">{planLabel}</span> or above to access {feature.toLowerCase()} and more premium insights.
          </p>
          <Button
            onClick={() => navigate('/pricing')}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white gap-2"
            data-testid="pro-gate-upgrade-btn"
          >
            View Plans <ArrowRight className="h-4 w-4" />
          </Button>
          <p className="text-[10px] text-slate-400 mt-2">
            Cancel anytime. Plans start from just a few pounds/month.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * ProGateList — Shows a limited number of items, then blurs the rest with an upgrade CTA.
 * Great for lists of cards/items where you want to show 1-2 teasers.
 * 
 * Usage:
 *   <ProGateList items={ads} freeLimit={2} feature="Ad Intelligence" requiredPlan="pro">
 *     {(item) => <AdCard ad={item} />}
 *   </ProGateList>
 */
export function ProGateList({ 
  items = [], 
  freeLimit = 2, 
  feature = 'this feature', 
  requiredPlan = 'pro',
  children: renderItem,
  className = '',
}) {
  const { plan } = useSubscription();
  const navigate = useNavigate();

  const userRank = PLAN_RANK[plan] ?? 0;
  const requiredRank = PLAN_RANK[requiredPlan] ?? 2;
  const hasAccess = userRank >= requiredRank;

  if (hasAccess || items.length <= freeLimit) {
    return (
      <div className={className}>
        {items.map((item, i) => renderItem(item, i))}
      </div>
    );
  }

  const planLabel = requiredPlan.charAt(0).toUpperCase() + requiredPlan.slice(1);
  const visibleItems = items.slice(0, freeLimit);
  const lockedItems = items.slice(freeLimit, freeLimit + 3); // Show a few blurred

  return (
    <div className={className} data-testid="pro-gate-list">
      {/* Visible free items */}
      {visibleItems.map((item, i) => renderItem(item, i))}

      {/* Blurred locked items with overlay */}
      <div className="relative">
        <div className="blur-[6px] pointer-events-none select-none opacity-40">
          {lockedItems.map((item, i) => renderItem(item, freeLimit + i))}
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-200 p-5 max-w-xs text-center">
            <Lock className="h-5 w-5 text-indigo-600 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-900 mb-1">
              +{items.length - freeLimit} more locked
            </p>
            <p className="text-xs text-slate-500 mb-3">
              Upgrade to {planLabel} to unlock all {feature.toLowerCase()}.
            </p>
            <Button
              onClick={() => navigate('/pricing')}
              size="sm"
              className="bg-indigo-600 hover:bg-indigo-700 text-white gap-1.5"
              data-testid="pro-gate-list-upgrade-btn"
            >
              Upgrade <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
