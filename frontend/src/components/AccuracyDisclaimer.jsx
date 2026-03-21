import React from 'react';
import { Link } from 'react-router-dom';
import { Info } from 'lucide-react';

const DISCLAIMERS = {
  margin: {
    text: 'Margin estimates include UK VAT (20%), estimated shipping, and platform fees. Your actual margins may vary based on supplier terms, fulfilment method, and return rates.',
    link: '/methodology',
    linkText: 'See full methodology',
  },
  score: {
    text: 'The viability score is a data-driven starting point based on 7 weighted signals. Always verify key assumptions with your own supplier quotes and market research before investing.',
    link: '/methodology',
    linkText: 'How we score products',
  },
  trend: {
    text: 'Trend data reflects current momentum from marketplace and social signals. Trends can shift rapidly — use this as direction, not guarantee.',
    link: '/accuracy',
    linkText: 'How accurate are we?',
  },
  calculator: {
    text: 'Calculator results are estimates based on the values you provide. Real-world results depend on your specific supplier costs, ad performance, and operational efficiency.',
    link: '/tools',
    linkText: 'Learn more about our tools',
  },
};

/**
 * Contextual accuracy disclaimer.
 * Usage: <AccuracyDisclaimer type="margin" />
 */
export default function AccuracyDisclaimer({ type = 'score', className = '' }) {
  const d = DISCLAIMERS[type] || DISCLAIMERS.score;

  return (
    <div className={`flex items-start gap-2 rounded-lg bg-slate-50 border border-slate-100 px-3 py-2.5 ${className}`} data-testid={`accuracy-disclaimer-${type}`}>
      <Info className="h-3.5 w-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
      <p className="text-xs text-slate-500 leading-relaxed">
        {d.text}{' '}
        <Link to={d.link} className="font-medium text-indigo-600 hover:text-indigo-700">
          {d.linkText} &rarr;
        </Link>
      </p>
    </div>
  );
}
