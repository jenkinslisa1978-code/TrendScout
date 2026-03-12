import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  Search, 
  Bookmark, 
  LogOut,
  TrendingUp,
  Shield,
  ChevronRight,
  Bell,
  Zap,
  Sparkles,
  Store,
  FileText,
  Settings,
  Gift,
  Target,
  Activity,
  Wifi,
  Brain,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getUnreadAlertCount } from '@/services/alertService';
import NotificationCenter from '@/components/notifications/NotificationCenter';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Discover', href: '/discover', icon: Search },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'My Stores', href: '/stores', icon: Store },
  { name: 'Outcomes', href: '/outcomes', icon: Target },
  { name: 'Ad Tests', href: '/ad-tests', icon: Zap },
  { name: 'Saved Products', href: '/saved', icon: Bookmark },
  { name: 'Referrals', href: '/referrals', icon: Gift },
];

const eliteNavigation = [
  { name: 'Trend Alerts', href: '/alerts', icon: Bell, badge: true },
  { name: 'Budget Optimizer', href: '/optimization', icon: Brain },
];

const adminNavigation = [
  { name: 'Admin Panel', href: '/admin', icon: Shield },
  { name: 'Automation', href: '/admin/automation', icon: Zap },
  { name: 'System Health', href: '/admin/health', icon: Activity },
  { name: 'Integrations', href: '/admin/integrations', icon: Wifi },
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
      const interval = setInterval(fetchAlertCount, 30000);
      return () => clearInterval(interval);
    }
  }, [isElite]);

  const handleSignOut = async () => {
    await signOut();
    window.location.href = '/';
  };

  const NavItem = ({ item, isActive }) => (
    <Link
      to={item.href}
      data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
      className={cn(
        'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
        isActive
          ? 'bg-indigo-50 text-indigo-700 shadow-sm'
          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
      )}
    >
      <div className={cn(
        'flex h-8 w-8 items-center justify-center rounded-lg transition-all duration-200',
        isActive 
          ? 'bg-indigo-100' 
          : 'bg-transparent group-hover:bg-slate-100'
      )}>
        <item.icon className={cn(
          'h-4 w-4 transition-colors',
          isActive ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600'
        )} />
      </div>
      <span className="flex-1">{item.name}</span>
      {item.badge && alertCount > 0 && (
        <Badge className="bg-red-500 text-white text-xs px-1.5 py-0.5 min-w-[20px] text-center shadow-sm">
          {alertCount > 99 ? '99+' : alertCount}
        </Badge>
      )}
      {isActive && !item.badge && (
        <ChevronRight className="h-4 w-4 text-indigo-400" />
      )}
    </Link>
  );

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Premium Sidebar */}
      <aside className="fixed left-0 top-0 z-40 h-screen w-72 border-r border-slate-200/80 bg-white/95 backdrop-blur-xl">
        {/* Logo Section */}
        <div className="flex h-16 items-center gap-3 border-b border-slate-100 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-indigo-700 shadow-lg shadow-indigo-200/50">
            <TrendingUp className="h-5 w-5 text-white" />
          </div>
          <div>
            <span className="font-manrope text-lg font-bold text-slate-900 tracking-tight">TrendScout</span>
            <div className="flex items-center gap-1">
              <Sparkles className="h-3 w-3 text-amber-500" />
              <span className="text-[10px] font-semibold text-amber-600 uppercase tracking-wider">Pro Research</span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1 p-4 premium-scrollbar overflow-y-auto" style={{ maxHeight: 'calc(100vh - 180px)' }}>
          {/* Main Navigation */}
          <div className="mb-2">
            <p className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              Main Menu
            </p>
          </div>
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || 
              (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
            return <NavItem key={item.name} item={item} isActive={isActive} />;
          })}

          {/* Elite Section */}
          {isElite && (
            <>
              <div className="my-4 border-t border-slate-100" />
              <div className="mb-2">
                <p className="px-3 py-2 text-[10px] font-bold text-indigo-500 uppercase tracking-widest flex items-center gap-1.5">
                  <Sparkles className="h-3 w-3" />
                  Elite Features
                </p>
              </div>
              {eliteNavigation.map((item) => {
                const isActive = location.pathname === item.href;
                return <NavItem key={item.name} item={item} isActive={isActive} />;
              })}
            </>
          )}

          {/* Admin Section */}
          {(profile?.role === 'admin' || isDemoMode) && (
            <>
              <div className="my-4 border-t border-slate-100" />
              <div className="mb-2">
                <p className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  Administration
                </p>
              </div>
              {adminNavigation.map((item) => {
                const isActive = location.pathname === item.href;
                return <NavItem key={item.name} item={item} isActive={isActive} />;
              })}
            </>
          )}
        </nav>

        {/* User Section - Fixed at bottom */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-slate-100 bg-white/95 p-4">
          {isDemoMode && (
            <div className="mb-3 rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/50 px-3 py-2.5 text-xs">
              <div className="flex items-center gap-2 text-amber-700 font-medium">
                <Sparkles className="h-3.5 w-3.5" />
                Demo Mode Active
              </div>
              <p className="text-amber-600/80 text-[10px] mt-0.5">Sign in for full features</p>
            </div>
          )}
          
          <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-600 text-sm font-bold text-white shadow-md">
              {(profile?.full_name || user?.email || 'U')[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="truncate text-sm font-semibold text-slate-900">
                {profile?.full_name || 'Demo User'}
              </p>
              <div className="flex items-center gap-1.5">
                <span className="inline-flex items-center rounded-full bg-indigo-100 px-2 py-0.5 text-[10px] font-semibold text-indigo-700 uppercase">
                  {profile?.plan || 'Elite'}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <NotificationCenter />
              <Link to="/settings/notifications">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                >
                  <Settings className="h-4 w-4" />
                </Button>
              </Link>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSignOut}
                data-testid="logout-btn"
                className="h-9 w-9 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-72 min-h-screen">
        <div className="p-8 animate-fade-in">
          {children}
        </div>
      </main>
    </div>
  );
}
