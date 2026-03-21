import React from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import { ArrowRight, TrendingUp, Target, Shield, Zap, Globe, BarChart3 } from 'lucide-react';

const VALUES = [
  { icon: Target, title: 'UK-first intelligence', desc: 'TrendScout is not a generic global tool retrofitted for the UK. Every feature, score, and insight is designed with UK ecommerce economics in mind — VAT, shipping costs, local demand, and UK-specific competition.' },
  { icon: Shield, title: 'Honesty over hype', desc: 'We do not promise guaranteed winners or easy money. Product research is hard. TrendScout gives you better data to make better decisions — not magic formulas.' },
  { icon: BarChart3, title: 'Data you can verify', desc: 'Our scoring methodology is transparent. You can see exactly which signals contribute to a product score and make your own judgement. We show our working.' },
  { icon: Zap, title: 'Speed to decision', desc: 'The goal is not to give you more data than you know what to do with. It is to help you decide faster whether a product is worth testing — saving you time, money, and wasted ad spend.' },
];

export default function AboutPage() {
  return (
    <LandingLayout>
      <PageMeta
        title="About"
        description="TrendScout is a product research and launch intelligence platform built specifically for UK ecommerce sellers."
        canonical="/about"
        schema={[
          { '@context': 'https://schema.org', '@type': 'AboutPage', name: 'About TrendScout', url: 'https://trendscout.click/about' },
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'About' }]),
        ]}
      />
      <div className="bg-white" data-testid="about-page">
        {/* Hero */}
        <section className="pt-16 pb-12 px-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              About TrendScout
            </h1>
            <p className="mt-4 text-lg text-slate-600 leading-relaxed">
              TrendScout is a product research and launch intelligence platform built specifically for UK ecommerce sellers. We help sellers discover trending products, analyse competition, estimate profitability, and make faster launch decisions.
            </p>
          </div>
        </section>

        {/* Story */}
        <section className="py-12 bg-slate-50">
          <div className="max-w-3xl mx-auto px-6">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-4">Why we built this</h2>
            <div className="prose prose-slate prose-sm max-w-none">
              <p className="text-slate-600 leading-relaxed">
                Most product research tools are built for the US market. They track Amazon.com trends, estimate margins based on US economics, and assume US shipping and tax structures. That is fine if you sell in the US.
              </p>
              <p className="text-slate-600 leading-relaxed mt-3">
                But UK sellers face different challenges: 20% VAT, higher shipping costs from overseas suppliers, different consumer expectations around delivery and returns, and a smaller but still significant addressable market. A product that works brilliantly in the US might lose money in the UK.
              </p>
              <p className="text-slate-600 leading-relaxed mt-3">
                TrendScout was built to answer the question that generic tools cannot: <strong className="text-slate-900">can this product actually sell profitably in the UK?</strong>
              </p>
              <p className="text-slate-600 leading-relaxed mt-3">
                We combine multi-channel trend detection with UK-specific commercial analysis to help sellers make better, faster decisions about which products to test — and which to avoid.
              </p>
            </div>
          </div>
        </section>

        {/* Values */}
        <section className="py-16 bg-white">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-8">What we believe</h2>
            <div className="grid sm:grid-cols-2 gap-5">
              {VALUES.map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.title} className="rounded-lg border border-slate-200 p-5">
                    <Icon className="h-5 w-5 text-indigo-600 mb-3" />
                    <h3 className="text-sm font-semibold text-slate-900">{item.title}</h3>
                    <p className="text-sm text-slate-500 mt-2 leading-relaxed">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Company */}
        <section className="py-16 bg-slate-50">
          <div className="max-w-3xl mx-auto px-6">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-4">Company</h2>
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <div className="grid sm:grid-cols-2 gap-6 text-sm">
                <div>
                  <p className="text-slate-500">Name</p>
                  <p className="font-medium text-slate-900 mt-0.5">TrendScout</p>
                </div>
                <div>
                  <p className="text-slate-500">Location</p>
                  <p className="font-medium text-slate-900 mt-0.5">United Kingdom</p>
                </div>
                <div>
                  <p className="text-slate-500">Email</p>
                  <a href="mailto:info@trendscout.click" className="font-medium text-indigo-600 hover:text-indigo-700 mt-0.5 block">info@trendscout.click</a>
                </div>
                <div>
                  <p className="text-slate-500">Website</p>
                  <a href="https://trendscout.click" className="font-medium text-indigo-600 hover:text-indigo-700 mt-0.5 block">trendscout.click</a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-16 bg-white">
          <div className="max-w-2xl mx-auto px-6 text-center">
            <h2 className="font-manrope text-2xl font-bold text-slate-900">See what TrendScout can do</h2>
            <p className="mt-3 text-base text-slate-500">Browse trending products and explore the platform for free.</p>
            <div className="mt-6 flex items-center justify-center gap-3">
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold px-6 h-11" data-testid="about-cta-signup">
                  Start Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/how-it-works">
                <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg font-medium px-6 h-11" data-testid="about-cta-hiw">
                  How It Works
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </LandingLayout>
  );
}
