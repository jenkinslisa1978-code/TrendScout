import React, { useState, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { TrendingUp, Menu, X, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import ExitIntentPopup from '@/components/ExitIntentPopup';
import SocialProofToast from '@/components/SocialProofToast';

const NAV_ITEMS = [
  { name: 'Features', href: '/features' },
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
      <div className="bg-[#18181b] rounded-xl border border-white/10 shadow-xl p-2 min-w-[240px]">
        {items.map((item) => (
          <Link
            key={item.name}
            to={item.href}
            className="block px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors"
            data-testid={`dropdown-${item.name.toLowerCase().replace(/\s/g, '-')}`}
          >
            <span className="text-sm font-medium text-zinc-200">{item.name}</span>
            {item.desc && <span className="block text-xs text-zinc-500 mt-0.5">{item.desc}</span>}
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
    <div className="min-h-screen bg-[#09090b] overflow-x-hidden">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#09090b]/80 backdrop-blur-xl border-b border-white/[0.06]">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3 lg:px-8">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group" data-testid="logo-link">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 group-hover:bg-emerald-500 transition-colors">
              <TrendingUp className="h-4.5 w-4.5 text-white" />
            </div>
            <span className="font-manrope text-lg font-bold text-white tracking-tight">TrendScout</span>
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
                    className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-zinc-400 hover:text-white transition-colors rounded-lg hover:bg-white/5"
                    data-testid={`nav-${item.name.toLowerCase().replace(/\s/g, '-')}`}
                  >
                    {item.name}
                    <ChevronDown className="h-3.5 w-3.5" />
                  </button>
                ) : (
                  <Link
                    to={item.href}
                    className={`px-3 py-2 text-sm font-medium transition-colors rounded-lg hover:bg-white/5 ${
                      location.pathname === item.href ? 'text-emerald-400' : 'text-zinc-400 hover:text-white'
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
                <Button data-testid="go-to-dashboard-btn" className="bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-sm font-semibold text-sm h-9 px-4">
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" data-testid="login-btn" className="text-zinc-400 hover:text-white rounded-lg text-sm font-medium h-9">
                    Log in
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button data-testid="signup-btn" className="bg-emerald-500 hover:bg-emerald-400 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.3)] font-bold text-sm h-9 px-5 text-white tracking-wide">
                    Validate a Product
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button className="lg:hidden p-2 -mr-2" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="mobile-menu-toggle">
            {mobileMenuOpen ? <X className="h-5 w-5 text-zinc-400" /> : <Menu className="h-5 w-5 text-zinc-400" />}
          </button>
        </nav>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-white/[0.06] bg-[#18181b] px-6 py-4 shadow-lg">
            <div className="flex flex-col gap-1">
              {NAV_ITEMS.map((item) => (
                <div key={item.name}>
                  {item.children ? (
                    <>
                      <p className="px-3 py-2 text-xs font-semibold text-zinc-500 uppercase tracking-wider">{item.name}</p>
                      {item.children.map((child) => (
                        <Link
                          key={child.name}
                          to={child.href}
                          className="block px-3 py-2 text-sm font-medium text-zinc-400 hover:text-emerald-400 rounded-lg"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          {child.name}
                        </Link>
                      ))}
                    </>
                  ) : (
                    <Link
                      to={item.href}
                      className="block px-3 py-2.5 text-sm font-medium text-zinc-300 hover:text-emerald-400 rounded-lg"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  )}
                </div>
              ))}
              <div className="flex flex-col gap-2 pt-4 mt-2 border-t border-white/[0.06]">
                {isAuthenticated ? (
                  <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                    <Button className="w-full bg-emerald-600 hover:bg-emerald-500 rounded-lg font-semibold">Go to Dashboard</Button>
                  </Link>
                ) : (
                  <>
                    <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="outline" className="w-full rounded-lg border-white/10 text-zinc-300 hover:bg-white/5">Log in</Button>
                    </Link>
                    <Link to="/signup" onClick={() => setMobileMenuOpen(false)}>
                      <Button className="w-full bg-emerald-500 hover:bg-emerald-400 rounded-lg font-bold text-white">Validate a Product</Button>
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
      <footer className="border-t border-white/[0.06] bg-[#09090b]">
        <div className="mx-auto max-w-7xl px-6 py-14 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-10">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600">
                  <TrendingUp className="h-3.5 w-3.5 text-white" />
                </div>
                <span className="font-manrope text-base font-bold text-white tracking-tight">TrendScout</span>
              </div>
              <p className="text-sm text-zinc-500 leading-relaxed max-w-xs">
                AI product research and launch intelligence for UK ecommerce sellers.
              </p>
              <p className="text-xs text-zinc-600 mt-3">TrendScout &middot; United Kingdom</p>
            </div>

            {/* Product */}
            <div>
              <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-3">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/trending-products" className="text-zinc-500 hover:text-emerald-400 transition-colors">Trending Products</Link></li>
                <li><Link to="/top-trending-products" className="text-zinc-500 hover:text-emerald-400 transition-colors">Leaderboard</Link></li>
                <li><Link to="/uk-product-viability-score" className="text-zinc-500 hover:text-emerald-400 transition-colors">UK Viability Score</Link></li>
                <li><Link to="/free-tools" className="text-zinc-500 hover:text-emerald-400 transition-colors">Free Tools</Link></li>
                <li><Link to="/profit-simulator" className="text-zinc-500 hover:text-emerald-400 transition-colors">Profit Simulator</Link></li>
                <li><Link to="/product-quiz" className="text-zinc-500 hover:text-emerald-400 transition-colors">Product Quiz</Link></li>
                <li><Link to="/sample-product-analysis" className="text-zinc-500 hover:text-emerald-400 transition-colors">Sample Analysis</Link></li>
                <li><Link to="/changelog" className="text-zinc-500 hover:text-emerald-400 transition-colors">Changelog</Link></li>
                <li><Link to="/pricing" className="text-zinc-500 hover:text-emerald-400 transition-colors">Pricing</Link></li>
              </ul>
            </div>

            {/* Solutions */}
            <div>
              <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-3">Solutions</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/for-shopify" className="text-zinc-500 hover:text-emerald-400 transition-colors">For Shopify Sellers</Link></li>
                <li><Link to="/for-amazon-uk" className="text-zinc-500 hover:text-emerald-400 transition-colors">For Amazon UK</Link></li>
                <li><Link to="/for-tiktok-shop-uk" className="text-zinc-500 hover:text-emerald-400 transition-colors">For TikTok Shop UK</Link></li>
                <li><Link to="/uk-product-research" className="text-zinc-500 hover:text-emerald-400 transition-colors">UK Product Research</Link></li>
                <li><Link to="/dropshipping-product-research-uk" className="text-zinc-500 hover:text-emerald-400 transition-colors">UK Dropshipping</Link></li>
                <li><Link to="/winning-products-uk" className="text-zinc-500 hover:text-emerald-400 transition-colors">Winning Products UK</Link></li>
              </ul>
            </div>

            {/* Compare */}
            <div>
              <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-3">Compare</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/compare/jungle-scout-vs-trendscout" className="text-zinc-500 hover:text-emerald-400 transition-colors">vs Jungle Scout</Link></li>
                <li><Link to="/compare/sell-the-trend-vs-trendscout" className="text-zinc-500 hover:text-emerald-400 transition-colors">vs Sell The Trend</Link></li>
                <li><Link to="/compare/minea-vs-trendscout" className="text-zinc-500 hover:text-emerald-400 transition-colors">vs Minea</Link></li>
                <li><Link to="/compare/helium-10-vs-trendscout" className="text-zinc-500 hover:text-emerald-400 transition-colors">vs Helium 10</Link></li>
                <li><Link to="/compare/ecomhunt-vs-trendscout" className="text-zinc-500 hover:text-emerald-400 transition-colors">vs Ecomhunt</Link></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-3">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/about" className="text-zinc-500 hover:text-emerald-400 transition-colors">About</Link></li>
                <li><Link to="/contact" className="text-zinc-500 hover:text-emerald-400 transition-colors">Contact</Link></li>
                <li><Link to="/blog" className="text-zinc-500 hover:text-emerald-400 transition-colors">Blog</Link></li>
                <li><Link to="/help" className="text-zinc-500 hover:text-emerald-400 transition-colors">Help Centre</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-white/[0.06] pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-xs text-zinc-600">&copy; {new Date().getFullYear()} TrendScout. All rights reserved.</p>
            <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-zinc-600">
              <Link to="/privacy" className="hover:text-zinc-400 transition-colors">Privacy Policy</Link>
              <Link to="/terms" className="hover:text-zinc-400 transition-colors">Terms of Service</Link>
              <Link to="/cookie-policy" className="hover:text-zinc-400 transition-colors">Cookies</Link>
              <Link to="/refund-policy" className="hover:text-zinc-400 transition-colors">Refunds</Link>
              <a href="mailto:info@trendscout.click" className="hover:text-zinc-400 transition-colors">info@trendscout.click</a>
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
