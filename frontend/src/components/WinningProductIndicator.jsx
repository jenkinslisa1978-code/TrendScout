import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, AlertTriangle, Target, PoundSterling } from 'lucide-react';

export default function WinningProductIndicator({ product }) {
  if (!product) return null;

  const score = product.launch_score || product.trend_score || 0;
  const competition = (product.competition_level || 'moderate').toLowerCase();
  const tiktokViews = product.tiktok_views || 0;
  const margin = (product.estimated_retail_price || 0) - (product.supplier_cost || 0);

  // Determine verdict
  let verdict, verdictColor, verdictBg;
  if (score >= 75) {
    verdict = 'Strong candidate for testing';
    verdictColor = 'text-emerald-700';
    verdictBg = 'bg-emerald-50 border-emerald-200';
  } else if (score >= 50) {
    verdict = 'Good candidate for testing';
    verdictColor = 'text-blue-700';
    verdictBg = 'bg-blue-50 border-blue-200';
  } else if (score >= 30) {
    verdict = 'Worth investigating further';
    verdictColor = 'text-amber-700';
    verdictBg = 'bg-amber-50 border-amber-200';
  } else {
    verdict = 'High risk — proceed with caution';
    verdictColor = 'text-red-700';
    verdictBg = 'bg-red-50 border-red-200';
  }

  // Build reasons and risks
  const reasons = [];
  const risks = [];

  if (tiktokViews > 100000) reasons.push('Strong social media traction');
  else if (tiktokViews > 10000) reasons.push('Growing social media interest');
  else risks.push('Limited social media traction');

  if (margin > 15) reasons.push('Healthy profit margins');
  else if (margin > 5) reasons.push('Moderate profit margins');
  else risks.push('Tight profit margins');

  if (competition === 'low') reasons.push('Low competition — good entry window');
  else if (competition === 'moderate') reasons.push('Moderate competition');
  else risks.push('High competition — requires strong ad creative');

  if (score >= 60) reasons.push('Strong overall product score');
  if (product.search_growth > 50) reasons.push('Strong search growth');
  else if (product.search_growth < 20) risks.push('Flat search growth');

  // Budget recommendation
  let budgetLow, budgetHigh;
  if (margin > 15) { budgetLow = 50; budgetHigh = 80; }
  else if (margin > 8) { budgetLow = 40; budgetHigh = 60; }
  else { budgetLow = 20; budgetHigh = 40; }

  // Score ring color
  const ringColor = score >= 75 ? 'text-emerald-500' : score >= 50 ? 'text-blue-500' : score >= 30 ? 'text-amber-500' : 'text-red-500';
  const ringTrack = score >= 75 ? 'stroke-emerald-100' : score >= 50 ? 'stroke-blue-100' : score >= 30 ? 'stroke-amber-100' : 'stroke-red-100';
  const ringStroke = score >= 75 ? 'stroke-emerald-500' : score >= 50 ? 'stroke-blue-500' : score >= 30 ? 'stroke-amber-500' : 'stroke-red-500';

  const circumference = 2 * Math.PI * 36;
  const offset = circumference - (score / 100) * circumference;

  return (
    <Card className={`border ${verdictBg}`} data-testid="winning-product-indicator">
      <CardContent className="p-5">
        <div className="flex items-start gap-5">
          {/* Score Ring */}
          <div className="relative flex-shrink-0">
            <svg width="88" height="88" viewBox="0 0 88 88">
              <circle cx="44" cy="44" r="36" fill="none" strokeWidth="6" className={ringTrack} />
              <circle
                cx="44" cy="44" r="36" fill="none" strokeWidth="6"
                className={ringStroke}
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                strokeLinecap="round"
                transform="rotate(-90 44 44)"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-xl font-bold ${ringColor}`} data-testid="product-score-value">{score}</span>
              <span className="text-[9px] text-slate-400 font-medium">/100</span>
            </div>
          </div>

          {/* Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-base font-bold text-slate-900 font-manrope">Product Score</h3>
              <Badge className={`${verdictBg} ${verdictColor} text-[10px]`}>{verdict}</Badge>
            </div>

            {/* Reasons */}
            {reasons.length > 0 && (
              <div className="mt-2">
                <div className="flex items-center gap-1 mb-1">
                  <TrendingUp className="h-3 w-3 text-emerald-500" />
                  <span className="text-[10px] font-semibold text-emerald-700 uppercase">Strengths</span>
                </div>
                <ul className="space-y-0.5">
                  {reasons.map((r, i) => (
                    <li key={i} className="text-xs text-emerald-600 flex items-center gap-1.5">
                      <span className="w-1 h-1 rounded-full bg-emerald-400" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Risks */}
            {risks.length > 0 && (
              <div className="mt-2">
                <div className="flex items-center gap-1 mb-1">
                  <AlertTriangle className="h-3 w-3 text-amber-500" />
                  <span className="text-[10px] font-semibold text-amber-700 uppercase">Risks</span>
                </div>
                <ul className="space-y-0.5">
                  {risks.map((r, i) => (
                    <li key={i} className="text-xs text-amber-600 flex items-center gap-1.5">
                      <span className="w-1 h-1 rounded-full bg-amber-400" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Budget */}
            <div className="mt-3 flex items-center gap-2">
              <PoundSterling className="h-3.5 w-3.5 text-slate-400" />
              <span className="text-xs text-slate-600">
                Suggested test budget: <strong className="text-slate-800">£{budgetLow} – £{budgetHigh}</strong>
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
