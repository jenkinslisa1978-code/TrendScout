import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Rocket, Store, Megaphone, ClipboardCheck, BarChart3,
  ChevronDown, ChevronUp, Users, PoundSterling, Clock,
} from 'lucide-react';

const STEP_ICONS = [Rocket, Store, Megaphone, Rocket, BarChart3];

export default function ProductLaunchPlaybook({ productId }) {
  const [data, setData] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    const token = localStorage.getItem('trendscout_token');
    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/launch-playbook/${productId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [productId]);

  if (loading || !data) return null;

  return (
    <Card className="border-slate-200 shadow-sm" data-testid="launch-playbook">
      <CardHeader
        className="cursor-pointer pb-3 hover:bg-slate-50/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-manrope flex items-center gap-2">
            <ClipboardCheck className="h-5 w-5 text-indigo-500" />
            Launch Playbook
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs text-slate-500">{data.launch_steps?.length || 5} steps</Badge>
            {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
          </div>
        </div>
        {!expanded && (
          <p className="text-sm text-slate-500 mt-1">Step-by-step guide to launch {data.product_name}</p>
        )}
      </CardHeader>

      {expanded && (
        <CardContent className="pt-0 space-y-5">
          {/* Steps */}
          <div className="space-y-3">
            {data.launch_steps?.map((step, i) => {
              const Icon = STEP_ICONS[i] || Rocket;
              return (
                <div key={i} className="flex gap-3" data-testid={`playbook-step-${step.step}`}>
                  <div className="flex flex-col items-center">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-600">
                      <span className="text-xs font-bold">{step.step}</span>
                    </div>
                    {i < data.launch_steps.length - 1 && <div className="w-px h-full bg-indigo-100 mt-1" />}
                  </div>
                  <div className="pb-3 flex-1">
                    <h4 className="text-sm font-semibold text-slate-800">{step.title}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">{step.description}</p>
                    <div className="flex items-center gap-1 mt-1">
                      <Clock className="h-3 w-3 text-slate-300" />
                      <span className="text-[10px] text-slate-400">{step.estimated_time}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Ad Angles */}
          <div>
            <h4 className="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
              <Megaphone className="h-4 w-4 text-purple-500" />
              Ad Creative Angles
            </h4>
            <div className="grid grid-cols-3 gap-2">
              {data.ad_angles?.map((angle, i) => (
                <div key={i} className="bg-purple-50/50 border border-purple-100 rounded-lg p-3" data-testid={`ad-angle-${i + 1}`}>
                  <p className="text-xs font-semibold text-purple-800">Ad {i + 1} — {angle.angle}</p>
                  <p className="text-[10px] text-purple-600 mt-1">{angle.description}</p>
                  <p className="text-[10px] text-purple-400 mt-1 italic">"{angle.example}"</p>
                </div>
              ))}
            </div>
          </div>

          {/* Audiences */}
          <div>
            <h4 className="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-500" />
              Target Audiences
            </h4>
            <div className="grid grid-cols-3 gap-2">
              {data.audience_suggestions?.map((aud, i) => (
                <div key={i} className="bg-blue-50/50 border border-blue-100 rounded-lg p-2.5">
                  <p className="text-xs font-semibold text-blue-800">{aud.name}</p>
                  <p className="text-[10px] text-blue-500">Age: {aud.age}</p>
                  <p className="text-[10px] text-blue-400">{aud.interests}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Budget */}
          <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-emerald-800 flex items-center gap-2 mb-2">
              <PoundSterling className="h-4 w-4" />
              Testing Budget
            </h4>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div>
                <p className="text-lg font-bold text-emerald-700">{data.testing_budget?.total_test_budget}</p>
                <p className="text-[10px] text-emerald-500">Total budget</p>
              </div>
              <div>
                <p className="text-lg font-bold text-emerald-700">{data.testing_budget?.creatives}</p>
                <p className="text-[10px] text-emerald-500">Ad creatives</p>
              </div>
              <div>
                <p className="text-lg font-bold text-emerald-700">{data.testing_budget?.test_period}</p>
                <p className="text-[10px] text-emerald-500">Test period</p>
              </div>
            </div>
            <p className="text-[10px] text-emerald-500 mt-2 text-center">{data.testing_budget?.note}</p>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
