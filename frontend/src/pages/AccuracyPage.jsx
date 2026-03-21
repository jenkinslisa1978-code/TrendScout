import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import useScrollDepth from '@/hooks/useScrollDepth';
import { ArrowRight, AlertTriangle, TrendingUp, BarChart3, Target, Clock, Database, RefreshCw } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function AccuracyPage() {
  useScrollDepth('accuracy');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/accuracy/stats`)
      .then(r => r.json())
      .then(d => { if (d.status === 'ok') setStats(d); })
      .catch(() => {});
  }, []);

  return (
    <LandingLayout>
      <PageMeta
        title="How Accurate is TrendScout? — Our Approach to Data Quality"
        description="Full transparency on how TrendScout measures and improves the accuracy of its product intelligence. See our live accuracy metrics and methodology."
        canonical="/accuracy"
        schema={[
          webPageSchema('TrendScout Accuracy', 'Our approach to data quality and prediction accuracy', '/accuracy'),
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
              We believe the best way to earn your trust is to be completely transparent about what we know, what we estimate, and where our data has limitations.
            </p>
          </div>
        </section>

        {/* Live accuracy metrics */}
        <section className="py-10 px-6 bg-slate-50">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-2">Live accuracy tracking</h2>
            <p className="text-sm text-slate-500 mb-6">
              We snapshot every product score when it is first calculated, then compare it against real market data 30 and 90 days later. These numbers update automatically.
            </p>

            {stats && stats.total_tracked > 0 ? (
              <>
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="rounded-xl border border-slate-200 bg-white p-5 text-center">
                    <p className="font-mono text-2xl font-bold text-slate-900">{stats.total_tracked}</p>
                    <p className="text-xs text-slate-500 mt-1">Products tracked</p>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-white p-5 text-center">
                    <p className="font-mono text-2xl font-bold text-emerald-600">{stats.margin_accuracy_pct}%</p>
                    <p className="text-xs text-slate-500 mt-1">Margin estimates within 5%</p>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-white p-5 text-center">
                    <p className="font-mono text-2xl font-bold text-indigo-600">{stats.trend_accuracy_pct}%</p>
                    <p className="text-xs text-slate-500 mt-1">Trend direction correct</p>
                  </div>
                </div>
                <p className="text-xs text-slate-400 text-center">
                  Last updated: {stats.last_updated || 'recently'} | Based on {stats.total_tracked} products tracked over 30+ days
                </p>
              </>
            ) : (
              <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center" data-testid="accuracy-building">
                <RefreshCw className="h-8 w-8 text-slate-300 mx-auto mb-3" />
                <h3 className="text-sm font-semibold text-slate-900">We are building our accuracy track record</h3>
                <p className="text-sm text-slate-500 mt-2 max-w-md mx-auto leading-relaxed">
                  We have recently started tracking prediction accuracy against real market outcomes. Once we have enough data (30+ products tracked over 30+ days), verified accuracy metrics will appear here automatically.
                </p>
                <p className="text-xs text-slate-400 mt-3">
                  In the meantime, read our methodology to understand exactly how scores are calculated.
                </p>
              </div>
            )}
          </div>
        </section>

        {/* What we measure and how */}
        <section className="py-12 px-6">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-6">How we measure accuracy</h2>
            <div className="space-y-4">
              <div className="rounded-lg border border-slate-200 p-5" data-testid="accuracy-method-snapshot">
                <div className="flex items-center gap-2 mb-2">
                  <Database className="h-4 w-4 text-indigo-600" />
                  <h3 className="text-sm font-semibold text-slate-900">Step 1: Snapshot predictions</h3>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">
                  When a product is first scored, we save a timestamped snapshot: the viability score, estimated margin, trend direction, competition level, and all 7 signal values. This is the prediction we are testing.
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 p-5" data-testid="accuracy-method-track">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="h-4 w-4 text-indigo-600" />
                  <h3 className="text-sm font-semibold text-slate-900">Step 2: Track over time</h3>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">
                  After 30 and 90 days, we re-evaluate the same product with fresh market data. We compare the original prediction against what actually happened: Did the trend go the direction we predicted? Was the margin estimate within 5% of reality? Did the competition level change as expected?
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 p-5" data-testid="accuracy-method-report">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 className="h-4 w-4 text-indigo-600" />
                  <h3 className="text-sm font-semibold text-slate-900">Step 3: Report honestly</h3>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">
                  The accuracy metrics on this page come directly from that comparison. We do not cherry-pick results. When we get something wrong, it counts against the overall accuracy score. As more products are tracked, these numbers become more statistically significant.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* What is real vs estimated */}
        <section className="py-12 px-6 bg-slate-50" data-testid="accuracy-data-types">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-4">What is real data vs what is estimated</h2>
            <div className="space-y-4">
              <div className="rounded-lg border border-emerald-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-emerald-700 mb-2">Real data (directly from source)</h3>
                <ul className="text-sm text-slate-600 space-y-1.5 leading-relaxed">
                  <li><strong>Search trends</strong> — pulled directly from Google Trends UK API</li>
                  <li><strong>Amazon rankings</strong> — BSR and category positions from Amazon UK</li>
                  <li><strong>Supplier prices</strong> — live pricing from CJ Dropshipping catalogue</li>
                  <li><strong>TikTok product listings</strong> — from TikTok Shop UK data</li>
                  <li><strong>Product details</strong> — names, images, categories from marketplace listings</li>
                </ul>
              </div>
              <div className="rounded-lg border border-amber-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-amber-700 mb-2">Estimated (calculated from data)</h3>
                <ul className="text-sm text-slate-600 space-y-1.5 leading-relaxed">
                  <li><strong>Profit margins</strong> — calculated from supplier price + estimated UK shipping + 20% VAT + platform fees. Your actual margins depend on your specific supplier terms and fulfilment costs.</li>
                  <li><strong>Competition level</strong> — based on visible seller count and review distribution. May miss sellers on platforms we do not track.</li>
                  <li><strong>Ad viability</strong> — estimated from keyword CPC data and product category benchmarks. Actual ad performance depends on your creatives and targeting.</li>
                  <li><strong>UK market fit</strong> — our assessment based on seasonal patterns and demand signals. Subjective element involved.</li>
                </ul>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-slate-700 mb-2">Not available</h3>
                <ul className="text-sm text-slate-600 space-y-1.5 leading-relaxed">
                  <li><strong>Exact competitor revenue</strong> — no tool can access this. Estimates are based on BSR and review velocity.</li>
                  <li><strong>Future trends</strong> — we show current momentum, not predictions of future events.</li>
                  <li><strong>Your specific ROI</strong> — this depends on execution (your ads, your store, your operations).</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Honest limitations */}
        <section className="py-12 px-6" data-testid="accuracy-limitations">
          <div className="max-w-2xl mx-auto">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-4.5 w-4.5 text-amber-600" />
              <h2 className="font-manrope text-xl font-bold text-slate-900">Known limitations</h2>
            </div>
            <div className="space-y-3">
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-slate-900">Viral products</h3>
                <p className="text-sm text-slate-600 mt-1 leading-relaxed">Products that go viral on TikTok can shift from 0 demand to massive demand in days. Our trend score captures current momentum but cannot predict viral events before they happen.</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-slate-900">New product categories</h3>
                <p className="text-sm text-slate-600 mt-1 leading-relaxed">For genuinely new product types with no historical data, our confidence is lower. We flag this with a "low confidence" indicator.</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-slate-900">Supplier pricing fluctuations</h3>
                <p className="text-sm text-slate-600 mt-1 leading-relaxed">Supplier prices can change, especially during high-demand periods. Our margin estimates use current pricing and may not reflect future cost changes.</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5">
                <h3 className="text-sm font-semibold text-slate-900">Platform coverage</h3>
                <p className="text-sm text-slate-600 mt-1 leading-relaxed">We track Amazon UK, Shopify stores, and TikTok Shop. Sellers on other platforms (eBay UK, Etsy, etc.) are not included in competition analysis.</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-14 px-6 bg-slate-50">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="font-manrope text-2xl font-bold text-slate-900">Understand the methodology</h2>
            <p className="mt-2 text-sm text-slate-500">See exactly how each of the 7 signals is calculated and weighted.</p>
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
