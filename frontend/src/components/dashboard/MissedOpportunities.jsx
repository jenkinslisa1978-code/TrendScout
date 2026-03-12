import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Lock, TrendingUp, ArrowRight, Sparkles } from 'lucide-react';
import { useSubscription } from '@/hooks/useSubscription';
import { apiGet } from '@/lib/api';

export default function MissedOpportunities() {
  const navigate = useNavigate();
  const { plan, isFree, isStarter } = useSubscription();
  const [opportunities, setOpportunities] = useState([]);

  useEffect(() => {
    if (!isFree && !isStarter) return;
    (async () => {
      try {
        const res = await apiGet('/api/products?sortBy=trend_score&sortOrder=desc&limit=8');
        if (res.ok) {
          const data = await res.json();
          const products = data.data || [];
          // Show products beyond the user's plan limit as "missed"
          const limit = isFree ? 3 : 5;
          setOpportunities(products.slice(limit, limit + 3));
        }
      } catch (e) { /* silent */ }
    })();
  }, [isFree, isStarter]);

  if (!isFree && !isStarter) return null;
  if (opportunities.length === 0) return null;

  const upgradePlan = isFree ? 'Starter' : 'Pro';

  return (
    <Card className="border-0 shadow-md overflow-hidden" data-testid="missed-opportunities">
      <CardHeader className="py-3 px-4 bg-gradient-to-r from-violet-600 to-indigo-600">
        <CardTitle className="text-sm font-semibold text-white flex items-center gap-2">
          <Lock className="h-4 w-4" />
          Missed Opportunities
          <Badge className="ml-auto bg-white/20 text-white border-white/30 text-[10px]">
            {upgradePlan} feature
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        {opportunities.map((p, i) => (
          <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl relative overflow-hidden">
            {/* Blur overlay */}
            <div className="absolute inset-0 backdrop-blur-[2px] bg-white/30 z-10 flex items-center justify-center">
              <Lock className="h-4 w-4 text-slate-400" />
            </div>
            <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
              <TrendingUp className="h-5 w-5 text-indigo-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-800 truncate">Product detected</p>
              <p className="text-[10px] text-slate-500">
                Launch Score: {p.win_score || Math.round((p.trend_score || 0) * 0.3 + (p.early_trend_score || 0) * 0.3 + (p.success_probability || 0) * 0.4)} &middot; {p.early_trend_label || 'Rising'}
              </p>
            </div>
            <Badge className="bg-violet-100 text-violet-700 border-violet-200 text-[10px] z-0">
              Locked
            </Badge>
          </div>
        ))}

        <div className="text-center pt-1 space-y-2">
          <p className="text-xs text-slate-500">
            <Sparkles className="h-3 w-3 inline mr-1" />
            TrendScout detected <strong>{opportunities.length} additional opportunities</strong> available on {upgradePlan}
          </p>
          <Button
            size="sm"
            className="bg-indigo-600 hover:bg-indigo-700 text-white"
            onClick={() => navigate('/pricing')}
            data-testid="upgrade-cta-btn"
          >
            Upgrade to {upgradePlan}
            <ArrowRight className="ml-1 h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
