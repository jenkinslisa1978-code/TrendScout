import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  Search, 
  Bookmark, 
  Settings, 
  LogOut,
  TrendingUp,
  Shield,
  ChevronRight,
  Bell,
  Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getUnreadAlertCount } from '@/services/alertService';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Discover', href: '/discover', icon: Search },
  { name: 'Saved Products', href: '/saved', icon: Bookmark },
];

const eliteNavigation = [
  { name: 'Trend Alerts', href: '/alerts', icon: Bell, badge: true },
];

const adminNavigation = [
  { name: 'Admin Panel', href: '/admin', icon: Shield },
  { name: 'Automation', href: '/admin/automation', icon: Zap },
];

export default function DashboardLayout({ children }) {
  const location = useLocation();
  const { user, profile, signOut, isDemoMode } = useAuth();
  const [alertCount, setAlertCount] = useState(0);

  const isElite = profile?.plan === 'elite' || profile?.role === 'admin' || isDemoMode;

  useEffect(() => {
    const fetchAlertCount = async () => {
      const count = await getUnreadAlertCount();
      setAlertCount(count);
    };
    
    if (isElite) {
      fetchAlertCount();
      // Refresh alert count every 30 seconds
      const interval = setInterval(fetchAlertCount, 30000);
      return () => clearInterval(interval);
    }
  }, [isElite]);

  const handleSignOut = async () => {
    await signOut();
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-slate-200 bg-white">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
            <TrendingUp className="h-5 w-5 text-white" />
          </div>
          <span className="font-manrope text-lg font-bold text-slate-900">TrendScout</span>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1 p-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || 
              (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                to={item.href}
                data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
                {isActive && <ChevronRight className="ml-auto h-4 w-4" />}
              </Link>
            );
          })}

          {/* Elite features (Trend Alerts) */}
          {isElite && (
            <>
              <div className="my-2 border-t border-slate-200" />
              <p className="px-3 py-1 text-xs font-semibold text-slate-400 uppercase tracking-wider">Elite</p>
              {eliteNavigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
                    className={cn(
                      'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    )}
                  >
                    <item.icon className="h-5 w-5" />
                    {item.name}
                    {item.badge && alertCount > 0 && (
                      <Badge className="ml-auto bg-red-500 text-white text-xs px-1.5 py-0.5 min-w-[20px] text-center">
                        {alertCount > 99 ? '99+' : alertCount}
                      </Badge>
                    )}
                    {isActive && !item.badge && <ChevronRight className="ml-auto h-4 w-4" />}
                  </Link>
                );
              })}
            </>
          )}

          {/* Admin navigation */}
          {(profile?.role === 'admin' || isDemoMode) && (
            <>
              <div className="my-2 border-t border-slate-200" />
              <p className="px-3 py-1 text-xs font-semibold text-slate-400 uppercase tracking-wider">Admin</p>
              {adminNavigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
                    className={cn(
                      'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    )}
                  >
                    <item.icon className="h-5 w-5" />
                    {item.name}
                    {isActive && <ChevronRight className="ml-auto h-4 w-4" />}
                  </Link>
                );
              })}
            </>
          )}
        </nav>

        {/* User section */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-slate-200 p-4">
          {isDemoMode && (
            <div className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">
              Demo Mode - Add Supabase credentials to enable full functionality
            </div>
          )}
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
              {(profile?.full_name || user?.email || 'U')[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="truncate text-sm font-medium text-slate-900">
                {profile?.full_name || 'User'}
              </p>
              <p className="truncate text-xs text-slate-500">
                {profile?.plan?.charAt(0).toUpperCase() + profile?.plan?.slice(1) || 'Starter'} Plan
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleSignOut}
              data-testid="logout-btn"
              className="h-8 w-8 text-slate-400 hover:text-slate-600"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-64 min-h-screen">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
