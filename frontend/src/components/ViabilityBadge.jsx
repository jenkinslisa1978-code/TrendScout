import React, { useState } from 'react';
import { Shield, ChevronDown, ChevronUp } from 'lucide-react';
import { trackEvent, EVENTS } from '@/services/analytics';

/**
 * UK Product Viability Score badge.
 * Shows a 0-100 score with colour band and optional expandable explainer.
 */
export function ViabilityBadge({ score, size = 'md', showLabel = true, expandable = false, productName = '' }) {
  const [expanded, setExpanded] = useState(false);
  const s = Math.round(score || 0);

  const band = s >= 70 ? { label: 'Strong UK Fit', color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200', bar: 'bg-emerald-500' }
    : s >= 45 ? { label: 'Moderate UK Fit', color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200', bar: 'bg-amber-500' }
    : { label: 'Weak UK Fit', color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200', bar: 'bg-red-500' };

  const handleClick = () => {
    if (expandable) {
      setExpanded(!expanded);
      trackEvent(EVENTS.VIABILITY_BADGE_CLICK, { score: s, product_name: productName });
    }
  };

  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : size === 'lg' ? 'text-sm px-3 py-1.5' : 'text-xs px-2.5 py-1';

  return (
    <div className="inline-block">
      <button
        onClick={handleClick}
        className={`inline-flex items-center gap-1.5 rounded-md border ${band.bg} ${band.border} ${band.color} ${sizeClasses} font-semibold transition-all hover:shadow-sm ${expandable ? 'cursor-pointer' : 'cursor-default'}`}
        data-testid="viability-badge"
        title="UK Product Viability Score — measures commercial viability in the UK market"
      >
        <Shield className={size === 'sm' ? 'h-3 w-3' : 'h-3.5 w-3.5'} />
        <span className="font-mono">{s}</span>
        {showLabel && <span className="font-sans font-medium">{band.label}</span>}
        {expandable && (expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}
      </button>
      {expanded && (
        <div className="mt-2 rounded-lg border border-slate-200 bg-white p-4 text-left max-w-xs shadow-md" data-testid="viability-explainer">
          <p className="text-xs font-semibold text-slate-900 mb-2">UK Viability Score: {s}/100</p>
          <div className="h-1.5 w-full bg-slate-100 rounded-full mb-3 overflow-hidden">
            <div className={`h-full ${band.bar} rounded-full`} style={{ width: `${s}%` }} />
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            This score estimates whether the product is commercially viable in the UK, based on trend momentum, saturation, margin potential, shipping practicality, VAT impact, and channel fit.
          </p>
          <a href="/uk-product-viability-score" className="inline-block mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-700">
            Learn how this score works &rarr;
          </a>
        </div>
      )}
    </div>
  );
}

/**
 * Inline viability indicator for product cards.
 * Compact version for grids and lists.
 */
export function ViabilityIndicator({ score }) {
  const s = Math.round(score || 0);
  const color = s >= 70 ? 'text-emerald-600' : s >= 45 ? 'text-amber-600' : 'text-red-500';

  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium ${color}`} data-testid="viability-indicator" title="UK Viability Score">
      <Shield className="h-3 w-3" />
      <span className="font-mono font-semibold">{s}</span>
      <span className="text-slate-400">UK</span>
    </span>
  );
}
