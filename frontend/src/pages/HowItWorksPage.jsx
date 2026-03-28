import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { faqSchema, breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import { RevealSection, RevealStagger } from '@/hooks/useScrollReveal';
import {
  ArrowRight, Search, BarChart3, Shield, Zap, TrendingUp,
  Target, PoundSterling, Truck, RefreshCw, Layers, Globe,
  Check, X, ChevronDown,
} from 'lucide-react';

const STEP_IMAGES = {
  discover: 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/bb5def00d5bcd213c2e3debe244a3ad6cfd3e3aa161f192c8a053766995501e4.png',
  scoring: 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/f08ffeba48f227a5bb3ef166c983108aa5c32df599e7b9a71ffd46eb10886a54.png',
  uk_viability: 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/dd833b72e93a1351d30532c57f0fa5acb807182a6981bb5c464b408e48ade19e.png',
  launch: 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/7052fdad6e198d442f59f58adb94ba65c2755ce11e97c5637582609547743612.png',
};

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
    key: 'discover',
    title: 'Discover trending products',
    desc: 'TrendScout continuously monitors product activity across TikTok, Amazon, Shopify stores, and Google Trends. When a product starts gaining traction across multiple channels, it appears in our trending feed.',
    detail: 'Products are not just scraped from one source. We look for signals across multiple channels simultaneously — a much stronger indicator of genuine demand than a single viral video.',
    icon: Search,
  },
  {
    num: '02',
    key: 'scoring',
    title: 'Evaluate with 7-signal scoring',
    desc: 'Each product is scored across seven weighted signals: trend momentum, market saturation, margin potential, ad opportunity, search growth, social buzz, and supplier availability.',
    detail: 'The overall launch score (0-100) gives you a single number to prioritise. But the individual signal breakdown is often more useful — a product might score well overall but have a critical weakness.',
    icon: BarChart3,
  },
  {
    num: '03',
    key: 'uk_viability',
    title: 'Check UK-specific viability',
    desc: 'This is where TrendScout differs. We estimate whether the product can work commercially in the UK by factoring in VAT, shipping costs, realistic margins, returns friction, and channel suitability.',
    detail: 'A product trending in the US might have completely different economics in the UK. Higher shipping, 20% VAT, different consumer expectations — all change the equation.',
    icon: Shield,
  },
  {
    num: '04',
    key: 'launch',
    title: 'Launch with confidence',
    desc: 'Use the product analysis, AI-generated ad angles, supplier data, and competitive intelligence to decide whether to test this product.',
    detail: 'TrendScout does not tell you to launch. It gives you information to make a better-informed decision. Fewer wasted ad spends, fewer failed product tests.',
    icon: Zap,
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
  const [openFaq, setOpenFaq] = useState(null);

  return (
    <LandingLayout>
      <PageMeta
        title="How TrendScout Validates Products for the UK Market"
        description="See how TrendScout scores products using 7 UK-specific signals: demand, competition, margins, VAT impact, shipping, channel fit, and trend trajectory."
        canonical="/how-it-works"
        schema={[
          webPageSchema('How TrendScout Works', 'Learn how TrendScout evaluates products using a 7-signal scoring model and UK-specific viability analysis.', '/how-it-works'),
          faqSchema(FAQS),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'How It Works' }]),
        ]}
      />

      {/* ═══ HERO ═══ */}
      <section className="relative bg-gradient-to-b from-slate-50 via-white to-white overflow-hidden pt-16 pb-12 lg:pt-24 lg:pb-16" data-testid="how-it-works-page">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(99,102,241,0.06),transparent)]" />
        <div className="relative mx-auto max-w-7xl px-6 lg:px-8 text-center">
          <RevealSection>
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">How It Works</p>
            <h1 className="font-manrope text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-[1.1]" data-testid="hiw-headline">
              From trend signal to{' '}
              <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">launch decision</span>
            </h1>
            <p className="mt-5 text-base sm:text-lg text-slate-500 leading-relaxed max-w-2xl mx-auto">
              TrendScout helps UK ecommerce sellers discover trending products, evaluate commercial viability, and make launch decisions backed by data instead of guesswork.
            </p>
          </RevealSection>
        </div>
      </section>

      {/* ═══ 4-STEP VISUAL WALKTHROUGH ═══ */}
      <section className="py-16 lg:py-20 bg-white" data-testid="hiw-steps">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="space-y-24 lg:space-y-32">
            {STEPS.map((step, idx) => {
              const Icon = step.icon;
              const isEven = idx % 2 === 1;
              return (
                <div key={step.num} className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center" data-testid={`hiw-step-${step.num}`}>
                  {/* Text */}
                  <RevealSection direction={isEven ? 'left' : 'right'} className={isEven ? 'lg:order-2' : ''}>
                    <div className="flex items-center gap-3 mb-5">
                      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white text-sm font-bold font-mono">{step.num}</span>
                      <div className="h-px flex-1 bg-gradient-to-r from-indigo-200 to-transparent" />
                    </div>
                    <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                      {step.title}
                    </h2>
                    <p className="mt-4 text-base text-slate-500 leading-relaxed">{step.desc}</p>
                    <div className="mt-4 rounded-lg border-l-2 border-indigo-200 bg-slate-50 pl-4 pr-4 py-3">
                      <p className="text-sm text-slate-600 leading-relaxed">{step.detail}</p>
                    </div>
                  </RevealSection>
                  {/* Image */}
                  <RevealSection direction={isEven ? 'right' : 'left'} delay={200} className={isEven ? 'lg:order-1' : ''}>
                    <div className="relative">
                      <div className="absolute -inset-6 bg-gradient-to-br from-indigo-50/50 to-violet-50/30 rounded-3xl" />
                      <div className="relative rounded-2xl overflow-hidden border border-slate-200/60 shadow-lg" style={{ backgroundColor: '#f1f5f9' }}>
                        <img
                          src={STEP_IMAGES[step.key]}
                          alt={step.title}
                          className="w-full h-auto"
                          loading="lazy"
                          data-testid={`hiw-step-img-${step.num}`}
                        />
                      </div>
                    </div>
                  </RevealSection>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ 7-SIGNAL SCORING MODEL ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50" data-testid="hiw-signals">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="max-w-2xl mb-12">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Scoring Model</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              The 7-signal scoring model
            </h2>
            <p className="mt-3 text-base text-slate-500">
              Every product receives a launch score from 0 to 100 calculated from seven weighted signals that indicate whether a product is worth testing.
            </p>
          </RevealSection>
          <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-5" staggerMs={80}>
            {SIGNALS.map((signal) => {
              const Icon = signal.icon;
              return (
                <div key={signal.name} className="rounded-xl border border-slate-200 bg-white p-5 hover:border-indigo-200 hover:shadow-md transition-all duration-300" data-testid={`signal-${signal.name.toLowerCase().replace(/\s/g, '-')}`}>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-sm font-semibold text-slate-900">{signal.name}</h3>
                    </div>
                    <span className="font-mono text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">{signal.weight}</span>
                  </div>
                  <p className="text-sm text-slate-500 leading-relaxed">{signal.desc}</p>
                </div>
              );
            })}
          </RevealStagger>
        </div>
      </section>

      {/* ═══ SCORE INTERPRETATION ═══ */}
      <section className="py-16 lg:py-20 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="max-w-2xl mb-10">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Score Guide</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              How to interpret scores
            </h2>
          </RevealSection>
          <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4" staggerMs={100}>
            {[
              { range: '75–100', label: 'Strong candidate', color: 'border-emerald-200 bg-emerald-50', text: 'text-emerald-800', barColor: 'bg-emerald-500', desc: 'Multiple strong signals. Worth prioritising for testing.' },
              { range: '55–74', label: 'Promising', color: 'border-blue-200 bg-blue-50', text: 'text-blue-800', barColor: 'bg-blue-500', desc: 'Solid potential with some caveats. Review individual signals.' },
              { range: '35–54', label: 'Mixed signals', color: 'border-amber-200 bg-amber-50', text: 'text-amber-800', barColor: 'bg-amber-500', desc: 'Some positive indicators but notable risks. Proceed carefully.' },
              { range: '0–34', label: 'High risk', color: 'border-red-200 bg-red-50', text: 'text-red-800', barColor: 'bg-red-500', desc: 'Multiple weak signals. Not recommended without strong conviction.' },
            ].map((tier) => (
              <div key={tier.range} className={`rounded-xl border p-6 ${tier.color} hover:shadow-md transition-shadow`}>
                <div className={`h-1.5 w-12 ${tier.barColor} rounded-full mb-4`} />
                <span className={`font-mono text-2xl font-bold ${tier.text}`}>{tier.range}</span>
                <p className={`text-sm font-semibold mt-1 ${tier.text}`}>{tier.label}</p>
                <p className="text-xs text-slate-600 mt-2 leading-relaxed">{tier.desc}</p>
              </div>
            ))}
          </RevealStagger>
          <p className="mt-8 text-sm text-slate-500 max-w-2xl">
            Scores are relative and best used for prioritisation and comparison. A high score does not guarantee success — it means more signals are pointing in a positive direction.
          </p>
        </div>
      </section>

      {/* ═══ WHO IT'S FOR ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12">
            <RevealSection direction="right">
              <h2 className="font-manrope text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100">
                  <Check className="h-4 w-4 text-emerald-600" />
                </div>
                Who TrendScout is for
              </h2>
              <ul className="space-y-3">
                {GOOD_FIT.map((item) => (
                  <li key={item} className="flex items-start gap-3 text-sm text-slate-600 bg-white rounded-lg border border-slate-200 p-3">
                    <Check className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </RevealSection>
            <RevealSection direction="left" delay={150}>
              <h2 className="font-manrope text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-100">
                  <X className="h-4 w-4 text-red-500" />
                </div>
                Who it is not for
              </h2>
              <ul className="space-y-3">
                {NOT_FIT.map((item) => (
                  <li key={item} className="flex items-start gap-3 text-sm text-slate-600 bg-white rounded-lg border border-slate-200 p-3">
                    <X className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </RevealSection>
          </div>
        </div>
      </section>

      {/* ═══ UK VIABILITY ═══ */}
      <section className="py-16 lg:py-20 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <RevealSection className="max-w-2xl mb-10">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">UK-Specific</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Why UK-specific product research matters
            </h2>
            <p className="mt-3 text-base text-slate-500">
              Most product research tools are built for US sellers. But the UK market has different economics, regulations, and consumer behaviour.
            </p>
          </RevealSection>
          <RevealStagger className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5" staggerMs={80}>
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
                <div key={item.title} className="rounded-xl border border-slate-200 bg-white p-5 hover:border-indigo-200 hover:shadow-md transition-all duration-300">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 mb-3">
                    <Icon className="h-4 w-4" />
                  </div>
                  <h3 className="text-sm font-semibold text-slate-900">{item.title}</h3>
                  <p className="text-sm text-slate-500 mt-1.5 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </RevealStagger>
        </div>
      </section>

      {/* ═══ FAQ — Accordion ═══ */}
      <section className="py-16 lg:py-20 bg-slate-50">
        <div className="mx-auto max-w-3xl px-6 lg:px-8">
          <RevealSection className="text-center mb-10">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">FAQ</p>
            <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Frequently asked questions
            </h2>
          </RevealSection>
          <RevealSection delay={100}>
            <div className="space-y-3">
              {FAQS.map((faq, idx) => (
                <div
                  key={idx}
                  className="rounded-xl border border-slate-200 bg-white overflow-hidden transition-all duration-300 hover:border-slate-300"
                  data-testid={`faq-item-${idx}`}
                >
                  <button
                    className="w-full flex items-center justify-between p-5 text-left"
                    onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                    data-testid={`faq-toggle-${idx}`}
                  >
                    <span className="text-sm font-semibold text-slate-900 pr-4">{faq.q}</span>
                    <ChevronDown className={`h-4 w-4 text-slate-400 shrink-0 transition-transform duration-300 ${openFaq === idx ? 'rotate-180' : ''}`} />
                  </button>
                  <div className={`overflow-hidden transition-all duration-300 ${openFaq === idx ? 'max-h-48 pb-5' : 'max-h-0'}`}>
                    <p className="text-sm text-slate-500 leading-relaxed px-5">{faq.a}</p>
                  </div>
                </div>
              ))}
            </div>
          </RevealSection>
        </div>
      </section>

      {/* ═══ CTA ═══ */}
      <RevealSection>
        <section className="py-16 lg:py-20">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="relative rounded-2xl bg-slate-900 overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,102,241,0.15),transparent_60%)]" />
              <div className="relative p-10 sm:p-16 text-center">
                <h2 className="font-manrope text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight max-w-2xl mx-auto">
                  Ready to validate your next product?
                </h2>
                <p className="mt-5 text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
                  Start free and browse trending products with real scores and UK viability data.
                </p>
                <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link to="/signup">
                    <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 text-base px-8 h-12 font-semibold rounded-xl shadow-lg" data-testid="hiw-cta-signup">
                      Validate Your First Product <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                  <Link to="/trending-products">
                    <Button variant="ghost" size="lg" className="text-base px-8 h-12 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl" data-testid="hiw-cta-products">
                      Browse Trending Products
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </RevealSection>
    </LandingLayout>
  );
}
