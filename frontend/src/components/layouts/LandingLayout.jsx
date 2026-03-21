import React, { useState, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { TrendingUp, Menu, X, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import ExitIntentPopup from '@/components/ExitIntentPopup';
import SocialProofToast from '@/components/SocialProofToast';

const NAV_ITEMS = [
  { name: 'Product', children: [
    { name: 'Trending Products', href: '/trending-products', desc: 'Browse rising products across channels' },
    { name: 'Leaderboard', href: '/top-trending-products', desc: 'Top-performing products ranked by score' },
    { name: 'Free Tools', href: '/free-tools', desc: 'Profit calculators and validation tools' },
    { name: 'Product Quiz', href: '/product-quiz', desc: 'Find out which tool suits you' },
  ]},
  { name: 'Solutions', children: [
    { name: 'For Shopify Sellers', href: '/for-shopify' },
    { name: 'For Amazon UK', href: '/for-amazon-uk' },
    { name: 'For TikTok Shop UK', href: '/for-tiktok-shop-uk' },
    { name: 'UK Product Research', href: '/uk-product-research' },
  ]},
  { name: 'How It Works', href: '/how-it-works' },
  { name: 'Pricing', href: '/pricing' },
];

function DropdownMenu({ items, isOpen }) {
  if (!isOpen) return null;
  return (
    <div className="absolute top-full left-1/2 -translate-x-1/2 pt-2 z-50">
      <div className="bg-white rounded-xl border border-slate-200 shadow-xl p-2 min-w-[240px]">
        {items.map((item) => (
          <Link
            key={item.name}
            to={item.href}
            className="block px-3 py-2.5 rounded-lg hover:bg-slate-50 transition-colors"
            data-testid={`dropdown-${item.name.toLowerCase().replace(/\s/g, '-')}`}
          >
            <span className="text-sm font-medium text-slate-900">{item.name}</span>
            {item.desc && <span className="block text-xs text-slate-500 mt-0.5">{item.desc}</span>}
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function LandingLayout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState(null);
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-100/80">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3 lg:px-8">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group" data-testid="logo-link">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 group-hover:bg-indigo-700 transition-colors">
              <TrendingUp className="h-4.5 w-4.5 text-white" />
            </div>
            <span className="font-manrope text-lg font-bold text-slate-900 tracking-tight">TrendScout</span>
          </Link>

          {/* Desktop navigation */}
          <div className="hidden lg:flex lg:items-center lg:gap-1">
            {NAV_ITEMS.map((item) => (
              <div
                key={item.name}
                className="relative"
                onMouseEnter={() => item.children && setOpenDropdown(item.name)}
                onMouseLeave={() => setOpenDropdown(null)}
              >
                {item.children ? (
                  <button
                    className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors rounded-lg hover:bg-slate-50"
                    data-testid={`nav-${item.name.toLowerCase().replace(/\s/g, '-')}`}
                  >
                    {item.name}
                    <ChevronDown className="h-3.5 w-3.5" />
                  </button>
                ) : (
                  <Link
                    to={item.href}
                    className={`px-3 py-2 text-sm font-medium transition-colors rounded-lg hover:bg-slate-50 ${
                      location.pathname === item.href ? 'text-indigo-600' : 'text-slate-600 hover:text-slate-900'
                    }`}
                    data-testid={`nav-${item.name.toLowerCase().replace(/\s/g, '-')}`}
                  >
                    {item.name}
                  </Link>
                )}
                {item.children && <DropdownMenu items={item.children} isOpen={openDropdown === item.name} />}
              </div>
            ))}
          </div>

          {/* Auth buttons */}
          <div className="hidden lg:flex lg:items-center lg:gap-3">
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button data-testid="go-to-dashboard-btn" className="bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm font-semibold text-sm h-9 px-4">
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" data-testid="login-btn" className="text-slate-600 hover:text-slate-900 rounded-lg text-sm font-medium h-9">
                    Log in
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button data-testid="signup-btn" className="bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm font-semibold text-sm h-9 px-5">
                    Start Free
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button className="lg:hidden p-2 -mr-2" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="mobile-menu-toggle">
            {mobileMenuOpen ? <X className="h-5 w-5 text-slate-600" /> : <Menu className="h-5 w-5 text-slate-600" />}
          </button>
        </nav>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-slate-100 bg-white px-6 py-4 shadow-lg">
            <div className="flex flex-col gap-1">
              {NAV_ITEMS.map((item) => (
                <div key={item.name}>
                  {item.children ? (
                    <>
                      <p className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">{item.name}</p>
                      {item.children.map((child) => (
                        <Link
                          key={child.name}
                          to={child.href}
                          className="block px-3 py-2 text-sm font-medium text-slate-600 hover:text-indigo-600 rounded-lg"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          {child.name}
                        </Link>
                      ))}
                    </>
                  ) : (
                    <Link
                      to={item.href}
                      className="block px-3 py-2.5 text-sm font-medium text-slate-700 hover:text-indigo-600 rounded-lg"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  )}
                </div>
              ))}
              <div className="flex flex-col gap-2 pt-4 mt-2 border-t border-slate-100">
                {isAuthenticated ? (
                  <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                    <Button className="w-full bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold">Go to Dashboard</Button>
                  </Link>
                ) : (
                  <>
                    <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="outline" className="w-full rounded-lg">Log in</Button>
                    </Link>
                    <Link to="/signup" onClick={() => setMobileMenuOpen(false)}>
                      <Button className="w-full bg-indigo-600 hover:bg-indigo-700 rounded-lg font-semibold">Start Free</Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main content */}
      <main className="pt-[57px]">{children}</main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-14 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-10">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600">
                  <TrendingUp className="h-3.5 w-3.5 text-white" />
                </div>
                <span className="font-manrope text-base font-bold text-slate-900 tracking-tight">TrendScout</span>
              </div>
              <p className="text-sm text-slate-500 leading-relaxed max-w-xs">
                AI product research and launch intelligence for UK ecommerce sellers.
              </p>
              <p className="text-xs text-slate-400 mt-3">TrendScout &middot; United Kingdom</p>
            </div>

            {/* Product */}
            <div>
              <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/trending-products" className="text-slate-500 hover:text-indigo-600 transition-colors">Trending Products</Link></li>
                <li><Link to="/top-trending-products" className="text-slate-500 hover:text-indigo-600 transition-colors">Leaderboard</Link></li>
                <li><Link to="/uk-product-viability-score" className="text-slate-500 hover:text-indigo-600 transition-colors">UK Viability Score</Link></li>
                <li><Link to="/free-tools" className="text-slate-500 hover:text-indigo-600 transition-colors">Free Tools</Link></li>
                <li><Link to="/product-quiz" className="text-slate-500 hover:text-indigo-600 transition-colors">Product Quiz</Link></li>
                <li><Link to="/sample-product-analysis" className="text-slate-500 hover:text-indigo-600 transition-colors">Sample Analysis</Link></li>
                <li><Link to="/changelog" className="text-slate-500 hover:text-indigo-600 transition-colors">Changelog</Link></li>
                <li><Link to="/methodology" className="text-slate-500 hover:text-indigo-600 transition-colors">Methodology</Link></li>
                <li><Link to="/accuracy" className="text-slate-500 hover:text-indigo-600 transition-colors">Accuracy</Link></li>
                <li><Link to="/pricing" className="text-slate-500 hover:text-indigo-600 transition-colors">Pricing</Link></li>
                <li><Link to="/how-it-works" className="text-slate-500 hover:text-indigo-600 transition-colors">How It Works</Link></li>
              </ul>
            </div>

            {/* Solutions */}
            <div>
              <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Solutions</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/for-shopify" className="text-slate-500 hover:text-indigo-600 transition-colors">For Shopify Sellers</Link></li>
                <li><Link to="/for-amazon-uk" className="text-slate-500 hover:text-indigo-600 transition-colors">For Amazon UK</Link></li>
                <li><Link to="/for-tiktok-shop-uk" className="text-slate-500 hover:text-indigo-600 transition-colors">For TikTok Shop UK</Link></li>
                <li><Link to="/uk-product-research" className="text-slate-500 hover:text-indigo-600 transition-colors">UK Product Research</Link></li>
                <li><Link to="/dropshipping-product-research-uk" className="text-slate-500 hover:text-indigo-600 transition-colors">UK Dropshipping</Link></li>
                <li><Link to="/winning-products-uk" className="text-slate-500 hover:text-indigo-600 transition-colors">Winning Products UK</Link></li>
              </ul>
            </div>

            {/* Compare */}
            <div>
              <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Compare</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/compare/jungle-scout-vs-trendscout" className="text-slate-500 hover:text-indigo-600 transition-colors">vs Jungle Scout</Link></li>
                <li><Link to="/compare/sell-the-trend-vs-trendscout" className="text-slate-500 hover:text-indigo-600 transition-colors">vs Sell The Trend</Link></li>
                <li><Link to="/compare/minea-vs-trendscout" className="text-slate-500 hover:text-indigo-600 transition-colors">vs Minea</Link></li>
                <li><Link to="/compare/helium-10-vs-trendscout" className="text-slate-500 hover:text-indigo-600 transition-colors">vs Helium 10</Link></li>
                <li><Link to="/compare/ecomhunt-vs-trendscout" className="text-slate-500 hover:text-indigo-600 transition-colors">vs Ecomhunt</Link></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/about" className="text-slate-500 hover:text-indigo-600 transition-colors">About</Link></li>
                <li><Link to="/contact" className="text-slate-500 hover:text-indigo-600 transition-colors">Contact</Link></li>
                <li><Link to="/blog" className="text-slate-500 hover:text-indigo-600 transition-colors">Blog</Link></li>
                <li><Link to="/help" className="text-slate-500 hover:text-indigo-600 transition-colors">Help Centre</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-slate-100 pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-xs text-slate-400">&copy; {new Date().getFullYear()} TrendScout. All rights reserved.</p>
            <div className="flex items-center gap-5 text-xs text-slate-400">
              <Link to="/privacy" className="hover:text-slate-600 transition-colors">Privacy Policy</Link>
              <Link to="/terms" className="hover:text-slate-600 transition-colors">Terms of Service</Link>
              <Link to="/cookie-policy" className="hover:text-slate-600 transition-colors">Cookies</Link>
              <Link to="/refund-policy" className="hover:text-slate-600 transition-colors">Refunds</Link>
              <a href="mailto:info@trendscout.click" className="hover:text-slate-600 transition-colors">info@trendscout.click</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Conversion components — only for non-authenticated visitors */}
      {!isAuthenticated && (
        <>
          <ExitIntentPopup />
          <SocialProofToast />
        </>
      )}
    </div>
  );
}
