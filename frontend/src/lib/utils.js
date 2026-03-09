import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

// Format currency
export function formatCurrency(amount, currency = 'GBP') {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: currency,
  }).format(amount);
}

// Format large numbers
export function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

// Get trend stage color
export function getTrendStageColor(stage) {
  const colors = {
    early: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    rising: 'bg-blue-50 text-blue-700 border-blue-200',
    peak: 'bg-amber-50 text-amber-700 border-amber-200',
    saturated: 'bg-slate-100 text-slate-600 border-slate-200',
  };
  return colors[stage] || colors.saturated;
}

// Get opportunity rating color
export function getOpportunityColor(rating) {
  const colors = {
    'very high': 'bg-emerald-50 text-emerald-700 border-emerald-200',
    high: 'bg-blue-50 text-blue-700 border-blue-200',
    medium: 'bg-amber-50 text-amber-700 border-amber-200',
    low: 'bg-slate-100 text-slate-600 border-slate-200',
  };
  return colors[rating] || colors.low;
}

// Get competition level color
export function getCompetitionColor(level) {
  const colors = {
    low: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    medium: 'bg-amber-50 text-amber-700 border-amber-200',
    high: 'bg-red-50 text-red-700 border-red-200',
  };
  return colors[level] || colors.medium;
}

// Get trend score color
export function getTrendScoreColor(score) {
  if (score >= 80) return 'text-emerald-600';
  if (score >= 60) return 'text-blue-600';
  if (score >= 40) return 'text-amber-600';
  return 'text-slate-500';
}
