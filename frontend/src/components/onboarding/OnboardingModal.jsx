/**
 * OnboardingModal Component
 * 
 * A 5-step onboarding flow for new users.
 * Shown once on first login, dismissible, and persists completion state.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogContent,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  TrendingUp,
  Trophy,
  Eye,
  Store,
  Bell,
  ChevronRight,
  ChevronLeft,
  X,
  Sparkles,
  Target,
  Rocket
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

// Onboarding steps configuration
const ONBOARDING_STEPS = [
  {
    id: 1,
    title: 'Welcome to ViralScout',
    subtitle: 'Your product research companion',
    description: 'ViralScout helps you discover trending products before they go viral, validate opportunities with data-driven insights, and launch winning e-commerce stores.',
    icon: TrendingUp,
    color: 'indigo',
    highlights: [
      'Find trending products early',
      'Analyze market opportunities',
      'Build stores with AI assistance'
    ]
  },
  {
    id: 2,
    title: 'Daily Winning Products',
    subtitle: 'Discover top opportunities',
    description: 'Every day, we analyze thousands of products and surface the top opportunities with the highest launch potential. Check the Dashboard to see today\'s winners.',
    icon: Trophy,
    color: 'amber',
    highlights: [
      'Top products ranked by Launch Score',
      'Updated daily with fresh opportunities',
      'See trend stage and profit margins'
    ],
    action: { label: 'Go to Dashboard', path: '/dashboard' }
  },
  {
    id: 3,
    title: 'Track with Watchlist',
    subtitle: 'Monitor products you love',
    description: 'Found a promising product? Add it to your Watchlist to track price changes, trend movements, and competition over time. Get notified when conditions change.',
    icon: Eye,
    color: 'purple',
    highlights: [
      'Track unlimited products',
      'See changes over time',
      'Get alerts on significant moves'
    ],
    action: { label: 'Browse Products', path: '/discover' }
  },
  {
    id: 4,
    title: 'Create Your Store',
    subtitle: 'Launch in minutes',
    description: 'Ready to sell? Create a complete store concept from any product. We\'ll generate product descriptions, pricing, and everything you need to launch on Shopify.',
    icon: Store,
    color: 'emerald',
    highlights: [
      'AI-generated store content',
      'One-click Shopify export',
      'Professional product pages'
    ],
    action: { label: 'View My Stores', path: '/stores' }
  },
  {
    id: 5,
    title: 'Stay Informed',
    subtitle: 'Reports & Alerts',
    description: 'Get weekly reports with the best opportunities delivered to your inbox. Set up alerts to be notified when high-potential products are detected.',
    icon: Bell,
    color: 'rose',
    highlights: [
      'Weekly winning products report',
      'Monthly market trends analysis',
      'Real-time opportunity alerts'
    ],
    action: { label: 'View Reports', path: '/reports' }
  }
];

// Color configurations
const COLORS = {
  indigo: {
    bg: 'bg-indigo-50',
    icon: 'bg-indigo-100 text-indigo-600',
    button: 'bg-indigo-600 hover:bg-indigo-700',
    progress: 'bg-indigo-600',
    highlight: 'text-indigo-600'
  },
  amber: {
    bg: 'bg-amber-50',
    icon: 'bg-amber-100 text-amber-600',
    button: 'bg-amber-500 hover:bg-amber-600',
    progress: 'bg-amber-500',
    highlight: 'text-amber-600'
  },
  purple: {
    bg: 'bg-purple-50',
    icon: 'bg-purple-100 text-purple-600',
    button: 'bg-purple-600 hover:bg-purple-700',
    progress: 'bg-purple-600',
    highlight: 'text-purple-600'
  },
  emerald: {
    bg: 'bg-emerald-50',
    icon: 'bg-emerald-100 text-emerald-600',
    button: 'bg-emerald-600 hover:bg-emerald-700',
    progress: 'bg-emerald-600',
    highlight: 'text-emerald-600'
  },
  rose: {
    bg: 'bg-rose-50',
    icon: 'bg-rose-100 text-rose-600',
    button: 'bg-rose-500 hover:bg-rose-600',
    progress: 'bg-rose-500',
    highlight: 'text-rose-600'
  }
};

export default function OnboardingModal({ isOpen, onClose }) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [isClosing, setIsClosing] = useState(false);
  
  const step = ONBOARDING_STEPS[currentStep];
  const colors = COLORS[step.color];
  const Icon = step.icon;
  const progress = ((currentStep + 1) / ONBOARDING_STEPS.length) * 100;
  
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === ONBOARDING_STEPS.length - 1;
  
  const handleNext = () => {
    if (isLastStep) {
      completeOnboarding();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };
  
  const handlePrev = () => {
    if (!isFirstStep) {
      setCurrentStep(prev => prev - 1);
    }
  };
  
  const handleSkip = () => {
    completeOnboarding();
  };
  
  const handleAction = () => {
    if (step.action) {
      completeOnboarding();
      navigate(step.action.path);
    }
  };
  
  const completeOnboarding = async () => {
    setIsClosing(true);
    
    try {
      // Mark onboarding as complete in backend
      await api.post('/api/user/complete-onboarding');
    } catch (error) {
      console.error('Failed to save onboarding status:', error);
    }
    
    onClose();
  };
  
  if (!isOpen) return null;
  
  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent 
        className="sm:max-w-lg p-0 gap-0 overflow-hidden"
        data-testid="onboarding-modal"
        onPointerDownOutside={(e) => e.preventDefault()}
        onEscapeKeyDown={(e) => e.preventDefault()}
      >
        {/* Header with progress */}
        <div className={`${colors.bg} px-6 pt-6 pb-4`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className={`h-4 w-4 ${colors.highlight}`} />
              <span className="text-sm font-medium text-slate-600">
                Step {currentStep + 1} of {ONBOARDING_STEPS.length}
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSkip}
              className="text-slate-400 hover:text-slate-600 h-8 px-2"
              data-testid="onboarding-skip-btn"
            >
              Skip
              <X className="h-4 w-4 ml-1" />
            </Button>
          </div>
          
          {/* Progress bar */}
          <div className="h-1.5 bg-white/50 rounded-full overflow-hidden">
            <div 
              className={`h-full ${colors.progress} transition-all duration-300 rounded-full`}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        
        {/* Content */}
        <div className="px-6 py-8">
          {/* Icon */}
          <div className={`w-16 h-16 rounded-2xl ${colors.icon} flex items-center justify-center mx-auto mb-6`}>
            <Icon className="h-8 w-8" />
          </div>
          
          {/* Title */}
          <h2 className="text-2xl font-bold text-slate-900 text-center mb-2">
            {step.title}
          </h2>
          <p className={`text-sm font-medium ${colors.highlight} text-center mb-4`}>
            {step.subtitle}
          </p>
          
          {/* Description */}
          <p className="text-slate-600 text-center mb-6 leading-relaxed">
            {step.description}
          </p>
          
          {/* Highlights */}
          <div className="space-y-2 mb-6">
            {step.highlights.map((highlight, idx) => (
              <div 
                key={idx}
                className="flex items-center gap-3 bg-slate-50 rounded-lg px-4 py-2.5"
              >
                <div className={`w-5 h-5 rounded-full ${colors.icon} flex items-center justify-center flex-shrink-0`}>
                  <Target className="h-3 w-3" />
                </div>
                <span className="text-sm text-slate-700">{highlight}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Footer with navigation */}
        <div className="px-6 pb-6 flex items-center justify-between gap-3">
          {/* Back button */}
          <Button
            variant="outline"
            onClick={handlePrev}
            disabled={isFirstStep}
            className={`${isFirstStep ? 'invisible' : ''}`}
            data-testid="onboarding-prev-btn"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          
          {/* Action / Next buttons */}
          <div className="flex items-center gap-2">
            {step.action && !isLastStep && (
              <Button
                variant="outline"
                onClick={handleAction}
                className="hidden sm:flex"
              >
                {step.action.label}
              </Button>
            )}
            
            <Button
              onClick={handleNext}
              className={`${colors.button} text-white min-w-[120px]`}
              data-testid="onboarding-next-btn"
            >
              {isLastStep ? (
                <>
                  Get Started
                  <Rocket className="h-4 w-4 ml-2" />
                </>
              ) : (
                <>
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </>
              )}
            </Button>
          </div>
        </div>
        
        {/* Step indicators */}
        <div className="flex justify-center gap-1.5 pb-4">
          {ONBOARDING_STEPS.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentStep(idx)}
              className={`w-2 h-2 rounded-full transition-all ${
                idx === currentStep 
                  ? `${colors.progress} w-6` 
                  : 'bg-slate-200 hover:bg-slate-300'
              }`}
              data-testid={`onboarding-step-${idx + 1}`}
            />
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
