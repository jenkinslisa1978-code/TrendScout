/**
 * Data Integrity Components
 * 
 * UI components for displaying data confidence, warnings, and source information.
 * Ensures users can distinguish between real and simulated data.
 */

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  CheckCircle, 
  AlertCircle, 
  HelpCircle,
  Database,
  Clock,
  TrendingUp,
  Info
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

/**
 * Confidence Badge - Shows data confidence level with color coding
 */
export function ConfidenceBadge({ confidence, level, showScore = false }) {
  const getConfidenceStyle = () => {
    if (confidence >= 80) return { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200' };
    if (confidence >= 50) return { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' };
    if (confidence >= 25) return { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-200' };
    return { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200' };
  };

  const getIcon = () => {
    if (confidence >= 80) return <CheckCircle className="h-3 w-3" />;
    if (confidence >= 50) return <Info className="h-3 w-3" />;
    if (confidence >= 25) return <AlertCircle className="h-3 w-3" />;
    return <AlertTriangle className="h-3 w-3" />;
  };

  const style = getConfidenceStyle();

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge 
            variant="outline" 
            className={`${style.bg} ${style.text} ${style.border} text-xs gap-1 cursor-help`}
          >
            {getIcon()}
            {showScore ? `${confidence}%` : level || 'Unknown'}
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>Confidence Score: {confidence}%</p>
          <p className="text-xs text-muted-foreground">
            {confidence >= 80 && "High confidence - Data from verified sources"}
            {confidence >= 50 && confidence < 80 && "Medium confidence - Data may be estimated"}
            {confidence >= 25 && confidence < 50 && "Low confidence - Limited data available"}
            {confidence < 25 && "Low confidence — limited data points available"}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Data Source Badge - Shows whether data is live, estimated, or simulated
 */
export function DataSourceBadge({ source, isSimulated }) {
  if (isSimulated) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge variant="outline" className="bg-orange-100 text-orange-700 border-orange-200 text-xs gap-1">
              <AlertTriangle className="h-3 w-3" />
              Simulated
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            <p className="font-medium">Simulated Data</p>
            <p className="text-xs text-muted-foreground">
              This data is not from a live source. Use for demonstration only.
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge variant="outline" className="bg-slate-100 text-slate-600 border-slate-200 text-xs gap-1">
            <Database className="h-3 w-3" />
            {source || 'Unknown'}
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>Data Source: {source}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Data Freshness Badge - Shows how old the data is
 */
export function DataFreshnessBadge({ freshness, lastUpdated }) {
  const getFreshnessStyle = () => {
    switch (freshness) {
      case 'real_time':
      case 'fresh':
        return { bg: 'bg-green-100', text: 'text-green-700', icon: <CheckCircle className="h-3 w-3" /> };
      case 'recent':
        return { bg: 'bg-blue-100', text: 'text-blue-700', icon: <Clock className="h-3 w-3" /> };
      case 'stale':
        return { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: <AlertCircle className="h-3 w-3" /> };
      default:
        return { bg: 'bg-slate-100', text: 'text-slate-600', icon: <HelpCircle className="h-3 w-3" /> };
    }
  };

  const getFreshnessLabel = () => {
    switch (freshness) {
      case 'real_time': return 'Real-time';
      case 'fresh': return 'Fresh';
      case 'recent': return 'Recent';
      case 'stale': return 'Stale';
      default: return 'Unknown';
    }
  };

  const style = getFreshnessStyle();

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge variant="outline" className={`${style.bg} ${style.text} text-xs gap-1 cursor-help`}>
            {style.icon}
            {getFreshnessLabel()}
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>Data Freshness: {getFreshnessLabel()}</p>
          {lastUpdated && (
            <p className="text-xs text-muted-foreground">
              Last updated: {new Date(lastUpdated).toLocaleString()}
            </p>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * Data Integrity Warning Banner - Shows warnings for low quality data
 */
export function DataIntegrityWarning({ warnings = [], className = '' }) {
  if (!warnings || warnings.length === 0) return null;

  return (
    <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-3 ${className}`}>
      <div className="flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm font-medium text-yellow-800">Data Quality Notice</p>
          <ul className="text-xs text-yellow-700 mt-1 space-y-0.5">
            {warnings.map((warning, idx) => (
              <li key={idx}>• {warning}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

/**
 * Simulated Data Alert - Prominent alert for simulated data
 */
export function SimulatedDataAlert({ className = '' }) {
  return (
    <div className={`bg-amber-50 border border-amber-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm font-semibold text-amber-800">Market Analysis Data</p>
          <p className="text-xs text-amber-700 mt-1">
            Product data is based on market analysis, trend modelling, and publicly available signals.
            Connect the CJ Dropshipping API for live supplier pricing and stock levels.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Value Display with Confidence - Shows a value with confidence indicator
 */
export function ValueWithConfidence({ 
  value, 
  label, 
  confidence, 
  isSimulated = false,
  prefix = '',
  suffix = '',
  fallback = 'Unknown'
}) {
  const displayValue = value !== null && value !== undefined && value !== '' && value !== 0
    ? `${prefix}${typeof value === 'number' ? value.toLocaleString() : value}${suffix}`
    : fallback;

  const isUnknown = displayValue === fallback;

  return (
    <div className="flex items-center gap-2">
      <span className={isUnknown ? 'text-muted-foreground italic' : ''}>
        {displayValue}
      </span>
      {isSimulated && (
        <span className="text-xs text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded">
          Estimated
        </span>
      )}
      {!isSimulated && confidence !== undefined && confidence < 50 && (
        <span className="text-xs text-yellow-600 bg-yellow-100 px-1.5 py-0.5 rounded">
          Low Confidence
        </span>
      )}
    </div>
  );
}

/**
 * Data Integrity Summary Card - Shows overall data quality for a product
 */
export function DataIntegritySummary({ integrity, className = '' }) {
  if (!integrity) return null;

  const {
    confidence_score = 0,
    confidence_level = 'unknown',
    data_freshness = 'unknown',
    is_simulated = false,
    simulated_signals_count = 0,
    total_signals_count = 0,
    sources_count = 0,
    live_sources_count = 0,
  } = integrity;

  return (
    <div className={`bg-slate-50 border border-slate-200 rounded-lg p-4 ${className}`}>
      <h4 className="text-sm font-medium text-slate-900 mb-3 flex items-center gap-2">
        <Database className="h-4 w-4" />
        Data Quality
      </h4>
      
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <span className="text-slate-500">Confidence</span>
          <div className="flex items-center gap-1 mt-1">
            <ConfidenceBadge confidence={confidence_score} level={confidence_level} showScore />
          </div>
        </div>
        
        <div>
          <span className="text-slate-500">Freshness</span>
          <div className="mt-1">
            <DataFreshnessBadge freshness={data_freshness} />
          </div>
        </div>
        
        <div>
          <span className="text-slate-500">Data Sources</span>
          <p className="font-medium text-slate-700 mt-1">
            {live_sources_count} live / {sources_count} total
          </p>
        </div>
        
        <div>
          <span className="text-slate-500">Signals</span>
          <p className="font-medium text-slate-700 mt-1">
            {is_simulated ? (
              <span className="text-amber-600">Market Analysis</span>
            ) : (
              `${total_signals_count - simulated_signals_count} / ${total_signals_count} verified`
            )}
          </p>
        </div>
      </div>

      {is_simulated && (
        <div className="mt-3 pt-3 border-t border-slate-200">
          <p className="text-xs text-amber-600 flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" />
            Based on market analysis and trend modelling. Connect CJ Dropshipping for live supplier data.
          </p>
        </div>
      )}
    </div>
  );
}

export default {
  ConfidenceBadge,
  DataSourceBadge,
  DataFreshnessBadge,
  DataIntegrityWarning,
  SimulatedDataAlert,
  ValueWithConfidence,
  DataIntegritySummary,
};
