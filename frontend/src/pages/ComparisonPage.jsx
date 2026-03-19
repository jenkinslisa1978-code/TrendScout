import React from 'react';
import { Link, useParams } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { faqSchema, breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import { trackEvent, EVENTS } from '@/services/analytics';
import { ArrowRight, Check, X, Minus } from 'lucide-react';

const COMPARISONS = {
  'jungle-scout-vs-trendscout': {
    competitor: 'Jungle Scout',
    headline: 'Jungle Scout vs TrendScout',
    subtitle: 'Jungle Scout is a well-established Amazon product research tool built for US sellers. TrendScout is a multi-channel product research platform built specifically for UK ecommerce sellers.',
    intro: 'Both tools help sellers find product opportunities, but they take fundamentally different approaches and serve different markets. Here is an honest comparison to help you decide which is right for you.',
    competitor_best_for: 'Jungle Scout is best for sellers focused exclusively on Amazon.com (US marketplace). It offers deep Amazon keyword data, sales estimates, and listing optimisation tools. If your entire business is on Amazon US, Jungle Scout is a mature and proven choice.',
    trendscout_best_for: 'TrendScout is best for UK-based sellers who sell across multiple channels (Shopify, Amazon.co.uk, TikTok Shop UK). It offers cross-channel trend detection, UK-specific margin estimation, and saturation analysis — things Jungle Scout does not cover.',
    rows: [
      { feature: 'Primary market', competitor: 'US / Amazon.com', trendscout: 'UK / Multi-channel' },
      { feature: 'Sales channels covered', competitor: 'Amazon only', trendscout: 'Shopify, Amazon UK, TikTok Shop' },
      { feature: 'Trend detection', competitor: 'Amazon keyword trends', trendscout: 'Cross-channel (TikTok, Amazon, Google, Shopify)' },
      { feature: 'UK margin estimation', competitor: false, trendscout: true },
      { feature: 'VAT factored into costs', competitor: false, trendscout: true },
      { feature: 'Saturation analysis', competitor: 'Amazon niche score', trendscout: 'Multi-channel saturation scoring' },
      { feature: 'AI ad suggestions', competitor: false, trendscout: true },
      { feature: 'Push to Shopify', competitor: false, trendscout: true },
      { feature: 'Amazon keyword research', competitor: true, trendscout: false },
      { feature: 'Listing optimisation', competitor: true, trendscout: false },
      { feature: 'Supplier database', competitor: true, trendscout: 'CJ Dropshipping integration' },
      { feature: 'Free plan available', competitor: false, trendscout: true },
      { feature: 'Starting price', competitor: '$49/mo (USD)', trendscout: '£19/mo (GBP)' },
    ],
    verdict: 'If you sell exclusively on Amazon US, Jungle Scout is the better tool. If you sell in the UK across Shopify, Amazon.co.uk, or TikTok Shop and need UK-specific product intelligence, TrendScout is built for you.',
  },
  'sell-the-trend-vs-trendscout': {
    competitor: 'Sell The Trend',
    headline: 'Sell The Trend vs TrendScout',
    subtitle: 'Sell The Trend is a product research tool focused on finding trending and viral products for dropshippers. TrendScout offers similar discovery with stronger UK market analysis and viability scoring.',
    intro: 'Both tools help sellers discover trending products, but they differ in how they evaluate whether those products are commercially viable. Here is a direct comparison.',
    competitor_best_for: 'Sell The Trend is best for dropshippers who want a wide catalog of trending products with AliExpress integration and store automation. It is good for beginners who want quick product ideas and are comfortable doing their own market validation.',
    trendscout_best_for: 'TrendScout is best for UK sellers who want deeper analysis beyond just "trending". It scores products on viability, saturation, and profitability specifically for the UK market — helping you filter genuine opportunities from viral noise.',
    rows: [
      { feature: 'Primary market', competitor: 'Global / US-leaning', trendscout: 'UK-first' },
      { feature: 'Product scoring', competitor: 'Basic trend score', trendscout: '7-signal launch score with breakdown' },
      { feature: 'UK margin estimation', competitor: false, trendscout: true },
      { feature: 'VAT factored into costs', competitor: false, trendscout: true },
      { feature: 'Saturation analysis', competitor: 'Basic', trendscout: 'Detailed multi-channel' },
      { feature: 'TikTok trends', competitor: true, trendscout: true },
      { feature: 'Amazon trends', competitor: true, trendscout: true },
      { feature: 'AI ad suggestions', competitor: 'Basic', trendscout: 'Detailed with audience targeting' },
      { feature: 'Competitor analysis', competitor: 'Store explorer', trendscout: 'Deep store analysis with revenue estimates' },
      { feature: 'Push to Shopify', competitor: true, trendscout: true },
      { feature: 'Free plan available', competitor: false, trendscout: true },
      { feature: 'Starting price', competitor: '$39.97/mo (USD)', trendscout: '£19/mo (GBP)' },
    ],
    verdict: 'If you want a broad catalog of global trending products with store automation, Sell The Trend is a reasonable choice. If you need UK-specific viability analysis, deeper scoring, and margin estimation, TrendScout gives you more actionable intelligence.',
  },
  'minea-vs-trendscout': {
    competitor: 'Minea',
    headline: 'Minea vs TrendScout',
    subtitle: 'Minea is an ad spy and product research tool focused on tracking competitor ads across social platforms. TrendScout combines trend detection with UK-specific commercial viability analysis.',
    intro: 'Minea and TrendScout approach product research from different angles. Here is what each does well and where the key differences lie.',
    competitor_best_for: 'Minea is best for sellers who want to spy on competitor ads across Facebook, TikTok, Pinterest, and other platforms. Its strength is in ad creative discovery — seeing what ads are running and which products are being promoted.',
    trendscout_best_for: 'TrendScout is best for UK sellers who need to go beyond ad spy data. Knowing that a product has ads running is useful, but TrendScout adds viability scoring, margin analysis, saturation data, and UK-specific commercial assessment.',
    rows: [
      { feature: 'Primary approach', competitor: 'Ad spy / ad creative tracking', trendscout: 'Multi-signal product research' },
      { feature: 'Primary market', competitor: 'Global', trendscout: 'UK-first' },
      { feature: 'Ad tracking', competitor: 'Extensive (FB, TikTok, Pinterest)', trendscout: 'Ad opportunity scoring' },
      { feature: 'Product viability scoring', competitor: 'Basic', trendscout: '7-signal launch score' },
      { feature: 'UK margin estimation', competitor: false, trendscout: true },
      { feature: 'Saturation analysis', competitor: 'Ad saturation only', trendscout: 'Full market saturation' },
      { feature: 'Competitor store analysis', competitor: 'Store finder', trendscout: 'Revenue estimates and pricing analysis' },
      { feature: 'TikTok trends', competitor: true, trendscout: true },
      { feature: 'Supplier integration', competitor: 'AliExpress', trendscout: 'CJ Dropshipping' },
      { feature: 'AI ad suggestions', competitor: false, trendscout: true },
      { feature: 'Free plan available', competitor: true, trendscout: true },
      { feature: 'Starting price', competitor: '€49/mo (EUR)', trendscout: '£19/mo (GBP)' },
    ],
    verdict: 'If your primary need is ad creative spying and tracking competitor ads across platforms, Minea is the specialised tool. If you need comprehensive product research with UK viability scoring, margin analysis, and launch intelligence, TrendScout is the stronger choice.',
  },
};

export default function ComparisonPage() {
  const { slug } = useParams();
  const data = COMPARISONS[slug];

  if (!data) {
    return (
      <LandingLayout>
        <div className="py-20 text-center">
          <h1 className="font-manrope text-2xl font-bold text-slate-900">Comparison not found</h1>
          <Link to="/" className="text-indigo-600 mt-4 inline-block">Return to homepage</Link>
        </div>
      </LandingLayout>
    );
  }

  const renderCell = (val) => {
    if (val === true) return <Check className="h-4 w-4 text-emerald-600 mx-auto" />;
    if (val === false) return <X className="h-4 w-4 text-slate-300 mx-auto" />;
    return <span className="text-sm text-slate-700">{val}</span>;
  };

  return (
    <LandingLayout>
      <div className="bg-white" data-testid="comparison-page">
        <PageMeta
          title={data.headline}
          description={data.subtitle}
          canonical={`/compare/${slug}`}
          schema={[
            webPageSchema(data.headline, data.subtitle, `/compare/${slug}`),
            breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Compare' }, { name: data.headline }]),
          ]}
        />
        {/* Hero */}
        <section className="pt-16 pb-8 px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">{data.headline}</h1>
            <p className="mt-4 text-lg text-slate-600 leading-relaxed">{data.subtitle}</p>
            <p className="mt-3 text-base text-slate-500 leading-relaxed">{data.intro}</p>
          </div>
        </section>

        {/* Who each is best for */}
        <section className="py-12 px-6">
          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-6">
            <div className="rounded-lg border border-slate-200 p-6">
              <h3 className="text-sm font-semibold text-slate-900 mb-3">Best for: {data.competitor}</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{data.competitor_best_for}</p>
            </div>
            <div className="rounded-lg border border-indigo-200 bg-indigo-50/30 p-6">
              <h3 className="text-sm font-semibold text-indigo-900 mb-3">Best for: TrendScout</h3>
              <p className="text-sm text-slate-600 leading-relaxed">{data.trendscout_best_for}</p>
            </div>
          </div>
        </section>

        {/* Comparison Table */}
        <section className="py-12 bg-slate-50 px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-6">Feature comparison</h2>
            <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">
              <table className="w-full text-sm" data-testid="comparison-table">
                <thead>
                  <tr className="border-b bg-slate-50">
                    <th className="text-left p-4 font-medium text-slate-700 w-[40%]">Feature</th>
                    <th className="text-center p-4 font-medium text-slate-700 w-[30%]">{data.competitor}</th>
                    <th className="text-center p-4 font-medium text-indigo-700 bg-indigo-50/50 w-[30%]">TrendScout</th>
                  </tr>
                </thead>
                <tbody>
                  {data.rows.map((row, idx) => (
                    <tr key={idx} className="border-b last:border-0 hover:bg-slate-50/50 transition-colors">
                      <td className="p-3.5 text-slate-700 font-medium">{row.feature}</td>
                      <td className="p-3.5 text-center">{renderCell(row.competitor)}</td>
                      <td className="p-3.5 text-center bg-indigo-50/20">{renderCell(row.trendscout)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Verdict */}
        <section className="py-12 px-6">
          <div className="max-w-3xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-4">The verdict</h2>
            <p className="text-base text-slate-600 leading-relaxed">{data.verdict}</p>
          </div>
        </section>

        {/* CTA */}
        <section className="py-14 bg-slate-50 px-6">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-manrope text-2xl font-bold text-slate-900">Try TrendScout free</h2>
            <p className="mt-3 text-base text-slate-500">See the difference for yourself. Browse trending products with UK viability data — no credit card needed.</p>
            <div className="mt-6 flex items-center justify-center gap-3">
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-6 h-11" data-testid="comparison-cta" onClick={() => trackEvent(EVENTS.COMPARE_PAGE_CTA, { competitor: data.competitor, cta_label: 'Start Free' })}>
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/pricing">
                <Button variant="outline" className="border-slate-300 text-slate-700 rounded-lg font-medium px-6 h-11">
                  See Pricing
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Related */}
        <section className="py-10 bg-white px-6">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Other comparisons</h3>
            <div className="flex flex-wrap gap-2">
              {Object.entries(COMPARISONS).filter(([k]) => k !== slug).map(([k, v]) => (
                <Link key={k} to={`/compare/${k}`} className="text-sm text-indigo-600 hover:text-indigo-700 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">
                  {v.headline}
                </Link>
              ))}
              <Link to="/uk-product-research" className="text-sm text-indigo-600 hover:text-indigo-700 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">
                UK Product Research
              </Link>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
