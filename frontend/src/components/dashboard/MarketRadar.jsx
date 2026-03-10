/**
 * Market Opportunity Radar Panel
 * 
 * Displays market clusters with opportunity scores.
 * Shows category-level trends rather than individual products.
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Radar, 
  TrendingUp, 
  TrendingDown,
  ChevronRight,
  Target,
  Zap,
  Loader2,
  Users,
  BarChart3,
  Flame
} from 'lucide-react';
import { getMarketRadar } from '@/services/dashboardService';

export default function MarketRadar({ limit = 5 }) {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRadar = async () => {
      setLoading(true);
      const { data } = await getMarketRadar(limit);
      setClusters(data || []);
      setLoading(false);
    };
    fetchRadar();
  }, [limit]);

  const getTrendStyle = (stage) => {
    switch (stage) {
      case 'exploding':
        return { color: 'text-red-600', bg: 'bg-red-50', icon: Flame, label: 'Exploding' };
      case 'rising':
        return { color: 'text-green-600', bg: 'bg-green-50', icon: TrendingUp, label: 'Rising' };
      case 'early_trend':
        return { color: 'text-blue-600', bg: 'bg-blue-50', icon: Zap, label: 'Early Trend' };
      case 'stable':
        return { color: 'text-slate-600', bg: 'bg-slate-50', icon: BarChart3, label: 'Stable' };
      case 'declining':
        return { color: 'text-orange-600', bg: 'bg-orange-50', icon: TrendingDown, label: 'Declining' };
      default:
        return { color: 'text-slate-500', bg: 'bg-slate-50', icon: BarChart3, label: stage };
    }
  };

  const getCompetitionBadge = (level) => {
    switch (level) {
      case 'low':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'medium':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-amber-600';
    return 'text-slate-500';
  };

  if (loading) {
    return (
      <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50">
        <CardContent className="p-8 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-purple-500" />
          <p className="text-sm text-purple-700 mt-2">Scanning market opportunities...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50 shadow-lg" data-testid="market-radar-panel">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-bold text-purple-900 flex items-center gap-2">
            <Radar className="h-6 w-6 text-purple-500" />
            Market Opportunity Radar
          </CardTitle>
          <Badge className="bg-purple-500 text-white">
            {clusters.length} Clusters
          </Badge>
        </div>
        <p className="text-sm text-purple-700">Category-level market trends and opportunities</p>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="space-y-3">
          {clusters.map((cluster, index) => {
            const trendStyle = getTrendStyle(cluster.trend_stage);
            const TrendIcon = trendStyle.icon;
            
            return (
              <Link 
                key={cluster.cluster_name} 
                to={`/discover?category=${encodeURIComponent(cluster.cluster_name)}`}
                className="block"
              >
                <div 
                  className="flex items-center gap-4 p-3 bg-white rounded-lg border border-purple-100 hover:border-purple-300 hover:shadow-md transition-all cursor-pointer group"
                  data-testid={`market-cluster-${cluster.cluster_name}`}
                >
                  {/* Rank */}
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full ${index === 0 ? 'bg-purple-500 text-white' : 'bg-purple-100 text-purple-700'} font-bold text-sm`}>
                    {index + 1}
                  </div>
                  
                  {/* Cluster Icon */}
                  <div className={`w-10 h-10 rounded-lg ${trendStyle.bg} flex items-center justify-center flex-shrink-0`}>
                    <TrendIcon className={`h-5 w-5 ${trendStyle.color}`} />
                  </div>
                  
                  {/* Cluster Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-slate-900 truncate group-hover:text-purple-600 transition-colors">
                        {cluster.cluster_name}
                      </h4>
                      <Badge variant="outline" className={`text-xs capitalize ${getCompetitionBadge(cluster.competition_level)}`}>
                        {cluster.competition_level}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Target className="h-3 w-3" />
                        {cluster.product_count} products
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        {Math.round(cluster.avg_success_probability)}% avg success
                      </span>
                      {cluster.avg_trend_velocity > 0 && (
                        <span className="flex items-center gap-1 text-green-600">
                          <TrendingUp className="h-3 w-3" />
                          +{Math.round(cluster.avg_trend_velocity)}%
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* Opportunity Score */}
                  <div className="text-right flex-shrink-0">
                    <div className={`font-bold text-lg ${getScoreColor(cluster.opportunity_score)}`}>
                      {Math.round(cluster.opportunity_score)}
                    </div>
                    <div className="text-xs text-slate-500">Score</div>
                  </div>
                  
                  <ChevronRight className="h-5 w-5 text-slate-400 group-hover:text-purple-500 transition-colors" />
                </div>
              </Link>
            );
          })}
        </div>
        
        {clusters.length === 0 && (
          <div className="text-center py-8">
            <Radar className="h-12 w-12 text-purple-300 mx-auto" />
            <p className="text-purple-700 mt-2">No market clusters detected</p>
            <p className="text-sm text-purple-600">Check back after more data is collected</p>
          </div>
        )}
        
        <div className="mt-4 text-center">
          <Link to="/discover">
            <Button variant="outline" className="border-purple-300 text-purple-700 hover:bg-purple-100">
              Explore All Categories
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
