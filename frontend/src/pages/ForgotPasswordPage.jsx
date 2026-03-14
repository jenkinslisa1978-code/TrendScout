import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { TrendingUp, Loader2, Mail, ArrowLeft, Check } from 'lucide-react';
import { API_URL } from '@/lib/config';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error?.message || data.detail || 'Something went wrong');
        setLoading(false);
        return;
      }

      setSent(true);
    } catch {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 p-12 flex-col justify-between">
        <div>
          <Link to="/" className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-white/20 flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">TrendScout</span>
          </Link>
        </div>
        <div>
          <h1 className="text-4xl font-bold text-white mb-4">Reset your password</h1>
          <p className="text-indigo-200 text-lg">We'll help you get back into your account.</p>
        </div>
        <p className="text-indigo-300 text-sm">AI product validation for ecommerce</p>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <Link to="/" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900">TrendScout</span>
            </Link>
          </div>

          {sent ? (
            <div className="text-center" data-testid="forgot-success">
              <div className="w-14 h-14 rounded-2xl bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                <Check className="h-7 w-7 text-emerald-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Check your email</h2>
              <p className="text-slate-500 mb-6">
                If an account exists for <strong>{email}</strong>, we've sent a password reset link.
              </p>
              <Link to="/login">
                <Button variant="outline" className="font-semibold rounded-xl" data-testid="back-to-login-btn">
                  <ArrowLeft className="mr-2 h-4 w-4" /> Back to Login
                </Button>
              </Link>
            </div>
          ) : (
            <>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Forgot your password?</h2>
              <p className="text-slate-500 mb-8">Enter your email and we'll send you a reset link.</p>

              {error && (
                <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700" data-testid="forgot-error">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5" data-testid="forgot-password-form">
                <div>
                  <Label htmlFor="email">Email address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                    data-testid="forgot-email-input"
                    className="mt-1.5 h-11"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading || !email}
                  data-testid="forgot-submit-btn"
                  className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 font-semibold disabled:opacity-50"
                >
                  {loading ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Sending...</>
                  ) : (
                    <><Mail className="mr-2 h-4 w-4" />Send Reset Link</>
                  )}
                </Button>
              </form>

              <p className="mt-6 text-center text-sm text-slate-500">
                Remember your password?{' '}
                <Link to="/login" className="font-semibold text-indigo-600 hover:text-indigo-500">Sign in</Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
