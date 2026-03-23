import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import PageMeta, { breadcrumbSchema } from '@/components/PageMeta';

export default function CookiePolicyPage() {
  return (
    <LandingLayout>
      <PageMeta
        title="Cookie Policy"
        description="How TrendScout uses cookies and similar technologies. Understand what cookies we set, why, and how to manage your preferences."
        canonical="/cookie-policy"
        schema={[breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Cookie Policy' }])]}
      />
      <div className="bg-white" data-testid="cookie-policy-page">
        <section className="pt-16 pb-20 px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-manrope text-3xl font-extrabold text-slate-900 tracking-tight">Cookie Policy</h1>
            <p className="mt-2 text-sm text-slate-400">Last updated: March 2026</p>

            <div className="mt-8 prose prose-slate prose-sm max-w-none space-y-6">
              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">What are cookies?</h2>
                <p className="text-slate-600 leading-relaxed">Cookies are small text files placed on your device when you visit a website. They help the site remember your preferences and understand how you use it.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Cookie categories</h2>
                <p className="text-slate-600 leading-relaxed">TrendScout uses cookies in the following categories:</p>

                <div className="mt-4 space-y-4">
                  <div className="rounded-lg border border-slate-200 p-4">
                    <h3 className="text-sm font-semibold text-slate-900">Essential cookies <span className="text-xs font-normal text-slate-500 ml-2">(Always active)</span></h3>
                    <p className="text-sm text-slate-600 mt-1 leading-relaxed">Required for TrendScout to function. These handle authentication, session management, CSRF protection, and security. You cannot opt out of these cookies.</p>
                    <div className="mt-2 text-xs text-slate-500">
                      <p><strong>Examples:</strong> ts_token (authentication), ts_csrf (security), ts_session_id (session tracking)</p>
                    </div>
                  </div>

                  <div className="rounded-lg border border-slate-200 p-4">
                    <h3 className="text-sm font-semibold text-slate-900">Analytics cookies <span className="text-xs font-normal text-slate-500 ml-2">(Requires consent)</span></h3>
                    <p className="text-sm text-slate-600 mt-1 leading-relaxed">Help us understand how visitors use TrendScout, which pages are popular, and where improvements are needed. This data is aggregated and does not personally identify you. These cookies are only set after you accept them via the consent banner.</p>
                    <div className="mt-2 text-xs text-slate-500">
                      <p><strong>Provider:</strong> Google Analytics (GA4)</p>
                      <p><strong>Examples:</strong> _ga, _ga_*, _gid</p>
                      <p><strong>Purpose:</strong> Page views, feature usage patterns, traffic sources</p>
                    </div>
                  </div>

                  <div className="rounded-lg border border-slate-200 p-4">
                    <h3 className="text-sm font-semibold text-slate-900">Preference cookies <span className="text-xs font-normal text-slate-500 ml-2">(Always active)</span></h3>
                    <p className="text-sm text-slate-600 mt-1 leading-relaxed">Remember your settings and preferences such as pricing toggle state, A/B test assignments, and cookie consent choice.</p>
                    <div className="mt-2 text-xs text-slate-500">
                      <p><strong>Examples:</strong> ts_cookie_consent (your consent choice), ts_ab_* (A/B test assignments)</p>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">How we handle consent</h2>
                <p className="text-slate-600 leading-relaxed">When you first visit TrendScout, a cookie consent banner is displayed. Analytics and marketing cookies are not set until you explicitly accept them. If you reject non-essential cookies, only essential and preference cookies will be used.</p>
                <p className="text-slate-600 leading-relaxed mt-2">Your consent choice is saved in localStorage so we remember your preference on future visits.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Third-party cookies</h2>
                <p className="text-slate-600 leading-relaxed">If you accept analytics cookies, Google Analytics (GA4) may set its own cookies. You can learn more about how Google uses data at the <a href="https://policies.google.com/privacy" className="text-indigo-600" rel="noopener noreferrer" target="_blank">Google Privacy Policy</a>.</p>
                <p className="text-slate-600 leading-relaxed mt-2">We do not use marketing or advertising tracking pixels unless explicitly stated.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Managing cookies</h2>
                <p className="text-slate-600 leading-relaxed">You can control and delete cookies through your browser settings. Note that disabling essential cookies may affect the functionality of TrendScout. Most browsers allow you to refuse or accept cookies, delete existing cookies, and set preferences for certain websites.</p>
                <p className="text-slate-600 leading-relaxed mt-2">To change your cookie consent preference on TrendScout, clear your browser&apos;s localStorage for this site and refresh the page. The consent banner will reappear.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Contact</h2>
                <p className="text-slate-600 leading-relaxed">If you have questions about our use of cookies, contact us at <a href="mailto:info@trendscout.click" className="text-indigo-600">info@trendscout.click</a>.</p>
              </section>
            </div>

            <div className="mt-10 pt-6 border-t border-slate-100">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Related policies</h3>
              <div className="flex flex-wrap gap-2">
                <Link to="/privacy" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">Privacy Policy</Link>
                <Link to="/terms" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">Terms of Service</Link>
                <Link to="/refund-policy" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">Refund Policy</Link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
