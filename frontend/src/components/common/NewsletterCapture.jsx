import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Mail, Check, Loader2, ArrowRight, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function NewsletterCapture() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('idle'); // idle | loading | success

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !email.includes('@')) {
      toast.error('Please enter a valid email address');
      return;
    }

    setStatus('loading');
    try {
      const res = await fetch(`${API_URL}/api/newsletter/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus('success');
        if (data.status === 'already_subscribed') {
          toast.info("You're already subscribed!");
        } else {
          toast.success('Subscribed! Watch your inbox for the next Product of the Week.');
        }
      } else {
        throw new Error(data.detail || 'Subscription failed');
      }
    } catch (err) {
      toast.error(err.message || 'Something went wrong. Please try again.');
      setStatus('idle');
    }
  };

  if (status === 'success') {
    return (
      <section className="py-16 bg-gradient-to-b from-slate-50 to-white" data-testid="newsletter-section">
        <div className="mx-auto max-w-xl px-6 text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-emerald-100 mb-4">
            <Check className="h-7 w-7 text-emerald-600" />
          </div>
          <h3 className="text-xl font-semibold text-slate-900 mb-2">You're on the list!</h3>
          <p className="text-slate-500">
            We'll send you the top product every Wednesday. No spam, unsubscribe anytime.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-gradient-to-b from-slate-50 to-white" data-testid="newsletter-section">
      <div className="mx-auto max-w-2xl px-6">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 sm:p-10 text-center">
          <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 text-xs font-medium px-3 py-1.5 rounded-full mb-4">
            <Sparkles className="h-3 w-3" />
            Free Weekly Digest
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-3">
            Get the Product of the Week
          </h2>
          <p className="text-slate-500 mb-8 max-w-md mx-auto">
            Every Wednesday, we'll send you the highest-scoring trending product with key metrics. Free forever, no account needed.
          </p>
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <div className="relative flex-1">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10 h-11"
                disabled={status === 'loading'}
                data-testid="newsletter-email-input"
              />
            </div>
            <Button
              type="submit"
              disabled={status === 'loading'}
              className="bg-indigo-600 hover:bg-indigo-700 h-11 px-6"
              data-testid="newsletter-subscribe-btn"
            >
              {status === 'loading' ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Subscribe
                  <ArrowRight className="h-4 w-4 ml-1" />
                </>
              )}
            </Button>
          </form>
          <p className="text-xs text-slate-400 mt-4">No spam, ever. Unsubscribe anytime.</p>
        </div>
      </div>
    </section>
  );
}
