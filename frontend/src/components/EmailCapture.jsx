import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import { Mail, ArrowRight, Check } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Email capture block — shows after a tool delivers value.
 * Light, credible, non-spammy.
 */
export default function EmailCapture({ source = 'free_tool', context = '' }) {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const tracked = useRef(false);

  useEffect(() => {
    if (!tracked.current) {
      trackEvent(EVENTS.EMAIL_CAPTURE_VIEW, { source, context });
      tracked.current = true;
    }
  }, [source, context]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !email.includes('@')) { setError('Please enter a valid email address.'); return; }
    setLoading(true);
    setError('');
    try {
      await fetch(`${API_URL}/api/leads/capture`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source, context }),
      });
    } catch {
      // Silently fail — don't block UX for lead capture
    }
    trackEvent(EVENTS.EMAIL_CAPTURE_SUBMIT, { source, context });
    setSubmitted(true);
    setLoading(false);
  };

  if (submitted) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-5 text-center" data-testid="email-capture-success">
        <div className="flex items-center justify-center gap-2 text-emerald-700 mb-1">
          <Check className="h-4 w-4" />
          <span className="text-sm font-semibold">You are in.</span>
        </div>
        <p className="text-xs text-slate-600">We will send you UK product research insights and new feature updates. No spam.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-5" data-testid="email-capture-block">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 flex-shrink-0 mt-0.5">
          <Mail className="h-4.5 w-4.5" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-slate-900">Get UK product insights in your inbox</h4>
          <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
            Useful product research tips, new tool updates, and UK ecommerce trends. No hype. Unsubscribe anytime.
          </p>
          <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
            <input
              type="email"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setError(''); }}
              placeholder="you@example.com"
              className="flex-1 min-w-0 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
              data-testid="email-capture-input"
              required
            />
            <Button
              type="submit"
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-sm px-4 flex-shrink-0"
              data-testid="email-capture-submit-btn"
            >
              {loading ? '...' : 'Subscribe'}
            </Button>
          </form>
          {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
        </div>
      </div>
    </div>
  );
}
