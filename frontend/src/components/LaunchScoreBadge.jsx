/**
 * Launch Score Badge Component
 * 
 * Displays the Product Launch Score - the primary decision metric.
 * Shows score with color-coded label and optional reasoning.
 */

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { 
  Rocket, 
  TrendingUp, 
  AlertTriangle, 
  XCircle,
  Info
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

// Launch score display configurations
const LAUNCH_SCORE_CONFIG = {
  strong_launch: {
    label: 'Strong Launch',
    shortLabel: 'Launch',
    icon: Rocket,
    bgColor: 'bg-green-500',
    textColor: 'text-green-700',
    badgeColor: 'bg-green-50 text-green-700 border-green-200',
    scoreColor: 'text-green-600',
    description: 'Excellent conditions for launch'
  },
  promising: {
    label: 'Promising',
    shortLabel: 'Promising',
    icon: TrendingUp,
    bgColor: 'bg-blue-500',
    textColor: 'text-blue-700',
    badgeColor: 'bg-blue-50 text-blue-700 border-blue-200',
    scoreColor: 'text-blue-600',
    description: 'Good potential with manageable risks'
  },
  risky: {
    label: 'Risky',
    shortLabel: 'Risky',
    icon: AlertTriangle,
    bgColor: 'bg-amber-500',
    textColor: 'text-amber-700',
    badgeColor: 'bg-amber-50 text-amber-700 border-amber-200',
    scoreColor: 'text-amber-600',
    description: 'Proceed with caution - test small first'
  },
  avoid: {
    label: 'Avoid',
    shortLabel: 'Avoid',
    icon: XCircle,
    bgColor: 'bg-red-500',
    textColor: 'text-red-700',
    badgeColor: 'bg-red-50 text-red-700 border-red-200',
    scoreColor: 'text-red-600',
    description: 'High risk - consider alternatives'
  }
};

// Get config from score
function getConfigFromScore(score) {
  if (score >= 80) return LAUNCH_SCORE_CONFIG.strong_launch;
  if (score >= 60) return LAUNCH_SCORE_CONFIG.promising;
  if (score >= 40) return LAUNCH_SCORE_CONFIG.risky;
  return LAUNCH_SCORE_CONFIG.avoid;
}

// Main badge component - shows score prominently
export function LaunchScoreBadge({ 
  score = 0, 
  label = null, 
  reasoning = null,
  showReasoning = false,
  size = 'default', // 'small', 'default', 'large'
  variant = 'full' // 'full', 'compact', 'score-only'
}) {
  const config = label ? LAUNCH_SCORE_CONFIG[label] : getConfigFromScore(score);
  const Icon = config?.icon || AlertTriangle;
  
  const sizeClasses = {
    small: {
      container: 'gap-1.5',
      score: 'text-lg font-bold',
      label: 'text-xs',
      icon: 'h-3 w-3'
    },
    default: {
      container: 'gap-2',
      score: 'text-2xl font-bold',
      label: 'text-sm',
      icon: 'h-4 w-4'
    },
    large: {
      container: 'gap-3',
      score: 'text-4xl font-bold',
      label: 'text-base',
      icon: 'h-5 w-5'
    }
  };
  
  const sizes = sizeClasses[size] || sizeClasses.default;

  if (variant === 'score-only') {
    return (
      <span className={`font-mono ${sizes.score} ${config.scoreColor}`}>
        {score}
      </span>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={`flex items-center ${sizes.container}`}>
        <span className={`font-mono ${sizes.score} ${config.scoreColor}`}>
          {score}
        </span>
        <Badge className={`${config.badgeColor} border ${sizes.label}`}>
          {config.shortLabel}
        </Badge>
      </div>
    );
  }

  // Full variant
  const content = (
    <div className={`flex items-center ${sizes.container}`}>
      <div className={`flex items-center justify-center p-1.5 rounded-lg ${config.bgColor}`}>
        <Icon className={`${sizes.icon} text-white`} />
      </div>
      <div>
        <div className="flex items-center gap-2">
          <span className={`font-mono ${sizes.score} ${config.scoreColor}`}>
            {score}
          </span>
          <span className={`${sizes.label} ${config.textColor} font-medium`}>
            {config.label}
          </span>
        </div>
        {showReasoning && reasoning && (
          <p className="text-xs text-slate-500 mt-0.5 max-w-[200px] line-clamp-2">
            {reasoning}
          </p>
        )}
      </div>
    </div>
  );

  if (reasoning && !showReasoning) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="cursor-help">{content}</div>
          </TooltipTrigger>
          <TooltipContent side="top" className="max-w-[250px]">
            <p className="text-sm">{reasoning}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return content;
}

// Simple badge for inline use
export function LaunchLabelBadge({ score = 0, label = null, size = 'default' }) {
  const config = label ? LAUNCH_SCORE_CONFIG[label] : getConfigFromScore(score);
  const Icon = config?.icon || AlertTriangle;
  
  const sizeClasses = {
    small: 'text-xs py-0.5 px-1.5',
    default: 'text-xs py-1 px-2',
    large: 'text-sm py-1.5 px-3'
  };
  
  return (
    <Badge className={`${config.badgeColor} border ${sizeClasses[size]} flex items-center gap-1`}>
      <Icon className="h-3 w-3" />
      {config.shortLabel}
    </Badge>
  );
}

// Score ring for visual display
export function LaunchScoreRing({ score = 0, size = 64 }) {
  const config = getConfigFromScore(score);
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="4"
          className="text-slate-200"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          className={config.scoreColor}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`font-mono font-bold ${config.scoreColor}`} style={{ fontSize: size * 0.3 }}>
          {score}
        </span>
      </div>
    </div>
  );
}

// Export utilities
export function getLaunchScoreColor(score) {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-blue-600';
  if (score >= 40) return 'text-amber-600';
  return 'text-red-600';
}

export function getLaunchScoreLabel(score) {
  if (score >= 80) return 'Strong Launch';
  if (score >= 60) return 'Promising';
  if (score >= 40) return 'Risky';
  return 'Avoid';
}

export function getLaunchScoreBgColor(score) {
  if (score >= 80) return 'bg-green-500';
  if (score >= 60) return 'bg-blue-500';
  if (score >= 40) return 'bg-amber-500';
  return 'bg-red-500';
}

export function getLaunchScoreBadgeColor(score) {
  if (score >= 80) return 'bg-green-50 text-green-700 border-green-200';
  if (score >= 60) return 'bg-blue-50 text-blue-700 border-blue-200';
  if (score >= 40) return 'bg-amber-50 text-amber-700 border-amber-200';
  return 'bg-red-50 text-red-700 border-red-200';
}

export default LaunchScoreBadge;
