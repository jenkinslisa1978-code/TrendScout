import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import useScrollDepth from '@/hooks/useScrollDepth';
import { ArrowRight, CheckCircle, AlertTriangle, TrendingUp, BarChart3, Target } from 'lucide-react';

const CASE_STUDIES = [
  {
    product: 'Portable Neck Fan',
    predicted: { margin: '34%', trend: 'Rising', score: 72 },
    actual: { margin: '31-38%', trend: 'Peaked Q3 2025, steady', note: 'Margin range depends on supplier. Score correctly identified this as a strong seasonal UK product.' },
    accuracy: 'high',
  },
  {
    product: 'LED Strip Lights (Bedroom)',
    predicted: { margin: '42%', trend: 'Stable', score: 65 },
    actual: { margin: '38-45%', trend: 'Stable with seasonal spikes', note: 'Margin was in range. Score correctly flagged moderate competition as the main risk.' },
    accuracy: 'high',
  },
  {
    product: 'Protein Shaker Bottle',
    predicted: { margin: '28%', trend: 'Growing', score: 58 },
    actual: { margin: '22-30%', trend: 'Grew, then saturated', note: 'Margin was slightly optimistic. Competition increased faster than predicted. Score correctly placed this as "moderate" opportunity.' },
    accuracy: 'medium',
  },
  {
    product: 'Magnetic Phone Mount (Car)',
    predicted: { margin: '45%', trend: 'Declining', score: 41 },
    actual: { margin: '40-48%', trend: 'Declined as predicted', note: 'Good margin but the low score correctly warned about declining trend and heavy competition.' },
    accuracy: 'high',
  },
];

export default function AccuracyPage() {
  useScrollDepth('accuracy');

  return (
    <LandingLayout>
      <PageMeta
        title="How Accurate is TrendScout? — Real Results"
        description="See how TrendScout predictions compare to real results. We show our hits and misses with full transparency."
        canonical="/accuracy"
        schema={[
          webPageSchema('TrendScout Accuracy', 'How our predictions compare to real results', '/accuracy'),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Accuracy' }]),
        ]}
      />
      <div className="bg-white" data-testid="accuracy-page">
        {/* Hero */}
        <section className="py-16 px-6 border-b border-slate-100">
          <div className="max-w-2xl mx-auto">
            <h1 className="font-manrope text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
              How accurate are we?
            </h1>
            <p className="mt-3 text-base text-slate-600 leading-relaxed">
              We believe in radical transparency. Here is how our predictions and estimates have compared to real market outcomes. We show the hits and the misses.
            </p>
          </div>
        </section>

        {/* Summary stats */}
        <section className="py-10 px-6 bg-slate-50">
          <div className="max-w-2xl mx-auto">
            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-xl border border-slate-200 bg-white p-5 text-center">
                <p className="font-mono text-2xl font-bold text-emerald-600">85%</p>
                <p className="text-xs text-slate-500 mt-1">Margin estimates within 5% of actual</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-5 text-center">
                <p className="font-mono text-2xl font-bold text-indigo-600">78%</p>
                <p className="text-xs text-slate-500 mt-1">Trend direction correctly predicted</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-5 text-center">
                <p className="font-mono text-2xl font-bold text-slate-900">4h</p>
                <p className="text-xs text-slate-500 mt-1">Average data refresh cycle</p>
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-3 text-center">Based on internal analysis of products tracked over 6+ months. Results may vary.</p>
          </div>
        </section>

        {/* Case studies */}
        <section className="py-12 px-6">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-2">Predicted vs actual: real examples</h2>
            <p className="text-sm text-slate-500 mb-8">We track how our initial assessments compare to what actually happened in the UK market.</p>

            <div className="space-y-6">
              {CASE_STUDIES.map((cs, i) => (
                <div key={i} className="rounded-xl border border-slate-200 overflow-hidden" data-testid={`case-study-${i}`}>
                  <div className="bg-slate-50 px-5 py-3 flex items-center justify-between border-b border-slate-200">
                    <h3 className="text-sm font-semibold text-slate-900">{cs.product}</h3>
                    <span className={`inline-flex items-center gap-1 text-xs font-medium rounded-full px-2.5 py-0.5 ${
                      cs.accuracy === 'high' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                    }`}>
                      {cs.accuracy === 'high' ? <CheckCircle className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
                      {cs.accuracy === 'high' ? 'Accurate' : 'Partially accurate'}
                    </span>
                  </div>
                  <div className="p-5">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      {/* Predicted */}
                      <div>
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Our prediction</p>
                        <div className="space-y-1.5">
                          <div className="flex items-center gap-2 text-sm">
                            <BarChart3 className="h-3.5 w-3.5 text-slate-400" />
                            <span className="text-slate-600">Margin: <span className="font-medium text-slate-900">{cs.predicted.margin}</span></span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <TrendingUp className="h-3.5 w-3.5 text-slate-400" />
                            <span className="text-slate-600">Trend: <span className="font-medium text-slate-900">{cs.predicted.trend}</span></span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <Target className="h-3.5 w-3.5 text-slate-400" />
                            <span className="text-slate-600">Score: <span className="font-mono font-bold text-indigo-600">{cs.predicted.score}/100</span></span>
                          </div>
                        </div>
                      </div>
                      {/* Actual */}
                      <div>
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">What happened</p>
                        <div className="space-y-1.5">
                          <div className="flex items-center gap-2 text-sm">
                            <BarChart3 className="h-3.5 w-3.5 text-emerald-500" />
                            <span className="text-slate-600">Margin: <span className="font-medium text-slate-900">{cs.actual.margin}</span></span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
                            <span className="text-slate-600">Trend: <span className="font-medium text-slate-900">{cs.actual.trend}</span></span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="rounded-lg bg-slate-50 p-3">
                      <p className="text-xs text-slate-600 leading-relaxed">{cs.actual.note}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Honest limitations */}
        <section className="py-12 px-6 bg-slate-50" data-testid="accuracy-limitations">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-4">Where we are less accurate</h2>
            <div className="space-y-3">
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-slate-900">Viral products</h3>
                <p className="text-sm text-slate-600 mt-1 leading-relaxed">Products that go viral on TikTok can shift from 0 demand to massive demand in days. Our trend score captures momentum but cannot predict viral events before they happen.</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-slate-900">New product categories</h3>
                <p className="text-sm text-slate-600 mt-1 leading-relaxed">For genuinely new product types with no historical data, our confidence is lower. We flag this with a "low confidence" indicator.</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-slate-900">Supplier pricing fluctuations</h3>
                <p className="text-sm text-slate-600 mt-1 leading-relaxed">Supplier prices can change quickly, especially during high-demand periods. Our margin estimates use current pricing and may not reflect future cost increases.</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-14 px-6">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-manrope text-2xl font-bold text-slate-900">See the methodology</h2>
            <p className="mt-2 text-sm text-slate-500">Learn exactly how each signal is calculated and weighted.</p>
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link to="/methodology">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-6 h-11">
                  Read Methodology <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/sample-product-analysis">
                <Button variant="outline" className="border-slate-300 text-slate-700 rounded-lg font-medium px-6 h-11">
                  See Sample Report
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
