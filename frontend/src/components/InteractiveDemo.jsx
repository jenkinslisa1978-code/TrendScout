import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { RevealSection } from '@/hooks/useScrollReveal';
import { trackEvent, EVENTS } from '@/services/analytics';
import {
  Search, BarChart3, Shield, Zap, TrendingUp,
  ArrowRight, ChevronRight, Package, Eye, Target,
} from 'lucide-react';

const HERO_IMG = 'https://static.prod-images.emergentagent.com/jobs/ac2f3a7b-43fc-47c2-a8a8-ff06d2e4c364/images/9e43031a2a6c68898323a79dc325d24cd4db83b9150424ed694dc19e140553b0.png';

const TOUR_STEPS = [
  {
    id: 'browse',
    label: 'Browse',
    icon: Eye,
    title: 'Browse trending products',
    desc: 'See products gaining traction across TikTok, Amazon, and Shopify — updated daily with real trend signals.',
    mockContent: (
      <div className="space-y-3">
        {[
          { name: 'LED Sunset Lamp', score: 78, trend: '+42%', cat: 'Home & Living' },
          { name: 'Portable Neck Fan', score: 65, trend: '+28%', cat: 'Electronics' },
          { name: 'Glass Water Bottle', score: 71, trend: '+35%', cat: 'Health' },
        ].map((p) => (
          <div key={p.name} className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 hover:border-indigo-200 transition-colors cursor-pointer">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 shrink-0">
              <Package className="h-5 w-5 text-slate-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-900 truncate">{p.name}</p>
              <p className="text-xs text-slate-500">{p.cat}</p>
            </div>
            <div className="text-right shrink-0">
              <span className={`inline-flex items-center rounded-md border px-1.5 py-0.5 text-xs font-bold ${p.score >= 70 ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : 'text-amber-700 bg-amber-50 border-amber-200'}`}>
                {p.score}/100
              </span>
              <p className="text-xs text-emerald-600 font-medium mt-0.5">{p.trend}</p>
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'score',
    label: 'Score',
    icon: BarChart3,
    title: 'See the viability score',
    desc: 'Every product gets a 0–100 UK Viability Score based on 7 weighted signals — not just hype.',
    mockContent: (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-900">LED Sunset Lamp</span>
          <span className="font-mono text-2xl font-extrabold text-indigo-600">78<span className="text-sm text-slate-400">/100</span></span>
        </div>
        {[
          { label: 'Trend momentum', val: 85 },
          { label: 'Market saturation', val: 42 },
          { label: 'Margin potential', val: 72 },
          { label: 'Ad opportunity', val: 68 },
          { label: 'Search growth', val: 90 },
          { label: 'Social buzz', val: 95 },
          { label: 'Supplier availability', val: 65 },
        ].map((s) => (
          <div key={s.label}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-600">{s.label}</span>
              <span className="font-mono font-bold text-slate-700">{s.val}%</span>
            </div>
            <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500" style={{ width: `${s.val}%` }} />
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'analyse',
    label: 'Analyse',
    icon: Shield,
    title: 'Check UK viability',
    desc: 'See estimated margins, VAT impact, shipping costs, and saturation — specifically for UK sellers.',
    mockContent: (
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-2">
          {[
            { label: 'Est. margin', val: '£8.40', sub: 'After VAT & shipping', color: 'text-emerald-600' },
            { label: 'Saturation', val: 'Medium', sub: '~120 UK sellers', color: 'text-amber-600' },
            { label: 'VAT impact', val: '-£3.33', sub: '20% standard rate', color: 'text-red-500' },
            { label: 'Shipping', val: '£2.80', sub: 'To UK mainland', color: 'text-slate-600' },
          ].map((m) => (
            <div key={m.label} className="rounded-lg border border-slate-200 bg-white p-3">
              <p className="text-xs text-slate-500">{m.label}</p>
              <p className={`text-lg font-bold ${m.color} font-mono`}>{m.val}</p>
              <p className="text-[10px] text-slate-400">{m.sub}</p>
            </div>
          ))}
        </div>
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-3">
          <p className="text-xs font-semibold text-emerald-800">Verdict: Promising for UK market</p>
          <p className="text-xs text-emerald-700 mt-1">Decent margins after VAT. Medium competition leaves room to enter. Strong social signals suggest growing demand.</p>
        </div>
      </div>
    ),
  },
  {
    id: 'launch',
    label: 'Launch',
    icon: Zap,
    title: 'Get launch insights',
    desc: 'AI-generated ad angles, competitor analysis, and a clear go/no-go recommendation.',
    mockContent: (
      <div className="space-y-3">
        <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-3">
          <p className="text-xs font-semibold text-indigo-800 flex items-center gap-1"><Zap className="h-3 w-3" /> AI Ad Angles</p>
          <ul className="mt-2 space-y-1.5">
            {[
              '"Transform any room in seconds — the TikTok-famous sunset lamp"',
              '"The £16.99 home upgrade going viral across the UK"',
              '"Gift idea alert: This lamp has 4.7 stars and 2M+ views"',
            ].map((a) => (
              <li key={a} className="text-xs text-indigo-700 flex items-start gap-1.5">
                <ChevronRight className="h-3 w-3 mt-0.5 shrink-0" />{a}
              </li>
            ))}
          </ul>
        </div>
        <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
            <Target className="h-5 w-5 text-emerald-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">Recommendation: Test this product</p>
            <p className="text-xs text-slate-500">Score 78/100 with strong social signals and viable UK margins.</p>
          </div>
        </div>
      </div>
    ),
  },
];

export default function InteractiveDemo() {
  const [activeStep, setActiveStep] = useState(0);
  const step = TOUR_STEPS[activeStep];

  return (
    <section className="py-20 lg:py-28 bg-slate-50" data-testid="interactive-demo-section">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <RevealSection className="text-center max-w-2xl mx-auto mb-12">
          <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest mb-3">Interactive Preview</p>
          <h2 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            See how TrendScout works — before you sign up
          </h2>
          <p className="mt-3 text-base text-slate-500">
            Click through the steps below to explore the product research workflow.
          </p>
        </RevealSection>

        <RevealSection delay={100}>
          <div className="grid lg:grid-cols-5 gap-8 items-start">
            {/* Step tabs */}
            <div className="lg:col-span-2 space-y-2">
              {TOUR_STEPS.map((s, idx) => {
                const Icon = s.icon;
                const isActive = idx === activeStep;
                return (
                  <button
                    key={s.id}
                    onClick={() => {
                      setActiveStep(idx);
                      trackEvent('demo_step_click', { step: s.id });
                    }}
                    className={`w-full text-left rounded-xl border p-4 transition-all duration-300 ${
                      isActive
                        ? 'border-indigo-500 bg-white shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500'
                        : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm'
                    }`}
                    data-testid={`demo-tab-${s.id}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`flex h-9 w-9 items-center justify-center rounded-lg transition-colors ${
                        isActive ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-400'
                      }`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs text-slate-400">0{idx + 1}</span>
                          <h3 className={`text-sm font-semibold ${isActive ? 'text-indigo-600' : 'text-slate-900'}`}>{s.label}</h3>
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{s.title}</p>
                      </div>
                    </div>
                  </button>
                );
              })}

              <div className="pt-3">
                <Link to="/signup">
                  <Button
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold shadow-sm h-11"
                    data-testid="demo-signup-cta"
                    onClick={() => trackEvent(EVENTS.SIGNUP_CLICK, { source: 'interactive_demo' })}
                  >
                    Try it for real — Start Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>

            {/* Preview panel */}
            <div className="lg:col-span-3">
              <div className="rounded-2xl border border-slate-200 bg-white shadow-lg overflow-hidden" data-testid="demo-preview-panel">
                {/* Mock browser chrome */}
                <div className="flex items-center gap-2 px-4 py-2.5 bg-slate-50 border-b border-slate-200">
                  <div className="flex gap-1.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-red-400" />
                    <div className="h-2.5 w-2.5 rounded-full bg-amber-400" />
                    <div className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
                  </div>
                  <div className="flex-1 mx-4">
                    <div className="bg-white rounded-md border border-slate-200 px-3 py-1 text-xs text-slate-400 font-mono">
                      trendscout.click/dashboard
                    </div>
                  </div>
                </div>

                {/* Content area */}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    {React.createElement(step.icon, { className: 'h-4 w-4 text-indigo-600' })}
                    <h3 className="text-base font-semibold text-slate-900">{step.title}</h3>
                  </div>
                  <p className="text-sm text-slate-500 mb-5">{step.desc}</p>
                  <div data-testid={`demo-content-${step.id}`}>
                    {step.mockContent}
                  </div>
                </div>

                {/* Step indicator */}
                <div className="flex items-center justify-between px-6 py-3 bg-slate-50 border-t border-slate-100">
                  <div className="flex gap-1.5">
                    {TOUR_STEPS.map((_, idx) => (
                      <div
                        key={idx}
                        className={`h-1.5 rounded-full transition-all duration-300 ${
                          idx === activeStep ? 'w-6 bg-indigo-500' : 'w-1.5 bg-slate-300'
                        }`}
                      />
                    ))}
                  </div>
                  {activeStep < TOUR_STEPS.length - 1 ? (
                    <button
                      onClick={() => setActiveStep(activeStep + 1)}
                      className="text-xs font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                      data-testid="demo-next-btn"
                    >
                      Next: {TOUR_STEPS[activeStep + 1].label} <ChevronRight className="h-3 w-3" />
                    </button>
                  ) : (
                    <Link to="/signup" className="text-xs font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
                      Try it for real <ArrowRight className="h-3 w-3" />
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        </RevealSection>
      </div>
    </section>
  );
}
