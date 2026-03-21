import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { RevealSection } from '@/hooks/useScrollReveal';
import { trackEvent, EVENTS } from '@/services/analytics';
import {
  Search, Loader2, ArrowRight, TrendingUp, Shield,
  AlertTriangle, CheckCircle2, XCircle, Mail, Lock, Sparkles,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const STORAGE_KEY = 'ts_viability_searches';
const EMAIL_KEY = 'ts_viability_email';
const FREE_BEFORE_GATE = 1;
const FREE_AFTER_GATE = 3;

function getSearchState() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return { count: 0, gated: false };
    return JSON.parse(stored);
  } catch { return { count: 0, gated: false }; }
}

function setSearchState(state) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch {}
}

function getSavedEmail() {
  try { return localStorage.getItem(EMAIL_KEY) || ''; } catch { return ''; }
}

export default function QuickViabilitySearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [searchState, setSearchStateLocal] = useState(getSearchState);
  const [showGate, setShowGate] = useState(false);
  const [email, setEmail] = useState('');
  const [emailSubmitting, setEmailSubmitting] = useState(false);
  const [emailCaptured, setEmailCaptured] = useState(!!getSavedEmail());

  const maxSearches = emailCaptured ? FREE_BEFORE_GATE + FREE_AFTER_GATE : FREE_BEFORE_GATE;
  const searchesLeft = Math.max(0, maxSearches - searchState.count);
  const isLocked = searchState.count >= maxSearches && !emailCaptured && searchState.count >= FREE_BEFORE_GATE;
  const isFullyUsed = searchState.count >= FREE_BEFORE_GATE + FREE_AFTER_GATE && emailCaptured;

  useEffect(() => {
    if (searchState.count >= FREE_BEFORE_GATE && !emailCaptured && result) {
      setShowGate(true);
    }
  }, [searchState.count, emailCaptured, result]);

  const handleSearch = async (e) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || trimmed.length < 2) return;

    if (isFullyUsed) return;
    if (isLocked) {
      setShowGate(true);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setShowGate(false);
    trackEvent('quick_viability_search', { product_name: trimmed, search_num: searchState.count + 1 });

    try {
      const res = await fetch(`${API_URL}/api/public/quick-viability`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: trimmed }),
      });
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      setResult(data);

      const newState = { ...searchState, count: searchState.count + 1 };
      setSearchStateLocal(newState);
      setSearchState(newState);

      if (newState.count >= FREE_BEFORE_GATE && !emailCaptured) {
        setShowGate(true);
      }
    } catch {
      setError('Could not analyse this product. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail || !trimmedEmail.includes('@')) return;

    setEmailSubmitting(true);
    try {
      await fetch(`${API_URL}/api/leads/capture`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: trimmedEmail,
          source: 'quick_viability_gate',
          context: `Searched: ${result?.product_name || query}`,
          viability_result: result || null,
        }),
      });
      localStorage.setItem(EMAIL_KEY, trimmedEmail);
      setEmailCaptured(true);
      setShowGate(false);
      trackEvent('viability_email_capture', { email: trimmedEmail, search_count: searchState.count });
    } catch {} finally {
      setEmailSubmitting(false);
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
              <div className={`flex items-center gap-2 rounded-xl border-2 p-1.5 transition-colors shadow-sm ${isFullyUsed ? 'border-slate-200 bg-slate-50' : 'border-slate-200 bg-white focus-within:border-indigo-500'}`}>
                <Search className="h-5 w-5 text-slate-400 ml-3 shrink-0" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={isFullyUsed ? 'Sign up for unlimited searches...' : 'e.g. LED sunset lamp, portable blender, posture corrector...'}
                  className="flex-1 bg-transparent text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none py-2.5 px-1 disabled:cursor-not-allowed"
                  maxLength={100}
                  disabled={isFullyUsed}
                  data-testid="viability-search-input"
                />
                <Button
                  type="submit"
                  disabled={loading || query.trim().length < 2 || isFullyUsed}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-5 h-10 text-sm shrink-0 disabled:opacity-50"
                  data-testid="viability-search-btn"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Check viability'}
                </Button>
              </div>
              {/* Search counter */}
              {!isFullyUsed && searchState.count > 0 && (
                <div className="mt-2 flex items-center justify-end gap-1" data-testid="search-counter">
                  <div className="flex gap-0.5">
                    {Array.from({ length: maxSearches }).map((_, i) => (
                      <div key={i} className={`h-1 w-4 rounded-full ${i < searchState.count ? 'bg-indigo-500' : 'bg-slate-200'}`} />
                    ))}
                  </div>
                  <span className="text-xs text-slate-400 ml-1">
                    {searchesLeft} free {searchesLeft === 1 ? 'search' : 'searches'} left
                  </span>
                </div>
              )}
            </form>

            {error && (
              <p className="mt-4 text-sm text-red-500 text-center" data-testid="viability-error">{error}</p>
            )}

            {/* Email capture gate */}
            {showGate && !emailCaptured && (
              <div className="mt-6 rounded-2xl border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 to-white p-6 shadow-sm" data-testid="email-gate">
                <div className="flex items-start gap-4">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-100 shrink-0">
                    <Sparkles className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-bold text-slate-900">Unlock {FREE_AFTER_GATE} more free searches</h3>
                    <p className="text-sm text-slate-500 mt-1">
                      Enter your email to get {FREE_AFTER_GATE} more viability checks — plus weekly trending product alerts.
                    </p>
                    <form onSubmit={handleEmailSubmit} className="mt-4 flex items-center gap-2" data-testid="email-gate-form">
                      <div className="flex-1 flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 focus-within:border-indigo-500 transition-colors">
                        <Mail className="h-4 w-4 text-slate-400 shrink-0" />
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="your@email.com"
                          className="flex-1 bg-transparent text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none"
                          required
                          data-testid="email-gate-input"
                        />
                      </div>
                      <Button
                        type="submit"
                        disabled={emailSubmitting || !email.includes('@')}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-4 h-10 text-sm shrink-0"
                        data-testid="email-gate-submit"
                      >
                        {emailSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <>Unlock <ArrowRight className="h-3.5 w-3.5 ml-1" /></>}
                      </Button>
                    </form>
                    <p className="text-xs text-slate-400 mt-2 flex items-center gap-1">
                      <Lock className="h-3 w-3" /> No spam. Unsubscribe anytime.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Success message after email capture */}
            {emailCaptured && showGate && (
              <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-center" data-testid="email-gate-success">
                <p className="text-sm font-semibold text-emerald-800 flex items-center justify-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4" /> Unlocked! You have {searchesLeft} more free searches.
                </p>
              </div>
            )}

            {/* Fully used - sign up CTA */}
            {isFullyUsed && (
              <div className="mt-6 rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-6 text-center" data-testid="searches-exhausted">
                <Lock className="h-8 w-8 text-slate-300 mx-auto mb-3" />
                <h3 className="text-base font-bold text-slate-900">You've used all your free searches</h3>
                <p className="text-sm text-slate-500 mt-1 mb-4">Sign up to get unlimited viability checks, plus full product analytics and UK market intelligence.</p>
                <Link to="/signup">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm" data-testid="exhausted-signup-cta">
                    Start Free — Unlimited Searches <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            )}

            {/* Result card */}
            {result && (
              <div className="mt-8 rounded-2xl border border-slate-200 bg-white shadow-lg overflow-hidden" data-testid="viability-result-card">
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
                            <div className={`h-full rounded-full transition-all duration-700 ${val >= 65 ? 'bg-emerald-500' : val >= 40 ? 'bg-amber-500' : 'bg-red-400'}`} style={{ width: `${val}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
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
                <div className="p-5 bg-slate-50">
                  <p className="text-sm text-slate-600 leading-relaxed">{result.summary}</p>
                  <div className="mt-4 flex items-center gap-3">
                    <Link to="/signup">
                      <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm text-sm h-9 px-4" data-testid="viability-result-cta" onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'quick_viability', product: result.product_name })}>
                        Get full analysis <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                      </Button>
                    </Link>
                    <span className="text-xs text-slate-400">Free to start. No credit card needed.</span>
                  </div>
                </div>
              </div>
            )}

            {!result && !loading && !isFullyUsed && !showGate && (
              <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
                <span className="text-xs text-slate-400">Try:</span>
                {['LED sunset lamp', 'Portable blender', 'Posture corrector', 'Ice roller'].map((s) => (
                  <button
                    key={s}
                    onClick={() => setQuery(s)}
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
