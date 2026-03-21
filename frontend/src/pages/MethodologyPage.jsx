import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { breadcrumbSchema, webPageSchema, faqSchema } from '@/components/PageMeta';
import useScrollDepth from '@/hooks/useScrollDepth';
import { ArrowRight, Shield, TrendingUp, BarChart3, Package, Truck, Receipt, Target, Users, Eye, AlertTriangle } from 'lucide-react';

const SIGNALS = [
  {
    name: 'Trend Momentum',
    weight: 20,
    icon: TrendingUp,
    color: 'text-violet-600',
    bg: 'bg-violet-50',
    sources: ['Google Trends UK', 'TikTok trending data', 'Amazon Movers & Shakers UK'],
    description: 'Measures whether demand for this product is growing, stable, or declining in the UK. We analyse search volume trends, social media buzz, and marketplace velocity to determine if this is an emerging opportunity or a fading trend.',
    how: 'We pull 90-day search trend data and compare current volume to the 30-day and 90-day averages. Rising trends with 20%+ growth score highest.',
  },
  {
    name: 'Competition Level',
    weight: 15,
    icon: Users,
    color: 'text-orange-600',
    bg: 'bg-orange-50',
    sources: ['Amazon UK listings', 'Shopify store discovery', 'TikTok Shop listings'],
    description: 'Assesses how saturated the market is for this product in the UK. Products with fewer established competitors and less aggressive pricing wars score higher.',
    how: 'We count active sellers, check review counts of top listings, and analyse price clustering. Under 50 active sellers with no dominant brand scores highest.',
  },
  {
    name: 'Margin Potential',
    weight: 20,
    icon: BarChart3,
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
    sources: ['CJ Dropshipping pricing', 'AliExpress supplier data', 'UK marketplace selling prices'],
    description: 'Estimates the profit margin after accounting for UK-specific costs: 20% VAT, Royal Mail/courier shipping, platform fees, and typical return rates of 15-20%.',
    how: 'We calculate: (Selling Price ex-VAT) - (Supplier Cost + UK Shipping + Platform Fees + Estimated Returns). Products with 30%+ net margin score highest.',
  },
  {
    name: 'Supplier Availability',
    weight: 10,
    icon: Package,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    sources: ['CJ Dropshipping catalogue', 'AliExpress supplier ratings'],
    description: 'Checks whether the product can be reliably sourced with acceptable minimum order quantities and consistent quality.',
    how: 'We verify supplier ratings, check stock availability, and assess MOQ requirements. Products with 3+ verified suppliers score highest.',
  },
  {
    name: 'Shipping Practicality',
    weight: 10,
    icon: Truck,
    color: 'text-teal-600',
    bg: 'bg-teal-50',
    sources: ['Shipping rate APIs', 'Product dimension data'],
    description: 'Evaluates whether the product can be shipped to UK customers within acceptable timeframes and costs. Heavy, oversized, or fragile items score lower.',
    how: 'We estimate shipping costs based on weight/dimensions, check for ePacket/tracked delivery availability, and assess breakage risk. Under-500g items with 7-day delivery score highest.',
  },
  {
    name: 'Ad Viability',
    weight: 15,
    icon: Target,
    color: 'text-pink-600',
    bg: 'bg-pink-50',
    sources: ['TikTok ad library', 'Facebook ad estimates', 'Google Ads keyword planner'],
    description: 'Estimates whether the product can be profitably advertised in the UK. Products with low CPCs and high visual appeal score higher.',
    how: 'We check estimated CPC for related keywords, assess competition in ad auctions, and evaluate whether the product is visually demonstrable (important for social ads). CPA under 30% of margin scores highest.',
  },
  {
    name: 'UK Market Fit',
    weight: 10,
    icon: Eye,
    color: 'text-indigo-600',
    bg: 'bg-indigo-50',
    sources: ['UK consumer data', 'Seasonal patterns', 'Cultural relevance analysis'],
    description: 'Assesses whether the product specifically resonates with UK buyers, considering seasonal patterns, cultural preferences, and regulatory requirements.',
    how: 'We check for UK-specific demand signals, seasonal relevance, and any import/compliance restrictions. Products with proven UK demand and no regulatory barriers score highest.',
  },
];

const FAQS = [
  { question: 'How often is the data updated?', answer: 'Product scores are automatically refreshed every 4 hours. Trend data is pulled from live marketplace APIs. Each product card shows a "last updated" timestamp so you can see exactly how fresh the data is.' },
  { question: 'What data sources do you use?', answer: 'We pull data from Amazon UK (Movers & Shakers, BSR, pricing), TikTok (trending products, shop listings), Google Trends (UK search volume), CJ Dropshipping (supplier pricing and availability), and AliExpress (supplier ratings). Each signal shows its specific source.' },
  { question: 'How accurate are the margin estimates?', answer: 'Our margin estimates account for UK VAT (20%), estimated shipping costs, platform fees, and a 15-20% return rate. They are designed to be conservative — real margins may be slightly higher if you negotiate better supplier terms or have lower return rates. We recommend using our free Profit Margin Calculator with your actual supplier quotes for the most accurate figures.' },
  { question: 'Can I trust the viability score?', answer: 'The score is a data-driven starting point, not a guarantee. It synthesises 7 real signals into a single number to help you prioritise research. We always recommend verifying key assumptions (supplier pricing, actual demand, competitor analysis) before committing significant investment. Products scoring 70+ have historically shown the strongest commercial performance.' },
  { question: 'What does "confidence level" mean?', answer: 'Confidence indicates how much data we have to support the score. "High confidence" means we have fresh data from multiple sources. "Medium" means some data points are estimated. "Low" means limited data is available — treat the score as directional rather than precise.' },
];

export default function MethodologyPage() {
  useScrollDepth('methodology');

  return (
    <LandingLayout>
      <PageMeta
        title="How We Score Products — TrendScout Methodology"
        description="Full transparency on how TrendScout calculates the UK Product Viability Score. Learn about our 7 signals, data sources, and scoring methodology."
        canonical="/methodology"
        schema={[
          webPageSchema('TrendScout Scoring Methodology', 'How we calculate the UK Product Viability Score', '/methodology'),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Methodology' }]),
          faqSchema(FAQS),
        ]}
      />
      <div className="bg-white" data-testid="methodology-page">
        {/* Hero */}
        <section className="py-16 px-6 border-b border-slate-100">
          <div className="max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700 mb-4">
              <Shield className="h-3.5 w-3.5" />
              Full Transparency
            </div>
            <h1 className="font-manrope text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
              How we score products
            </h1>
            <p className="mt-3 text-base text-slate-600 leading-relaxed">
              Every product on TrendScout receives a UK Viability Score from 0 to 100. Here is exactly how we calculate it, where the data comes from, and what the limitations are.
            </p>
          </div>
        </section>

        {/* Scoring overview */}
        <section className="py-12 px-6">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-2">The 7-signal framework</h2>
            <p className="text-sm text-slate-500 mb-8">
              Each product is scored across 7 weighted signals. The total adds up to 100 points maximum. No single signal can make or break a score — it is the combination that matters.
            </p>

            {/* Weight distribution bar */}
            <div className="rounded-xl border border-slate-200 p-5 mb-8">
              <p className="text-xs font-semibold text-slate-600 mb-3">Weight distribution</p>
              <div className="flex h-6 rounded-lg overflow-hidden">
                {SIGNALS.map((s) => (
                  <div
                    key={s.name}
                    className={`${s.bg} flex items-center justify-center text-[10px] font-mono font-bold ${s.color}`}
                    style={{ width: `${s.weight}%` }}
                    title={`${s.name}: ${s.weight}%`}
                  >
                    {s.weight}
                  </div>
                ))}
              </div>
              <div className="flex flex-wrap gap-3 mt-3">
                {SIGNALS.map((s) => (
                  <span key={s.name} className={`inline-flex items-center gap-1 text-[10px] font-medium ${s.color}`}>
                    <span className={`w-2 h-2 rounded-sm ${s.bg}`} />
                    {s.name}
                  </span>
                ))}
              </div>
            </div>

            {/* Each signal */}
            <div className="space-y-6">
              {SIGNALS.map((signal) => {
                const Icon = signal.icon;
                return (
                  <div key={signal.name} className="rounded-xl border border-slate-200 p-6" data-testid={`signal-${signal.name.toLowerCase().replace(/\s/g, '-')}`}>
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-9 h-9 rounded-lg ${signal.bg} flex items-center justify-center`}>
                        <Icon className={`h-4.5 w-4.5 ${signal.color}`} />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900">{signal.name}</h3>
                        <span className="text-xs text-slate-400 font-mono">{signal.weight}% weight</span>
                      </div>
                    </div>
                    <p className="text-sm text-slate-600 leading-relaxed">{signal.description}</p>
                    <div className="mt-3 rounded-lg bg-slate-50 p-3">
                      <p className="text-xs font-semibold text-slate-700 mb-1">How we calculate it</p>
                      <p className="text-xs text-slate-500 leading-relaxed">{signal.how}</p>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {signal.sources.map((src) => (
                        <span key={src} className="text-[10px] bg-white border border-slate-200 rounded px-2 py-0.5 text-slate-500">
                          {src}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Limitations & disclaimers */}
        <section className="py-12 px-6 bg-slate-50" data-testid="methodology-disclaimers">
          <div className="max-w-2xl mx-auto">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-4.5 w-4.5 text-amber-600" />
              <h2 className="font-manrope text-xl font-bold text-slate-900">What we get right, and what we do not</h2>
            </div>
            <div className="space-y-4">
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-emerald-700 mb-1">What the score is good at</h3>
                <ul className="text-sm text-slate-600 space-y-1.5 leading-relaxed">
                  <li>Quickly filtering out products that are clearly not viable in the UK (saving weeks of research)</li>
                  <li>Highlighting products with strong multi-signal alignment (trend + margin + low competition)</li>
                  <li>Comparing relative opportunity between products in the same category</li>
                  <li>Providing a structured framework for product validation</li>
                </ul>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-amber-700 mb-1">Where accuracy varies</h3>
                <ul className="text-sm text-slate-600 space-y-1.5 leading-relaxed">
                  <li><strong>Margin estimates</strong> are based on average supplier pricing and standard UK shipping. Your actual costs may differ based on supplier negotiation, volume, and fulfilment method.</li>
                  <li><strong>Competition data</strong> may not capture very new sellers or those selling through non-indexed channels.</li>
                  <li><strong>Trend predictions</strong> reflect current momentum, not future events. External factors (viral TikTok, celebrity endorsement, seasonal shift) can change trajectories overnight.</li>
                </ul>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-red-700 mb-1">What the score cannot tell you</h3>
                <ul className="text-sm text-slate-600 space-y-1.5 leading-relaxed">
                  <li>Whether <em>you specifically</em> can execute on this product (your skills, capital, and channel access matter)</li>
                  <li>Regulatory or compliance issues specific to your business structure</li>
                  <li>Brand-specific dynamics (if a major brand enters the category, the landscape shifts)</li>
                </ul>
              </div>
            </div>
            <p className="text-sm text-slate-500 mt-6 leading-relaxed">
              <strong>Our recommendation:</strong> Use the viability score as your first filter, not your final decision. Products scoring 70+ are strong candidates worth deeper research. Always verify margins with actual supplier quotes, test with small inventory, and validate demand with a small ad budget before scaling.
            </p>
          </div>
        </section>

        {/* Confidence levels */}
        <section className="py-12 px-6" data-testid="confidence-levels">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-6">Understanding confidence levels</h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3 rounded-lg border border-emerald-200 bg-emerald-50/50 p-4">
                <div className="w-2 h-2 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-slate-900">High confidence</p>
                  <p className="text-sm text-slate-600 mt-0.5">Fresh data from multiple sources, all signals have real data points. Treat this score as reliable.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50/50 p-4">
                <div className="w-2 h-2 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-slate-900">Medium confidence</p>
                  <p className="text-sm text-slate-600 mt-0.5">Some data points are estimated or from a single source. The score is directionally correct but verify key assumptions.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="w-2 h-2 rounded-full bg-slate-400 mt-1.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-slate-900">Low confidence</p>
                  <p className="text-sm text-slate-600 mt-0.5">Limited data available. Treat as a rough indication only. The product may need manual research to validate.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-12 px-6 bg-slate-50">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-6">Frequently asked questions</h2>
            <div className="space-y-3">
              {FAQS.map((faq, i) => (
                <div key={i} className="rounded-lg border border-slate-200 bg-white p-5" data-testid={`methodology-faq-${i}`}>
                  <h3 className="text-sm font-semibold text-slate-900">{faq.question}</h3>
                  <p className="text-sm text-slate-600 mt-2 leading-relaxed">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-14 px-6">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-manrope text-2xl font-bold text-slate-900">See it in action</h2>
            <p className="mt-2 text-sm text-slate-500">Check out a full product analysis with all 7 signals scored.</p>
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link to="/sample-product-analysis">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-6 h-11">
                  View Sample Analysis <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/tools">
                <Button variant="outline" className="border-slate-300 text-slate-700 rounded-lg font-medium px-6 h-11">
                  Try Free Calculators
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
