import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import {
  BarChart3, Megaphone, Rocket, ArrowRight, Check, TrendingUp,
  Package, Target, Zap, Eye, DollarSign,
} from 'lucide-react';

export default function DemoPage() {
  return (
    <LandingLayout>
      <Helmet>
        <title>{`See TrendScout in Action - Examples`}</title>
        <meta name="description" content="See what TrendScout looks like before signing up. Example product analysis, launch plan, and ad ideas." />
      </Helmet>

      <div className="mx-auto max-w-5xl px-6 py-16" data-testid="demo-page">
        <div className="text-center mb-14">
          <h1 className="font-manrope text-4xl font-extrabold text-slate-900" data-testid="demo-title">See TrendScout in Action</h1>
          <p className="mt-3 text-slate-500 max-w-lg mx-auto">No account needed. Here's exactly what you get when you analyse a product.</p>
        </div>

        {/* Example Product Analysis */}
        <section className="mb-16" data-testid="demo-analysis">
          <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-6 flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-indigo-500" /> Example Product Analysis
          </h2>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold">Portable Blender Bottle</h3>
                  <p className="text-slate-400 text-sm mt-1">Health & Fitness</p>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-mono font-bold text-emerald-400">81</div>
                  <p className="text-xs text-slate-400 mt-1">Launch Score</p>
                </div>
              </div>
              <div className="flex items-center gap-2 mt-3">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Strong Candidate</span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">Rising on TikTok</span>
              </div>
            </div>
            <div className="p-6">
              <div className="grid sm:grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Demand', value: 'Rising', icon: TrendingUp, color: 'text-emerald-600 bg-emerald-50' },
                  { label: 'Competition', value: 'Low-Moderate', icon: Target, color: 'text-amber-600 bg-amber-50' },
                  { label: 'Supplier Cost', value: '$8.50', icon: Package, color: 'text-slate-600 bg-slate-50' },
                  { label: 'Est. Retail', value: '$24.99', icon: DollarSign, color: 'text-indigo-600 bg-indigo-50' },
                ].map(({ label, value, icon: Icon, color }) => (
                  <div key={label} className={`rounded-xl p-4 text-center ${color.split(' ')[1]}`}>
                    <Icon className={`h-5 w-5 mx-auto mb-2 ${color.split(' ')[0]}`} />
                    <p className="text-xs text-slate-500">{label}</p>
                    <p className={`font-semibold text-sm mt-0.5 ${color.split(' ')[0]}`}>{value}</p>
                  </div>
                ))}
              </div>
              <div className="mb-6">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Why this product scores well</h4>
                <ul className="space-y-1.5">
                  {['High TikTok engagement (2.4M+ views)', 'Health-conscious trend is growing', '65% estimated profit margin', 'Easy to demonstrate in short-form video', 'Low competition from established brands'].map(r => (
                    <li key={r} className="flex items-center gap-2 text-sm text-slate-600">
                      <Check className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" /> {r}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="text-center pt-4 border-t border-slate-100">
                <p className="text-sm text-slate-400 mb-3">Sign up to unlock the full analysis, supplier data, and ad generation.</p>
                <Link to="/signup">
                  <Button className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl" data-testid="demo-signup-analysis">
                    Get Full Access <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Example Launch Plan */}
        <section className="mb-16" data-testid="demo-launch-plan">
          <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-6 flex items-center gap-2">
            <Rocket className="h-6 w-6 text-violet-500" /> Example Launch Plan
          </h2>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <p className="text-sm text-slate-500 mb-6">Every product comes with a step-by-step launch plan.</p>
            <div className="space-y-4">
              {[
                { step: 1, title: 'Import product to Shopify', desc: 'One-click export with optimised title, description, and pricing.' },
                { step: 2, title: 'Create product page', desc: 'Auto-generated product page with benefit-focused copy.' },
                { step: 3, title: 'Generate ad creatives', desc: 'AI creates 3 ad angles with headlines and descriptions.' },
                { step: 4, title: 'Launch TikTok campaign', desc: 'Start with a $20–$50 test budget targeting the suggested audience.' },
                { step: 5, title: 'Evaluate after 48 hours', desc: 'Check CPC, CTR, and ATC rate. Scale winners, cut losers.' },
              ].map(({ step, title, desc }) => (
                <div key={step} className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 text-white flex items-center justify-center text-sm font-bold">
                    {step}
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm text-slate-900">{title}</h4>
                    <p className="text-sm text-slate-500 mt-0.5">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="text-center pt-6 mt-6 border-t border-slate-100">
              <p className="text-sm text-slate-400 mb-3">Get personalized launch plans for any product.</p>
              <Link to="/signup">
                <Button className="bg-violet-600 hover:bg-violet-700 text-white font-semibold rounded-xl" data-testid="demo-signup-launch">
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Example Ad Ideas */}
        <section className="mb-16" data-testid="demo-ad-ideas">
          <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-6 flex items-center gap-2">
            <Megaphone className="h-6 w-6 text-amber-500" /> Example Ad Ideas
          </h2>
          <div className="grid sm:grid-cols-3 gap-4">
            {[
              { type: 'Problem-Solution', hook: '"Tired of lumpy protein shakes on the go?"', angle: 'Position as the solution to a common frustration. Show the problem, then reveal the product.', cta: 'Get yours while in stock' },
              { type: 'Product Demo', hook: 'Satisfying blending demo', angle: 'Short-form video showing the blender in action. Focus on the visual satisfaction of perfectly smooth results.', cta: 'Shop now — free shipping' },
              { type: 'Curiosity Hook', hook: '"This $25 gadget replaced my $200 blender"', angle: 'Lead with a bold comparison. Create curiosity about how a portable blender can compete.', cta: 'See why 10K+ people switched' },
            ].map(({ type, hook, angle, cta }) => (
              <div key={type} className="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-sm transition-shadow">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">{type}</span>
                <h4 className="font-semibold text-sm text-slate-900 mt-3">{hook}</h4>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed">{angle}</p>
                <div className="mt-4 pt-3 border-t border-slate-100">
                  <p className="text-[11px] text-slate-400">Suggested CTA</p>
                  <p className="text-xs font-medium text-indigo-600">{cta}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="text-center mt-8">
            <p className="text-sm text-slate-400 mb-3">Get AI-generated ad ideas for any product.</p>
            <Link to="/signup">
              <Button className="bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-xl" data-testid="demo-signup-ads">
                Create Free Account <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </section>

        {/* CTA */}
        <section className="text-center bg-gradient-to-r from-indigo-50 to-violet-50 rounded-2xl p-10">
          <h2 className="font-manrope text-2xl font-bold text-slate-900 mb-2">Ready to find your next product?</h2>
          <p className="text-slate-500 text-sm mb-6 max-w-md mx-auto">
            Browse real trending products or create a free account for full access.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link to="/trending-products">
              <Button className="bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl px-6" data-testid="demo-browse-btn">
                Browse Trending Products <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/signup">
              <Button variant="outline" className="font-semibold rounded-xl px-6" data-testid="demo-signup-final">
                Sign Up Free
              </Button>
            </Link>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
