import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { RevealSection } from '@/hooks/useScrollReveal';
import { trackEvent, EVENTS } from '@/services/analytics';
import {
  Search, Loader2, ArrowRight, TrendingUp, Shield,
  AlertTriangle, CheckCircle2, XCircle,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function QuickViabilitySearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || trimmed.length < 2) return;

    setLoading(true);
    setError('');
    setResult(null);
    trackEvent('quick_viability_search', { product_name: trimmed });

    try {
      const res = await fetch(`${API_URL}/api/public/quick-viability`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: trimmed }),
      });
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      setResult(data);
    } catch {
      setError('Could not analyse this product. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const verdictConfig = {
    'Strong Potential': { color: 'text-emerald-700 bg-emerald-50 border-emerald-200', icon: CheckCircle2 },
    'Promising': { color: 'text-blue-700 bg-blue-50 border-blue-200', icon: TrendingUp },
    'Mixed Signals': { color: 'text-amber-700 bg-amber-50 border-amber-200', icon: AlertTriangle },
    'High Risk': { color: 'text-red-700 bg-red-50 border-red-200', icon: XCircle },
  };

  return (
    <section className="py-20 lg:py-28 bg-white" data-testid="quick-viability-section">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <RevealSection className="max-w-2xl mx-auto text-center mb-10">
          <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Try It Now</p>
          <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Check any product idea — free, no signup
          </h2>
          <p className="mt-3 text-base text-slate-500">
            Type a product name and get an instant UK viability assessment powered by AI.
          </p>
        </RevealSection>

        <RevealSection delay={100}>
          <div className="max-w-2xl mx-auto">
            {/* Search form */}
            <form onSubmit={handleSearch} className="relative" data-testid="viability-search-form">
              <div className="flex items-center gap-2 rounded-xl border-2 border-slate-200 bg-white p-1.5 focus-within:border-indigo-500 transition-colors shadow-sm">
                <Search className="h-5 w-5 text-slate-400 ml-3 shrink-0" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g. LED sunset lamp, portable blender, posture corrector..."
                  className="flex-1 bg-transparent text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none py-2.5 px-1"
                  maxLength={100}
                  data-testid="viability-search-input"
                />
                <Button
                  type="submit"
                  disabled={loading || query.trim().length < 2}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-5 h-10 text-sm shrink-0 disabled:opacity-50"
                  data-testid="viability-search-btn"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Check viability'}
                </Button>
              </div>
            </form>

            {error && (
              <p className="mt-4 text-sm text-red-500 text-center" data-testid="viability-error">{error}</p>
            )}

            {/* Result card */}
            {result && (
              <div className="mt-8 rounded-2xl border border-slate-200 bg-white shadow-lg overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500" data-testid="viability-result-card">
                {/* Header */}
                <div className="p-5 border-b border-slate-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-slate-500">UK Viability Assessment</p>
                      <h3 className="text-lg font-bold text-slate-900 mt-0.5">{result.product_name}</h3>
                    </div>
                    <div className="text-right">
                      <span className="font-mono text-3xl font-extrabold text-indigo-600">{result.score}</span>
                      <span className="text-sm text-slate-400 font-mono">/100</span>
                    </div>
                  </div>
                  {result.verdict && (() => {
                    const vc = verdictConfig[result.verdict] || verdictConfig['Mixed Signals'];
                    const VIcon = vc.icon;
                    return (
                      <div className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 mt-3 text-xs font-semibold ${vc.color}`}>
                        <VIcon className="h-3.5 w-3.5" /> {result.verdict}
                      </div>
                    );
                  })()}
                </div>

                {/* Signals */}
                {result.signals && (
                  <div className="p-5 border-b border-slate-100">
                    <p className="text-xs font-semibold text-slate-700 mb-3">Signal Breakdown</p>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(result.signals).map(([key, val]) => (
                        <div key={key}>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-slate-600 capitalize">{key.replace(/_/g, ' ')}</span>
                            <span className="font-mono font-bold text-slate-700">{val}%</span>
                          </div>
                          <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all duration-700 ${val >= 65 ? 'bg-emerald-500' : val >= 40 ? 'bg-amber-500' : 'bg-red-400'}`}
                              style={{ width: `${val}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Strengths & Risks */}
                <div className="grid grid-cols-2 divide-x divide-slate-100 border-b border-slate-100">
                  <div className="p-5">
                    <p className="text-xs font-semibold text-emerald-700 mb-2">Strengths</p>
                    <ul className="space-y-1.5">
                      {(result.strengths || []).map((s, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs text-slate-600">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 mt-0.5 shrink-0" /> {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="p-5">
                    <p className="text-xs font-semibold text-red-600 mb-2">Risks</p>
                    <ul className="space-y-1.5">
                      {(result.risks || []).map((r, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs text-slate-600">
                          <AlertTriangle className="h-3.5 w-3.5 text-red-400 mt-0.5 shrink-0" /> {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Summary + CTA */}
                <div className="p-5 bg-slate-50">
                  <p className="text-sm text-slate-600 leading-relaxed">{result.summary}</p>
                  <div className="mt-4 flex items-center gap-3">
                    <Link to="/signup">
                      <Button
                        className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm text-sm h-9 px-4"
                        data-testid="viability-result-cta"
                        onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'quick_viability', product: result.product_name })}
                      >
                        Get full analysis <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                      </Button>
                    </Link>
                    <span className="text-xs text-slate-400">Free to start. No credit card needed.</span>
                  </div>
                </div>
              </div>
            )}

            {!result && !loading && (
              <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
                <span className="text-xs text-slate-400">Try:</span>
                {['LED sunset lamp', 'Portable blender', 'Posture corrector', 'Ice roller'].map((s) => (
                  <button
                    key={s}
                    onClick={() => { setQuery(s); }}
                    className="text-xs text-indigo-600 hover:text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-full px-3 py-1 transition-colors font-medium"
                    data-testid={`suggestion-${s.toLowerCase().replace(/\s/g, '-')}`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        </RevealSection>
      </div>
    </section>
  );
}
