import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Users, 
  Gift, 
  Copy, 
  Check, 
  Store,
  Share2,
  Twitter,
  Linkedin,
  MessageCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { apiGet } from '@/lib/api';

export default function ReferralCard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiGet('/api/viral/referral/stats');
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Error fetching referral stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleCopyCode = async () => {
    if (!stats?.referral_code) return;
    
    try {
      await navigator.clipboard.writeText(stats.referral_code);
      setCopied(true);
      toast.success('Referral code copied!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy code');
    }
  };

  const handleCopyLink = async () => {
    if (!stats?.referral_code) return;
    
    const link = `${window.location.origin}/signup?ref=${stats.referral_code}`;
    try {
      await navigator.clipboard.writeText(link);
      toast.success('Referral link copied!');
    } catch (err) {
      toast.error('Failed to copy link');
    }
  };

  const shareText = `Join me on ViralScout and find winning products before they go viral! Use my referral code: ${stats?.referral_code || ''}`;
  const shareUrl = stats ? `${window.location.origin}/signup?ref=${stats.referral_code}` : '';

  const handleTwitterShare = () => {
    const text = encodeURIComponent(shareText);
    const url = encodeURIComponent(shareUrl);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  };

  const handleLinkedInShare = () => {
    const url = encodeURIComponent(shareUrl);
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank');
  };

  const handleWhatsAppShare = () => {
    const text = encodeURIComponent(shareText + '\n\n' + shareUrl);
    window.open(`https://wa.me/?text=${text}`, '_blank');
  };

  if (loading) {
    return (
      <Card className="border-slate-200">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-slate-200 rounded w-1/3"></div>
            <div className="h-10 bg-slate-200 rounded"></div>
            <div className="h-4 bg-slate-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) return null;

  const progressPercent = (stats.bonus_store_slots / stats.max_bonus_slots) * 100;

  return (
    <Card className="border-slate-200 overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Gift className="h-5 w-5 text-indigo-600" />
          Referral Program
        </CardTitle>
        <p className="text-sm text-slate-600 mt-1">
          Invite friends and unlock more store builds!
        </p>
      </CardHeader>
      
      <CardContent className="p-6 space-y-6">
        {/* Referral Code */}
        <div>
          <label className="text-sm font-medium text-slate-600">Your Referral Code</label>
          <div className="mt-2 flex gap-2">
            <div className="flex-1 bg-slate-100 rounded-lg px-4 py-3 font-mono font-bold text-lg text-indigo-600 text-center">
              {stats.referral_code}
            </div>
            <Button 
              variant="outline" 
              size="icon"
              onClick={handleCopyCode}
              className="h-12 w-12"
              data-testid="copy-referral-code"
            >
              {copied ? (
                <Check className="h-5 w-5 text-emerald-600" />
              ) : (
                <Copy className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-50 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-slate-900">{stats.verified_referrals}</p>
            <p className="text-sm text-slate-500">Verified Referrals</p>
          </div>
          <div className="bg-emerald-50 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-emerald-600">+{stats.bonus_store_slots}</p>
            <p className="text-sm text-slate-500">Bonus Store Slots</p>
          </div>
        </div>

        {/* Progress */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-600">Bonus Progress</span>
            <span className="text-sm font-medium text-slate-900">
              {stats.bonus_store_slots}/{stats.max_bonus_slots} slots earned
            </span>
          </div>
          <Progress value={progressPercent} className="h-2" />
          {stats.remaining_bonus_capacity > 0 ? (
            <p className="text-xs text-slate-500 mt-2">
              <Store className="h-3 w-3 inline mr-1" />
              {stats.remaining_bonus_capacity} more bonus slots available
            </p>
          ) : (
            <p className="text-xs text-emerald-600 mt-2">
              <Check className="h-3 w-3 inline mr-1" />
              Maximum bonus achieved!
            </p>
          )}
        </div>

        {/* Share Buttons */}
        <div className="space-y-3">
          <Button 
            variant="outline" 
            className="w-full"
            onClick={handleCopyLink}
            data-testid="copy-referral-link"
          >
            <Share2 className="h-4 w-4 mr-2" />
            Copy Referral Link
          </Button>
          
          <div className="grid grid-cols-3 gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleTwitterShare}
              className="text-[#1DA1F2]"
            >
              <Twitter className="h-4 w-4" />
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleLinkedInShare}
              className="text-[#0A66C2]"
            >
              <Linkedin className="h-4 w-4" />
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleWhatsAppShare}
              className="text-[#25D366]"
            >
              <MessageCircle className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Pending Referrals */}
        {stats.total_referrals > stats.verified_referrals && (
          <div className="bg-amber-50 rounded-lg p-3 text-center">
            <Badge className="bg-amber-100 text-amber-700 border-amber-200">
              {stats.total_referrals - stats.verified_referrals} pending verification
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
