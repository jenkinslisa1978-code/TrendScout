/**
 * Notification Settings Page
 * 
 * Allows users to manage their notification preferences:
 * - Email on/off
 * - In-app on/off
 * - Alert threshold
 * - Quiet hours
 * - Notification types
 * - Watchlist priority
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import {
  Bell,
  Mail,
  Smartphone,
  Clock,
  Target,
  Bookmark,
  Rocket,
  TrendingUp,
  Star,
  Save,
  Loader2,
  CheckCircle,
  ArrowLeft
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function NotificationSettingsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  
  // Preferences state
  const [preferences, setPreferences] = useState({
    email_enabled: true,
    in_app_enabled: true,
    alert_threshold: 80,
    quiet_hours_enabled: false,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    watchlist_priority_enabled: true,
    notification_types: {
      strong_launch: true,
      exploding_trend: true,
      watchlist_alert: true,
      score_milestone: true
    }
  });
  
  // Fetch preferences on load
  useEffect(() => {
    const fetchPreferences = async () => {
      if (!user) return;
      
      try {
        const response = await api.get('/api/notifications/preferences');
        if (response.data) {
          setPreferences(prev => ({
            ...prev,
            ...response.data
          }));
        }
      } catch (error) {
        console.error('Failed to fetch preferences:', error);
        toast.error('Failed to load notification preferences');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPreferences();
  }, [user]);
  
  // Save preferences
  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    
    try {
      await api.put('/api/notifications/preferences', preferences);
      setSaved(true);
      toast.success('Notification preferences saved');
      
      // Reset saved indicator after 3 seconds
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save preferences:', error);
      toast.error('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };
  
  // Update a preference
  const updatePreference = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  // Update notification type
  const updateNotificationType = (type, enabled) => {
    setPreferences(prev => ({
      ...prev,
      notification_types: {
        ...prev.notification_types,
        [type]: enabled
      }
    }));
  };
  
  // Get threshold label
  const getThresholdLabel = (value) => {
    if (value >= 90) return 'Very High (90+)';
    if (value >= 85) return 'High (85+)';
    if (value >= 80) return 'Standard (80+)';
    if (value >= 75) return 'Lower (75+)';
    return 'All Alerts';
  };
  
  if (!user) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <Bell className="h-12 w-12 text-slate-300 mx-auto" />
          <h2 className="text-xl font-semibold text-slate-900 mt-4">Sign in required</h2>
          <p className="text-slate-500 mt-2">Please sign in to manage your notification preferences</p>
        </div>
      </DashboardLayout>
    );
  }
  
  if (loading) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-indigo-500" />
          <p className="text-slate-500 mt-2">Loading preferences...</p>
        </div>
      </DashboardLayout>
    );
  }
  
  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto space-y-6" data-testid="notification-settings-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(-1)}
              className="h-8 w-8"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                <Bell className="h-6 w-6 text-indigo-500" />
                Notification Settings
              </h1>
              <p className="text-slate-500 mt-1">
                Control how and when you receive product alerts
              </p>
            </div>
          </div>
          
          <Button
            onClick={handleSave}
            disabled={saving}
            className="bg-indigo-600 hover:bg-indigo-700"
            data-testid="save-preferences-btn"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : saved ? (
              <CheckCircle className="h-4 w-4 mr-2" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            {saved ? 'Saved!' : 'Save Changes'}
          </Button>
        </div>
        
        {/* Notification Channels */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Smartphone className="h-5 w-5 text-indigo-500" />
              Notification Channels
            </CardTitle>
            <CardDescription>
              Choose how you want to receive alerts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Email Notifications */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-50">
                  <Mail className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <Label className="text-base font-medium">Email Notifications</Label>
                  <p className="text-sm text-slate-500">
                    Receive alerts via email with direct product links
                  </p>
                </div>
              </div>
              <Switch
                checked={preferences.email_enabled}
                onCheckedChange={(checked) => updatePreference('email_enabled', checked)}
                data-testid="email-enabled-switch"
              />
            </div>
            
            <Separator />
            
            {/* In-App Notifications */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-50">
                  <Bell className="h-5 w-5 text-purple-500" />
                </div>
                <div>
                  <Label className="text-base font-medium">In-App Notifications</Label>
                  <p className="text-sm text-slate-500">
                    See alerts in the notification center on your dashboard
                  </p>
                </div>
              </div>
              <Switch
                checked={preferences.in_app_enabled}
                onCheckedChange={(checked) => updatePreference('in_app_enabled', checked)}
                data-testid="in-app-enabled-switch"
              />
            </div>
          </CardContent>
        </Card>
        
        {/* Alert Threshold */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Target className="h-5 w-5 text-indigo-500" />
              Alert Threshold
            </CardTitle>
            <CardDescription>
              Set the minimum Launch Score required to trigger an alert
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label className="text-base font-medium">Minimum Launch Score</Label>
                <span className="text-lg font-bold text-indigo-600">
                  {preferences.alert_threshold}+
                </span>
              </div>
              
              <Slider
                value={[preferences.alert_threshold]}
                onValueChange={([value]) => updatePreference('alert_threshold', value)}
                min={70}
                max={95}
                step={5}
                className="w-full"
                data-testid="alert-threshold-slider"
              />
              
              <div className="flex justify-between text-xs text-slate-500">
                <span>More alerts (70+)</span>
                <span>{getThresholdLabel(preferences.alert_threshold)}</span>
                <span>Fewer alerts (95+)</span>
              </div>
              
              <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">
                You'll receive alerts for products with Launch Score of <strong>{preferences.alert_threshold}</strong> or higher.
                {preferences.alert_threshold >= 80 && (
                  <span className="text-green-600"> This includes Strong Launch opportunities.</span>
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        {/* Quiet Hours */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Clock className="h-5 w-5 text-indigo-500" />
              Quiet Hours
            </CardTitle>
            <CardDescription>
              Pause notifications during specific hours (watchlist alerts still notify)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base font-medium">Enable Quiet Hours</Label>
                <p className="text-sm text-slate-500">
                  No notifications during these hours
                </p>
              </div>
              <Switch
                checked={preferences.quiet_hours_enabled}
                onCheckedChange={(checked) => updatePreference('quiet_hours_enabled', checked)}
                data-testid="quiet-hours-enabled-switch"
              />
            </div>
            
            {preferences.quiet_hours_enabled && (
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <Label className="text-sm text-slate-600">Start Time</Label>
                  <Input
                    type="time"
                    value={preferences.quiet_hours_start}
                    onChange={(e) => updatePreference('quiet_hours_start', e.target.value)}
                    className="mt-1"
                    data-testid="quiet-hours-start"
                  />
                </div>
                <div>
                  <Label className="text-sm text-slate-600">End Time</Label>
                  <Input
                    type="time"
                    value={preferences.quiet_hours_end}
                    onChange={(e) => updatePreference('quiet_hours_end', e.target.value)}
                    className="mt-1"
                    data-testid="quiet-hours-end"
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* Notification Types */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Bell className="h-5 w-5 text-indigo-500" />
              Notification Types
            </CardTitle>
            <CardDescription>
              Choose which types of alerts you want to receive
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Strong Launch */}
            <div className="flex items-center justify-between p-3 rounded-lg border">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-50">
                  <Rocket className="h-5 w-5 text-green-500" />
                </div>
                <div>
                  <Label className="text-base font-medium">Strong Launch Alerts</Label>
                  <p className="text-sm text-slate-500">
                    Products entering Strong Launch category (score 80+)
                  </p>
                </div>
              </div>
              <Switch
                checked={preferences.notification_types.strong_launch}
                onCheckedChange={(checked) => updateNotificationType('strong_launch', checked)}
                data-testid="type-strong-launch-switch"
              />
            </div>
            
            {/* Exploding Trend */}
            <div className="flex items-center justify-between p-3 rounded-lg border">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-orange-50">
                  <TrendingUp className="h-5 w-5 text-orange-500" />
                </div>
                <div>
                  <Label className="text-base font-medium">Exploding Trend Alerts</Label>
                  <p className="text-sm text-slate-500">
                    Products with rapidly accelerating trend momentum
                  </p>
                </div>
              </div>
              <Switch
                checked={preferences.notification_types.exploding_trend}
                onCheckedChange={(checked) => updateNotificationType('exploding_trend', checked)}
                data-testid="type-exploding-trend-switch"
              />
            </div>
            
            {/* Watchlist Alert */}
            <div className="flex items-center justify-between p-3 rounded-lg border">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-50">
                  <Bookmark className="h-5 w-5 text-purple-500" />
                </div>
                <div>
                  <Label className="text-base font-medium">Watchlist Alerts</Label>
                  <p className="text-sm text-slate-500">
                    Significant changes to products in your watchlist
                  </p>
                </div>
              </div>
              <Switch
                checked={preferences.notification_types.watchlist_alert}
                onCheckedChange={(checked) => updateNotificationType('watchlist_alert', checked)}
                data-testid="type-watchlist-alert-switch"
              />
            </div>
            
            {/* Score Milestone */}
            <div className="flex items-center justify-between p-3 rounded-lg border">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-50">
                  <Star className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <Label className="text-base font-medium">Score Milestone Alerts</Label>
                  <p className="text-sm text-slate-500">
                    Products crossing your alert threshold
                  </p>
                </div>
              </div>
              <Switch
                checked={preferences.notification_types.score_milestone}
                onCheckedChange={(checked) => updateNotificationType('score_milestone', checked)}
                data-testid="type-score-milestone-switch"
              />
            </div>
          </CardContent>
        </Card>
        
        {/* Watchlist Priority */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Bookmark className="h-5 w-5 text-indigo-500" />
              Watchlist Priority
            </CardTitle>
            <CardDescription>
              Give priority to products in your watchlist
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-base font-medium">Priority Alerts for Watchlist</Label>
                <p className="text-sm text-slate-500">
                  Watchlist items get immediate notifications and bypass quiet hours
                </p>
              </div>
              <Switch
                checked={preferences.watchlist_priority_enabled}
                onCheckedChange={(checked) => updatePreference('watchlist_priority_enabled', checked)}
                data-testid="watchlist-priority-switch"
              />
            </div>
          </CardContent>
        </Card>
        
        {/* Save Button (Bottom) */}
        <div className="flex justify-end pb-8">
          <Button
            onClick={handleSave}
            disabled={saving}
            size="lg"
            className="bg-indigo-600 hover:bg-indigo-700"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : saved ? (
              <CheckCircle className="h-4 w-4 mr-2" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            {saved ? 'Saved!' : 'Save Changes'}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}
