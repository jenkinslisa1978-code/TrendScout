import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, BarChart3, Megaphone, PoundSterling, ArrowRight, X } from 'lucide-react';

export default function BeginnerPanel({ onDismiss }) {
  const navigate = useNavigate();
  const dismissed = localStorage.getItem('trendscout_beginner_dismissed');
  if (dismissed) return null;

  const steps = [
    { icon: Search, label: 'Browse trending products', desc: 'Find products gaining traction online right now' },
    { icon: BarChart3, label: 'Open a product analysis', desc: 'See if a product is worth testing with real data' },
    { icon: Megaphone, label: 'Check ad ideas', desc: 'Get suggested marketing angles for advertising' },
    { icon: PoundSterling, label: 'Estimate profit', desc: 'Check if a product could be profitable before spending' },
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
            <h3 className="text-base font-bold text-slate-900 font-manrope">New to TrendScout? Start here.</h3>
            <p className="text-xs text-slate-500 mt-0.5">Follow these steps to find your first winning product</p>
          </div>
          <button onClick={handleDismiss} className="text-slate-400 hover:text-slate-600" data-testid="beginner-dismiss">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {steps.map(({ icon: Icon, label, desc }, i) => (
            <div key={i} className="bg-white rounded-lg border border-slate-100 p-3">
              <div className="flex items-center gap-2 mb-1.5">
                <div className="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-100">
                  <Icon className="h-3.5 w-3.5 text-indigo-600" />
                </div>
                <span className="text-xs font-semibold text-slate-800">Step {i + 1}</span>
              </div>
              <p className="text-xs font-medium text-slate-700">{label}</p>
              <p className="text-[10px] text-slate-400 mt-0.5">{desc}</p>
            </div>
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
