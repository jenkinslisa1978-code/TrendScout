import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import LandingLayout from '@/components/layouts/LandingLayout';
import {
  HelpCircle, Search, BarChart3, Rocket, ShoppingBag,
  Megaphone, Mail, ChevronRight, ArrowRight,
} from 'lucide-react';

const faqs = [
  { q: 'What is TrendScout?', a: 'TrendScout is an AI-powered platform that helps ecommerce sellers discover trending products, evaluate whether they are worth testing, and get simple launch ideas — before spending money on ads.' },
  { q: 'How does the Launch Score work?', a: 'The Launch Score (0–100) is calculated from multiple signals: search growth, social media traction, product uniqueness, visual ad potential, competition level, profit margin, and audience size. A higher score means stronger potential.' },
  { q: 'Is TrendScout free?', a: 'Yes, there is a free plan that lets you browse trending products and view basic analyses. Paid plans unlock deeper analytics, ad generation, and Shopify integration.' },
  { q: 'How do I connect my Shopify store?', a: 'Go to Dashboard > Connections, enter your store domain, and follow the Shopify OAuth flow to securely connect your store. You can then export products directly.' },
  { q: 'Where does TrendScout get its data?', a: 'We aggregate data from multiple sources including Google Trends, TikTok, Amazon, and other ecommerce signals. Our AI processes these into a single actionable score.' },
  { q: 'Can I cancel my subscription?', a: 'Yes, you can cancel anytime from your account settings. Your access continues until the end of the billing period.' },
  { q: 'How often is product data updated?', a: 'Product scores and trending data are updated daily. Some signals (like TikTok views) update more frequently.' },
];

const howItWorks = [
  { icon: Search, title: 'Find a product', desc: 'Browse products gaining traction online. Filter by category, score, or trend stage.' },
  { icon: BarChart3, title: 'Check the launch score', desc: 'TrendScout analyses demand, competition, margins, and ad potential to give you a 0–100 score.' },
  { icon: ShoppingBag, title: 'Decide and act', desc: 'Use the UK Viability Score, margin estimates, and competition data to make a confident go/no-go decision on whether to test the product.' },
  { icon: Megaphone, title: 'Launch ads', desc: 'Get AI-generated ad creative ideas and target audience suggestions. Test with a small budget.' },
  { icon: Rocket, title: 'Evaluate results', desc: 'Track performance and decide whether to scale, pivot, or move on.' },
];

export default function HelpPage() {
  return (
    <LandingLayout>
      <Helmet>
        <title>Help & FAQ - TrendScout</title>
        <meta name="description" content="Frequently asked questions about TrendScout. Learn how the platform works, how the Launch Score is calculated, and how to get started." />
      </Helmet>

      <div className="mx-auto max-w-4xl px-6 py-16" data-testid="help-page">
        <div className="text-center mb-14">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center mx-auto mb-4 shadow-lg">
            <HelpCircle className="h-7 w-7 text-white" />
          </div>
          <h1 className="font-manrope text-4xl font-extrabold text-slate-900" data-testid="help-title">Help & FAQ</h1>
          <p className="mt-3 text-slate-500 max-w-lg mx-auto">Everything you need to know about using TrendScout.</p>
        </div>

        {/* How TrendScout Works */}
        <section className="mb-16" data-testid="how-it-works-help">
          <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-6">How TrendScout Works</h2>
          <div className="space-y-4">
            {howItWorks.map((step, i) => {
              const Icon = step.icon;
              return (
                <div key={i} className="flex items-start gap-4 bg-white rounded-xl border border-slate-100 p-5 hover:shadow-sm transition-shadow">
                  <div className="flex-shrink-0 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 text-sm">Step {i + 1}: {step.title}</h3>
                    <p className="text-sm text-slate-500 mt-1">{step.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* FAQ */}
        <section className="mb-16" data-testid="faq-section">
          <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-6">Frequently Asked Questions</h2>
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <details key={i} className="group bg-white rounded-xl border border-slate-100 overflow-hidden" data-testid={`faq-${i}`}>
                <summary className="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-slate-50 transition-colors">
                  <span className="font-medium text-sm text-slate-900">{faq.q}</span>
                  <ChevronRight className="h-4 w-4 text-slate-400 group-open:rotate-90 transition-transform" />
                </summary>
                <div className="px-5 pb-4">
                  <p className="text-sm text-slate-500 leading-relaxed">{faq.a}</p>
                </div>
              </details>
            ))}
          </div>
        </section>

        {/* Support */}
        <section className="text-center bg-gradient-to-r from-indigo-50 to-violet-50 rounded-2xl p-8" data-testid="support-section">
          <Mail className="h-8 w-8 text-indigo-500 mx-auto mb-3" />
          <h2 className="font-manrope text-xl font-bold text-slate-900 mb-2">Still have questions?</h2>
          <p className="text-slate-500 text-sm mb-4">Our support team is here to help.</p>
          <a href="mailto:info@trendscout.click" className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2.5 rounded-xl transition-colors" data-testid="contact-support-btn">
            <Mail className="h-4 w-4" /> Contact Support
          </a>
        </section>
      </div>
    </LandingLayout>
  );
}
