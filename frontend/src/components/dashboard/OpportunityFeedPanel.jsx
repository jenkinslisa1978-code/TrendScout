/**
 * Live Opportunity Feed Panel
 * 
 * Displays real-time product opportunity events and signal changes.
 * Makes the dashboard feel like a live intelligence platform.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Rocket,
  Star,
  TrendingUp,
  Users,
  AlertTriangle,
  Clock,
  Activity,
  Zap,
  ChevronRight,
  RefreshCw,
  Loader2,
  Package,
  Database
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { formatCurrency } from '@/lib/utils';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Event type configurations
const EVENT_CONFIG = {
  entered_strong_launch: {
    icon: Rocket,
    color: 'bg-green-500',
    badgeColor: 'bg-green-50 text-green-700 border-green-200',
    textColor: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    label: 'Strong Launch'
  },
  new_high_score: {
    icon: Star,
    color: 'bg-emerald-500',
    badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    textColor: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    label: 'High Score'
  },
  trend_spike: {
    icon: TrendingUp,
    color: 'bg-blue-500',
    badgeColor: 'bg-blue-50 text-blue-700 border-blue-200',
    textColor: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    label: 'Trend Spike'
  },
  competition_increase: {
    icon: Users,
    color: 'bg-amber-500',
    badgeColor: 'bg-amber-50 text-amber-700 border-amber-200',
    textColor: 'text-amber-600',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    label: 'Competition'
  },
  approaching_saturation: {
    icon: AlertTriangle,
    color: 'bg-red-500',
    badgeColor: 'bg-red-50 text-red-700 border-red-200',
    textColor: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Saturation'
  }
};

// Format relative time
function formatRelativeTime(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'Yesterday';
  return `${diffDays}d ago`;
}

// Get launch score color
function getLaunchScoreColor(score) {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-blue-600';
  if (score >= 40) return 'text-amber-600';
  return 'text-red-600';
}

// Single feed event item
function FeedEventItem({ event }) {
  const config = EVENT_CONFIG[event.event_type] || EVENT_CONFIG.new_high_score;
  const Icon = config.icon;
  
  return (
    <Link to={`/product/${event.product_id}`} className="block">
      <div 
        className={`p-3 rounded-lg border ${config.borderColor} ${config.bgColor} hover:shadow-md transition-all cursor-pointer group`}
        data-testid={`feed-event-${event.id}`}
      >
        <div className="flex items-start gap-3">
          {/* Event Icon */}
          <div className={`p-2 rounded-lg ${config.color} flex-shrink-0`}>
            <Icon className="h-4 w-4 text-white" />
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-semibold text-slate-900 text-sm truncate group-hover:text-indigo-600 transition-colors">
                {event.product_name}
              </h4>
              <Badge className={`${config.badgeColor} border text-xs`}>
                {config.label}
              </Badge>
            </div>
            
            {/* Reason */}
            <p className="text-xs text-slate-600 mt-1 line-clamp-2">
              {event.reason}
            </p>
            
            {/* Metrics Row */}
            <div className="flex items-center gap-4 mt-2 text-xs">
              {/* Launch Score */}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="flex items-center gap-1 cursor-help">
                      <Zap className={`h-3 w-3 ${getLaunchScoreColor(event.launch_score)}`} />
                      <span className={`font-mono font-bold ${getLaunchScoreColor(event.launch_score)}`}>
                        {event.launch_score}
                      </span>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    <p>Launch Score: {event.launch_score}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              
              {/* Trend Stage */}
              <span className="text-slate-500 capitalize">
                {event.trend_stage}
              </span>
              
              {/* Margin */}
              <span className="text-emerald-600 font-medium">
                {formatCurrency(event.estimated_margin)}
              </span>
              
              {/* Competition */}
              <span className="text-slate-500 capitalize">
                {event.competition_level} comp.
              </span>
            </div>
            
            {/* Footer */}
            <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-200/50">
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatRelativeTime(event.created_at)}
                </span>
                {event.confidence && (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="flex items-center gap-1 cursor-help">
                          <Database className="h-3 w-3" />
                          {Math.round(event.confidence * 100)}%
                        </span>
                      </TooltipTrigger>
                      <TooltipContent side="top">
                        <p>Confidence: {Math.round(event.confidence * 100)}%</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                )}
                {event.is_simulated && (
                  <span className="text-orange-500">Simulated</span>
                )}
              </div>
              <ChevronRight className="h-4 w-4 text-slate-400 group-hover:text-indigo-500 transition-colors" />
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}

// Main component
export default function OpportunityFeedPanel({ limit = 10, refreshInterval = 60000 }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchFeed = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    
    try {
      const response = await fetch(`${API_URL}/api/dashboard/opportunity-feed?limit=${limit}&hours=48`);
      if (response.ok) {
        const data = await response.json();
        setEvents(data.events || []);
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch opportunity feed:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [limit]);

  // Initial fetch
  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  // Auto-refresh
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(() => {
        fetchFeed(true);
      }, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchFeed, refreshInterval]);

  const handleRefresh = () => {
    fetchFeed(true);
  };

  if (loading) {
    return (
      <Card className="border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 to-purple-50">
        <CardContent className="p-8 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-indigo-500" />
          <p className="text-sm text-indigo-700 mt-2">Loading opportunity feed...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      className="border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 to-purple-50 shadow-lg"
      data-testid="opportunity-feed-panel"
    >
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-bold text-indigo-900 flex items-center gap-2">
            <Activity className="h-6 w-6 text-indigo-500" />
            Live Opportunity Feed
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge className="bg-indigo-500 text-white">
              {events.length} Events
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
              className="h-8 w-8 p-0 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-100"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
        <p className="text-sm text-indigo-700">
          Real-time product signals and market opportunities
        </p>
        {lastUpdated && (
          <p className="text-xs text-indigo-500 mt-1">
            Last updated: {formatRelativeTime(lastUpdated.toISOString())}
          </p>
        )}
      </CardHeader>
      
      <CardContent className="pt-2">
        {events.length > 0 ? (
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {events.map((event) => (
              <FeedEventItem key={event.id} event={event} />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Activity className="h-12 w-12 text-indigo-300 mx-auto" />
            <p className="text-indigo-800 mt-3 font-medium">No recent opportunities</p>
            <p className="text-sm text-indigo-600 mt-1">
              New events will appear here when product signals change
            </p>
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleRefresh}
              className="mt-4 border-indigo-300 text-indigo-700 hover:bg-indigo-100"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Check for Updates
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
