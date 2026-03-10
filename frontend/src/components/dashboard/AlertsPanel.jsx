/**
 * Alerts Panel
 * 
 * Displays user's opportunity alerts with read/unread state
 * and quick actions for reviewing products.
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Bell, 
  BellOff,
  TrendingUp,
  Rocket,
  AlertTriangle,
  Zap,
  Flame,
  ChevronRight,
  Loader2,
  Check,
  CheckCheck,
  Clock,
  Eye
} from 'lucide-react';
import { getAlerts, markAlertRead, markAllAlertsRead } from '@/services/dashboardService';
import { useAuth } from '@/contexts/AuthContext';

export default function AlertsPanel({ limit = 5 }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [markingRead, setMarkingRead] = useState(null);
  const [markingAllRead, setMarkingAllRead] = useState(false);

  useEffect(() => {
    if (user) {
      fetchAlerts();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchAlerts = async () => {
    setLoading(true);
    const { data, unreadCount: unread } = await getAlerts(false, limit);
    setAlerts(data || []);
    setUnreadCount(unread || 0);
    setLoading(false);
  };

  const handleMarkRead = async (e, alertId) => {
    e.preventDefault();
    e.stopPropagation();
    setMarkingRead(alertId);
    
    const result = await markAlertRead(alertId);
    if (result.success) {
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, is_read: true } : alert
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
    setMarkingRead(null);
  };

  const handleMarkAllRead = async () => {
    setMarkingAllRead(true);
    const result = await markAllAlertsRead();
    if (result.success) {
      setAlerts(prev => prev.map(alert => ({ ...alert, is_read: true })));
      setUnreadCount(0);
    }
    setMarkingAllRead(false);
  };

  const getAlertIcon = (alertType) => {
    switch (alertType) {
      case 'exploding_trend':
        return { icon: Flame, color: 'text-red-500', bg: 'bg-red-100' };
      case 'rising_early_trend':
        return { icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-100' };
      case 'launch_opportunity':
        return { icon: Rocket, color: 'text-blue-500', bg: 'bg-blue-100' };
      case 'trend_spike':
        return { icon: Zap, color: 'text-amber-500', bg: 'bg-amber-100' };
      case 'success_increase':
        return { icon: TrendingUp, color: 'text-emerald-500', bg: 'bg-emerald-100' };
      case 'competition_change':
        return { icon: AlertTriangle, color: 'text-orange-500', bg: 'bg-orange-100' };
      default:
        return { icon: Bell, color: 'text-slate-500', bg: 'bg-slate-100' };
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'success':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'warning':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'info':
      default:
        return 'bg-blue-100 text-blue-700 border-blue-200';
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  if (!user) {
    return (
      <Card className="border-2 border-rose-200 bg-gradient-to-br from-rose-50 to-pink-50" data-testid="alerts-panel">
        <CardContent className="p-8 text-center">
          <Bell className="h-12 w-12 text-rose-300 mx-auto" />
          <p className="text-rose-800 mt-3 font-medium">Sign in to receive alerts</p>
          <p className="text-sm text-rose-600 mt-1">Get notified about market opportunities and product changes</p>
          <Button 
            className="mt-4 bg-rose-600 hover:bg-rose-700"
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
      <Card className="border-2 border-rose-200 bg-gradient-to-br from-rose-50 to-pink-50">
        <CardContent className="p-8 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-rose-500" />
          <p className="text-sm text-rose-700 mt-2">Loading your alerts...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-rose-200 bg-gradient-to-br from-rose-50 to-pink-50 shadow-lg" data-testid="alerts-panel">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-bold text-rose-900 flex items-center gap-2">
            <Bell className="h-6 w-6 text-rose-500" />
            Opportunity Alerts
            {unreadCount > 0 && (
              <Badge className="bg-rose-500 text-white ml-1">
                {unreadCount} new
              </Badge>
            )}
          </CardTitle>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="text-rose-600 hover:text-rose-700 hover:bg-rose-100"
              onClick={handleMarkAllRead}
              disabled={markingAllRead}
              data-testid="mark-all-read-btn"
            >
              {markingAllRead ? (
                <Loader2 className="h-4 w-4 animate-spin mr-1" />
              ) : (
                <CheckCheck className="h-4 w-4 mr-1" />
              )}
              Mark all read
            </Button>
          )}
        </div>
        <p className="text-sm text-rose-700">Real-time notifications about market changes</p>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="space-y-3">
          {alerts.map((alert) => {
            const alertStyle = getAlertIcon(alert.alert_type);
            const AlertIcon = alertStyle.icon;
            
            return (
              <Link 
                key={alert.id} 
                to={`/product/${alert.product_id}`}
                className="block"
              >
                <div 
                  className={`flex items-start gap-3 p-3 bg-white rounded-lg border transition-all cursor-pointer group ${
                    alert.is_read 
                      ? 'border-rose-100 hover:border-rose-200' 
                      : 'border-rose-300 hover:border-rose-400 shadow-sm'
                  }`}
                  data-testid={`alert-item-${alert.id}`}
                >
                  {/* Alert Icon */}
                  <div className={`w-10 h-10 rounded-lg ${alertStyle.bg} flex items-center justify-center flex-shrink-0`}>
                    <AlertIcon className={`h-5 w-5 ${alertStyle.color}`} />
                  </div>
                  
                  {/* Alert Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className={`font-medium truncate group-hover:text-rose-600 transition-colors ${
                        alert.is_read ? 'text-slate-700' : 'text-slate-900'
                      }`}>
                        {alert.title}
                      </h4>
                      {!alert.is_read && (
                        <span className="w-2 h-2 rounded-full bg-rose-500 flex-shrink-0" />
                      )}
                    </div>
                    <p className={`text-sm mt-0.5 line-clamp-2 ${
                      alert.is_read ? 'text-slate-500' : 'text-slate-600'
                    }`}>
                      {alert.message}
                    </p>
                    <div className="flex items-center gap-2 mt-1.5">
                      <Badge variant="outline" className={`text-xs ${getSeverityBadge(alert.severity)}`}>
                        {alert.severity}
                      </Badge>
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatTimeAgo(alert.created_at)}
                      </span>
                    </div>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {!alert.is_read && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="p-1 h-8 w-8 text-slate-400 hover:text-rose-500 hover:bg-rose-50"
                        onClick={(e) => handleMarkRead(e, alert.id)}
                        disabled={markingRead === alert.id}
                        data-testid={`mark-read-${alert.id}`}
                      >
                        {markingRead === alert.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Check className="h-4 w-4" />
                        )}
                      </Button>
                    )}
                    <ChevronRight className="h-5 w-5 text-slate-400 group-hover:text-rose-500 transition-colors" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
        
        {alerts.length === 0 && (
          <div className="text-center py-8">
            <BellOff className="h-12 w-12 text-rose-300 mx-auto" />
            <p className="text-rose-800 mt-2 font-medium">No alerts yet</p>
            <p className="text-sm text-rose-600">We'll notify you when we detect opportunities</p>
            <Link to="/discover">
              <Button className="mt-4 bg-rose-600 hover:bg-rose-700">
                <Eye className="h-4 w-4 mr-2" />
                Explore Products
              </Button>
            </Link>
          </div>
        )}
        
        {alerts.length > 0 && (
          <div className="mt-4 text-center">
            <Link to="/alerts">
              <Button variant="outline" className="border-rose-300 text-rose-700 hover:bg-rose-100">
                View All Alerts
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
