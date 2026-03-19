import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import { ArrowRight, Check, ChevronDown, ChevronUp } from 'lucide-react';
import { trackEvent, EVENTS } from '@/services/analytics';
import PageMeta, { faqSchema, breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import { useState } from 'react';

/**
 * Reusable SEO landing page template.
 * Props: headline, subtitle, intro, features[], steps[], faqs[], ctaText, relatedLinks[], canonical, metaDesc
 */
export default function SeoLandingTemplate({ headline, subtitle, intro, features, steps, ukPoints, faqs, ctaText, relatedLinks, children, canonical, metaDesc }) {
  const [openFaq, setOpenFaq] = useState(null);

  const schemas = [];
  if (canonical) schemas.push(webPageSchema(headline, metaDesc || subtitle, canonical));
  if (canonical) schemas.push(breadcrumbSchema([{ name: 'Home', url: '/' }, { name: headline }]));
  if (faqs && faqs.length) schemas.push(faqSchema(faqs));

  return (
    <LandingLayout>
      {canonical && (
        <PageMeta title={headline} description={metaDesc || subtitle} canonical={canonical} schema={schemas} />
      )}
      <div className="bg-white">
        {/* Hero */}
        <section className="pt-16 pb-12 px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">{headline}</h1>
            {subtitle && <p className="mt-4 text-lg text-slate-600 leading-relaxed">{subtitle}</p>}
          </div>
        </section>

        {/* Intro */}
        {intro && (
          <section className="pb-12 px-6">
            <div className="max-w-3xl mx-auto text-base text-slate-600 leading-relaxed space-y-3">
              {intro.map((p, i) => <p key={i}>{p}</p>)}
            </div>
          </section>
        )}

        {/* Features */}
        {features && features.length > 0 && (
          <section className="py-14 bg-slate-50 px-6">
            <div className="max-w-4xl mx-auto">
              <h2 className="font-manrope text-xl font-bold text-slate-900 mb-8">What TrendScout offers</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                {features.map((f) => {
                  const Icon = f.icon;
                  return (
                    <div key={f.title} className="rounded-lg border border-slate-200 bg-white p-5">
                      {Icon && <Icon className="h-5 w-5 text-indigo-600 mb-2" />}
                      <h3 className="text-sm font-semibold text-slate-900">{f.title}</h3>
                      <p className="text-sm text-slate-500 mt-1 leading-relaxed">{f.desc}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* Steps */}
        {steps && steps.length > 0 && (
          <section className="py-14 bg-white px-6">
            <div className="max-w-4xl mx-auto">
              <h2 className="font-manrope text-xl font-bold text-slate-900 mb-8">How it works</h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
                {steps.map((s, i) => (
                  <div key={i}>
                    <span className="font-mono text-xs font-bold text-indigo-500">{String(i + 1).padStart(2, '0')}</span>
                    <h3 className="font-manrope text-sm font-semibold text-slate-900 mt-2">{s.title}</h3>
                    <p className="text-sm text-slate-500 mt-1 leading-relaxed">{s.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* UK Points */}
        {ukPoints && ukPoints.length > 0 && (
          <section className="py-14 bg-slate-50 px-6">
            <div className="max-w-4xl mx-auto">
              <h2 className="font-manrope text-xl font-bold text-slate-900 mb-6">Why this matters for UK sellers</h2>
              <ul className="space-y-3">
                {ukPoints.map((point, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-sm text-slate-600">
                    <Check className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          </section>
        )}

        {/* Custom children */}
        {children}

        {/* FAQ */}
        {faqs && faqs.length > 0 && (
          <section className="py-14 bg-white px-6">
            <div className="max-w-2xl mx-auto">
              <h2 className="font-manrope text-xl font-bold text-slate-900 mb-6">Frequently asked questions</h2>
              <div className="space-y-2">
                {faqs.map((faq, idx) => (
                  <div key={idx} className="border border-slate-200 rounded-lg">
                    <button className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors" onClick={() => setOpenFaq(openFaq === idx ? null : idx)}>
                      <span className="text-sm font-medium text-slate-900">{faq.q}</span>
                      {openFaq === idx ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
                    </button>
                    {openFaq === idx && <div className="px-4 pb-4"><p className="text-sm text-slate-600 leading-relaxed">{faq.a}</p></div>}
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* CTA */}
        <section className="py-14 bg-slate-50 px-6">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-manrope text-2xl font-bold text-slate-900">{ctaText || 'Start validating products today'}</h2>
            <p className="mt-3 text-base text-slate-500">Free to start. No credit card needed.</p>
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-6 h-11" onClick={() => trackEvent(EVENTS.UK_LANDING_CTA, { page_type: 'seo_landing', cta_label: 'Start Free' })}>
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/trending-products">
                <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-white rounded-lg font-medium px-6 h-11">
                  See Trending Products
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Related Links */}
        {relatedLinks && relatedLinks.length > 0 && (
          <section className="py-10 bg-white px-6">
            <div className="max-w-4xl mx-auto">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Related pages</h3>
              <div className="flex flex-wrap gap-2">
                {relatedLinks.map((link) => (
                  <Link key={link.href} to={link.href} className="text-sm text-indigo-600 hover:text-indigo-700 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          </section>
        )}
      </div>
    </LandingLayout>
  );
}
