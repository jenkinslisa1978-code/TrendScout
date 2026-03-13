import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { TrendingUp, Eye, EyeOff, Loader2, Gift } from 'lucide-react';
import { toast } from 'sonner';
import { API_URL } from '@/lib/config';

export default function SignupPage() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { signUp } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const referralCode = searchParams.get('ref');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    const { data, error } = await signUp(email, password, fullName);

    if (error) {
      toast.error(error.message || 'Failed to create account');
      setLoading(false);
      return;
    }

    // Track referral if code present
    if (referralCode && data?.user?.id) {
      try {
        await fetch(`${API_URL}/api/viral/referral/track?referral_code=${encodeURIComponent(referralCode)}&referred_user_id=${encodeURIComponent(data.user.id)}`, {
          method: 'POST',
        });
      } catch (err) {
        console.error('Failed to track referral:', err);
      }
    }

    toast.success('Welcome to TrendScout!');
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 p-12 flex-col justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-white/20 flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">TrendScout</span>
          </div>
        </div>
        <div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Start finding winning products today
          </h1>
          <p className="text-indigo-200 text-lg">
            Join thousands of e-commerce sellers using AI to discover trending products.
          </p>
        </div>
        <p className="text-indigo-300 text-sm">Free plan available - no credit card required</p>
      </div>

      {/* Right Panel - Signup Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900">TrendScout</span>
          </div>

          <h2 className="text-2xl font-bold text-slate-900 mb-2">Start Free Product Discovery</h2>
          <p className="text-slate-500 mb-8">No credit card required. Explore trending products instantly.</p>

          {referralCode && (
            <div className="mb-6 rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3 text-sm text-emerald-700 flex items-center gap-2" data-testid="referral-badge">
              <Gift className="h-4 w-4" />
              <span>You were referred by a friend!</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Label htmlFor="fullName">Full Name</Label>
              <Input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                data-testid="signup-name-input"
                className="mt-1.5 h-11"
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                data-testid="signup-email-input"
                className="mt-1.5 h-11"
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <div className="relative mt-1.5">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 6 characters"
                  required
                  data-testid="signup-password-input"
                  className="h-11 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              data-testid="signup-submit-btn"
              className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 font-semibold"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Start Free Product Discovery'
              )}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-indigo-600 hover:text-indigo-500">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
