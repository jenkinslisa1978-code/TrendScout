import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import { ViabilityBadge } from '@/components/ViabilityBadge';
import { trackEvent, EVENTS } from '@/services/analytics';
import {
  ArrowRight, TrendingUp, Shield, Target, PoundSterling, Truck,
  AlertTriangle, Check, X, BarChart3, Zap, Store, Eye, Layers,
  ShoppingBag, RefreshCw,
} from 'lucide-react';

const PRODUCT = {
  name: 'Portable Neck Fan (Bladeless)',
  image: null,
  category: 'Personal Electronics',
  launchScore: 74,
  viabilityScore: 78,
  trendMomentum: 82,
  saturation: 38,
  marginPotential: 71,
  adOpportunity: 65,
  searchGrowth: 77,
  socialBuzz: 88,
  supplierAvailability: 62,
  sellingPriceRange: '£18.99 – £27.99',
  estimatedCost: '£4.50 – £7.20',
  estimatedMargin: '35% – 52%',
  shippingTime: '7–14 days (ePacket/CJ)',
  vatImpact: '20% VAT reduces effective margin by ~£4–5 per unit',
  channelFit: [
    { channel: 'TikTok Shop UK', fit: 'Strong', reason: 'Highly visual, impulse purchase, strong TikTok engagement' },
    { channel: 'Shopify Store', fit: 'Good', reason: 'Works well with targeted Facebook/TikTok ads for UK summer audience' },
    { channel: 'Amazon.co.uk', fit: 'Moderate', reason: 'Growing competition, but seasonal demand peaks create windows' },
  ],
  aiSummary: 'This product shows strong commercial potential for UK sellers. Trend momentum is high with consistent growth across TikTok and Google search. The bladeless design is a differentiator that supports higher pricing. Margins remain healthy after VAT and shipping, particularly at the £24.99 price point. The main risk is seasonal dependency — demand peaks in May–August and drops sharply in autumn. Saturation is currently moderate but rising. Sellers entering now have a viable window, particularly on TikTok Shop UK where organic reach still supports new entrants.',
  risks: [
    'Seasonal product — demand drops significantly outside summer months',
    'Saturation rising — more UK sellers entering this space each month',
    'Electrical product category has higher return rates (estimated 8–12%)',
    'Multiple suppliers with inconsistent quality — due diligence needed',
  ],
  strengths: [
    'Strong TikTok engagement with high shareability',
    'Healthy margins even after VAT and shipping',
    'Low shipping weight keeps costs manageable',
    'Clear target audience (UK commuters, office workers, festival-goers)',
    'Bladeless angle is a meaningful product differentiator',
  ],
  nextSteps: [
    'Order 2–3 samples from different suppliers to compare quality',
    'Test a £50–100 TikTok ad campaign targeting UK 18–35 demographic',
    'Price at £24.99 to maximise margin while staying competitive',
    'Prepare for seasonal ramp-up — best launch window is April–May',
  ],
};

export default function SampleAnalysisPage() {
  useEffect(() => {
    trackEvent(EVENTS.SAMPLE_ANALYSIS_VIEW, { product_name: PRODUCT.name });
  }, []);

  const signalBar = (label, value, icon) => {
    const Icon = icon;
    const color = value >= 70 ? 'bg-emerald-500' : value >= 45 ? 'bg-amber-500' : 'bg-red-400';
    const textColor = value >= 70 ? 'text-emerald-600' : value >= 45 ? 'text-amber-600' : 'text-red-500';
    return (
      <div className="flex items-center gap-3">
        <Icon className="h-4 w-4 text-slate-400 flex-shrink-0" />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium text-slate-700">{label}</span>
            <span className={`font-mono text-xs font-semibold ${textColor}`}>{value}%</span>
          </div>
          <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
            <div className={`h-full ${color} rounded-full`} style={{ width: `${value}%` }} />
          </div>
        </div>
      </div>
    );
  };

  return (
    <LandingLayout>
      <PageMeta
        title="Sample Product Analysis — Portable Neck Fan"
        description="See how TrendScout analyses a real product. UK Viability Score, margin estimates, saturation data, channel fit, and AI summary — all in one view."
        canonical="/sample-product-analysis"
        schema={[
          webPageSchema('Sample Product Analysis', 'See how TrendScout analyses a real product for UK commercial viability.', '/sample-product-analysis'),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Sample Product Analysis' }]),
        ]}
      />
      <div className="bg-white" data-testid="sample-analysis-page">
        {/* Header */}
        <section className="pt-16 pb-6 px-6">
          <div className="max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 border border-indigo-100 px-3 py-1 mb-5">
              <Eye className="h-3.5 w-3.5 text-indigo-600" />
              <span className="text-xs font-medium text-indigo-700">Sample analysis — see what TrendScout shows you</span>
            </div>
            <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight" data-testid="sample-headline">
              Product Analysis: {PRODUCT.name}
            </h1>
            <p className="mt-3 text-base text-slate-500">
              This is a sample product analysis showing the kind of intelligence TrendScout provides for every trending product. Real data. Real scoring. Real UK viability assessment.
            </p>
          </div>
        </section>

        {/* Main Analysis Grid */}
        <section className="pb-8 px-6">
          <div className="max-w-4xl mx-auto">
            <div className="grid lg:grid-cols-3 gap-5">
              {/* Left: Scores + Signals */}
              <div className="lg:col-span-2 space-y-5">
                {/* Score cards */}
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="rounded-xl border border-slate-200 p-5">
                    <p className="text-xs font-medium text-slate-500 mb-2">Launch Score</p>
                    <div className="flex items-baseline gap-2">
                      <span className="font-mono text-3xl font-extrabold text-slate-900">{PRODUCT.launchScore}</span>
                      <span className="text-sm text-slate-400">/100</span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">Combined opportunity score across all signals</p>
                  </div>
                  <div className="rounded-xl border border-indigo-200 bg-indigo-50/30 p-5">
                    <p className="text-xs font-medium text-indigo-600 mb-2">UK Viability Score</p>
                    <div className="flex items-center gap-3">
                      <ViabilityBadge score={PRODUCT.viabilityScore} size="lg" showLabel expandable productName={PRODUCT.name} />
                    </div>
                    <p className="text-xs text-slate-500 mt-2">Commercial viability in the UK market</p>
                  </div>
                </div>

                {/* Signal Breakdown */}
                <div className="rounded-xl border border-slate-200 p-5" data-testid="signal-breakdown">
                  <h3 className="font-manrope text-sm font-semibold text-slate-900 mb-4">7-Signal Breakdown</h3>
                  <div className="space-y-3">
                    {signalBar('Trend momentum', PRODUCT.trendMomentum, TrendingUp)}
                    {signalBar('Market saturation (inverted)', 100 - PRODUCT.saturation, Shield)}
                    {signalBar('Margin potential', PRODUCT.marginPotential, PoundSterling)}
                    {signalBar('Ad opportunity', PRODUCT.adOpportunity, Target)}
                    {signalBar('Search growth', PRODUCT.searchGrowth, BarChart3)}
                    {signalBar('Social buzz', PRODUCT.socialBuzz, Eye)}
                    {signalBar('Supplier availability', PRODUCT.supplierAvailability, Truck)}
                  </div>
                </div>

                {/* AI Summary */}
                <div className="rounded-xl border border-slate-200 p-5" data-testid="ai-summary">
                  <h3 className="font-manrope text-sm font-semibold text-slate-900 mb-2 flex items-center gap-2">
                    <Zap className="h-4 w-4 text-indigo-600" /> AI Analysis Summary
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{PRODUCT.aiSummary}</p>
                </div>
              </div>

              {/* Right: Quick Facts */}
              <div className="space-y-4">
                <div className="rounded-xl border border-slate-200 p-5 sticky top-20">
                  <h3 className="font-manrope text-sm font-semibold text-slate-900 mb-4">Quick Facts</h3>
                  <dl className="space-y-3 text-sm">
                    <div>
                      <dt className="text-xs text-slate-500">Category</dt>
                      <dd className="font-medium text-slate-900">{PRODUCT.category}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate-500">Selling price range</dt>
                      <dd className="font-mono font-semibold text-slate-900">{PRODUCT.sellingPriceRange}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate-500">Estimated cost</dt>
                      <dd className="font-mono font-semibold text-slate-900">{PRODUCT.estimatedCost}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate-500">Estimated margin</dt>
                      <dd className="font-mono font-semibold text-emerald-600">{PRODUCT.estimatedMargin}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate-500">Shipping time</dt>
                      <dd className="text-slate-700">{PRODUCT.shippingTime}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate-500">VAT impact</dt>
                      <dd className="text-slate-700">{PRODUCT.vatImpact}</dd>
                    </div>
                  </dl>
                  <div className="mt-5 pt-4 border-t border-slate-100">
                    <Link to="/signup">
                      <Button
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-sm h-10"
                        data-testid="sidebar-cta"
                        onClick={() => trackEvent(EVENTS.SAMPLE_ANALYSIS_CTA, { cta_label: 'Analyse Real Products', position: 'sidebar' })}
                      >
                        Analyse Real Products <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                      </Button>
                    </Link>
                    <p className="text-xs text-slate-400 text-center mt-2">Free to start. No credit card.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Channel Fit */}
        <section className="py-8 px-6">
          <div className="max-w-4xl mx-auto">
            <div className="rounded-xl border border-slate-200 p-5" data-testid="channel-fit">
              <h3 className="font-manrope text-sm font-semibold text-slate-900 mb-4">Channel Fit — UK Sales Channels</h3>
              <div className="grid sm:grid-cols-3 gap-3">
                {PRODUCT.channelFit.map((ch) => {
                  const fitColor = ch.fit === 'Strong' ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : ch.fit === 'Good' ? 'text-blue-700 bg-blue-50 border-blue-200' : 'text-amber-700 bg-amber-50 border-amber-200';
                  return (
                    <div key={ch.channel} className="rounded-lg border border-slate-200 p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-slate-900">{ch.channel}</span>
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${fitColor}`}>{ch.fit}</span>
                      </div>
                      <p className="text-xs text-slate-500 leading-relaxed">{ch.reason}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        {/* Strengths & Risks */}
        <section className="py-8 px-6 bg-slate-50">
          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-5">
            <div className="rounded-xl border border-slate-200 bg-white p-5" data-testid="strengths">
              <h3 className="font-manrope text-sm font-semibold text-emerald-800 mb-3 flex items-center gap-2">
                <Check className="h-4 w-4 text-emerald-600" /> Strengths
              </h3>
              <ul className="space-y-2">
                {PRODUCT.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                    <Check className="h-3.5 w-3.5 text-emerald-500 mt-0.5 flex-shrink-0" />{s}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-5" data-testid="risks">
              <h3 className="font-manrope text-sm font-semibold text-amber-800 mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-600" /> Key Risks
              </h3>
              <ul className="space-y-2">
                {PRODUCT.risks.map((r, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                    <AlertTriangle className="h-3.5 w-3.5 text-amber-500 mt-0.5 flex-shrink-0" />{r}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* Recommended Next Steps */}
        <section className="py-8 px-6">
          <div className="max-w-4xl mx-auto">
            <div className="rounded-xl border border-slate-200 p-5" data-testid="next-steps">
              <h3 className="font-manrope text-sm font-semibold text-slate-900 mb-3">Recommended Next Steps</h3>
              <ol className="space-y-2">
                {PRODUCT.nextSteps.map((step, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-600">
                    <span className="font-mono text-xs font-bold text-indigo-600 bg-indigo-50 rounded px-1.5 py-0.5 flex-shrink-0">{i + 1}</span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </section>

        {/* Mid-page CTA */}
        <section className="py-10 px-6 bg-slate-50">
          <div className="max-w-2xl mx-auto text-center">
            <p className="text-sm text-slate-500 mb-2">This is a sample analysis. Real products include live data, daily updates, and full competitive intelligence.</p>
            <h2 className="font-manrope text-xl font-bold text-slate-900">
              Get this level of analysis on every trending product
            </h2>
            <div className="mt-5 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link to="/signup">
                <Button
                  className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-6 h-11"
                  data-testid="mid-cta"
                  onClick={() => trackEvent(EVENTS.SAMPLE_ANALYSIS_CTA, { cta_label: 'Start Free', position: 'mid_page' })}
                >
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/uk-product-viability-score">
                <Button variant="outline" className="border-slate-300 text-slate-700 rounded-lg font-medium px-6 h-11">
                  How Viability Scores Work
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Related Links */}
        <section className="py-8 px-6 bg-white">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Related</h3>
            <div className="flex flex-wrap gap-2">
              <Link to="/trending-products" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">Trending Products</Link>
              <Link to="/uk-product-viability-score" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">UK Viability Score</Link>
              <Link to="/how-it-works" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">How It Works</Link>
              <Link to="/pricing" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">Pricing</Link>
              <Link to="/free-tools" className="text-sm text-indigo-600 bg-indigo-50 rounded-md px-3 py-1.5 font-medium">Free Tools</Link>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
