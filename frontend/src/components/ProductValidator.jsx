import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Loader2, TrendingUp, ShieldCheck, AlertTriangle, XCircle, Lock, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const LABEL_CONFIG = {
  strong_launch: { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', icon: TrendingUp, text: 'Strong Launch' },
  promising: { color: 'text-sky-400', bg: 'bg-sky-500/10', border: 'border-sky-500/25', icon: ShieldCheck, text: 'Promising' },
  risky: { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/25', icon: AlertTriangle, text: 'Risky' },
  avoid: { color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/25', icon: XCircle, text: 'Avoid' },
};

function SignalBar({ label, value }) {
  const barColor = value >= 70 ? 'bg-emerald-500' : value >= 40 ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-zinc-500 w-28 shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-white/[0.06] rounded-full overflow-hidden">
        <div className={`h-full ${barColor} rounded-full transition-all duration-700`} style={{ width: `${value}%` }} />
      </div>
      <span className="text-xs font-mono font-semibold text-zinc-300 w-8 text-right">{value}</span>
    </div>
  );
}

export default function ProductValidator() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const validate = async (e) => {
    e.preventDefault();
    if (!query.trim() || query.trim().length < 2) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/api/public/validate-product`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim() }),
      });
      if (!res.ok) throw new Error('Validation failed');
      const data = await res.json();
      setResult(data);
    } catch {
      setError('Could not validate this product. Try a different name.');
    }
    setLoading(false);
  };

  const cfg = result ? (LABEL_CONFIG[result.launch_label] || LABEL_CONFIG.risky) : null;

  return (
    <div className="w-full" data-testid="product-validator">
      <form onSubmit={validate} className="relative">
        <div className="flex items-center bg-black/50 backdrop-blur-xl rounded-xl border border-white/10 focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/30 transition-all shadow-[0_4px_30px_rgba(0,0,0,0.3)]">
          <Search className="h-5 w-5 text-zinc-500 ml-5 shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type any product idea... e.g. 'LED dog collar'"
            className="flex-1 px-4 py-4 text-base text-white placeholder:text-zinc-600 bg-transparent outline-none"
            data-testid="validator-input"
          />
          <Button
            type="submit"
            disabled={loading || query.trim().length < 2}
            className="mr-2 bg-emerald-500 hover:bg-emerald-400 text-white rounded-lg px-6 h-10 text-sm font-bold tracking-wide shrink-0 shadow-[0_0_15px_rgba(16,185,129,0.3)]"
            data-testid="validator-submit"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Check'}
          </Button>
        </div>
      </form>

      {error && <p className="mt-3 text-sm text-red-400" data-testid="validator-error">{error}</p>}

      {result && cfg && (
        <div className={`mt-5 rounded-xl border ${cfg.border} ${cfg.bg} backdrop-blur-sm p-5 animate-in fade-in slide-in-from-bottom-2 duration-500`} data-testid="validator-result">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              {result.image_url && (
                <img src={result.image_url} alt="" className="h-14 w-14 rounded-xl object-cover border border-white/10 shadow-sm" />
              )}
              <div>
                <p className="text-sm font-bold text-white">{result.product_name}</p>
                {result.category && <p className="text-xs text-zinc-500">{result.category}</p>}
              </div>
            </div>
            <div className="text-right">
              <div className={`text-3xl font-extrabold font-mono ${cfg.color}`} data-testid="validator-score">
                {result.launch_score}
              </div>
              <p className={`text-xs font-bold ${cfg.color}`}>{cfg.text}</p>
            </div>
          </div>

          <p className="mt-3 text-sm text-zinc-400">{result.reasoning}</p>

          <div className="mt-4 space-y-2">
            <SignalBar label="Trend momentum" value={result.signals?.trend_momentum || 0} />
            <SignalBar label="Profit margins" value={result.signals?.profit_margins || 0} />
            <SignalBar label="Competition" value={result.signals?.competition || 0} />
            <SignalBar label="Ad opportunity" value={result.signals?.ad_opportunity || 0} />
            <SignalBar label="Supplier strength" value={result.signals?.supplier_reliability || 0} />
          </div>

          {result.supplier_cost > 0 && (
            <div className="mt-4 flex gap-3 text-xs">
              <span className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-zinc-400">
                Supplier: <strong className="text-white">${result.supplier_cost}</strong>
              </span>
              <span className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-zinc-400">
                Est. retail: <strong className="text-white">${result.estimated_retail}</strong>
              </span>
              <span className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-zinc-400">
                Margin: <strong className="text-emerald-400">{result.estimated_margin_pct}%</strong>
              </span>
            </div>
          )}

          <div className="mt-5 flex items-center justify-between gap-3 pt-4 border-t border-white/[0.06]">
            <div className="flex items-center gap-2 text-xs text-zinc-600">
              <Lock className="h-3.5 w-3.5" />
              AI deep analysis, competitor intel & ad copy
            </div>
            <Link to="/signup">
              <Button size="sm" className="bg-emerald-500 hover:bg-emerald-400 text-white text-xs rounded-lg h-8 px-4 font-bold tracking-wide shadow-[0_0_10px_rgba(16,185,129,0.3)]" data-testid="validator-upgrade-cta">
                Unlock Full Analysis <ArrowRight className="ml-1 h-3 w-3" />
              </Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
