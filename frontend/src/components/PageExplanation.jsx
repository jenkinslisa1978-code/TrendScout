import React from 'react';
import { Info } from 'lucide-react';

const PAGE_EXPLANATIONS = {
  '/discover': {
    title: 'Find Products',
    description: 'Browse products currently gaining traction online. TrendScout scans thousands of products daily to surface the ones with the best potential.',
  },
  '/product': {
    title: 'Product Analysis',
    description: 'TrendScout evaluates whether this product may be worth testing. See scores, profit estimates, competitor data, and a step-by-step launch plan.',
  },
  '/ad-tests': {
    title: 'Ad Ideas',
    description: 'Suggested marketing angles for advertising products. AI-generated ad copy for TikTok, Facebook, Instagram, and more.',
  },
  '/outcomes': {
    title: 'Profit Estimate',
    description: 'Estimate whether a product could be profitable before launching ads. Track your estimated returns across products.',
  },
  '/stores': {
    title: 'My Stores',
    description: 'Manage your store configurations. Products exported here can be published to your connected Shopify, WooCommerce, or other platforms.',
  },
  '/settings/connections': {
    title: 'Connections',
    description: 'Connect your e-commerce store and ad platform accounts. This enables one-click product publishing and automatic ad posting.',
  },
};

export default function PageExplanation({ pathname }) {
  // Match exact or partial path
  const info = PAGE_EXPLANATIONS[pathname] ||
    Object.entries(PAGE_EXPLANATIONS).find(([key]) => pathname.startsWith(key))?.[1];

  if (!info) return null;

  const dismissed = localStorage.getItem(`page_explanation_${pathname}_dismissed`);
  if (dismissed) return null;

  return (
    <div className="flex items-start gap-2 bg-indigo-50/60 border border-indigo-100 rounded-lg px-4 py-2.5 mb-4" data-testid="page-explanation">
      <Info className="h-4 w-4 text-indigo-500 mt-0.5 shrink-0" />
      <div>
        <p className="text-xs text-indigo-700">{info.description}</p>
      </div>
      <button
        onClick={() => {
          localStorage.setItem(`page_explanation_${pathname}_dismissed`, 'true');
          window.location.reload();
        }}
        className="text-[10px] text-indigo-400 hover:text-indigo-600 shrink-0 ml-auto"
      >
        Dismiss
      </button>
    </div>
  );
}
