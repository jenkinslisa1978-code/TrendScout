import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  CheckCircle2, Circle, TrendingUp, Eye, Sparkles, Bookmark,
  ArrowRight, X, Rocket,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const CHECKLIST_STEPS = [
  {
    id: 'browse_trending',
    title: 'Browse trending products',
    description: 'Explore the product feed to see what\'s hot right now',
    icon: TrendingUp,
    link: '/discover',
    linkText: 'Browse Products',
  },
  {
    id: 'analyse_product',
    title: 'Analyse a product',
    description: 'Click into a product to see the full trend analysis',
    icon: Eye,
    link: '/discover',
    linkText: 'Find a Product',
  },
  {
    id: 'generate_ads',
    title: 'Generate ad ideas',
    description: 'Use the AI ad generator to create TikTok ad concepts',
    icon: Sparkles,
    link: '/discover',
    linkText: 'Try Ad Generator',
  },
  {
    id: 'save_product',
    title: 'Save a product',
    description: 'Save a product to your workspace for later',
    icon: Bookmark,
    link: '/discover',
    linkText: 'Save a Product',
  },
];

export default function OnboardingChecklist() {
  const { user } = useAuth();
  const [completed, setCompleted] = useState({});
  const [dismissed, setDismissed] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) { setLoading(false); return; }
    // Load checklist progress from localStorage
    const key = `ts_checklist_${user.id}`;
    const stored = localStorage.getItem(key);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed.dismissed) { setDismissed(true); }
      setCompleted(parsed.completed || {});
    }
    setLoading(false);
  }, [user]);

  // Auto-detect completions
  useEffect(() => {
    if (!user || dismissed) return;
    const key = `ts_checklist_${user.id}`;

    // Check workspace for saved products
    fetch(`${API_URL}/api/workspace/products`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('ts_token')}` },
    })
      .then(r => r.json())
      .then(data => {
        if (data.count > 0) {
          setCompleted(prev => {
            const next = { ...prev, save_product: true };
            localStorage.setItem(key, JSON.stringify({ completed: next, dismissed: false }));
            return next;
          });
        }
      })
      .catch(() => {});
  }, [user, dismissed]);

  const markComplete = (stepId) => {
    if (!user) return;
    const key = `ts_checklist_${user.id}`;
    setCompleted(prev => {
      const next = { ...prev, [stepId]: true };
      localStorage.setItem(key, JSON.stringify({ completed: next, dismissed: false }));
      return next;
    });
  };

  const handleDismiss = () => {
    if (!user) return;
    const key = `ts_checklist_${user.id}`;
    localStorage.setItem(key, JSON.stringify({ completed, dismissed: true }));
    setDismissed(true);
  };

  if (loading || dismissed) return null;

  const completedCount = Object.values(completed).filter(Boolean).length;
  const allDone = completedCount === CHECKLIST_STEPS.length;
  const progressPercent = (completedCount / CHECKLIST_STEPS.length) * 100;

  if (allDone) return null;

  return (
    <Card className="border border-indigo-100 shadow-md bg-gradient-to-r from-indigo-50/50 via-white to-violet-50/50 overflow-hidden" data-testid="onboarding-checklist">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-sm">
              <Rocket className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-manrope font-bold text-slate-900 text-base">Get started with TrendScout</h3>
              <p className="text-xs text-slate-500 mt-0.5">Complete these steps to unlock your first winning product</p>
            </div>
          </div>
          <button
            onClick={handleDismiss}
            className="text-slate-400 hover:text-slate-600 transition-colors p-1"
            data-testid="dismiss-checklist"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center gap-3 mb-4">
          <Progress value={progressPercent} className="h-2 flex-1" />
          <span className="text-xs font-medium text-slate-500 whitespace-nowrap">{completedCount}/{CHECKLIST_STEPS.length}</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {CHECKLIST_STEPS.map((step) => {
            const Icon = step.icon;
            const isDone = completed[step.id];
            return (
              <div
                key={step.id}
                className={`flex flex-col justify-between rounded-xl border p-4 transition-all duration-300 ${
                  isDone
                    ? 'border-emerald-200 bg-emerald-50/50'
                    : 'border-slate-200 bg-white hover:border-indigo-200 hover:shadow-sm'
                }`}
                data-testid={`checklist-step-${step.id}`}
              >
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {isDone ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
                    ) : (
                      <Circle className="h-5 w-5 text-slate-300 flex-shrink-0" />
                    )}
                    <span className={`font-medium text-sm ${isDone ? 'text-emerald-700 line-through' : 'text-slate-800'}`}>
                      {step.title}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 ml-7">{step.description}</p>
                </div>
                {!isDone && (
                  <Link
                    to={step.link}
                    onClick={() => markComplete(step.id)}
                    className="mt-3 ml-7"
                  >
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs text-indigo-600 border-indigo-200 hover:bg-indigo-50"
                      data-testid={`checklist-action-${step.id}`}
                    >
                      {step.linkText}
                      <ArrowRight className="ml-1 h-3 w-3" />
                    </Button>
                  </Link>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
