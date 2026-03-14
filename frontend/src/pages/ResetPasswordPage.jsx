import React, { useState, useMemo } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { TrendingUp, Loader2, Eye, EyeOff, Check, X as XIcon, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import { API_URL } from '@/lib/config';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const navigate = useNavigate();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const passwordRules = useMemo(() => [
    { label: 'Minimum 8 characters', met: password.length >= 8 },
    { label: 'At least one number', met: /\d/.test(password) },
  ], [password]);

  const allRulesMet = passwordRules.every(r => r.met);
  const passwordsMatch = password === confirmPassword && confirmPassword.length > 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!allRulesMet || !passwordsMatch) return;

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_URL}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error?.message || data.detail || 'Failed to reset password');
        setLoading(false);
        return;
      }

      setSuccess(true);
      toast.success('Password reset successfully!');
    } catch {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-8">
        <div className="text-center max-w-md" data-testid="no-token-error">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Invalid reset link</h2>
          <p className="text-slate-500 mb-6">This password reset link is invalid or has expired.</p>
          <Link to="/forgot-password">
            <Button className="bg-indigo-600 hover:bg-indigo-700 font-semibold rounded-xl" data-testid="request-new-link-btn">
              Request a new reset link
            </Button>
          </Link>
        </div>
      </div>
    );
  }

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
          <h1 className="text-4xl font-bold text-white mb-4">Set a new password</h1>
          <p className="text-indigo-200 text-lg">Choose a strong password for your account.</p>
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

          {success ? (
            <div className="text-center" data-testid="reset-success">
              <div className="w-14 h-14 rounded-2xl bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                <Check className="h-7 w-7 text-emerald-600" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Password reset!</h2>
              <p className="text-slate-500 mb-6">Your password has been updated. You can now log in.</p>
              <Link to="/login">
                <Button className="bg-indigo-600 hover:bg-indigo-700 font-semibold rounded-xl" data-testid="go-to-login-btn">
                  Go to Login
                </Button>
              </Link>
            </div>
          ) : (
            <>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Reset your password</h2>
              <p className="text-slate-500 mb-8">Enter your new password below.</p>

              {error && (
                <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700" data-testid="reset-error">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5" data-testid="reset-password-form">
                <div>
                  <Label htmlFor="password">New Password</Label>
                  <div className="relative mt-1.5">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter new password"
                      required
                      data-testid="reset-password-input"
                      className="h-11 pr-10"
                    />
                    <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {password.length > 0 && (
                    <div className="mt-2 space-y-1" data-testid="reset-password-rules">
                      {passwordRules.map((rule, i) => (
                        <div key={i} className={`flex items-center gap-1.5 text-xs ${rule.met ? 'text-emerald-600' : 'text-slate-400'}`}>
                          {rule.met ? <Check className="h-3 w-3" /> : <XIcon className="h-3 w-3" />}
                          {rule.label}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter new password"
                    required
                    data-testid="reset-confirm-password-input"
                    className={`mt-1.5 h-11 ${confirmPassword.length > 0 ? (passwordsMatch ? 'border-emerald-300' : 'border-red-300') : ''}`}
                  />
                  {confirmPassword.length > 0 && !passwordsMatch && (
                    <p className="text-xs text-red-500 mt-1">Passwords do not match</p>
                  )}
                </div>

                <Button
                  type="submit"
                  disabled={loading || !allRulesMet || !passwordsMatch}
                  data-testid="reset-submit-btn"
                  className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 font-semibold disabled:opacity-50"
                >
                  {loading ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Resetting...</>
                  ) : (
                    'Reset Password'
                  )}
                </Button>
              </form>

              <p className="mt-6 text-center text-sm text-slate-500">
                <Link to="/login" className="font-semibold text-indigo-600 hover:text-indigo-500 flex items-center justify-center gap-1">
                  <ArrowLeft className="h-3 w-3" /> Back to Login
                </Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
