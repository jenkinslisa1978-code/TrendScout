import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Lock, TrendingUp, ArrowRight } from 'lucide-react';

export function SignupGate({ title, description }) {
  return (
    <div className="relative" data-testid="signup-gate">
      {/* Blur overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-white via-white/95 to-white/60 z-10 flex items-center justify-center">
        <div className="text-center px-6 max-w-md">
          <div className="mx-auto h-12 w-12 rounded-2xl bg-indigo-100 flex items-center justify-center mb-4">
            <Lock className="h-6 w-6 text-indigo-600" />
          </div>
          <h3 className="text-lg sm:text-xl font-bold text-slate-900">
            {title || 'Sign up to see full data'}
          </h3>
          <p className="text-sm text-slate-500 mt-2 leading-relaxed">
            {description || 'Create a free account to access launch scores, profit margins, supplier costs, and more.'}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-5">
            <Link to="/signup">
              <Button className="bg-indigo-600 hover:bg-indigo-700 gap-2 rounded-xl px-6" data-testid="gate-signup-btn">
                Start Free Trial <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" className="rounded-xl px-6" data-testid="gate-login-btn">
                Log in
              </Button>
            </Link>
          </div>
        </div>
      </div>
      {/* Blurred placeholder rows */}
      <div className="filter blur-sm pointer-events-none select-none" aria-hidden="true">
        {[1,2,3,4,5].map(i => (
          <div key={i} className="flex items-center gap-4 p-4 border-b border-slate-100">
            <div className="w-14 h-14 rounded-lg bg-slate-200" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-slate-200 rounded w-3/4" />
              <div className="h-3 bg-slate-100 rounded w-1/2" />
            </div>
            <div className="h-8 w-20 bg-slate-200 rounded-lg" />
          </div>
        ))}
      </div>
    </div>
  );
}
