/**
 * NotificationCenter Component
 * 
 * Bell icon with dropdown showing user notifications.
 * Supports real-time updates, priority ordering, and mark as read.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Bell,
  Rocket,
  TrendingUp,
  Star,
  Bookmark,
  Check,
  CheckCheck,
  Settings,
  Loader2,
  X
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

// Notification type icons and colors
const NOTIFICATION_CONFIG = {
  strong_launch: {
    icon: Rocket,
    color: 'text-green-500',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200'
  },
  exploding_trend: {
    icon: TrendingUp,
    color: 'text-orange-500',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200'
  },
  watchlist_alert: {
    icon: Bookmark,
    color: 'text-purple-500',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200'
  },
  score_milestone: {
    icon: Star,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200'
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

// Get score color
function getScoreColor(score) {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-blue-600';
  if (score >= 40) return 'text-amber-600';
  return 'text-red-600';
}

// Single notification item
function NotificationItem({ notification, onMarkRead, onClose }) {
  const config = NOTIFICATION_CONFIG[notification.notification_type] || NOTIFICATION_CONFIG.strong_launch;
  const Icon = config.icon;
  
  const handleClick = () => {
    if (!notification.is_read) {
      onMarkRead([notification.id]);
    }
    onClose();
  };
  
  return (
    <Link
      to={`/product/${notification.product_id}`}
      onClick={handleClick}
      className={`block p-3 border-b last:border-b-0 hover:bg-slate-50 transition-colors ${
        notification.is_read ? 'opacity-60' : ''
      }`}
    >
      <div className="flex gap-3">
        {/* Icon */}
        <div className={`p-2 rounded-lg ${config.bgColor} flex-shrink-0`}>
          <Icon className={`h-4 w-4 ${config.color}`} />
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className={`text-sm font-medium text-slate-900 truncate ${
              notification.is_read ? '' : 'font-semibold'
            }`}>
              {notification.product_name}
            </h4>
            {notification.is_watchlist && (
              <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200 flex-shrink-0">
                Watchlist
              </Badge>
            )}
          </div>
          
          <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">
            {notification.reason}
          </p>
          
          <div className="flex items-center gap-3 mt-1.5 text-xs">
            <span className={`font-mono font-bold ${getScoreColor(notification.launch_score)}`}>
              {notification.launch_score}
            </span>
            <span className="text-slate-400 capitalize">
              {notification.trend_stage}
            </span>
            <span className="text-slate-400">
              {formatRelativeTime(notification.created_at)}
            </span>
            {!notification.is_read && (
              <span className="w-2 h-2 rounded-full bg-indigo-500 flex-shrink-0" />
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}

export default function NotificationCenter() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const pollInterval = useRef(null);
  
  // Fetch notifications
  const fetchNotifications = useCallback(async () => {
    if (!user) return;
    
    try {
      const response = await api.get('/api/notifications/?limit=20');
      if (response.data) {
        setNotifications(response.data.notifications || []);
        setUnreadCount(response.data.unread_count || 0);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }, [user]);
  
  // Fetch unread count only (for polling)
  const fetchUnreadCount = useCallback(async () => {
    if (!user) return;
    
    try {
      const response = await api.get('/api/notifications/unread-count');
      if (response.data) {
        setUnreadCount(response.data.unread_count || 0);
      }
    } catch (error) {
      // Silent fail for polling
    }
  }, [user]);
  
  // Initial fetch
  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user, fetchNotifications]);
  
  // Poll for unread count every 30 seconds (fallback if SSE disconnects)
  useEffect(() => {
    if (user) {
      pollInterval.current = setInterval(fetchUnreadCount, 30000);
      return () => clearInterval(pollInterval.current);
    }
  }, [user, fetchUnreadCount]);

  // WebSocket real-time listener with reconnection
  useEffect(() => {
    if (!user) return;
    const token = localStorage.getItem('trendscout_token');
    if (!token) return;

    let ws;
    let reconnectTimer;
    let retryCount = 0;
    const MAX_RETRIES = 10;
    let alive = true;

    function connect() {
      if (!alive) return;
      const rawUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      const base = rawUrl.replace(/^https:/, 'wss:').replace(/^http:/, 'ws:');
      ws = new WebSocket(`${base}/api/notifications/ws?token=${token}`);

      ws.onopen = () => { retryCount = 0; };

      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          if (msg.type === 'notification') {
            const notif = msg.data || msg;
            setNotifications((prev) => [notif, ...prev].slice(0, 20));
            setUnreadCount((c) => c + 1);
          } else if (msg.type === 'unread_count') {
            setUnreadCount(msg.data?.count ?? msg.count ?? 0);
          }
          // heartbeat/pong ignored silently
        } catch { /* ignore bad frames */ }
      };

      ws.onclose = () => {
        if (!alive) return;
        const delay = Math.min(1000 * 2 ** retryCount, 30000);
        retryCount = Math.min(retryCount + 1, MAX_RETRIES);
        reconnectTimer = setTimeout(connect, delay);
      };

      ws.onerror = () => { ws.close(); };
    }

    connect();

    return () => {
      alive = false;
      clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, [user]);
  
  // Refetch when popover opens
  useEffect(() => {
    if (isOpen && user) {
      fetchNotifications();
    }
  }, [isOpen, user, fetchNotifications]);
  
  // Mark notifications as read
  const handleMarkRead = async (notificationIds) => {
    try {
      await api.post('/api/notifications/mark-read', notificationIds);
      setNotifications(prev => 
        prev.map(n => 
          notificationIds.includes(n.id) ? { ...n, is_read: true } : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - notificationIds.length));
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };
  
  // Mark all as read
  const handleMarkAllRead = async () => {
    try {
      await api.post('/api/notifications/mark-all-read');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };
  
  if (!user) {
    return null;
  }
  
  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative h-9 w-9"
          data-testid="notification-center-btn"
        >
          <Bell className="h-5 w-5 text-slate-600" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 h-4 min-w-4 px-1 rounded-full bg-red-500 text-white text-xs font-medium flex items-center justify-center">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      
      <PopoverContent 
        className="w-96 p-0 max-h-[500px] overflow-hidden"
        align="end"
        data-testid="notification-center-dropdown"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b bg-slate-50">
          <h3 className="font-semibold text-slate-900 flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
            {unreadCount > 0 && (
              <Badge className="bg-indigo-500 text-white ml-1">
                {unreadCount}
              </Badge>
            )}
          </h3>
          <div className="flex items-center gap-1">
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMarkAllRead}
                className="h-7 text-xs text-slate-600 hover:text-slate-900"
              >
                <CheckCheck className="h-3.5 w-3.5 mr-1" />
                Mark all read
              </Button>
            )}
            <Link to="/settings/notifications" onClick={() => setIsOpen(false)}>
              <Button variant="ghost" size="icon" className="h-7 w-7">
                <Settings className="h-4 w-4 text-slate-500" />
              </Button>
            </Link>
          </div>
        </div>
        
        {/* Notifications List */}
        <div className="max-h-[400px] overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center">
              <Loader2 className="h-6 w-6 animate-spin mx-auto text-indigo-500" />
              <p className="text-sm text-slate-500 mt-2">Loading...</p>
            </div>
          ) : notifications.length > 0 ? (
            notifications.map(notification => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onMarkRead={handleMarkRead}
                onClose={() => setIsOpen(false)}
              />
            ))
          ) : (
            <div className="p-8 text-center">
              <Bell className="h-10 w-10 text-slate-300 mx-auto" />
              <p className="text-slate-600 mt-3 font-medium">No notifications yet</p>
              <p className="text-sm text-slate-500 mt-1">
                You'll be notified when strong opportunities appear
              </p>
            </div>
          )}
        </div>
        
        {/* Footer */}
        {notifications.length > 0 && (
          <div className="p-2 border-t bg-slate-50">
            <Link 
              to="/notifications" 
              onClick={() => setIsOpen(false)}
              className="block text-center text-sm text-indigo-600 hover:text-indigo-700 font-medium py-1"
            >
              View all notifications
            </Link>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}
