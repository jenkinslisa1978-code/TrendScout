import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Button } from '@/components/ui/button';
import PageMeta, { breadcrumbSchema, webPageSchema } from '@/components/PageMeta';
import { trackEvent, EVENTS } from '@/services/analytics';
import { ArrowRight, ArrowLeft, CheckCircle, Target } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const QUESTIONS = [
  {
    id: 'channel',
    question: 'Where do you mainly sell (or plan to sell)?',
    options: [
      { value: 'shopify', label: 'Shopify / Own website' },
      { value: 'amazon', label: 'Amazon UK' },
      { value: 'tiktok', label: 'TikTok Shop UK' },
      { value: 'multi', label: 'Multiple channels' },
      { value: 'not_started', label: 'Not started yet' },
    ],
  },
  {
    id: 'stage',
    question: 'What stage is your ecommerce business at?',
    options: [
      { value: 'idea', label: 'Just researching ideas' },
      { value: 'first', label: 'Looking for my first product' },
      { value: 'scaling', label: 'Already selling, looking for next products' },
      { value: 'established', label: 'Established store, optimising range' },
    ],
  },
  {
    id: 'challenge',
    question: 'What is your biggest challenge right now?',
    options: [
      { value: 'finding', label: 'Finding products that are not already saturated' },
      { value: 'margins', label: 'Understanding real profit margins after UK costs' },
      { value: 'validation', label: 'Knowing if a product will actually sell in the UK' },
      { value: 'trends', label: 'Spotting trends before competitors do' },
      { value: 'suppliers', label: 'Finding reliable suppliers' },
    ],
  },
  {
    id: 'budget',
    question: 'What is your monthly budget for product research tools?',
    options: [
      { value: 'free', label: 'Free only for now' },
      { value: 'low', label: 'Under £20/month' },
      { value: 'mid', label: '£20-50/month' },
      { value: 'high', label: 'Over £50/month' },
    ],
  },
];

function getRecommendation(answers) {
  const recs = {
    headline: '',
    description: '',
    features: [],
    plan: 'starter',
    planLabel: 'Starter',
    score: 0,
  };

  // Channel-based recommendations
  if (answers.channel === 'multi') {
    recs.features.push('Cross-channel trend detection across Shopify, Amazon, and TikTok');
    recs.score += 85;
  } else if (answers.channel === 'shopify') {
    recs.features.push('Shopify-optimised product discovery with push-to-store');
    recs.score += 78;
  } else if (answers.channel === 'tiktok') {
    recs.features.push('TikTok viral product tracking with UK audience data');
    recs.score += 80;
  } else if (answers.channel === 'amazon') {
    recs.features.push('Amazon UK product opportunity analysis');
    recs.score += 75;
  } else {
    recs.features.push('Guided product discovery for new sellers');
    recs.score += 70;
  }

  // Challenge-based features
  if (answers.challenge === 'finding') {
    recs.features.push('Saturation scoring to filter out overcrowded niches');
  } else if (answers.challenge === 'margins') {
    recs.features.push('UK margin estimation with VAT, shipping, and returns factored in');
  } else if (answers.challenge === 'validation') {
    recs.features.push('UK Product Viability Score — 0-100 rating of commercial potential');
  } else if (answers.challenge === 'trends') {
    recs.features.push('Real-time multi-channel trend signals updated daily');
  } else if (answers.challenge === 'suppliers') {
    recs.features.push('CJ Dropshipping integration with supplier discovery');
  }

  // Stage-based recommendations
  if (answers.stage === 'scaling' || answers.stage === 'established') {
    recs.features.push('Competitor tracking and market intelligence dashboards');
    recs.plan = 'pro';
    recs.planLabel = 'Pro';
    recs.score += 5;
  } else {
    recs.features.push('Free tools and calculators to validate before spending');
  }

  // Budget-based plan
  if (answers.budget === 'free') {
    recs.plan = 'free';
    recs.planLabel = 'Free';
  } else if (answers.budget === 'high') {
    recs.plan = 'elite';
    recs.planLabel = 'Elite';
  }

  recs.score = Math.min(recs.score, 95);

  recs.headline = `TrendScout is a ${recs.score}% match for your needs`;
  recs.description = answers.stage === 'idea' || answers.stage === 'first'
    ? 'Based on your answers, TrendScout can help you find and validate your first UK product opportunity with confidence.'
    : 'Based on your answers, TrendScout can give you a competitive edge with deeper UK market intelligence and cross-channel trend data.';

  return recs;
}

export default function ProductQuizPage() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [email, setEmail] = useState('');
  const [emailSubmitted, setEmailSubmitted] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const currentQ = QUESTIONS[step];
  const isLastQuestion = step === QUESTIONS.length - 1;

  const selectAnswer = (value) => {
    const updated = { ...answers, [currentQ.id]: value };
    setAnswers(updated);
    trackEvent('quiz_answer', { question: currentQ.id, answer: value, step: step + 1 });

    if (isLastQuestion) {
      setShowResults(true);
      trackEvent('quiz_complete', { answers: updated });
    } else {
      setTimeout(() => setStep(step + 1), 150);
    }
  };

  const goBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    if (!email || !email.includes('@')) return;
    try {
      await fetch(`${API_URL}/api/leads/capture`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: 'product_quiz', context: JSON.stringify(answers) }),
      });
    } catch {}
    trackEvent('quiz_email_submit', { answers });
    setEmailSubmitted(true);
  };

  const recommendation = showResults ? getRecommendation(answers) : null;
  const progress = showResults ? 100 : ((step / QUESTIONS.length) * 100);

  return (
    <LandingLayout>
      <PageMeta
        title="Which product research tool is right for you?"
        description="Take our quick quiz to find out if TrendScout is the right product research tool for your UK ecommerce business."
        canonical="/product-quiz"
        schema={[
          webPageSchema('Product Research Tool Quiz', 'Find out which product research approach is right for your UK ecommerce business.', '/product-quiz'),
          breadcrumbSchema([{ name: 'Home', url: '/' }, { name: 'Product Quiz' }]),
        ]}
      />
      <div className="bg-white min-h-[70vh]" data-testid="product-quiz-page">
        {/* Progress bar */}
        <div className="h-1 bg-slate-100">
          <div
            className="h-full bg-indigo-600 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
            data-testid="quiz-progress"
          />
        </div>

        <div className="max-w-xl mx-auto px-6 py-16">
          {!showResults ? (
            <>
              {/* Question */}
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-mono text-slate-400">
                  {step + 1} of {QUESTIONS.length}
                </span>
                {step > 0 && (
                  <button onClick={goBack} className="text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1" data-testid="quiz-back-btn">
                    <ArrowLeft className="h-3 w-3" /> Back
                  </button>
                )}
              </div>
              <h1 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight" data-testid="quiz-question">
                {currentQ.question}
              </h1>
              <div className="mt-8 space-y-3">
                {currentQ.options.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => selectAnswer(opt.value)}
                    className={`w-full text-left px-5 py-4 rounded-xl border transition-all text-sm font-medium ${
                      answers[currentQ.id] === opt.value
                        ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                        : 'border-slate-200 text-slate-700 hover:border-indigo-300 hover:bg-slate-50'
                    }`}
                    data-testid={`quiz-option-${opt.value}`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              {/* Results */}
              <div className="text-center mb-8" data-testid="quiz-results">
                <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-4">
                  <Target className="h-8 w-8 text-indigo-600" />
                </div>
                <h1 className="font-manrope text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                  {recommendation.headline}
                </h1>
                <p className="mt-3 text-base text-slate-600 leading-relaxed max-w-md mx-auto">
                  {recommendation.description}
                </p>
              </div>

              {/* Recommended features */}
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 mb-6">
                <h3 className="text-sm font-semibold text-slate-900 mb-3">What we recommend for you</h3>
                <ul className="space-y-2.5">
                  {recommendation.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-sm text-slate-700">
                      <CheckCircle className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <div className="mt-4 pt-4 border-t border-slate-200">
                  <p className="text-xs text-slate-500">
                    Recommended plan: <span className="font-semibold text-indigo-600">{recommendation.planLabel}</span>
                  </p>
                </div>
              </div>

              {/* Email capture for results */}
              {!emailSubmitted ? (
                <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-6 mb-6" data-testid="quiz-email-capture">
                  <h3 className="text-sm font-semibold text-slate-900 mb-1">Get your personalised report</h3>
                  <p className="text-xs text-slate-500 mb-3">
                    We will email you a detailed breakdown of your quiz results with actionable next steps.
                  </p>
                  <form onSubmit={handleEmailSubmit} className="flex gap-2">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      className="flex-1 min-w-0 rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
                      data-testid="quiz-email-input"
                      required
                    />
                    <Button
                      type="submit"
                      className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-sm px-5 flex-shrink-0"
                      data-testid="quiz-email-submit"
                    >
                      Send Report
                    </Button>
                  </form>
                </div>
              ) : (
                <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 text-center mb-6" data-testid="quiz-email-success">
                  <p className="text-sm font-semibold text-emerald-700">Report sent! Check your inbox.</p>
                </div>
              )}

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Link to="/signup" className="flex-1">
                  <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold h-11" data-testid="quiz-signup-cta">
                    Start Free <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/sample-product-analysis" className="flex-1">
                  <Button variant="outline" className="w-full border-slate-300 text-slate-700 rounded-lg font-medium h-11">
                    See Sample Analysis
                  </Button>
                </Link>
              </div>

              {/* Retake */}
              <button
                onClick={() => { setStep(0); setAnswers({}); setShowResults(false); setEmailSubmitted(false); setEmail(''); }}
                className="block mx-auto mt-6 text-sm text-slate-500 hover:text-indigo-600 transition-colors"
                data-testid="quiz-retake"
              >
                Retake quiz
              </button>
            </>
          )}
        </div>
      </div>
    </LandingLayout>
  );
}
