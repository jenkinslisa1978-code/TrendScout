import React, { useState, useMemo } from 'react';
import { trackEvent, EVENTS } from '@/services/analytics';
import { Check, X, AlertTriangle } from 'lucide-react';

const CHECKLIST_ITEMS = [
  { id: 'demand', label: 'There is evidence of growing demand (search trends, social buzz)', weight: 15, category: 'Market' },
  { id: 'competition', label: 'Competition is not already saturated in the UK', weight: 15, category: 'Market' },
  { id: 'margin', label: 'I can achieve 30%+ margin after VAT, shipping, and returns', weight: 15, category: 'Financials' },
  { id: 'price', label: 'Price point is right for my target channel (£10-30 for TikTok, £15-60 for Shopify)', weight: 10, category: 'Financials' },
  { id: 'supplier', label: 'I have identified at least one reliable supplier', weight: 10, category: 'Operations' },
  { id: 'shipping', label: 'Shipping to UK customers is under 10 days', weight: 10, category: 'Operations' },
  { id: 'visual', label: 'The product photographs/videos well', weight: 5, category: 'Marketing' },
  { id: 'problem', label: 'It solves a clear problem or fulfils a desire', weight: 10, category: 'Marketing' },
  { id: 'repeat', label: 'There is potential for repeat purchases or upsells', weight: 5, category: 'Growth' },
  { id: 'legal', label: 'No UK import restrictions, certifications, or compliance issues', weight: 5, category: 'Risk' },
];

/**
 * Product Validation Checklist
 * Interactive checklist that scores product readiness for UK launch.
 */
export default function ProductValidationChecklist() {
  const [checked, setChecked] = useState({});

  const toggle = (id) => {
    setChecked(prev => {
      const next = { ...prev, [id]: !prev[id] };
      trackEvent('validation_checklist_toggle', { item: id, checked: next[id] });
      return next;
    });
  };

  const checkedCount = Object.values(checked).filter(Boolean).length;
  const totalScore = useMemo(() => {
    return CHECKLIST_ITEMS.reduce((sum, item) => sum + (checked[item.id] ? item.weight : 0), 0);
  }, [checked]);

  const getVerdict = () => {
    if (totalScore >= 80) return { label: 'Strong candidate', color: 'text-emerald-600', bg: 'bg-emerald-50', desc: 'This product ticks most boxes. Consider moving to sourcing and small-scale testing.' };
    if (totalScore >= 50) return { label: 'Promising but gaps', color: 'text-amber-600', bg: 'bg-amber-50', desc: 'Good potential but address the unchecked items before committing significant budget.' };
    return { label: 'Needs more work', color: 'text-red-600', bg: 'bg-red-50', desc: 'Several key criteria are not met. Research further or consider a different product.' };
  };

  const verdict = getVerdict();
  const categories = [...new Set(CHECKLIST_ITEMS.map(i => i.category))];

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="product-validation-checklist">
      <h3 className="font-manrope text-lg font-semibold text-slate-900 mb-1">Product Validation Checklist</h3>
      <p className="text-sm text-slate-500 mb-5">Tick each criterion your product meets. We will score its UK launch readiness.</p>

      {categories.map(cat => (
        <div key={cat} className="mb-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">{cat}</p>
          <div className="space-y-2">
            {CHECKLIST_ITEMS.filter(i => i.category === cat).map(item => (
              <button
                key={item.id}
                onClick={() => toggle(item.id)}
                className={`w-full text-left flex items-start gap-3 px-4 py-3 rounded-lg border transition-all text-sm ${
                  checked[item.id]
                    ? 'border-emerald-200 bg-emerald-50/50 text-emerald-800'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300'
                }`}
                data-testid={`checklist-item-${item.id}`}
              >
                <div className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5 ${
                  checked[item.id] ? 'bg-emerald-500' : 'bg-slate-200'
                }`}>
                  {checked[item.id] && <Check className="h-3.5 w-3.5 text-white" />}
                </div>
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      ))}

      {/* Score */}
      <div className={`rounded-lg ${verdict.bg} p-4 mt-4`} data-testid="checklist-score">
        <div className="flex items-center justify-between mb-2">
          <span className={`text-sm font-semibold ${verdict.color}`}>{verdict.label}</span>
          <span className="font-mono text-lg font-bold text-slate-900">{totalScore}/100</span>
        </div>
        <div className="w-full h-2 bg-white/60 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${totalScore >= 80 ? 'bg-emerald-500' : totalScore >= 50 ? 'bg-amber-500' : 'bg-red-500'}`}
            style={{ width: `${totalScore}%` }}
          />
        </div>
        <p className="text-xs text-slate-600 mt-2">{verdict.desc}</p>
        <p className="text-xs text-slate-400 mt-1">{checkedCount} of {CHECKLIST_ITEMS.length} criteria met</p>
      </div>
    </div>
  );
}
