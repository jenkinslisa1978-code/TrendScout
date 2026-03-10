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

// Get early trend label info
export function getEarlyTrendInfo(label) {
  const info = {
    exploding: { 
      text: '🔥 Exploding', 
      color: 'bg-red-50 text-red-700 border-red-200',
      icon: '🔥',
      priority: 'critical'
    },
    rising: { 
      text: '📈 Rising', 
      color: 'bg-orange-50 text-orange-700 border-orange-200',
      icon: '📈',
      priority: 'high'
    },
    early_trend: { 
      text: '🌱 Early Trend', 
      color: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      icon: '🌱',
      priority: 'medium'
    },
    stable: { 
      text: 'Stable', 
      color: 'bg-slate-100 text-slate-600 border-slate-200',
      icon: '—',
      priority: 'low'
    },
  };
  return info[label] || info.stable;
}

// Get early trend score color
export function getEarlyTrendScoreColor(score) {
  if (score >= 85) return 'text-red-600';
  if (score >= 65) return 'text-orange-600';
  if (score >= 45) return 'text-emerald-600';
  return 'text-slate-500';
}

// Get success probability color
export function getSuccessProbabilityColor(score) {
  if (score >= 80) return 'text-emerald-600';
  if (score >= 60) return 'text-blue-600';
  if (score >= 40) return 'text-amber-600';
  return 'text-slate-500';
}

// Get success probability badge color
export function getSuccessBadgeColor(score) {
  if (score >= 80) return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (score >= 60) return 'bg-blue-50 text-blue-700 border-blue-200';
  if (score >= 40) return 'bg-amber-50 text-amber-700 border-amber-200';
  return 'bg-slate-100 text-slate-600 border-slate-200';
}

// Get market score color
export function getMarketScoreColor(score) {
  if (score >= 80) return 'text-emerald-600';
  if (score >= 60) return 'text-blue-600';
  if (score >= 40) return 'text-amber-600';
  return 'text-slate-500';
}

// Get market opportunity badge info
export function getMarketOpportunityInfo(label) {
  const info = {
    massive: { 
      text: 'Massive Opportunity', 
      shortText: 'Massive',
      color: 'bg-purple-50 text-purple-700 border-purple-200',
      bgColor: 'bg-purple-500',
      textColor: 'text-purple-600',
      description: 'Exceptional opportunity with high demand, margins, and low competition'
    },
    strong: { 
      text: 'Strong Opportunity', 
      shortText: 'Strong',
      color: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      bgColor: 'bg-emerald-500',
      textColor: 'text-emerald-600',
      description: 'Strong market demand with favorable margins and manageable competition'
    },
    competitive: { 
      text: 'Competitive', 
      shortText: 'Competitive',
      color: 'bg-amber-50 text-amber-700 border-amber-200',
      bgColor: 'bg-amber-500',
      textColor: 'text-amber-600',
      description: 'Good market potential but requires differentiation strategy'
    },
    saturated: { 
      text: 'Saturated', 
      shortText: 'Saturated',
      color: 'bg-slate-100 text-slate-600 border-slate-200',
      bgColor: 'bg-slate-400',
      textColor: 'text-slate-500',
      description: 'High competition - consider alternative products'
    },
    // Legacy labels (backwards compatibility)
    high: { 
      text: 'High Opportunity', 
      shortText: 'High',
      color: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      bgColor: 'bg-emerald-500',
      textColor: 'text-emerald-600',
      description: 'Strong market demand with favorable margins and low competition'
    },
    medium: { 
      text: 'Medium Opportunity', 
      shortText: 'Medium',
      color: 'bg-blue-50 text-blue-700 border-blue-200',
      bgColor: 'bg-blue-500',
      textColor: 'text-blue-600',
      description: 'Good market potential with balanced competition'
    },
    low: { 
      text: 'Low Opportunity', 
      shortText: 'Low',
      color: 'bg-amber-50 text-amber-700 border-amber-200',
      bgColor: 'bg-amber-500',
      textColor: 'text-amber-600',
      description: 'Moderate market potential, consider differentiation'
    },
    very_low: { 
      text: 'Very Low', 
      shortText: 'V. Low',
      color: 'bg-slate-100 text-slate-600 border-slate-200',
      bgColor: 'bg-slate-400',
      textColor: 'text-slate-500',
      description: 'Challenging market conditions'
    },
  };
  return info[label] || info.competitive;
}

// Get market saturation color
export function getMarketSaturationColor(saturation) {
  if (saturation >= 70) return 'text-red-600';
  if (saturation >= 50) return 'text-amber-600';
  if (saturation >= 30) return 'text-blue-600';
  return 'text-emerald-600';
}

// Get market saturation label
export function getMarketSaturationLabel(saturation) {
  if (saturation >= 70) return 'Saturated';
  if (saturation >= 50) return 'Competitive';
  if (saturation >= 30) return 'Growing';
  return 'Emerging';
}
