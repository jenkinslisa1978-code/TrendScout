import React from 'react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Info } from 'lucide-react';

const TOOLTIPS = {
  'launch-score': {
    title: 'Launch Score',
    text: 'A prediction of product success based on 7 market signals. Higher is better. 80+ = Strong Launch.',
  },
  'success-probability': {
    title: 'Success Probability',
    text: 'The estimated likelihood this product will be a winner, based on historical patterns and current signals.',
  },
  'trend-stage': {
    title: 'Trend Stage',
    text: 'Where this product is in its lifecycle: Exploding (peak momentum), Emerging (early opportunity), Rising, Stable, or Declining.',
  },
  'supplier': {
    title: 'Supplier',
    text: 'Where the product ships from. You don\'t hold stock — the supplier ships directly to your customer (dropshipping).',
  },
  'profit-estimate': {
    title: 'Estimated Profit',
    text: 'The difference between the recommended selling price and the supplier cost, per unit sold.',
  },
  'trend-score': {
    title: 'Trend Score',
    text: 'Measures how strongly this product is trending across TikTok, Amazon, and Google — based on engagement, rank movement, and search interest.',
  },
  'margin-score': {
    title: 'Margin Score',
    text: 'Rates the profit potential. Considers selling price vs supplier cost, with higher margins earning a better score.',
  },
  'competition-score': {
    title: 'Competition Score',
    text: 'Measures how competitive the market is. Lower competition = higher score = better opportunity for you.',
  },
  'ad-activity': {
    title: 'Ad Activity Score',
    text: 'Tracks active ads across TikTok, Meta, and Google Shopping. Some activity is good (validates demand), too much means saturation.',
  },
  'supplier-demand': {
    title: 'Supplier Demand Score',
    text: 'Based on supplier order velocity and availability. High demand from suppliers indicates a proven market.',
  },
  'search-growth': {
    title: 'Search Growth Score',
    text: 'Measures how fast people are searching for this product on Google. Rapid growth signals an emerging opportunity.',
  },
  'order-velocity': {
    title: 'Order Velocity Score',
    text: 'Tracks how fast the product is selling on supplier platforms. High velocity means proven buyer demand.',
  },
  'confidence': {
    title: 'Data Confidence',
    text: 'How reliable our data is for this product. Higher confidence means more data sources and fresher signals.',
  },
};

export function EducationTooltip({ term, children, className = '' }) {
  const tip = TOOLTIPS[term];
  if (!tip) return children || null;

  return (
    <TooltipProvider>
      <Tooltip delayDuration={200}>
        <TooltipTrigger asChild>
          <span className={`inline-flex items-center gap-1 cursor-help ${className}`} data-testid={`tooltip-${term}`}>
            {children}
            <Info className="h-3 w-3 text-slate-400 hover:text-indigo-500 transition-colors flex-shrink-0" />
          </span>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-[260px]">
          <p className="font-semibold text-xs mb-0.5">{tip.title}</p>
          <p className="text-xs text-slate-300 leading-relaxed">{tip.text}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export { TOOLTIPS };
