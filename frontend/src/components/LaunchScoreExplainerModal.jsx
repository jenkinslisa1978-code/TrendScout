/**
 * Launch Score Explainer Modal
 * 
 * Provides a detailed, educational breakdown of how a product's Launch Score
 * was calculated. Shows component scores, weights, contributions, and
 * plain-English explanations to build user trust and understanding.
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import {
  Rocket,
  TrendingUp,
  AlertTriangle,
  XCircle,
  DollarSign,
  Users,
  Megaphone,
  Truck,
  Flame,
  Info,
  Lightbulb,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { API_URL } from '@/lib/config';

// Component icons mapping
const COMPONENT_ICONS = {
  trend: Flame,
  margin: DollarSign,
  competition: Users,
  ad_activity: Megaphone,
  supplier_demand: Truck
};

// Score level colors
const getScoreColor = (score) => {
  if (score >= 70) return { bg: 'bg-green-500', text: 'text-green-600', fill: 'bg-green-100' };
  if (score >= 50) return { bg: 'bg-blue-500', text: 'text-blue-600', fill: 'bg-blue-100' };
  if (score >= 30) return { bg: 'bg-amber-500', text: 'text-amber-600', fill: 'bg-amber-100' };
  return { bg: 'bg-red-500', text: 'text-red-600', fill: 'bg-red-100' };
};

// Launch label styling
const getLaunchLabelStyle = (label) => {
  const styles = {
    strong_launch: { bg: 'bg-green-500', badge: 'bg-green-50 text-green-700 border-green-200', icon: Rocket, text: 'Strong Launch Opportunity' },
    promising: { bg: 'bg-blue-500', badge: 'bg-blue-50 text-blue-700 border-blue-200', icon: TrendingUp, text: 'Promising' },
    risky: { bg: 'bg-amber-500', badge: 'bg-amber-50 text-amber-700 border-amber-200', icon: AlertTriangle, text: 'Risky' },
    avoid: { bg: 'bg-red-500', badge: 'bg-red-50 text-red-700 border-red-200', icon: XCircle, text: 'Avoid' }
  };
  return styles[label] || styles.risky;
};

// Component breakdown item
function ComponentBreakdown({ component }) {
  const Icon = COMPONENT_ICONS[component.key] || Info;
  const colors = getScoreColor(component.raw_score);
  
  return (
    <div className="p-4 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${colors.fill}`}>
            <Icon className={`h-5 w-5 ${colors.text}`} />
          </div>
          <div>
            <h4 className="font-semibold text-slate-900">{component.name}</h4>
            <p className="text-xs text-slate-500">Weight: {component.weight_percent}</p>
          </div>
        </div>
        <div className="text-right">
          <div className={`font-mono text-2xl font-bold ${colors.text}`}>
            {component.raw_score}
          </div>
          <div className="text-xs text-slate-500">
            +{component.contribution} pts
          </div>
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="mb-3">
        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
          <div 
            className={`h-full ${colors.bg} transition-all duration-500`}
            style={{ width: `${component.raw_score}%` }}
          />
        </div>
      </div>
      
      {/* Explanation */}
      <p className="text-sm text-slate-600 leading-relaxed">
        {component.explanation}
      </p>
      
      {/* Impact badge */}
      <div className="mt-2">
        <Badge 
          variant="outline" 
          className={`text-xs ${
            component.impact === 'positive' ? 'bg-green-50 text-green-700 border-green-200' :
            component.impact === 'neutral' ? 'bg-slate-50 text-slate-600 border-slate-200' :
            'bg-red-50 text-red-700 border-red-200'
          }`}
        >
          {component.impact === 'positive' ? 'Helping score' : 
           component.impact === 'neutral' ? 'Neutral impact' : 'Hurting score'}
        </Badge>
      </div>
    </div>
  );
}

// Main modal component
export default function LaunchScoreExplainerModal({ 
  isOpen, 
  onClose, 
  productId,
  productName = null,
  launchScore = null 
}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && productId) {
      fetchBreakdown();
    }
  }, [isOpen, productId]);

  const fetchBreakdown = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/products/${productId}/launch-score-breakdown`);
      if (!response.ok) {
        throw new Error('Failed to load score breakdown');
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError('Failed to load score breakdown');
      console.error('Launch score breakdown error:', err);
    } finally {
      setLoading(false);
    }
  };

  const labelStyle = data ? getLaunchLabelStyle(data.launch_label) : getLaunchLabelStyle('risky');
  const LabelIcon = labelStyle.icon;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3 text-xl">
            <div className={`p-2 rounded-lg ${labelStyle.bg}`}>
              <LabelIcon className="h-5 w-5 text-white" />
            </div>
            Launch Score Explained
          </DialogTitle>
          <DialogDescription>
            Understanding how {productName || 'this product'} scored {launchScore || data?.launch_score || '—'}
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
            <span className="ml-3 text-slate-600">Analyzing score breakdown...</span>
          </div>
        ) : error ? (
          <div className="text-center py-8 text-red-600">
            <AlertCircle className="h-8 w-8 mx-auto mb-2" />
            {error}
          </div>
        ) : data ? (
          <div className="space-y-6 mt-4">
            {/* Overall Score Header */}
            <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200">
              <div>
                <p className="text-sm text-slate-500 mb-1">Final Launch Score</p>
                <div className="flex items-center gap-3">
                  <span className={`font-mono text-4xl font-bold ${
                    data.launch_score >= 80 ? 'text-green-600' :
                    data.launch_score >= 60 ? 'text-blue-600' :
                    data.launch_score >= 40 ? 'text-amber-600' : 'text-red-600'
                  }`}>
                    {data.launch_score}
                  </span>
                  <Badge className={`${labelStyle.badge} border text-sm py-1 px-3`}>
                    {labelStyle.text}
                  </Badge>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-500 mb-1">Score Range</p>
                <div className="flex gap-1">
                  <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-700">80-100</span>
                  <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-700">60-79</span>
                  <span className="text-xs px-2 py-1 rounded bg-amber-100 text-amber-700">40-59</span>
                  <span className="text-xs px-2 py-1 rounded bg-red-100 text-red-700">0-39</span>
                </div>
              </div>
            </div>

            {/* Formula */}
            <div className="p-4 rounded-lg bg-indigo-50 border border-indigo-100">
              <div className="flex items-center gap-2 mb-2">
                <Info className="h-4 w-4 text-indigo-600" />
                <span className="text-sm font-medium text-indigo-900">How It's Calculated</span>
              </div>
              <p className="text-xs text-indigo-700 font-mono">{data.formula.description}</p>
              <p className="text-xs text-indigo-600 mt-1 font-mono">{data.formula.breakdown}</p>
            </div>

            {/* Component Breakdown */}
            <div>
              <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                <span>Score Components</span>
                <span className="text-xs text-slate-500 font-normal">(sorted by contribution)</span>
              </h3>
              <div className="grid gap-3">
                {data.components.map((component) => (
                  <ComponentBreakdown key={component.key} component={component} />
                ))}
              </div>
            </div>

            <Separator />

            {/* Summary Section */}
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900">Analysis Summary</h3>
              
              {/* Rating Explanation */}
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                <p className="text-sm text-slate-700 leading-relaxed">
                  {data.summary.rating_explanation}
                </p>
              </div>

              {/* Strengths */}
              {data.summary.strengths.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-green-700 mb-2 flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    Key Strengths
                  </h4>
                  <div className="space-y-2">
                    {data.summary.strengths.map((strength, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-green-50 border border-green-100">
                        <span className="font-mono text-sm font-bold text-green-600">{strength.score}</span>
                        <div>
                          <p className="text-sm font-medium text-green-800">{strength.name}</p>
                          <p className="text-xs text-green-600">{strength.explanation}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Weaknesses */}
              {data.summary.weaknesses.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-amber-700 mb-2 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Areas of Concern
                  </h4>
                  <div className="space-y-2">
                    {data.summary.weaknesses.map((weakness, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-amber-50 border border-amber-100">
                        <span className="font-mono text-sm font-bold text-amber-600">{weakness.score}</span>
                        <div>
                          <p className="text-sm font-medium text-amber-800">{weakness.name}</p>
                          <p className="text-xs text-amber-600">{weakness.explanation}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Improvement Suggestions */}
              {data.summary.improvements.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-indigo-700 mb-2 flex items-center gap-2">
                    <Lightbulb className="h-4 w-4" />
                    What Would Improve This Score
                  </h4>
                  <div className="space-y-2">
                    {data.summary.improvements.map((improvement, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-indigo-50 border border-indigo-100">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-indigo-800">{improvement.component}</span>
                          <span className="text-xs text-indigo-600">(currently {improvement.current_score})</span>
                        </div>
                        <p className="text-xs text-indigo-600">{improvement.suggestion}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Educational Footer */}
            <div className="p-4 rounded-lg bg-slate-100 border border-slate-200">
              <h4 className="text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
                <Info className="h-4 w-4" />
                Understanding Launch Scores
              </h4>
              <ul className="text-xs text-slate-600 space-y-1">
                <li>• <strong>80-100:</strong> Excellent conditions - strong candidates for immediate launch</li>
                <li>• <strong>60-79:</strong> Good potential - worth testing with small initial orders</li>
                <li>• <strong>40-59:</strong> Proceed carefully - significant risks to consider</li>
                <li>• <strong>0-39:</strong> High risk - look for better alternatives</li>
              </ul>
            </div>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

// Export a trigger button component for easy integration
export function ExplainScoreButton({ 
  productId, 
  productName, 
  launchScore,
  variant = 'icon', // 'icon', 'button', 'text'
  className = ''
}) {
  const [isOpen, setIsOpen] = useState(false);

  if (variant === 'icon') {
    return (
      <>
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsOpen(true);
          }}
          className={`p-1 rounded-full hover:bg-slate-100 transition-colors ${className}`}
          title="Explain this score"
          data-testid={`explain-score-${productId}`}
        >
          <Info className="h-4 w-4 text-slate-400 hover:text-indigo-600" />
        </button>
        <LaunchScoreExplainerModal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          productId={productId}
          productName={productName}
          launchScore={launchScore}
        />
      </>
    );
  }

  if (variant === 'text') {
    return (
      <>
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsOpen(true);
          }}
          className={`text-xs text-indigo-600 hover:text-indigo-700 hover:underline ${className}`}
          data-testid={`explain-score-${productId}`}
        >
          Why this score?
        </button>
        <LaunchScoreExplainerModal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          productId={productId}
          productName={productName}
          launchScore={launchScore}
        />
      </>
    );
  }

  // Button variant
  return (
    <>
      <button
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setIsOpen(true);
        }}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors ${className}`}
        data-testid={`explain-score-${productId}`}
      >
        <Info className="h-4 w-4" />
        Explain Score
      </button>
      <LaunchScoreExplainerModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        productId={productId}
        productName={productName}
        launchScore={launchScore}
      />
    </>
  );
}
