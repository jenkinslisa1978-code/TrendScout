import React from 'react';
import LandingLayout from '@/components/layouts/LandingLayout';
import PageMeta, { breadcrumbSchema } from '@/components/PageMeta';

export default function CookiePolicyPage() {
  return (
    <LandingLayout>
      <PageMeta
        title="Cookie Policy"
        description="How TrendScout uses cookies and similar technologies."
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
                <h2 className="font-manrope text-lg font-bold text-slate-900">How we use cookies</h2>
                <p className="text-slate-600 leading-relaxed">TrendScout uses cookies for the following purposes:</p>
                <ul className="mt-2 space-y-2 text-sm text-slate-600">
                  <li><strong>Essential cookies:</strong> Required for the website to function. These handle authentication, session management, and security. You cannot opt out of these.</li>
                  <li><strong>Analytics cookies:</strong> We use analytics to understand how visitors use TrendScout, which pages are popular, and where improvements are needed. This data is aggregated and does not personally identify you.</li>
                  <li><strong>Preference cookies:</strong> Remember your settings and preferences such as billing toggle state and tool selections.</li>
                </ul>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Third-party cookies</h2>
                <p className="text-slate-600 leading-relaxed">We may use Google Analytics (GA4) to measure site usage. Google Analytics uses its own cookies. You can learn more about how Google uses data at <a href="https://policies.google.com/privacy" className="text-indigo-600" rel="noopener noreferrer" target="_blank">Google Privacy Policy</a>.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Managing cookies</h2>
                <p className="text-slate-600 leading-relaxed">You can control and delete cookies through your browser settings. Note that disabling essential cookies may affect the functionality of TrendScout. Most browsers allow you to refuse or accept cookies, delete existing cookies, and set preferences for certain websites.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Contact</h2>
                <p className="text-slate-600 leading-relaxed">If you have questions about our use of cookies, contact us at <a href="mailto:info@trendscout.click" className="text-indigo-600">info@trendscout.click</a>.</p>
              </section>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
