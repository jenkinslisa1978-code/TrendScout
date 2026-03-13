import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Bell, 
  BellOff,
  Sparkles,
  TrendingUp,
  PoundSterling,
  Target,
  Clock,
  CheckCircle2,
  X,
  ArrowRight,
  Loader2,
  Filter
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { getAlerts, markAlertRead, dismissAlertById, markAllAlertsRead } from '@/services/alertService';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';
import ThresholdSubscriptionCard from '@/components/alerts/ThresholdSubscriptionCard';

const ALERT_TYPE_CONFIG = {
  early_stage: {
    icon: Sparkles,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    label: 'Early Stage',
  },
  rising_trend: {
    icon: TrendingUp,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    label: 'Rising Trend',
  },
  high_margin: {
    icon: PoundSterling,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
    label: 'High Margin',
  },
  new_opportunity: {
    icon: Target,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    label: 'New Opportunity',
  },
  exploding_trend: {
    icon: TrendingUp,
    color: 'text-rose-600',
    bgColor: 'bg-rose-50',
    label: 'Trending Fast',
  },
  rising_early_trend: {
    icon: TrendingUp,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    label: 'Rising Trend',
  },
  massive_opportunity: {
    icon: Target,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    label: 'Big Opportunity',
  },
  early_trend_opportunity: {
    icon: Sparkles,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    label: 'Early Opportunity',
  },
  strong_opportunity: {
    icon: Target,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
    label: 'Strong Opportunity',
  },
};

const PRIORITY_CONFIG = {
  critical: {
    color: 'border-red-200 bg-red-50',
    badge: 'bg-red-100 text-red-700 border-red-200',
    label: 'Critical',
  },
  high: {
    color: 'border-amber-200 bg-amber-50/50',
    badge: 'bg-amber-100 text-amber-700 border-amber-200',
    label: 'High',
  },
  medium: {
    color: 'border-slate-200 bg-white',
    badge: 'bg-slate-100 text-slate-600 border-slate-200',
    label: 'Medium',
  },
};

export default function TrendAlertsPage() {
  const { profile, isDemoMode } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  const isElite = profile?.plan === 'elite' || profile?.role === 'admin' || isDemoMode;

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    const { data, stats, error } = await getAlerts(profile?.id, { limit: 100 });
    
    if (data) {
      setAlerts(data);
      setStats(stats);
    }
    setLoading(false);
  };

  const handleMarkRead = async (alertId) => {
    await markAlertRead(alertId);
    setAlerts(prev => prev.map(a => 
      a.id === alertId ? { ...a, read: true } : a
    ));
  };

  const handleDismiss = async (alertId) => {
    await dismissAlertById(alertId);
    setAlerts(prev => prev.map(a => 
      a.id === alertId ? { ...a, dismissed: true } : a
    ));
    toast.success('Alert dismissed');
  };

  const handleMarkAllRead = async () => {
    await markAllAlertsRead();
    setAlerts(prev => prev.map(a => ({ ...a, read: true })));
    toast.success('All alerts marked as read');
  };

  const filteredAlerts = alerts.filter(alert => {
    if (alert.dismissed) return false;
    if (filter === 'unread') return !alert.read;
    if (filter === 'critical') return alert.priority === 'critical';
    if (filter === 'high') return alert.priority === 'high';
    return true;
  });

  const formatTime = (dateString) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return 'recently';
    }
  };

  if (!isElite) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center py-24">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50 mb-6">
            <Bell className="h-8 w-8 text-indigo-600" />
          </div>
          <h2 className="font-manrope text-2xl font-bold text-slate-900">Trend Alerts</h2>
          <p className="mt-2 text-slate-500 text-center max-w-md">
            Get real-time alerts when high-opportunity products are detected. 
            Upgrade to Elite to unlock this feature.
          </p>
          <Button className="mt-6 bg-indigo-600 hover:bg-indigo-700">
            Upgrade to Elite
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">Trend Alerts</h1>
            <p className="mt-1 text-slate-500">Real-time notifications for high-opportunity products</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-[140px] h-9 bg-white" data-testid="alert-filter">
                <Filter className="mr-2 h-4 w-4 text-slate-400" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Alerts</SelectItem>
                <SelectItem value="unread">Unread</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High Priority</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm" onClick={handleMarkAllRead} data-testid="mark-all-read-btn">
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Mark All Read
            </Button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card className="border-slate-200">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-50">
                    <Bell className="h-5 w-5 text-slate-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
                    <p className="text-xs text-slate-500">Total Alerts</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-indigo-200 bg-indigo-50/50">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-100">
                    <Bell className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-indigo-900">{stats.unread}</p>
                    <p className="text-xs text-indigo-600">Unread</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-red-200 bg-red-50/50">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-100">
                    <Target className="h-5 w-5 text-red-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-red-900">{stats.critical}</p>
                    <p className="text-xs text-red-600">Critical</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="border-emerald-200 bg-emerald-50/50">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                    <Sparkles className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-emerald-900">{stats.byType?.early_stage || 0}</p>
                    <p className="text-xs text-emerald-600">Early Stage</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Threshold Subscription */}
        <ThresholdSubscriptionCard />

        {/* Alerts List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : filteredAlerts.length === 0 ? (
          <Card className="border-slate-200">
            <CardContent className="py-16 text-center">
              <BellOff className="mx-auto h-12 w-12 text-slate-300" />
              <h3 className="mt-4 font-manrope text-lg font-semibold text-slate-900">
                No alerts found
              </h3>
              <p className="mt-2 text-slate-500 max-w-md mx-auto">
                {filter === 'all' 
                  ? 'New trend alerts will appear here when high-opportunity products are detected.'
                  : 'No alerts match your current filter.'}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredAlerts.map((alert) => {
              const typeConfig = ALERT_TYPE_CONFIG[alert.alert_type] || ALERT_TYPE_CONFIG.new_opportunity;
              const severity = alert.severity || alert.priority || 'medium';
              const priorityConfig = PRIORITY_CONFIG[severity] || PRIORITY_CONFIG.medium;
              const TypeIcon = typeConfig.icon;

              return (
                <Card 
                  key={alert.id}
                  className={`${priorityConfig.color} border transition-all duration-200 ${
                    !alert.read ? 'shadow-md' : ''
                  }`}
                  data-testid={`alert-card-${alert.id}`}
                >
                  <CardContent className="p-5">
                    <div className="flex items-start gap-4">
                      {/* Icon */}
                      <div className={`flex-shrink-0 flex h-12 w-12 items-center justify-center rounded-xl ${typeConfig.bgColor}`}>
                        <TypeIcon className={`h-6 w-6 ${typeConfig.color}`} />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <div className="flex items-center gap-2 flex-wrap">
                              <h3 className="font-semibold text-slate-900">{alert.title}</h3>
                              {!alert.read && (
                                <span className="flex h-2 w-2 rounded-full bg-indigo-600" />
                              )}
                            </div>
                            <p className="mt-1 text-sm text-slate-600">{alert.body}</p>
                            <div className="mt-3 flex items-center gap-3 flex-wrap">
                              <Badge className={`${priorityConfig.badge} border text-xs`}>
                                {priorityConfig.label}
                              </Badge>
                              <Badge className={`${typeConfig.bgColor} ${typeConfig.color} border-transparent text-xs`}>
                                {typeConfig.label}
                              </Badge>
                              <div className="flex items-center gap-1 text-xs text-slate-400">
                                <Clock className="h-3 w-3" />
                                {formatTime(alert.created_at)}
                              </div>
                              {(alert.launch_score || alert.trend_score) && (
                                <div className="text-xs font-mono font-semibold text-slate-600">
                                  Launch Score: {alert.launch_score || alert.trend_score}/100
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-2">
                            <Link to={`/product/${alert.product_id}`}>
                              <Button 
                                size="sm" 
                                className="bg-indigo-600 hover:bg-indigo-700"
                                onClick={() => handleMarkRead(alert.id)}
                                data-testid={`view-product-${alert.id}`}
                              >
                                View
                                <ArrowRight className="ml-1 h-4 w-4" />
                              </Button>
                            </Link>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-slate-400 hover:text-slate-600"
                              onClick={() => handleDismiss(alert.id)}
                              data-testid={`dismiss-alert-${alert.id}`}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
