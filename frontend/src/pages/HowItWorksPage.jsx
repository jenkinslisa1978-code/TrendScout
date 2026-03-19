import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { faqSchema, breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import {
  ArrowRight, Search, BarChart3, Shield, Zap, TrendingUp,
  Target, PoundSterling, Truck, RefreshCw, Layers, Globe,
  Check, X, AlertTriangle,
} from 'lucide-react';

const SIGNALS = [
  { name: 'Trend momentum', weight: '20%', desc: 'Measures whether demand for a product is growing, stable, or declining. Based on search volume changes, social engagement velocity, and marketplace listing growth over the past 30 days.', icon: TrendingUp },
  { name: 'Market saturation', weight: '15%', desc: 'Analyses how many sellers are already active in this product space. High saturation reduces score. Factors in ad competition density and marketplace listing count.', icon: Shield },
  { name: 'Margin potential', weight: '20%', desc: 'Estimates whether the product can be sold profitably after accounting for supplier costs, shipping to UK, VAT, platform fees, and returns.', icon: PoundSterling },
  { name: 'Ad opportunity', weight: '15%', desc: 'Evaluates whether there is room to advertise profitably. Oversaturated ad channels score lower. Considers CPM estimates and ad creative diversity.', icon: Target },
  { name: 'Search growth', weight: '10%', desc: 'Tracks whether people are actively searching for this product or related terms. Uses Google Trends data and marketplace search volume indicators.', icon: Search },
  { name: 'Social buzz', weight: '10%', desc: 'Measures organic social media engagement including TikTok views, shares, and comment sentiment. High engagement with positive sentiment scores well.', icon: Globe },
  { name: 'Supplier availability', weight: '10%', desc: 'Checks whether there are reliable suppliers with reasonable lead times, minimum order quantities, and shipping options to the UK.', icon: Truck },
];

const STEPS = [
  {
    num: '01',
    title: 'Discover trending products',
    desc: 'TrendScout continuously monitors product activity across TikTok, Amazon, Shopify stores, and Google Trends. When a product starts gaining traction across multiple channels, it appears in our trending feed with a preliminary score.',
    detail: 'Products are not just scraped from one source. We look for signals that appear across multiple channels simultaneously, which is a much stronger indicator of genuine demand than a single viral video.',
  },
  {
    num: '02',
    title: 'Evaluate with the 7-signal scoring model',
    desc: 'Each product is scored across seven weighted signals: trend momentum, market saturation, margin potential, ad opportunity, search growth, social buzz, and supplier availability.',
    detail: 'The overall launch score (0-100) gives you a single number to help prioritise products. But the individual signal breakdown is often more useful — a product might score well overall but have a critical weakness in one area.',
  },
  {
    num: '03',
    title: 'Check UK-specific viability',
    desc: 'This is where TrendScout differs from generic tools. We estimate whether the product can work commercially in the UK by factoring in VAT, UK shipping costs, realistic margins, returns friction, and channel suitability.',
    detail: 'A product trending in the US might have completely different economics in the UK. Higher shipping costs, 20% VAT, different consumer expectations, and smaller addressable markets all change the equation.',
  },
  {
    num: '04',
    title: 'Make a launch decision with confidence',
    desc: 'Use the product analysis, AI-generated ad angles, supplier data, and competitive intelligence to decide whether to test this product. If you proceed, you do so with data — not just a hunch.',
    detail: 'TrendScout does not tell you to launch. It gives you the information to make a better-informed decision. The goal is fewer wasted ad spends and fewer failed product tests.',
  },
];

const GOOD_FIT = [
  'UK-based Shopify store owners looking for new products to test',
  'Amazon UK sellers researching product opportunities',
  'TikTok Shop UK sellers who want data behind their product picks',
  'Dropshippers targeting UK customers who need margin and saturation data',
  'Ecommerce founders who want to validate ideas before investing',
  'Agencies researching products for clients',
];

const NOT_FIT = [
  'Sellers who only operate in the US market (use US-focused tools instead)',
  'People looking for a magic "winning product" list with no analysis needed',
  'Businesses that need manufacturing or wholesale sourcing (we focus on research)',
];

const FAQS = [
  { q: 'How accurate are the launch scores?', a: 'Launch scores are indicators, not guarantees. They help you prioritise and filter products, but no tool can predict exact sales outcomes. We recommend using the score as one input alongside your own market knowledge and testing.' },
  { q: 'How often is the data updated?', a: 'Product scores and trend data are refreshed daily. New products are added as they start gaining multi-channel traction. Data freshness indicators on each product show exactly when it was last updated.' },
  { q: 'What data sources does TrendScout use?', a: 'We aggregate signals from TikTok engagement data, Amazon marketplace activity, Google Trends search data, Shopify store monitoring, and ad platform activity. This multi-source approach gives more reliable signals than single-channel tools.' },
  { q: 'Can I trust the margin estimates?', a: 'Margin estimates are based on average supplier costs, typical UK selling prices, VAT, and shipping estimates. They are useful for initial screening but you should verify exact costs with your specific suppliers and pricing strategy before committing.' },
  { q: 'Does TrendScout work for non-UK sellers?', a: 'TrendScout is designed for sellers targeting UK customers. If your primary market is the UK, it is useful regardless of where you are based. For sellers focused purely on the US market, a US-focused tool would be more appropriate.' },
  { q: 'What does "saturation" actually mean?', a: 'Saturation measures how crowded a product space already is. It factors in the number of active sellers, ad competition density, and marketplace listing growth. High saturation means more competition for the same customers.' },
];

export default function HowItWorksPage() {
  return (
    <LandingLayout>
      <PageMeta
        title="How It Works"
        description="Learn how TrendScout evaluates products using a 7-signal scoring model, UK-specific viability analysis, and multi-channel trend detection."
        canonical="/how-it-works"
        schema={[
          webPageSchema('How TrendScout Works', 'Learn how TrendScout evaluates products using a 7-signal scoring model and UK-specific viability analysis.', '/how-it-works'),
          faqSchema(FAQS),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'How It Works' }]),
        ]}
      />
      <div className="bg-white" data-testid="how-it-works-page">
        {/* Hero */}
        <section className="pt-16 pb-12 px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight" data-testid="hiw-headline">
              How TrendScout works
            </h1>
            <p className="mt-4 text-lg text-slate-600 leading-relaxed">
              TrendScout is a product research and validation platform built for UK ecommerce sellers. It helps you discover trending products, evaluate their commercial viability, and make faster launch decisions backed by data instead of guesswork.
            </p>
          </div>
        </section>

        {/* 4-Step Process */}
        <section className="py-16 bg-slate-50" data-testid="hiw-steps">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-10">
              The process: from trend signal to launch decision
            </h2>
            <div className="space-y-8">
              {STEPS.map((step) => (
                <div key={step.num} className="rounded-xl border border-slate-200 bg-white p-6" data-testid={`hiw-step-${step.num}`}>
                  <div className="flex items-start gap-4">
                    <span className="font-mono text-sm font-bold text-indigo-600 bg-indigo-50 rounded-md px-2.5 py-1 flex-shrink-0">{step.num}</span>
                    <div>
                      <h3 className="font-manrope text-lg font-semibold text-slate-900">{step.title}</h3>
                      <p className="mt-2 text-sm text-slate-600 leading-relaxed">{step.desc}</p>
                      <p className="mt-3 text-sm text-slate-500 leading-relaxed border-l-2 border-slate-200 pl-4">{step.detail}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 7-Signal Scoring */}
        <section className="py-16 bg-white" data-testid="hiw-signals">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-3">
              The 7-signal scoring model
            </h2>
            <p className="text-base text-slate-600 mb-10 max-w-2xl">
              Every product receives a launch score from 0 to 100. This score is calculated from seven weighted signals that together indicate whether a product is worth testing.
            </p>
            <div className="space-y-3">
              {SIGNALS.map((signal) => {
                const Icon = signal.icon;
                return (
                  <div key={signal.name} className="rounded-lg border border-slate-200 p-5 hover:border-slate-300 transition-colors" data-testid={`signal-${signal.name.toLowerCase().replace(/\s/g, '-')}`}>
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 flex-shrink-0">
                        <Icon className="h-4.5 w-4.5" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold text-slate-900">{signal.name}</h3>
                          <span className="font-mono text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">{signal.weight}</span>
                        </div>
                        <p className="mt-1.5 text-sm text-slate-500 leading-relaxed">{signal.desc}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Score Interpretation */}
        <section className="py-16 bg-slate-50">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-8">
              How to interpret scores
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { range: '75-100', label: 'Strong candidate', color: 'border-emerald-200 bg-emerald-50', text: 'text-emerald-800', desc: 'Multiple strong signals. Worth prioritising for testing.' },
                { range: '55-74', label: 'Promising', color: 'border-blue-200 bg-blue-50', text: 'text-blue-800', desc: 'Solid potential with some caveats. Review individual signals.' },
                { range: '35-54', label: 'Mixed signals', color: 'border-amber-200 bg-amber-50', text: 'text-amber-800', desc: 'Some positive indicators but notable risks. Proceed carefully.' },
                { range: '0-34', label: 'High risk', color: 'border-red-200 bg-red-50', text: 'text-red-800', desc: 'Multiple weak signals. Not recommended without strong conviction.' },
              ].map((tier) => (
                <div key={tier.range} className={`rounded-lg border p-5 ${tier.color}`}>
                  <span className={`font-mono text-lg font-bold ${tier.text}`}>{tier.range}</span>
                  <p className={`text-sm font-semibold mt-1 ${tier.text}`}>{tier.label}</p>
                  <p className="text-xs text-slate-600 mt-2 leading-relaxed">{tier.desc}</p>
                </div>
              ))}
            </div>
            <p className="mt-6 text-sm text-slate-500">
              Scores are relative and best used for prioritisation and comparison. A high score does not guarantee success — it means more signals are pointing in a positive direction.
            </p>
          </div>
        </section>

        {/* Who it's for / not for */}
        <section className="py-16 bg-white">
          <div className="max-w-4xl mx-auto px-6">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h2 className="font-manrope text-xl font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Check className="h-5 w-5 text-emerald-600" /> Who TrendScout is for
                </h2>
                <ul className="space-y-3">
                  {GOOD_FIT.map((item) => (
                    <li key={item} className="flex items-start gap-2.5 text-sm text-slate-600">
                      <Check className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h2 className="font-manrope text-xl font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <X className="h-5 w-5 text-red-500" /> Who it is not for
                </h2>
                <ul className="space-y-3">
                  {NOT_FIT.map((item) => (
                    <li key={item} className="flex items-start gap-2.5 text-sm text-slate-600">
                      <X className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* UK Viability Section */}
        <section className="py-16 bg-slate-50">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-3">
              Why UK-specific product research matters
            </h2>
            <p className="text-base text-slate-600 mb-8 max-w-2xl">
              Most product research tools are built for US sellers. But the UK market has different economics, regulations, and consumer behaviour that change whether a product is actually viable.
            </p>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { icon: PoundSterling, title: 'VAT adds 20%', desc: 'UK sellers must account for 20% VAT on most products, which significantly impacts margins compared to US pricing.' },
                { icon: Truck, title: 'Shipping costs differ', desc: 'Shipping to UK customers from overseas suppliers often costs more and takes longer than US equivalents.' },
                { icon: Target, title: 'Smaller addressable market', desc: 'The UK market is roughly one-fifth the size of the US. Products need different volume expectations.' },
                { icon: RefreshCw, title: 'Returns friction', desc: 'UK consumer protection laws and expectations around returns differ from other markets.' },
                { icon: Layers, title: 'Different saturation levels', desc: 'A product might be oversaturated in the US but still have opportunity in the UK, or vice versa.' },
                { icon: Globe, title: 'Channel fit varies', desc: 'TikTok Shop UK, Amazon.co.uk, and Shopify UK each have different product-market dynamics.' },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.title} className="rounded-lg border border-slate-200 bg-white p-5">
                    <Icon className="h-5 w-5 text-indigo-600 mb-2" />
                    <h3 className="text-sm font-semibold text-slate-900">{item.title}</h3>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-16 bg-white">
          <div className="max-w-2xl mx-auto px-6">
            <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-8">Frequently asked questions</h2>
            <div className="space-y-4">
              {FAQS.map((faq, idx) => (
                <div key={idx}>
                  <h3 className="text-sm font-semibold text-slate-900">{faq.q}</h3>
                  <p className="mt-1.5 text-sm text-slate-500 leading-relaxed">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-16 bg-slate-50">
          <div className="max-w-2xl mx-auto px-6 text-center">
            <h2 className="font-manrope text-2xl font-bold text-slate-900">
              Ready to validate your next product?
            </h2>
            <p className="mt-3 text-base text-slate-500">
              Start free and browse trending products with real scores and UK viability data.
            </p>
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-6 h-11" data-testid="hiw-cta-signup">
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/trending-products">
                <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-white rounded-lg font-medium px-6 h-11" data-testid="hiw-cta-products">
                  Browse Trending Products
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
