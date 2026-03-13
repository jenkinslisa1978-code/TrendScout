import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Zap, ArrowRight, Crown } from 'lucide-react';
import api from '@/lib/api';
import { useSubscription } from '@/hooks/useSubscription';

export default function DailyUsageBanner() {
  const { isFree, isStarter, plan } = useSubscription();
  const [usage, setUsage] = useState(null);

  useEffect(() => {
    if (!isFree && !isStarter) return;
    api.get('/api/user/daily-usage')
      .then(res => setUsage(res.data))
      .catch(() => {});
  }, [isFree, isStarter]);

  if (!usage || usage.is_unlimited) return null;

  const { daily_limit, insights_used, remaining } = usage;
  const pct = Math.min(100, (insights_used / daily_limit) * 100);
  const isExhausted = remaining <= 0;

  return (
    <div
      className={`rounded-xl border px-4 py-3 flex items-center justify-between gap-4 transition-all ${
        isExhausted
          ? 'bg-gradient-to-r from-rose-50 to-orange-50 border-rose-200'
          : 'bg-gradient-to-r from-slate-50 to-indigo-50/50 border-slate-200'
      }`}
      data-testid="daily-usage-banner"
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className={`p-1.5 rounded-lg ${isExhausted ? 'bg-rose-100' : 'bg-indigo-100'}`}>
          <Zap className={`h-4 w-4 ${isExhausted ? 'text-rose-500' : 'text-indigo-500'}`} />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-800">
            {isExhausted
              ? 'Daily insight limit reached'
              : `${remaining} insight${remaining !== 1 ? 's' : ''} remaining today`}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <div className="w-24 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  isExhausted ? 'bg-rose-500' : pct > 60 ? 'bg-amber-500' : 'bg-indigo-500'
                }`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-xs text-slate-500">{insights_used}/{daily_limit}</span>
          </div>
        </div>
      </div>

      {isExhausted && (
        <Link to="/pricing">
          <Button
            size="sm"
            className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold rounded-lg whitespace-nowrap shadow-sm"
            data-testid="usage-upgrade-btn"
          >
            <Crown className="h-3.5 w-3.5 mr-1.5" />
            Upgrade
          </Button>
        </Link>
      )}
    </div>
  );
}
