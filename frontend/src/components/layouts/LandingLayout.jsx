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
    { name: 'Find Products', href: '/trending-products' },
    { name: 'Leaderboard', href: '/top-trending-products' },
    { name: 'Examples', href: '/demo' },
    { name: 'Pricing', href: '/pricing' },
    { name: 'Help', href: '/help' },
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
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2.5 mb-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600">
                  <TrendingUp className="h-4 w-4 text-white" />
                </div>
                <span className="font-manrope text-lg font-bold text-slate-900">TrendScout</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">AI product validation for ecommerce. Find products worth launching before you spend money on ads.</p>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Products</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/trending-products" className="text-slate-400 hover:text-slate-600 transition-colors">Find Products</Link></li>
                <li><Link to="/top-trending-products" className="text-slate-400 hover:text-slate-600 transition-colors">Leaderboard</Link></li>
                <li><Link to="/trending-products-today" className="text-slate-400 hover:text-slate-600 transition-colors">Trending Today</Link></li>
                <li><Link to="/demo" className="text-slate-400 hover:text-slate-600 transition-colors">Examples</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/help" className="text-slate-400 hover:text-slate-600 transition-colors">Help &amp; FAQ</Link></li>
                <li><Link to="/blog" className="text-slate-400 hover:text-slate-600 transition-colors">Blog</Link></li>
                <li><Link to="/pricing" className="text-slate-400 hover:text-slate-600 transition-colors">Pricing</Link></li>
                <li><Link to="/tools" className="text-slate-400 hover:text-slate-600 transition-colors">Free Tools</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/privacy" className="text-slate-400 hover:text-slate-600 transition-colors">Privacy Policy</Link></li>
                <li><Link to="/terms" className="text-slate-400 hover:text-slate-600 transition-colors">Terms of Service</Link></li>
                <li><a href="mailto:info@trendscout.click" className="text-slate-400 hover:text-slate-600 transition-colors">info@trendscout.click</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-100 pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-xs text-slate-400">&copy; {new Date().getFullYear()} TrendScout Ltd. All rights reserved.</p>
            <div className="flex items-center gap-4 text-xs text-slate-400">
              <Link to="/privacy" className="hover:text-slate-600 transition-colors">Privacy</Link>
              <Link to="/terms" className="hover:text-slate-600 transition-colors">Terms</Link>
              <Link to="/sitemap.xml" className="hover:text-slate-600 transition-colors">Sitemap</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
