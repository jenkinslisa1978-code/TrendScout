/**
 * Product Validation Display Components
 * 
 * Shows launch recommendations, success predictions, and actionable insights.
 * Core UI for answering "Should I launch this product?"
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Rocket, 
  Eye, 
  AlertTriangle, 
  HelpCircle,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  XCircle,
  Target,
  Gauge,
  ArrowUpRight,
  Clock,
  Shield,
  Sparkles
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

/**
 * Main Launch Recommendation Badge
 */
export function LaunchRecommendationBadge({ recommendation, label }) {
  const getStyle = () => {
    switch (recommendation) {
      case 'launch_opportunity':
        return {
          bg: 'bg-green-500',
          text: 'text-white',
          icon: <Rocket className="h-4 w-4" />,
        };
      case 'promising_monitor':
        return {
          bg: 'bg-blue-500',
          text: 'text-white',
          icon: <Eye className="h-4 w-4" />,
        };
      case 'high_risk':
        return {
          bg: 'bg-red-500',
          text: 'text-white',
          icon: <AlertTriangle className="h-4 w-4" />,
        };
      default:
        return {
          bg: 'bg-gray-400',
          text: 'text-white',
          icon: <HelpCircle className="h-4 w-4" />,
        };
    }
  };

  const style = getStyle();

  return (
    <Badge className={`${style.bg} ${style.text} px-3 py-1.5 text-sm font-medium gap-2`}>
      {style.icon}
      {label}
    </Badge>
  );
}

/**
 * Score Display with Visual Progress
 */
export function ScoreDisplay({ score, label, size = 'md', showLabel = true }) {
  const getColor = () => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 50) return 'bg-blue-500';
    if (score >= 30) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
  };

  return (
    <div className="space-y-1">
      {showLabel && (
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">{label}</span>
          <span className="font-semibold text-slate-900">{Math.round(score)}/100</span>
        </div>
      )}
      <div className={`w-full bg-slate-200 rounded-full ${sizeClasses[size]}`}>
        <div 
          className={`${getColor()} ${sizeClasses[size]} rounded-full transition-all`}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
    </div>
  );
}

/**
 * Risk Level Badge
 */
export function RiskLevelBadge({ riskLevel }) {
  const getStyle = () => {
    switch (riskLevel) {
      case 'low':
        return { bg: 'bg-green-100', text: 'text-green-700', label: 'Low Risk' };
      case 'moderate':
        return { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Moderate Risk' };
      case 'high':
        return { bg: 'bg-orange-100', text: 'text-orange-700', label: 'High Risk' };
      case 'very_high':
        return { bg: 'bg-red-100', text: 'text-red-700', label: 'Very High Risk' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-600', label: 'Unknown' };
    }
  };

  const style = getStyle();

  return (
    <Badge variant="outline" className={`${style.bg} ${style.text} border-0`}>
      <Shield className="h-3 w-3 mr-1" />
      {style.label}
    </Badge>
  );
}

/**
 * Success Probability Display
 */
export function SuccessProbabilityDisplay({ probability, outcome }) {
  const getColor = () => {
    if (probability >= 70) return 'text-green-600';
    if (probability >= 50) return 'text-blue-600';
    if (probability >= 30) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getIcon = () => {
    if (probability >= 70) return <TrendingUp className="h-5 w-5" />;
    if (probability >= 50) return <Target className="h-5 w-5" />;
    return <TrendingDown className="h-5 w-5" />;
  };

  return (
    <div className="flex items-center gap-3">
      <div className={`${getColor()}`}>
        {getIcon()}
      </div>
      <div>
        <div className={`text-2xl font-bold ${getColor()}`}>
          {Math.round(probability)}%
        </div>
        <div className="text-xs text-slate-500">{outcome}</div>
      </div>
    </div>
  );
}

/**
 * Trend Stage Badge
 */
export function TrendStageBadge({ stage, velocity }) {
  const getStyle = () => {
    switch (stage) {
      case 'exploding':
        return { bg: 'bg-red-100', text: 'text-red-700', icon: '🔥' };
      case 'rising':
        return { bg: 'bg-green-100', text: 'text-green-700', icon: '📈' };
      case 'early_trend':
        return { bg: 'bg-purple-100', text: 'text-purple-700', icon: '🎯' };
      case 'stable':
        return { bg: 'bg-blue-100', text: 'text-blue-700', icon: '➡️' };
      case 'declining':
        return { bg: 'bg-gray-100', text: 'text-gray-700', icon: '📉' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-600', icon: '❓' };
    }
  };

  const style = getStyle();

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge variant="outline" className={`${style.bg} ${style.text} border-0 capitalize cursor-help`}>
            <span className="mr-1">{style.icon}</span>
            {stage?.replace('_', ' ')}
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>Trend Velocity: {velocity ? `${velocity > 0 ? '+' : ''}${Math.round(velocity)}%` : 'Unknown'}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Insights List (Strengths/Weaknesses/Actions)
 */
export function InsightsList({ items, type = 'neutral', title }) {
  const getIcon = () => {
    switch (type) {
      case 'strength':
        return <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />;
      case 'weakness':
        return <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />;
      case 'action':
        return <ArrowUpRight className="h-4 w-4 text-blue-500 flex-shrink-0" />;
      default:
        return <Target className="h-4 w-4 text-slate-400 flex-shrink-0" />;
    }
  };

  if (!items || items.length === 0) return null;

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-2">{title}</h4>}
      <ul className="space-y-2">
        {items.map((item, idx) => (
          <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
            {getIcon()}
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Complete Product Validation Card
 */
export function ProductValidationCard({ validation, className = '' }) {
  if (!validation) return null;

  const {
    recommendation,
    recommendation_label,
    overall_score,
    risk_level,
    confidence_score,
    strengths,
    weaknesses,
    action_items,
    summary,
  } = validation;

  return (
    <Card className={`border-slate-200 ${className}`}>
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg font-semibold text-slate-900 flex items-center gap-2">
              <Gauge className="h-5 w-5 text-indigo-600" />
              Launch Validation
            </CardTitle>
            <p className="text-sm text-slate-500 mt-1">Should you launch this product?</p>
          </div>
          <LaunchRecommendationBadge recommendation={recommendation} label={recommendation_label} />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Score and Risk */}
        <div className="grid grid-cols-2 gap-6">
          <div>
            <ScoreDisplay score={overall_score} label="Viability Score" />
          </div>
          <div className="flex flex-col justify-end">
            <div className="flex items-center gap-2">
              <RiskLevelBadge riskLevel={risk_level} />
              <span className="text-sm text-slate-500">{confidence_score}% confidence</span>
            </div>
          </div>
        </div>

        {/* Summary */}
        {summary && (
          <div className="p-3 bg-slate-50 rounded-lg">
            <p className="text-sm text-slate-700">{summary}</p>
          </div>
        )}

        {/* Strengths & Weaknesses */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InsightsList items={strengths} type="strength" title="Strengths" />
          <InsightsList items={weaknesses} type="weakness" title="Concerns" />
        </div>

        {/* Action Items */}
        {action_items && action_items.length > 0 && (
          <div className="border-t border-slate-100 pt-4">
            <InsightsList items={action_items} type="action" title="Recommended Actions" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Success Prediction Card
 */
export function SuccessPredictionCard({ prediction, className = '' }) {
  if (!prediction) return null;

  const {
    success_probability,
    outcome_label,
    top_positive_factors,
    top_negative_factors,
    prediction_explanation,
  } = prediction;

  return (
    <Card className={`border-slate-200 ${className}`}>
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold text-slate-900 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-indigo-600" />
          Success Prediction
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <SuccessProbabilityDisplay probability={success_probability} outcome={outcome_label} />
        
        <ScoreDisplay score={success_probability} label="Success Probability" />

        {prediction_explanation && (
          <p className="text-sm text-slate-600">{prediction_explanation}</p>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {top_positive_factors && top_positive_factors.length > 0 && (
            <InsightsList items={top_positive_factors} type="strength" title="Positive Signals" />
          )}
          {top_negative_factors && top_negative_factors.length > 0 && (
            <InsightsList items={top_negative_factors} type="weakness" title="Risk Signals" />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Trend Analysis Card
 */
export function TrendAnalysisCard({ trendAnalysis, className = '' }) {
  if (!trendAnalysis) return null;

  const {
    trend_stage,
    velocity_percent,
    is_early_opportunity,
    days_until_saturation,
    momentum_score,
    reasoning,
  } = trendAnalysis;

  return (
    <Card className={`border-slate-200 ${className}`}>
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-indigo-600" />
            Trend Analysis
          </CardTitle>
          <TrendStageBadge stage={trend_stage} velocity={velocity_percent} />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className={`text-2xl font-bold ${velocity_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {velocity_percent > 0 ? '+' : ''}{Math.round(velocity_percent)}%
            </div>
            <div className="text-xs text-slate-500">Velocity</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-indigo-600">
              {Math.round(momentum_score)}
            </div>
            <div className="text-xs text-slate-500">Momentum</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-700">
              {days_until_saturation ? `${days_until_saturation}d` : '—'}
            </div>
            <div className="text-xs text-slate-500">To Saturation</div>
          </div>
        </div>

        {is_early_opportunity && (
          <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center gap-2 text-purple-700 font-medium text-sm">
              <Target className="h-4 w-4" />
              Early Opportunity Detected
            </div>
            <p className="text-xs text-purple-600 mt-1">
              Low competition window available - consider acting quickly
            </p>
          </div>
        )}

        {reasoning && reasoning.length > 0 && (
          <div className="space-y-1">
            {reasoning.map((reason, idx) => (
              <p key={idx} className="text-sm text-slate-600">• {reason}</p>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Quick Validation Summary (for product cards)
 */
export function QuickValidationSummary({ 
  recommendation, 
  score, 
  successProbability,
  riskLevel,
  isSimulated = false,
}) {
  return (
    <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
      <div className="flex items-center gap-3">
        <LaunchRecommendationBadge 
          recommendation={recommendation} 
          label={score >= 70 ? 'Launch' : score >= 50 ? 'Monitor' : 'High Risk'}
        />
        {isSimulated && (
          <span className="text-xs text-orange-600 bg-orange-100 px-2 py-0.5 rounded">
            Simulated
          </span>
        )}
      </div>
      <div className="text-right">
        <div className="text-lg font-bold text-slate-900">{Math.round(successProbability)}%</div>
        <div className="text-xs text-slate-500">Success Probability</div>
      </div>
    </div>
  );
}

export default {
  LaunchRecommendationBadge,
  ScoreDisplay,
  RiskLevelBadge,
  SuccessProbabilityDisplay,
  TrendStageBadge,
  InsightsList,
  ProductValidationCard,
  SuccessPredictionCard,
  TrendAnalysisCard,
  QuickValidationSummary,
};
