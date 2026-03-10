import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { TrendingUp, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function LandingLayout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: 'Trending', href: '/trending-products' },
    { name: 'Features', href: '/#features' },
    { name: 'Pricing', href: '/#pricing' },
  ];

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/50">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2" data-testid="logo-link">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600">
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
                className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-900"
              >
                {item.name}
              </a>
            ))}
          </div>

          {/* Auth buttons */}
          <div className="hidden md:flex md:items-center md:gap-3">
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button data-testid="go-to-dashboard-btn" className="bg-indigo-600 hover:bg-indigo-700">
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" data-testid="login-btn" className="text-slate-600">
                    Log in
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button data-testid="signup-btn" className="bg-indigo-600 hover:bg-indigo-700">
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
          <div className="md:hidden border-t border-slate-200 bg-white px-6 py-4">
            <div className="flex flex-col gap-4">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-sm font-medium text-slate-600"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </a>
              ))}
              <div className="flex flex-col gap-2 pt-4 border-t border-slate-200">
                {isAuthenticated ? (
                  <Link to="/dashboard">
                    <Button className="w-full bg-indigo-600 hover:bg-indigo-700">
                      Go to Dashboard
                    </Button>
                  </Link>
                ) : (
                  <>
                    <Link to="/login">
                      <Button variant="outline" className="w-full">Log in</Button>
                    </Link>
                    <Link to="/signup">
                      <Button className="w-full bg-indigo-600 hover:bg-indigo-700">
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
      <main className="pt-[73px]">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
              <span className="font-manrope text-lg font-bold text-slate-900">TrendScout</span>
            </div>
            <p className="text-sm text-slate-500">
              © {new Date().getFullYear()} TrendScout. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
