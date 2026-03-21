import React, { useState, useEffect } from 'react';
import LandingLayout from '@/components/layouts/LandingLayout';
import PageMeta, { breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import { Sparkles, Zap, BarChart3, Target, Shield, Megaphone, Rocket } from 'lucide-react';

const ICON_MAP = {
  feature: Sparkles,
  performance: Zap,
  analytics: BarChart3,
  conversion: Target,
  security: Shield,
  content: Megaphone,
  launch: Rocket,
};

const CHANGELOG = [
  {
    version: '3.4',
    date: 'March 2026',
    entries: [
      { type: 'feature', title: 'Interactive Product Quiz', desc: '4-step quiz at /product-quiz that gives personalised tool recommendations based on your business.' },
      { type: 'feature', title: 'Exit-Intent Lead Magnet', desc: 'Desktop popup offers a free UK Product Research Checklist when visitors are about to leave.' },
      { type: 'feature', title: 'Social Proof Notifications', desc: 'Live activity toasts showing real-time platform activity to build trust with new visitors.' },
      { type: 'feature', title: 'Tool Recommender', desc: '"Which tool is right for me?" widget on comparison pages with honest recommendations.' },
      { type: 'feature', title: 'Shareable Calculator Results', desc: 'Share your free tool results on X/Twitter or copy to clipboard with branded attribution.' },
      { type: 'content', title: '3 Starter Blog Articles', desc: 'Product validation guide, UK VAT guide, and TikTok Shop UK analysis.' },
    ],
  },
  {
    version: '3.3',
    date: 'March 2026',
    entries: [
      { type: 'performance', title: 'Route-Level Code Splitting', desc: '80+ pages now lazy-loaded via React.lazy() for significantly faster initial page load.' },
      { type: 'performance', title: 'Image Lazy Loading', desc: 'All product images now use native lazy loading across 20+ components.' },
      { type: 'performance', title: 'Static Pre-Rendering', desc: '30 marketing pages configured for react-snap pre-rendering in production builds.' },
      { type: 'analytics', title: 'Scroll Depth Tracking', desc: 'Comparison and sample analysis pages now track scroll depth at 25/50/75/100% thresholds.' },
      { type: 'analytics', title: 'Automated Weekly Digest', desc: 'Lead subscribers automatically receive top 5 trending products every Monday.' },
      { type: 'analytics', title: 'Automated Blog Generation', desc: 'AI-generated blog posts for top product categories every Monday.' },
    ],
  },
  {
    version: '3.2',
    date: 'March 2026',
    entries: [
      { type: 'feature', title: 'Sample Product Analysis', desc: 'Public-facing page showing a detailed product report with mock data to demonstrate TrendScout value.' },
      { type: 'feature', title: 'Email Lead Capture', desc: 'Email capture forms on free tools, landing pages, and comparison pages.' },
      { type: 'content', title: '4 New Landing Pages', desc: 'Best products UK, TikTok research, Shopify research, and product validation pages.' },
      { type: 'content', title: '2 New Competitor Comparisons', desc: 'Helium 10 and Ecomhunt added to the comparison hub.' },
      { type: 'conversion', title: 'Mid-Page CTAs', desc: 'Strategic CTA placement and social proof across all marketing pages.' },
    ],
  },
  {
    version: '3.1',
    date: 'March 2026',
    entries: [
      { type: 'analytics', title: 'GA4 Analytics Bridge', desc: '20+ named events wired to key user actions across the site.' },
      { type: 'feature', title: 'UK Product Viability Score', desc: 'Flagship 7-signal scoring system — 0-100 rating of UK commercial potential.' },
      { type: 'content', title: 'JSON-LD Schema Markup', desc: 'Structured data on all public pages for better search engine understanding.' },
    ],
  },
  {
    version: '3.0',
    date: 'March 2026',
    entries: [
      { type: 'launch', title: 'Complete Website Rebuild', desc: 'New homepage, pricing, how it works, about, and contact pages with conversion-focused design.' },
      { type: 'feature', title: 'Free Tools Suite', desc: '4 UK-specific calculators: profit margin, ROAS, VAT, and product pricing.' },
      { type: 'content', title: 'UK Landing Pages', desc: '8+ SEO-optimised landing pages targeting UK ecommerce search terms.' },
      { type: 'content', title: 'Competitor Comparison Hub', desc: 'Detailed comparisons vs Jungle Scout, Sell The Trend, and Minea.' },
    ],
  },
];

export default function ChangelogPage() {
  return (
    <LandingLayout>
      <PageMeta
        title="What's New at TrendScout — Changelog & Product Updates"
        description="See the latest features, improvements, and updates to TrendScout. We ship weekly to help UK ecommerce sellers find better products faster."
        canonical="/changelog"
        schema={[
          webPageSchema('TrendScout Changelog', 'Latest features and product updates', '/changelog'),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Changelog' }]),
        ]}
      />
      <div className="bg-white min-h-[60vh]" data-testid="changelog-page">
        <div className="max-w-2xl mx-auto px-6 py-16">
          <h1 className="font-manrope text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">Changelog</h1>
          <p className="mt-2 text-base text-slate-500">What we have been building for UK sellers.</p>

          <div className="mt-12 space-y-12">
            {CHANGELOG.map((release) => (
              <div key={release.version} data-testid={`changelog-v${release.version}`}>
                <div className="flex items-baseline gap-3 mb-5">
                  <span className="font-mono text-sm font-bold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md">v{release.version}</span>
                  <span className="text-sm text-slate-400">{release.date}</span>
                </div>
                <div className="space-y-3 pl-1 border-l-2 border-slate-100">
                  {release.entries.map((entry, i) => {
                    const Icon = ICON_MAP[entry.type] || Sparkles;
                    return (
                      <div key={i} className="pl-5 relative">
                        <div className="absolute left-[-5px] top-1.5 w-2 h-2 rounded-full bg-slate-300" />
                        <div className="flex items-start gap-2.5">
                          <Icon className="h-4 w-4 text-slate-400 mt-0.5 flex-shrink-0" />
                          <div>
                            <h3 className="text-sm font-semibold text-slate-900">{entry.title}</h3>
                            <p className="text-sm text-slate-500 leading-relaxed mt-0.5">{entry.desc}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </LandingLayout>
  );
}
