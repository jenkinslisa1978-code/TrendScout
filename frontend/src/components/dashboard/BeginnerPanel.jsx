import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, BarChart3, ShoppingBag, Megaphone, ArrowRight, X } from 'lucide-react';

export default function BeginnerPanel({ onDismiss }) {
  const navigate = useNavigate();
  const dismissed = localStorage.getItem('trendscout_beginner_dismissed');
  if (dismissed) return null;

  const steps = [
    { icon: Search, label: 'Find a product', desc: 'Browse products gaining traction online', href: '/discover', color: 'bg-indigo-100 text-indigo-600' },
    { icon: BarChart3, label: 'Check the launch score', desc: 'See if a product is worth testing with real data', href: '/trending-products', color: 'bg-violet-100 text-violet-600' },
    { icon: ShoppingBag, label: 'Import to Shopify', desc: 'Connect your store and export products', href: '/settings/connections', color: 'bg-emerald-100 text-emerald-600' },
    { icon: Megaphone, label: 'Test ads', desc: 'Get ad ideas and launch a test campaign', href: '/ad-tests', color: 'bg-amber-100 text-amber-600' },
  ];

  const handleDismiss = () => {
    localStorage.setItem('trendscout_beginner_dismissed', 'true');
    if (onDismiss) onDismiss();
  };

  return (
    <Card className="border-indigo-200 bg-gradient-to-br from-indigo-50 to-white shadow-sm" data-testid="beginner-panel">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900 font-manrope">New to TrendScout?</h3>
            <p className="text-xs text-slate-500 mt-0.5">Follow this simple process.</p>
          </div>
          <button onClick={handleDismiss} className="text-slate-400 hover:text-slate-600" data-testid="beginner-dismiss">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {steps.map(({ icon: Icon, label, desc, href, color }, i) => (
            <button
              key={i}
              onClick={() => navigate(href)}
              className="bg-white rounded-lg border border-slate-100 p-3 text-left hover:border-indigo-200 hover:shadow-sm transition-all group"
              data-testid={`beginner-step-${i + 1}`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div className={`flex h-6 w-6 items-center justify-center rounded-md ${color}`}>
                  <Icon className="h-3.5 w-3.5" />
                </div>
                <span className="text-xs font-semibold text-slate-800">Step {i + 1}</span>
              </div>
              <p className="text-xs font-medium text-slate-700 group-hover:text-indigo-600 transition-colors">{label}</p>
              <p className="text-[10px] text-slate-400 mt-0.5">{desc}</p>
            </button>
          ))}
        </div>

        <Button
          onClick={() => navigate('/discover')}
          className="bg-indigo-600 hover:bg-indigo-700"
          size="sm"
          data-testid="browse-trending-btn"
        >
          Browse Trending Products
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
      </CardContent>
    </Card>
  );
}
