import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { trackEvent, EVENTS } from '@/services/analytics';
import { X, ArrowRight, FileText } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const DISMISS_KEY = 'ts_exit_popup_dismissed';

/**
 * Exit-intent popup — shows when mouse leaves viewport on desktop.
 * Offers a lead magnet (free checklist) in exchange for email.
 * Only shows once per session, respects localStorage dismissal for 7 days.
 */
export default function ExitIntentPopup() {
  const [visible, setVisible] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const triggered = useRef(false);

  useEffect(() => {
    const dismissed = localStorage.getItem(DISMISS_KEY);
    if (dismissed && Date.now() - parseInt(dismissed) < 7 * 86400000) return;

    const handleMouseLeave = (e) => {
      if (e.clientY > 5 || triggered.current) return;
      triggered.current = true;
      setVisible(true);
      trackEvent('exit_intent_popup_view', { page: window.location.pathname });
    };

    // Only on desktop — no exit intent on mobile
    if (window.innerWidth >= 1024) {
      document.addEventListener('mouseleave', handleMouseLeave);
    }
    return () => document.removeEventListener('mouseleave', handleMouseLeave);
  }, []);

  const dismiss = () => {
    setVisible(false);
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    trackEvent('exit_intent_popup_dismiss', { page: window.location.pathname });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !email.includes('@')) return;
    setLoading(true);
    try {
      await fetch(`${API_URL}/api/leads/capture`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: 'exit_intent', context: window.location.pathname }),
      });
    } catch {}
    trackEvent('exit_intent_popup_submit', { page: window.location.pathname });
    setSubmitted(true);
    setLoading(false);
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" data-testid="exit-intent-popup">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={dismiss} />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 animate-in fade-in zoom-in-95 duration-200">
        <button onClick={dismiss} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600" data-testid="exit-popup-close">
          <X className="h-5 w-5" />
        </button>

        {submitted ? (
          <div className="text-center py-4" data-testid="exit-popup-success">
            <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
              <FileText className="h-6 w-6 text-emerald-600" />
            </div>
            <h3 className="font-manrope text-xl font-bold text-slate-900">Check your inbox</h3>
            <p className="text-sm text-slate-500 mt-2 leading-relaxed">
              We have sent the UK Product Research Checklist to your email. You will also receive weekly product insights.
            </p>
            <Link to="/tools" onClick={dismiss}>
              <Button className="mt-5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-sm px-5">
                Try Free Tools <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>
        ) : (
          <>
            <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mb-4">
              <FileText className="h-6 w-6 text-indigo-600" />
            </div>
            <h3 className="font-manrope text-xl font-bold text-slate-900">Before you go...</h3>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Get our free <span className="font-semibold text-slate-900">UK Product Research Checklist</span> — 
              the same framework our top sellers use to validate products before investing.
            </p>
            <ul className="mt-4 space-y-2">
              {['7-step validation framework', 'UK margin calculation template', 'Competition assessment criteria'].map((item) => (
                <li key={item} className="flex items-center gap-2 text-sm text-slate-600">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
            <form onSubmit={handleSubmit} className="mt-5 flex gap-2">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="flex-1 min-w-0 rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
                data-testid="exit-popup-email-input"
                required
              />
              <Button
                type="submit"
                disabled={loading}
                className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-sm px-5 flex-shrink-0"
                data-testid="exit-popup-submit-btn"
              >
                {loading ? '...' : 'Send it'}
              </Button>
            </form>
            <p className="text-xs text-slate-400 mt-3">No spam. Unsubscribe anytime.</p>
          </>
        )}
      </div>
    </div>
  );
}
