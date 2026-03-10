import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Users,
  Gift,
  Copy,
  Check,
  Share2,
  Twitter,
  Facebook,
  MessageCircle,
  Store,
  TrendingUp,
  Clock,
  ArrowRight,
} from 'lucide-react';
import { toast } from 'sonner';
import { apiGet } from '@/lib/api';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function ReferralPage() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, historyRes] = await Promise.all([
          apiGet('/api/viral/referral/stats'),
          apiGet('/api/viral/referral/history'),
        ]);

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
        if (historyRes.ok) {
          const historyData = await historyRes.json();
          setHistory(historyData.referrals || []);
        }
      } catch (err) {
        console.error('Failed to load referral data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const referralLink = stats
    ? `${window.location.origin}/signup?ref=${stats.referral_code}`
    : '';

  const copyLink = () => {
    navigator.clipboard.writeText(referralLink);
    setCopied(true);
    toast.success('Referral link copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  const shareOnTwitter = () => {
    const text = `Join me on TrendScout - discover trending ecommerce products before they go viral! Sign up with my referral link:`;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(referralLink)}`, '_blank');
  };

  const shareOnFacebook = () => {
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(referralLink)}`, '_blank');
  };

  const shareOnWhatsApp = () => {
    const text = `Join me on TrendScout! Discover trending ecommerce products before they go viral: ${referralLink}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="referral-page">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900" data-testid="referral-page-title">
            Refer & Earn
          </h1>
          <p className="text-slate-500 mt-1">
            Invite friends and earn bonus store slots for every verified signup.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                  <Users className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900" data-testid="total-referrals">
                    {stats?.total_referrals || 0}
                  </p>
                  <p className="text-xs text-slate-500">Total Referrals</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-emerald-100 flex items-center justify-center">
                  <Check className="h-5 w-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900" data-testid="verified-referrals">
                    {stats?.verified_referrals || 0}
                  </p>
                  <p className="text-xs text-slate-500">Verified</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-amber-100 flex items-center justify-center">
                  <Store className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900" data-testid="bonus-slots">
                    {stats?.bonus_store_slots || 0}
                  </p>
                  <p className="text-xs text-slate-500">Bonus Store Slots</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <Gift className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900" data-testid="remaining-capacity">
                    {stats?.remaining_bonus_capacity || 5}
                  </p>
                  <p className="text-xs text-slate-500">Slots Remaining</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Referral Link Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Share2 className="h-5 w-5 text-indigo-600" />
              Your Referral Link
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                readOnly
                value={referralLink}
                className="font-mono text-sm bg-slate-50"
                data-testid="referral-link-input"
              />
              <Button onClick={copyLink} data-testid="copy-referral-link-btn">
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-500">Share via:</span>
              <Button variant="outline" size="sm" onClick={shareOnTwitter} data-testid="share-twitter-btn">
                <Twitter className="h-4 w-4 mr-1" /> Twitter
              </Button>
              <Button variant="outline" size="sm" onClick={shareOnFacebook} data-testid="share-facebook-btn">
                <Facebook className="h-4 w-4 mr-1" /> Facebook
              </Button>
              <Button variant="outline" size="sm" onClick={shareOnWhatsApp} data-testid="share-whatsapp-btn">
                <MessageCircle className="h-4 w-4 mr-1" /> WhatsApp
              </Button>
            </div>

            <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-100">
              <p className="text-sm font-medium text-indigo-900 mb-1">How it works</p>
              <ol className="text-sm text-indigo-700 space-y-1">
                <li className="flex items-start gap-2">
                  <span className="font-semibold text-indigo-500">1.</span>
                  Share your unique referral link with friends
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-semibold text-indigo-500">2.</span>
                  They sign up using your link
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-semibold text-indigo-500">3.</span>
                  Once verified, you earn a bonus store slot (up to 5)
                </li>
              </ol>
            </div>
          </CardContent>
        </Card>

        {/* Referral History */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Clock className="h-5 w-5 text-slate-500" />
              Referral History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {history.length > 0 ? (
              <div className="divide-y divide-slate-100">
                {history.map((ref) => (
                  <div key={ref.id} className="flex items-center justify-between py-3" data-testid={`referral-item-${ref.id}`}>
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center">
                        <Users className="h-4 w-4 text-slate-500" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-700">
                          Referral {ref.id.slice(0, 8)}...
                        </p>
                        <p className="text-xs text-slate-400">
                          {new Date(ref.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <Badge
                      className={
                        ref.status === 'verified'
                          ? 'bg-emerald-100 text-emerald-700'
                          : ref.status === 'pending'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-red-100 text-red-700'
                      }
                    >
                      {ref.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <Users className="h-10 w-10 mx-auto mb-3 opacity-50" />
                <p className="font-medium">No referrals yet</p>
                <p className="text-sm mt-1">Share your link to start earning bonus store slots!</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
