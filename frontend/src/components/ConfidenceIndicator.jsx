import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Data confidence indicator — shows High/Medium/Low based on data availability.
 * Sits next to scores to tell users how much they can trust the number.
 *
 * Usage: <ConfidenceIndicator level="high" />
 *   or:  <ConfidenceIndicator dataPoints={45} />
 */
export default function ConfidenceIndicator({ level, dataPoints, className = '' }) {
  // Auto-determine level from data points if not provided
  const resolved = level || (
    dataPoints >= 30 ? 'high' :
    dataPoints >= 10 ? 'medium' : 'low'
  );

  const config = {
    high: { label: 'High confidence', dot: 'bg-emerald-500', text: 'text-emerald-700', bg: 'bg-emerald-50' },
    medium: { label: 'Medium confidence', dot: 'bg-amber-500', text: 'text-amber-700', bg: 'bg-amber-50' },
    low: { label: 'Low confidence', dot: 'bg-slate-400', text: 'text-slate-600', bg: 'bg-slate-50' },
  };

  const c = config[resolved] || config.medium;

  return (
    <Link
      to="/methodology#confidence-levels"
      className={`inline-flex items-center gap-1.5 rounded-md ${c.bg} px-2 py-0.5 text-[10px] font-medium ${c.text} hover:opacity-80 transition-opacity ${className}`}
      data-testid={`confidence-${resolved}`}
      title={`${c.label} — Click to learn more`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {c.label}
    </Link>
  );
}
