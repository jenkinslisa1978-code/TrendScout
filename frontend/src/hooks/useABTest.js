import { useMemo } from 'react';
import { trackEvent } from '@/services/analytics';

/**
 * Lightweight A/B testing for CTA copy and UI variants.
 *
 * Usage:
 *   const variant = useABTest('hero_cta', ['Start Free', 'Try TrendScout Free', 'Get Started']);
 *   <Button>{variant}</Button>
 *
 * Persists variant per user via localStorage so they see the same version.
 * Tracks which variant was shown via analytics.
 */
export default function useABTest(testName, variants) {
  const variant = useMemo(() => {
    const key = `ab_${testName}`;
    const stored = localStorage.getItem(key);

    if (stored && variants.includes(stored)) {
      return stored;
    }

    // Assign a random variant
    const picked = variants[Math.floor(Math.random() * variants.length)];
    localStorage.setItem(key, picked);
    trackEvent('ab_test_assigned', { test: testName, variant: picked });
    return picked;
  }, [testName, variants]);

  return variant;
}

/**
 * Track an A/B test conversion (e.g., CTA click).
 */
export function trackABConversion(testName) {
  const key = `ab_${testName}`;
  const variant = localStorage.getItem(key);
  if (variant) {
    trackEvent('ab_test_conversion', { test: testName, variant });
  }
}
