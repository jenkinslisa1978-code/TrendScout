import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { faqSchema, breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import { ViabilityBadge } from '@/components/ViabilityBadge';
import {
  ArrowRight, Shield, TrendingUp, Target, PoundSterling, Truck,
  RefreshCw, Layers, Globe, Search, BarChart3, ChevronDown, ChevronUp,
} from 'lucide-react';

const FACTORS = [
  { icon: TrendingUp, name: 'Trend momentum', weight: '15%', desc: 'Measures whether demand is growing, stable, or declining over the past 30 days across TikTok, Amazon, and Google Trends.' },
  { icon: Layers, name: 'Market saturation', weight: '15%', desc: 'Analyses how many sellers are already active in this product space. High saturation reduces the viability score.' },
  { icon: PoundSterling, name: 'Margin potential', weight: '20%', desc: 'Estimates whether the product can be sold profitably after supplier costs, UK shipping, 20% VAT, platform fees, and estimated returns.' },
  { icon: Truck, name: 'Shipping practicality', weight: '10%', desc: 'Evaluates whether the product can be reliably shipped to UK customers within acceptable timeframes and costs.' },
  { icon: RefreshCw, name: 'Return risk', weight: '10%', desc: 'Estimates return friction based on product category. Fragile, sizing-dependent, and electronics products score lower.' },
  { icon: Globe, name: 'Channel fit', weight: '15%', desc: 'Assesses which UK sales channels (Shopify, Amazon.co.uk, TikTok Shop UK) suit this product and scores accordingly.' },
  { icon: Target, name: 'UK commercial fit', weight: '15%', desc: 'A composite signal combining UK consumer demand patterns, local competition density, and general market readiness.' },
];

const EXAMPLES = [
  { name: 'Portable Neck Fan', score: 78, band: 'Strong UK Fit', reason: 'Strong summer demand signal, reasonable margins after VAT, low shipping weight, growing TikTok interest, moderate saturation.' },
  { name: 'LED Strip Lights', score: 42, band: 'Weak UK Fit', reason: 'Highly saturated category with thin margins. Many UK sellers already active. Returns risk for electrical products.' },
  { name: 'Magnetic Phone Mount', score: 61, band: 'Moderate UK Fit', reason: 'Steady demand and reasonable margins, but competition is growing and ad costs are rising in this category.' },
];

const FAQS = [
  { q: 'How accurate is the UK Viability Score?', a: 'The score is an indicator to help prioritise products, not a guarantee. It combines multiple data signals to estimate commercial viability, but you should always verify key assumptions with your own research before committing.' },
  { q: 'How often is the score updated?', a: 'Scores are recalculated daily as new trend, competition, and market data becomes available. Each product page shows when its data was last refreshed.' },
  { q: 'What makes this different from a launch score?', a: 'The launch score measures overall product opportunity across all markets. The UK Viability Score specifically focuses on whether a product can work in the UK — factoring in VAT, UK shipping, local competition, and UK consumer demand.' },
  { q: 'Can I see the individual factor breakdown?', a: 'Yes. On any product detail page, you can see how the score breaks down across all seven factors, helping you identify specific strengths and risks.' },
  { q: 'Does a low score mean I should not sell the product?', a: 'Not necessarily. A low score means more signals are pointing to challenges. Some sellers succeed with low-scoring products by finding a niche angle or having a cost advantage. The score helps you prioritise, not dictate.' },
  { q: 'Is the score UK-specific or global?', a: 'The UK Viability Score is entirely UK-focused. It factors in UK-specific costs, competition, demand, and market dynamics that differ from other regions.' },
];

export default function ViabilityScorePage() {
  const [openFaq, setOpenFaq] = useState(null);

  return (
    <LandingLayout>
      <PageMeta
        title="UK Product Viability Score"
        description="Understand the UK Product Viability Score — a 0-100 rating that measures whether a product can sell profitably in the UK market. Built for Shopify, Amazon UK, and TikTok Shop sellers."
        canonical="/uk-product-viability-score"
        schema={[
          webPageSchema('UK Product Viability Score', 'A 0-100 score measuring commercial viability of products in the UK ecommerce market.', '/uk-product-viability-score'),
          faqSchema(FAQS),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'UK Product Viability Score' }]),
        ]}
      />
      <div className="bg-white" data-testid="viability-score-page">
        {/* Hero */}
        <section className="pt-16 pb-10 px-6">
          <div className="max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 border border-indigo-100 px-3 py-1 mb-5">
              <Shield className="h-3.5 w-3.5 text-indigo-600" />
              <span className="text-xs font-medium text-indigo-700">Flagship Feature</span>
            </div>
            <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight" data-testid="viability-headline">
              UK Product Viability Score
            </h1>
            <p className="mt-4 text-lg text-slate-600 leading-relaxed">
              A 0-100 score that measures whether a product can sell profitably in the UK. Not just popularity — commercial viability. Factoring in VAT, margins, saturation, shipping, returns, and channel fit.
            </p>
            <div className="mt-6 flex items-center gap-4">
              <ViabilityBadge score={78} size="lg" showLabel expandable productName="Example Product" />
              <span className="text-sm text-slate-500">Example: Portable Neck Fan</span>
            </div>
          </div>
        </section>

        {/* Why UK sellers need this */}
        <section className="py-14 bg-slate-50 px-6">
          <div className="max-w-3xl mx-auto">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-4">Why UK sellers need a viability score</h2>
            <p className="text-base text-slate-600 leading-relaxed mb-4">
              Trending product lists are everywhere. But a product that is trending globally might be unprofitable, over-saturated, or impractical for UK sellers. The UK market has unique economics:
            </p>
            <ul className="space-y-2 text-sm text-slate-600">
              <li className="flex items-start gap-2"><PoundSterling className="h-4 w-4 text-indigo-600 mt-0.5 flex-shrink-0" /> <strong>20% VAT</strong> significantly impacts margins compared to US sellers</li>
              <li className="flex items-start gap-2"><Truck className="h-4 w-4 text-indigo-600 mt-0.5 flex-shrink-0" /> <strong>Higher shipping costs</strong> from overseas suppliers to UK addresses</li>
              <li className="flex items-start gap-2"><Target className="h-4 w-4 text-indigo-600 mt-0.5 flex-shrink-0" /> <strong>Smaller addressable market</strong> requiring different volume assumptions</li>
              <li className="flex items-start gap-2"><RefreshCw className="h-4 w-4 text-indigo-600 mt-0.5 flex-shrink-0" /> <strong>UK consumer protection</strong> and returns expectations differ significantly</li>
              <li className="flex items-start gap-2"><Layers className="h-4 w-4 text-indigo-600 mt-0.5 flex-shrink-0" /> <strong>Different saturation levels</strong> — what is crowded in the US might still have space in the UK</li>
            </ul>
            <p className="text-base text-slate-600 leading-relaxed mt-4">
              The UK Viability Score solves this by combining multiple signals into a single, interpretable number specifically calibrated for UK market conditions.
            </p>
          </div>
        </section>

        {/* How the score is calculated */}
        <section className="py-14 bg-white px-6" data-testid="viability-factors">
          <div className="max-w-4xl mx-auto">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-3">How the score is calculated</h2>
            <p className="text-base text-slate-600 mb-8">
              The UK Viability Score is a weighted composite of seven factors. Each factor is scored individually and combined into an overall 0-100 rating.
            </p>
            <div className="space-y-3">
              {FACTORS.map((f) => {
                const Icon = f.icon;
                return (
                  <div key={f.name} className="rounded-lg border border-slate-200 p-5 hover:border-slate-300 transition-colors" data-testid={`viability-factor-${f.name.toLowerCase().replace(/\s/g, '-')}`}>
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 flex-shrink-0">
                        <Icon className="h-4.5 w-4.5" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold text-slate-900">{f.name}</h3>
                          <span className="font-mono text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">{f.weight}</span>
                        </div>
                        <p className="mt-1.5 text-sm text-slate-500 leading-relaxed">{f.desc}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Score interpretation */}
        <section className="py-14 bg-slate-50 px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-8">How to interpret the score</h2>
            <div className="grid sm:grid-cols-3 gap-4">
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-5">
                <div className="flex items-center gap-2 mb-2">
                  <ViabilityBadge score={78} size="sm" showLabel={false} />
                  <span className="font-mono text-sm font-bold text-emerald-800">70–100</span>
                </div>
                <h3 className="text-sm font-semibold text-emerald-800 mb-1">Strong UK Fit</h3>
                <p className="text-xs text-slate-600 leading-relaxed">Multiple signals suggest this product has strong commercial potential in the UK. Worth prioritising for testing.</p>
              </div>
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-5">
                <div className="flex items-center gap-2 mb-2">
                  <ViabilityBadge score={55} size="sm" showLabel={false} />
                  <span className="font-mono text-sm font-bold text-amber-800">45–69</span>
                </div>
                <h3 className="text-sm font-semibold text-amber-800 mb-1">Moderate UK Fit</h3>
                <p className="text-xs text-slate-600 leading-relaxed">Some positive indicators but also notable risks. Review the individual factor breakdown before deciding.</p>
              </div>
              <div className="rounded-lg border border-red-200 bg-red-50 p-5">
                <div className="flex items-center gap-2 mb-2">
                  <ViabilityBadge score={30} size="sm" showLabel={false} />
                  <span className="font-mono text-sm font-bold text-red-800">0–44</span>
                </div>
                <h3 className="text-sm font-semibold text-red-800 mb-1">Weak UK Fit</h3>
                <p className="text-xs text-slate-600 leading-relaxed">Multiple signals suggest challenges for UK sellers. Not recommended without strong conviction or unique advantage.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Examples */}
        <section className="py-14 bg-white px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-6">Example scores</h2>
            <div className="space-y-4">
              {EXAMPLES.map((ex) => (
                <div key={ex.name} className="rounded-lg border border-slate-200 p-5">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-semibold text-slate-900">{ex.name}</h3>
                    <ViabilityBadge score={ex.score} showLabel />
                  </div>
                  <p className="text-sm text-slate-500 leading-relaxed">{ex.reason}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-14 bg-slate-50 px-6">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-8">Frequently asked questions</h2>
            <div className="space-y-2" data-testid="viability-faq">
              {FAQS.map((faq, idx) => (
                <div key={idx} className="border border-slate-200 rounded-lg bg-white">
                  <button className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors" onClick={() => setOpenFaq(openFaq === idx ? null : idx)} data-testid={`viability-faq-${idx}`}>
                    <span className="text-sm font-medium text-slate-900">{faq.q}</span>
                    {openFaq === idx ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
                  </button>
                  {openFaq === idx && <div className="px-4 pb-4"><p className="text-sm text-slate-600 leading-relaxed">{faq.a}</p></div>}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-14 bg-white px-6">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-manrope text-2xl font-bold text-slate-900">
              See UK Viability Scores on real products
            </h2>
            <p className="mt-3 text-base text-slate-500">
              Browse trending products with viability scores, margin estimates, and saturation data — free to start.
            </p>
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-6 h-11" data-testid="viability-cta-signup">
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/trending-products">
                <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg font-medium px-6 h-11" data-testid="viability-cta-products">
                  Browse Trending Products
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Related */}
        <section className="py-8 bg-slate-50 px-6">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Related</h3>
            <div className="flex flex-wrap gap-2">
              <Link to="/how-it-works" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">How It Works</Link>
              <Link to="/uk-product-research" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">UK Product Research</Link>
              <Link to="/pricing" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">Pricing</Link>
              <Link to="/free-tools" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">Free Tools</Link>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
