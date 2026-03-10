/**
 * Opportunity Watchlist Panel
 * 
 * Displays user's watchlist with change indicators showing
 * how metrics have changed since the product was added.
 * Now prominently featuring Launch Score as the primary metric.
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Eye, 
  TrendingUp, 
  TrendingDown,
  Minus,
  ChevronRight,
  Loader2,
  Package,
  Trash2,
  Clock,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Rocket,
  XCircle
} from 'lucide-react';
import { getWatchlist, removeFromWatchlist } from '@/services/dashboardService';
import { useAuth } from '@/contexts/AuthContext';
import { ExplainScoreButton } from '@/components/LaunchScoreExplainerModal';

export default function OpportunityWatchlist({ limit = 5 }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [removing, setRemoving] = useState(null);

  useEffect(() => {
    if (user) {
      fetchWatchlist();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchWatchlist = async () => {
    setLoading(true);
    const { data } = await getWatchlist();
    setWatchlist((data || []).slice(0, limit));
    setLoading(false);
  };

  const handleRemove = async (e, productId) => {
    e.preventDefault();
    e.stopPropagation();
    setRemoving(productId);
    
    const result = await removeFromWatchlist(productId);
    if (result.success) {
      setWatchlist(prev => prev.filter(item => item.product_id !== productId));
    }
    setRemoving(null);
  };

  // Launch Score styling - PRIMARY METRIC
  const getLaunchScoreStyle = (score, label) => {
    if (label === 'strong_launch' || score >= 80) {
      return { bg: 'bg-green-500', text: 'text-green-600', badge: 'bg-green-50 text-green-700 border-green-200', icon: Rocket, label: 'Strong Launch' };
    }
    if (label === 'promising' || score >= 60) {
      return { bg: 'bg-blue-500', text: 'text-blue-600', badge: 'bg-blue-50 text-blue-700 border-blue-200', icon: TrendingUp, label: 'Promising' };
    }
    if (label === 'risky' || score >= 40) {
      return { bg: 'bg-amber-500', text: 'text-amber-600', badge: 'bg-amber-50 text-amber-700 border-amber-200', icon: AlertTriangle, label: 'Risky' };
    }
    return { bg: 'bg-red-500', text: 'text-red-600', badge: 'bg-red-50 text-red-700 border-red-200', icon: XCircle, label: 'Avoid' };
  };

  const getSignalIcon = (signal) => {
    switch (signal) {
      case 'improving':
        return <ArrowUpRight className="h-3 w-3 text-green-500" />;
      case 'declining':
        return <ArrowDownRight className="h-3 w-3 text-red-500" />;
      case 'worsening':
        return <ArrowDownRight className="h-3 w-3 text-red-500" />;
      default:
        return <Minus className="h-3 w-3 text-slate-400" />;
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  if (!user) {
    return (
      <Card className="border-2 border-cyan-200 bg-gradient-to-br from-cyan-50 to-teal-50" data-testid="watchlist-panel">
        <CardContent className="p-8 text-center">
          <Eye className="h-12 w-12 text-cyan-300 mx-auto" />
          <p className="text-cyan-800 mt-3 font-medium">Sign in to track opportunities</p>
          <p className="text-sm text-cyan-600 mt-1">Add products to your watchlist and track changes over time</p>
          <Button 
            className="mt-4 bg-cyan-600 hover:bg-cyan-700"
            onClick={() => navigate('/login')}
          >
            Sign In
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="border-2 border-cyan-200 bg-gradient-to-br from-cyan-50 to-teal-50">
        <CardContent className="p-8 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-cyan-500" />
          <p className="text-sm text-cyan-700 mt-2">Loading your watchlist...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-cyan-200 bg-gradient-to-br from-cyan-50 to-teal-50 shadow-lg" data-testid="watchlist-panel">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-bold text-cyan-900 flex items-center gap-2">
            <Eye className="h-6 w-6 text-cyan-500" />
            Your Watchlist
          </CardTitle>
          <Badge className="bg-cyan-500 text-white">
            {watchlist.length} Products
          </Badge>
        </div>
        <p className="text-sm text-cyan-700">Products you're monitoring with Launch Score tracking</p>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="space-y-3">
          {watchlist.map((item) => {
            const launchScore = item.launch_score || item.success_probability || 0;
            const launchStyle = getLaunchScoreStyle(launchScore, item.launch_score_label);
            const LaunchIcon = launchStyle.icon;
            
            return (
              <Link 
                key={item.watchlist_id} 
                to={`/product/${item.product_id}`}
                className="block"
              >
                <div 
                  className="flex items-center gap-4 p-3 bg-white rounded-lg border border-cyan-100 hover:border-cyan-300 hover:shadow-md transition-all cursor-pointer group"
                  data-testid={`watchlist-item-${item.product_id}`}
                >
                  {/* Product Image Placeholder */}
                  <div className="w-12 h-12 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
                    <Package className="h-6 w-6 text-slate-400" />
                  </div>
                  
                  {/* Product Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-slate-900 truncate group-hover:text-cyan-600 transition-colors">
                        {item.product_name}
                      </h4>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatTimeAgo(item.added_at)}
                      </span>
                      <span className="flex items-center gap-1 capitalize">
                        {item.trend_stage}
                      </span>
                      {item.is_simulated && (
                        <span className="text-orange-500">Simulated</span>
                      )}
                    </div>
                  </div>
                  
                  {/* Launch Score - PRIMARY METRIC */}
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="text-center">
                      <div className="flex items-center gap-1.5">
                        <div className={`p-1 rounded ${launchStyle.bg}`}>
                          <LaunchIcon className="h-3 w-3 text-white" />
                        </div>
                        <span className={`font-mono font-bold text-lg ${launchStyle.text}`}>
                          {Math.round(launchScore)}
                        </span>
                        {getSignalIcon(item.signals?.success)}
                        <ExplainScoreButton 
                          productId={item.product_id}
                          productName={item.product_name}
                          launchScore={Math.round(launchScore)}
                          variant="icon"
                        />
                      </div>
                      <Badge className={`${launchStyle.badge} border text-xs mt-1`}>
                        {launchStyle.label}
                      </Badge>
                    </div>
                    
                    {/* Remove Button */}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="p-1 h-8 w-8 text-slate-400 hover:text-red-500 hover:bg-red-50"
                      onClick={(e) => handleRemove(e, item.product_id)}
                      disabled={removing === item.product_id}
                      data-testid={`remove-watchlist-${item.product_id}`}
                    >
                      {removing === item.product_id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  
                  <ChevronRight className="h-5 w-5 text-slate-400 group-hover:text-cyan-500 transition-colors" />
                </div>
              </Link>
            );
          })}
        </div>
        
        {watchlist.length === 0 && (
          <div className="text-center py-8">
            <Eye className="h-12 w-12 text-cyan-300 mx-auto" />
            <p className="text-cyan-800 mt-2 font-medium">No products in watchlist</p>
            <p className="text-sm text-cyan-600">Add products from the Discover page to track their performance</p>
            <Link to="/discover">
              <Button className="mt-4 bg-cyan-600 hover:bg-cyan-700">
                Find Products to Watch
              </Button>
            </Link>
          </div>
        )}
        
        {watchlist.length > 0 && (
          <div className="mt-4 text-center">
            <Link to="/watchlist">
              <Button variant="outline" className="border-cyan-300 text-cyan-700 hover:bg-cyan-100">
                View Full Watchlist
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
