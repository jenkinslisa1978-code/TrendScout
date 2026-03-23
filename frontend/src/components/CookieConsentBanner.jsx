import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';

const CONSENT_KEY = 'ts_cookie_consent';

/**
 * Returns current consent state: null (not yet decided), 'accepted', or 'rejected'.
 */
export function getConsentState() {
  try {
    return localStorage.getItem(CONSENT_KEY);
  } catch {
    return null;
  }
}

/** True only if user has explicitly accepted analytics cookies. */
export function hasAnalyticsConsent() {
  return getConsentState() === 'accepted';
}

export default function CookieConsentBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const consent = getConsentState();
    if (!consent) {
      // Small delay so it doesn't flash on load
      const timer = setTimeout(() => setVisible(true), 1200);
      return () => clearTimeout(timer);
    }
  }, []);

  const accept = useCallback(() => {
    localStorage.setItem(CONSENT_KEY, 'accepted');
    setVisible(false);
    // Fire deferred analytics init
    window.dispatchEvent(new CustomEvent('ts_consent_granted'));
  }, []);

  const reject = useCallback(() => {
    localStorage.setItem(CONSENT_KEY, 'rejected');
    setVisible(false);
  }, []);

  if (!visible) return null;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-[9998] bg-white border-t border-slate-200 shadow-lg px-4 py-4 sm:px-6 sm:py-4 animate-in slide-in-from-bottom-4 duration-300"
      role="alert"
      aria-label="Cookie consent"
      data-testid="cookie-consent-banner"
    >
      <div className="mx-auto max-w-5xl flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-5">
        <p className="text-sm text-slate-600 flex-1 leading-relaxed">
          We use cookies to improve your experience and analyse site usage.
          Essential cookies are always active.
          Analytics cookies help us understand how you use TrendScout.{' '}
          <Link to="/cookie-policy" className="text-indigo-600 hover:text-indigo-700 font-medium underline underline-offset-2">
            Cookie policy
          </Link>
        </p>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={reject}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            data-testid="cookie-reject-btn"
          >
            Reject non-essential
          </button>
          <button
            onClick={accept}
            className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
            data-testid="cookie-accept-btn"
          >
            Accept all
          </button>
        </div>
      </div>
    </div>
  );
}
