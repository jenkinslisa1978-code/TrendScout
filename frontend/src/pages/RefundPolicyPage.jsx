import React from 'react';
import LandingLayout from '@/components/layouts/LandingLayout';
import PageMeta, { breadcrumbSchema } from '@/components/PageMeta';

export default function RefundPolicyPage() {
  return (
    <LandingLayout>
      <PageMeta
        title="Refund & Cancellation Policy"
        description="TrendScout refund policy, cancellation terms, and billing information."
        canonical="/refund-policy"
        schema={[breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Refund Policy' }])]}
      />
      <div className="bg-white" data-testid="refund-policy-page">
        <section className="pt-16 pb-20 px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-manrope text-3xl font-extrabold text-slate-900 tracking-tight">Refund & Cancellation Policy</h1>
            <p className="mt-2 text-sm text-slate-400">Last updated: March 2026</p>

            <div className="mt-8 prose prose-slate prose-sm max-w-none space-y-6">
              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Free trial</h2>
                <p className="text-slate-600 leading-relaxed">Paid plans include a 7-day free trial. You will not be charged during the trial period. If you cancel before the trial ends, no payment will be taken.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Cancellation</h2>
                <p className="text-slate-600 leading-relaxed">You can cancel your subscription at any time from your account settings. When you cancel, you retain access to paid features until the end of your current billing period. After that, your account reverts to the free plan.</p>
                <p className="text-slate-600 leading-relaxed mt-2">We do not require notice periods or impose cancellation fees.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Refunds</h2>
                <p className="text-slate-600 leading-relaxed">If you are not satisfied within the first 7 days of a paid subscription, contact us at <a href="mailto:info@trendscout.click" className="text-indigo-600">info@trendscout.click</a> and we will arrange a refund. After the first 7 days, cancellations take effect at the end of the billing period and no partial refunds are issued.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Annual plans</h2>
                <p className="text-slate-600 leading-relaxed">Annual subscriptions are billed once per year. If you cancel an annual plan, you retain access until the end of the annual period. Refund requests for annual plans within the first 14 days are handled on a case-by-case basis — contact us and we will do our best to help.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Billing</h2>
                <p className="text-slate-600 leading-relaxed">Payments are processed securely through Stripe. All prices are in British pounds (GBP). VAT may apply depending on your billing address. Invoices are available in your account settings.</p>
              </section>

              <section>
                <h2 className="font-manrope text-lg font-bold text-slate-900">Contact</h2>
                <p className="text-slate-600 leading-relaxed">For billing questions or refund requests, email <a href="mailto:info@trendscout.click" className="text-indigo-600">info@trendscout.click</a>. We aim to respond within 24 hours on business days.</p>
              </section>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
