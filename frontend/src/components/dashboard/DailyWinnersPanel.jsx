/**
 * Daily Winning Products Panel
 * 
 * Displays top products ranked by opportunity score.
 * Answers: "What product should I launch today?"
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Trophy, 
  TrendingUp, 
  TrendingDown,
  Rocket,
  Eye,
  AlertTriangle,
  Sparkles,
  ChevronRight,
  Star,
  Package,
  Loader2
} from 'lucide-react';
import { getDailyWinners } from '@/services/dashboardService';

export default function DailyWinnersPanel({ limit = 5 }) {
  const [winners, setWinners] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWinners = async () => {
      setLoading(true);
      const { data } = await getDailyWinners(limit);
      setWinners(data || []);
      setLoading(false);
    };
    fetchWinners();
  }, [limit]);

  const getRecommendationStyle = (result) => {
    switch (result) {
      case 'launch_opportunity':
        return { bg: 'bg-green-500', icon: Rocket };
      case 'promising_monitor':
        return { bg: 'bg-blue-500', icon: Eye };
      case 'high_risk':
        return { bg: 'bg-red-500', icon: AlertTriangle };
      default:
        return { bg: 'bg-gray-400', icon: Sparkles };
    }
  };

  const getTrendIcon = (stage) => {
    if (stage === 'exploding' || stage === 'rising') {
      return <TrendingUp className="h-3 w-3 text-green-500" />;
    }
    if (stage === 'declining') {
      return <TrendingDown className="h-3 w-3 text-red-500" />;
    }
    return null;
  };

  if (loading) {
    return (
      <Card className="border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50">
        <CardContent className="p-8 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-amber-500" />
          <p className="text-sm text-amber-700 mt-2">Finding today's winners...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 shadow-lg" data-testid="daily-winners-panel">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-bold text-amber-900 flex items-center gap-2">
            <Trophy className="h-6 w-6 text-amber-500" />
            Daily Winning Products
          </CardTitle>
          <Badge className="bg-amber-500 text-white">
            {winners.length} Opportunities
          </Badge>
        </div>
        <p className="text-sm text-amber-700">Top products ranked by launch potential</p>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="space-y-3">
          {winners.map((product, index) => {
            const recStyle = getRecommendationStyle(product.validation_result);
            const RecIcon = recStyle.icon;
            
            return (
              <Link 
                key={product.product_id} 
                to={`/product/${product.product_id}`}
                className="block"
              >
                <div className="flex items-center gap-4 p-3 bg-white rounded-lg border border-amber-100 hover:border-amber-300 hover:shadow-md transition-all cursor-pointer group">
                  {/* Rank */}
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full ${index === 0 ? 'bg-amber-500 text-white' : 'bg-amber-100 text-amber-700'} font-bold text-sm`}>
                    {index + 1}
                  </div>
                  
                  {/* Product Image Placeholder */}
                  <div className="w-12 h-12 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
                    <Package className="h-6 w-6 text-slate-400" />
                  </div>
                  
                  {/* Product Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-slate-900 truncate group-hover:text-amber-600 transition-colors">
                        {product.product_name}
                      </h4>
                      {getTrendIcon(product.trend_stage)}
                      {product.is_early_opportunity && (
                        <Star className="h-3 w-3 text-purple-500 fill-purple-500" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs capitalize">
                        {product.trend_stage}
                      </Badge>
                      <span className="text-xs text-slate-500">
                        {product.competition_level} competition
                      </span>
                      {product.is_simulated && (
                        <span className="text-xs text-orange-500">Simulated</span>
                      )}
                    </div>
                  </div>
                  
                  {/* Metrics */}
                  <div className="text-right flex-shrink-0">
                    <div className="flex items-center gap-1 justify-end">
                      <RecIcon className="h-4 w-4 text-white p-0.5 rounded" style={{backgroundColor: recStyle.bg.replace('bg-', '')}} />
                      <span className="font-bold text-lg text-slate-900">
                        {Math.round(product.success_probability)}%
                      </span>
                    </div>
                    <div className="text-xs text-slate-500">
                      {product.margin_percent}% margin
                    </div>
                  </div>
                  
                  <ChevronRight className="h-5 w-5 text-slate-400 group-hover:text-amber-500 transition-colors" />
                </div>
              </Link>
            );
          })}
        </div>
        
        {winners.length === 0 && (
          <div className="text-center py-8">
            <Trophy className="h-12 w-12 text-amber-300 mx-auto" />
            <p className="text-amber-700 mt-2">No winning products found today</p>
            <p className="text-sm text-amber-600">Check back after the next data refresh</p>
          </div>
        )}
        
        <div className="mt-4 text-center">
          <Link to="/discover">
            <Button variant="outline" className="border-amber-300 text-amber-700 hover:bg-amber-100">
              View All Products
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
