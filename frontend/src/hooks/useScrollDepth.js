import { useEffect, useRef } from 'react';
import { trackEvent, EVENTS } from '@/services/analytics';

/**
 * Fires SCROLL_DEPTH events at 25%, 50%, 75%, 100% thresholds.
 * Uses Intersection Observer on sentinel elements placed in the page.
 * @param {string} pageName — identifier for the analytics event (e.g. "compare_jungle_scout")
 */
export default function useScrollDepth(pageName) {
  const fired = useRef(new Set());

  useEffect(() => {
    fired.current = new Set();
    const thresholds = [25, 50, 75, 100];

    const handleScroll = () => {
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight <= 0) return;
      const pct = Math.round((window.scrollY / docHeight) * 100);
      for (const t of thresholds) {
        if (pct >= t && !fired.current.has(t)) {
          fired.current.add(t);
          trackEvent(EVENTS.SCROLL_DEPTH, { page: pageName, depth: t });
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [pageName]);
}
