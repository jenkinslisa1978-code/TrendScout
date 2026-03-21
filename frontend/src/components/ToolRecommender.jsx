import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { trackEvent } from '@/services/analytics';
import { ArrowRight, CheckCircle, HelpCircle } from 'lucide-react';

const QUESTIONS = [
  {
    id: 'market',
    text: 'Which market are you selling in?',
    options: [
      { value: 'uk', label: 'UK only' },
      { value: 'us', label: 'US only' },
      { value: 'both', label: 'Both UK and US' },
    ],
  },
  {
    id: 'channels',
    text: 'Which sales channels do you use?',
    options: [
      { value: 'amazon_only', label: 'Amazon only' },
      { value: 'shopify_only', label: 'Shopify only' },
      { value: 'multi', label: 'Multiple (Shopify + Amazon / TikTok)' },
    ],
  },
  {
    id: 'priority',
    text: 'What matters most to you?',
    options: [
      { value: 'uk_data', label: 'UK-specific margin & viability data' },
      { value: 'keyword', label: 'Amazon keyword research depth' },
      { value: 'trends', label: 'Spotting viral trends early' },
    ],
  },
];

function getResult(answers) {
  let tsScore = 0;
  let reason = '';

  // Market
  if (answers.market === 'uk') { tsScore += 40; }
  else if (answers.market === 'us') { tsScore -= 20; }
  else { tsScore += 15; }

  // Channels
  if (answers.channels === 'multi') { tsScore += 30; }
  else if (answers.channels === 'shopify_only') { tsScore += 20; }
  else if (answers.channels === 'amazon_only') { tsScore -= 10; }

  // Priority
  if (answers.priority === 'uk_data') { tsScore += 30; }
  else if (answers.priority === 'trends') { tsScore += 20; }
  else if (answers.priority === 'keyword') { tsScore -= 15; }

  if (tsScore >= 50) {
    reason = 'TrendScout is a strong fit — it is built specifically for UK multi-channel sellers with built-in viability scoring and margin estimation.';
  } else if (tsScore >= 20) {
    reason = 'TrendScout could work well for you. It covers your needs, though another tool may have deeper features in one specific area.';
  } else {
    reason = 'Based on your answers, a US-focused Amazon tool like Jungle Scout may be a better primary fit. However, TrendScout is still useful if you plan to expand into the UK market.';
  }

  return { tsScore: Math.max(0, Math.min(100, tsScore + 50)), reason, recommend: tsScore >= 20 };
}

/**
 * "Which tool is right for me?" — inline interactive recommender for comparison pages.
 */
export default function ToolRecommender() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResult, setShowResult] = useState(false);

  const currentQ = QUESTIONS[step];

  const selectAnswer = (value) => {
    const updated = { ...answers, [currentQ.id]: value };
    setAnswers(updated);
    trackEvent('tool_recommender_answer', { question: currentQ.id, answer: value });

    if (step === QUESTIONS.length - 1) {
      setShowResult(true);
      trackEvent('tool_recommender_complete', { answers: updated });
    } else {
      setStep(step + 1);
    }
  };

  const reset = () => {
    setStep(0);
    setAnswers({});
    setShowResult(false);
  };

  const result = showResult ? getResult(answers) : null;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="tool-recommender">
      <div className="flex items-center gap-2 mb-4">
        <HelpCircle className="h-4.5 w-4.5 text-indigo-600" />
        <h3 className="text-sm font-semibold text-slate-900">Which tool is right for me?</h3>
      </div>

      {!showResult ? (
        <div>
          <p className="text-xs text-slate-500 mb-1">{step + 1} of {QUESTIONS.length}</p>
          <p className="text-sm font-medium text-slate-800 mb-3" data-testid="recommender-question">{currentQ.text}</p>
          <div className="space-y-2">
            {currentQ.options.map((opt) => (
              <button
                key={opt.value}
                onClick={() => selectAnswer(opt.value)}
                className="w-full text-left px-4 py-3 rounded-lg border border-slate-200 text-sm text-slate-700 hover:border-indigo-300 hover:bg-indigo-50/50 transition-all"
                data-testid={`recommender-option-${opt.value}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div data-testid="recommender-result">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className={`h-4 w-4 ${result.recommend ? 'text-emerald-500' : 'text-amber-500'}`} />
            <span className="text-sm font-semibold text-slate-900">
              {result.recommend ? 'TrendScout is a good fit' : 'Consider your options'}
            </span>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed mb-4">{result.reason}</p>
          <div className="flex items-center gap-3">
            {result.recommend && (
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-sm h-9 px-4" data-testid="recommender-signup-cta">
                  Try TrendScout Free <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                </Button>
              </Link>
            )}
            <button onClick={reset} className="text-xs text-slate-500 hover:text-indigo-600 transition-colors" data-testid="recommender-retake">
              Retake
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
