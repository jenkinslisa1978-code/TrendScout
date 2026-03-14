import React, { useState, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { TrendingUp, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function LandingLayout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const navigation = [
    { name: 'Trending', href: '/trending-products' },
    { name: 'Leaderboard', href: '/top-trending-products' },
    { name: 'Tools', href: '/tools' },
    { name: 'Blog', href: '/blog' },
    { name: 'Features', href: '/#features' },
    { name: 'Pricing', href: '/#pricing' },
  ];

  const handleNavClick = useCallback((e, href) => {
    if (href.startsWith('/#')) {
      e.preventDefault();
      const id = href.slice(2);
      if (location.pathname === '/') {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      } else {
        navigate('/');
        setTimeout(() => {
          document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
      setMobileMenuOpen(false);
    }
  }, [location.pathname, navigate]);

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/70 backdrop-blur-2xl border-b border-slate-100/70">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3.5 lg:px-8">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group" data-testid="logo-link">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 shadow-sm group-hover:shadow-md group-hover:scale-105 transition-all duration-300">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <span className="font-manrope text-xl font-bold text-slate-900">TrendScout</span>
          </Link>

          {/* Desktop navigation */}
          <div className="hidden md:flex md:items-center md:gap-8">
            {navigation.map((item) => (
              <a
                key={item.name}
                href={item.href}
                onClick={(e) => handleNavClick(e, item.href)}
                className="text-sm font-medium text-slate-500 transition-colors duration-200 hover:text-slate-900"
                data-testid={`nav-link-${item.name.toLowerCase()}`}
              >
                {item.name}
              </a>
            ))}
          </div>

          {/* Auth buttons */}
          <div className="hidden md:flex md:items-center md:gap-3">
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button data-testid="go-to-dashboard-btn" className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 rounded-xl shadow-sm">
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" data-testid="login-btn" className="text-slate-600 rounded-xl">
                    Log in
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button data-testid="signup-btn" className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 rounded-xl shadow-sm">
                    Start Free Trial
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6 text-slate-600" />
            ) : (
              <Menu className="h-6 w-6 text-slate-600" />
            )}
          </button>
        </nav>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-100 bg-white/95 backdrop-blur-xl px-6 py-5">
            <div className="flex flex-col gap-4">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-sm font-medium text-slate-600"
                  onClick={(e) => handleNavClick(e, item.href)}
                  data-testid={`mobile-nav-link-${item.name.toLowerCase()}`}
                >
                  {item.name}
                </a>
              ))}
              <div className="flex flex-col gap-2 pt-4 border-t border-slate-100">
                {isAuthenticated ? (
                  <Link to="/dashboard">
                    <Button className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 rounded-xl">
                      Go to Dashboard
                    </Button>
                  </Link>
                ) : (
                  <>
                    <Link to="/login">
                      <Button variant="outline" className="w-full rounded-xl">Log in</Button>
                    </Link>
                    <Link to="/signup">
                      <Button className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 rounded-xl">
                        Start Free Trial
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main content */}
      <main className="pt-[65px]">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-100 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
              <span className="font-manrope text-lg font-bold text-slate-900">TrendScout</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-slate-400">
              <Link to="/tools" className="hover:text-slate-600 transition-colors">Free Tools</Link>
              <Link to="/trending-products" className="hover:text-slate-600 transition-colors">Trending Products</Link>
              <Link to="/trending-products-today" className="hover:text-slate-600 transition-colors">Trending Today</Link>
              <Link to="/top-trending-products" className="hover:text-slate-600 transition-colors">Leaderboard</Link>
              <Link to="/blog" className="hover:text-slate-600 transition-colors">Blog</Link>
            </div>
            <p className="text-sm text-slate-400">
              &copy; {new Date().getFullYear()} TrendScout. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
