import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { TrendingUp, Eye, EyeOff, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [showResend, setShowResend] = useState(false);
  const { signIn, isDemoMode } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setShowResend(false);

    const { error } = await signIn(email, password);

    if (error) {
      if (error.showResend) {
        setShowResend(true);
      }
      toast.error(error.message || 'Failed to sign in');
      setLoading(false);
      return;
    }

    toast.success('Welcome back!');
    navigate('/dashboard');
  };

  const handleResendVerification = async () => {
    if (!email) {
      toast.error('Please enter your email address first');
      return;
    }
    setResending(true);
    try {
      const { supabase } = await import('@/lib/supabase');
      if (supabase) {
        const { error } = await supabase.auth.resend({
          type: 'signup',
          email: email,
        });
        if (error) {
          toast.error(error.message || 'Failed to resend. Please wait a minute and try again.');
        } else {
          toast.success('Verification email sent! Check your inbox and spam folder.');
        }
      }
    } catch (err) {
      toast.error('Failed to resend. Please wait a minute and try again.');
    }
    setResending(false);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex">
      {/* Left side - Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 mb-8">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <span className="font-manrope text-xl font-bold text-slate-900">TrendScout</span>
          </Link>

          <h1 className="font-manrope text-2xl font-bold text-slate-900">Welcome back</h1>
          <p className="mt-2 text-sm text-slate-600">
            Enter your credentials to access your account
          </p>

          {isDemoMode && (
            <div className="mt-4 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700">
              <strong>Demo Mode:</strong> Enter any email/password to explore the dashboard.
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="login-email-input"
                className="h-11"
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link 
                  to="/forgot-password" 
                  className="text-sm text-indigo-600 hover:text-indigo-700"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  data-testid="login-password-input"
                  className="h-11 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              data-testid="login-submit-btn"
              className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 font-semibold"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </Button>
          </form>

          {showResend && (
            <div className="mt-4 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3" data-testid="resend-verification-section">
              <p className="text-sm text-amber-700 mb-2">
                Your email hasn't been verified yet. Check your inbox and spam folder.
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={handleResendVerification}
                disabled={resending}
                data-testid="resend-verification-btn"
                className="w-full"
              >
                {resending ? (
                  <>
                    <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                    Sending...
                  </>
                ) : (
                  'Resend verification email'
                )}
              </Button>
            </div>
          )}

          <p className="mt-6 text-center text-sm text-slate-600">
            Don't have an account?{' '}
            <Link to="/signup" className="font-semibold text-indigo-600 hover:text-indigo-700">
              Sign up for free
            </Link>
          </p>
        </div>
      </div>

      {/* Right side - Visual */}
      <div className="hidden lg:flex lg:flex-1 items-center justify-center bg-indigo-600 p-12">
        <div className="max-w-md text-center text-white">
          <h2 className="font-manrope text-3xl font-bold">
            Discover winning products before your competition
          </h2>
          <p className="mt-4 text-indigo-100 leading-relaxed">
            Join thousands of successful dropshippers who use TrendScout to find 
            trending products and maximize their profits.
          </p>
          <div className="mt-8 flex justify-center gap-8">
            <div>
              <div className="font-mono text-4xl font-bold">2.8K+</div>
              <div className="text-sm text-indigo-200">Products Tracked</div>
            </div>
            <div>
              <div className="font-mono text-4xl font-bold">98%</div>
              <div className="text-sm text-indigo-200">Satisfaction Rate</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
