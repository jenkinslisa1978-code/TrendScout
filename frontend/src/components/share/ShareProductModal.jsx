import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Share2, 
  Twitter, 
  Facebook, 
  Linkedin, 
  Link2, 
  Download,
  Check,
  TrendingUp,
  Flame,
  Trophy
} from 'lucide-react';
import { toast } from 'sonner';
import { formatCurrency, getEarlyTrendInfo } from '@/lib/utils';

export default function ShareProductModal({ product, isOpen, onClose }) {
  const [copied, setCopied] = useState(false);
  
  if (!product) return null;
  
  const publicUrl = `${window.location.origin}/insights/${product.id}`;
  
  // Generate share text
  const shareTitle = `🔥 Trending Product Alert: ${product.product_name}`;
  const shareDescription = `Win Score: ${product.win_score || Math.round((product.trend_score + product.early_trend_score) / 2)} | ${formatCurrency(product.estimated_margin)} margin | ${product.early_trend_label === 'exploding' ? '🚀 EXPLODING' : product.early_trend_label === 'rising' ? '📈 Rising Fast' : 'Trending'}`;
  const shareText = `${shareTitle}\n\n${shareDescription}\n\nDiscover winning products on ViralScout 👇`;
  
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(publicUrl);
      setCopied(true);
      toast.success('Link copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy link');
    }
  };
  
  const handleShare = (platform) => {
    const encodedUrl = encodeURIComponent(publicUrl);
    const encodedText = encodeURIComponent(shareText);
    
    const shareUrls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedText}`,
      linkedin: `https://www.linkedin.com/shareArticle?mini=true&url=${encodedUrl}&title=${encodeURIComponent(shareTitle)}&summary=${encodeURIComponent(shareDescription)}`,
    };
    
    window.open(shareUrls[platform], '_blank', 'width=600,height=400');
  };
  
  const handleDownloadCard = () => {
    // Create a canvas for the share card
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = 1200;
    canvas.height = 630;
    
    // Background gradient
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#4F46E5');
    gradient.addColorStop(1, '#7C3AED');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Add some visual elements
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.beginPath();
    ctx.arc(100, 100, 200, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(canvas.width - 100, canvas.height - 100, 300, 0, Math.PI * 2);
    ctx.fill();
    
    // Card background
    ctx.fillStyle = 'white';
    ctx.roundRect(60, 80, canvas.width - 120, canvas.height - 160, 20);
    ctx.fill();
    
    // Product name
    ctx.fillStyle = '#1E293B';
    ctx.font = 'bold 48px Inter, sans-serif';
    ctx.fillText(product.product_name, 100, 180);
    
    // Category
    ctx.fillStyle = '#64748B';
    ctx.font = '24px Inter, sans-serif';
    ctx.fillText(product.category, 100, 220);
    
    // Metrics
    const metrics = [
      { label: 'Win Score', value: product.win_score || Math.round((product.trend_score + product.early_trend_score) / 2), color: '#F59E0B' },
      { label: 'Trend Score', value: product.trend_score, color: '#10B981' },
      { label: 'Est. Margin', value: `£${product.estimated_margin?.toFixed(0)}`, color: '#6366F1' },
    ];
    
    metrics.forEach((metric, i) => {
      const x = 100 + i * 350;
      const y = 320;
      
      ctx.fillStyle = metric.color;
      ctx.font = 'bold 64px Inter, sans-serif';
      ctx.fillText(String(metric.value), x, y);
      
      ctx.fillStyle = '#64748B';
      ctx.font = '20px Inter, sans-serif';
      ctx.fillText(metric.label, x, y + 40);
    });
    
    // Early trend label
    if (product.early_trend_label && product.early_trend_label !== 'stable') {
      const labelText = product.early_trend_label === 'exploding' ? '🔥 EXPLODING' : 
                       product.early_trend_label === 'rising' ? '📈 RISING' : '🌱 EARLY TREND';
      ctx.fillStyle = product.early_trend_label === 'exploding' ? '#DC2626' : 
                      product.early_trend_label === 'rising' ? '#EA580C' : '#059669';
      ctx.font = 'bold 28px Inter, sans-serif';
      ctx.fillText(labelText, 100, 440);
    }
    
    // Branding
    ctx.fillStyle = '#6366F1';
    ctx.font = 'bold 32px Inter, sans-serif';
    ctx.fillText('ViralScout', 100, 530);
    
    ctx.fillStyle = '#94A3B8';
    ctx.font = '20px Inter, sans-serif';
    ctx.fillText('Find Winning Products • Launch Stores Fast', 280, 530);
    
    // Download
    const link = document.createElement('a');
    link.download = `${product.product_name.replace(/\s+/g, '-').toLowerCase()}-viralscout.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    
    toast.success('Share card downloaded!');
  };
  
  const earlyTrendInfo = getEarlyTrendInfo(product.early_trend_label);
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5 text-indigo-600" />
            Share Winning Product
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Preview Card */}
          <div className="rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 p-1">
            <div className="bg-white rounded-lg p-5">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-lg text-slate-900">{product.product_name}</h3>
                  <p className="text-sm text-slate-500">{product.category}</p>
                </div>
                {product.early_trend_label && product.early_trend_label !== 'stable' && (
                  <Badge className={`${earlyTrendInfo.color} border`}>
                    {earlyTrendInfo.text}
                  </Badge>
                )}
              </div>
              
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className="text-center p-3 rounded-lg bg-amber-50">
                  <Trophy className="h-5 w-5 text-amber-600 mx-auto mb-1" />
                  <p className="font-mono text-xl font-bold text-amber-600">
                    {product.win_score || Math.round((product.trend_score + product.early_trend_score) / 2)}
                  </p>
                  <p className="text-xs text-slate-500">Win Score</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-emerald-50">
                  <TrendingUp className="h-5 w-5 text-emerald-600 mx-auto mb-1" />
                  <p className="font-mono text-xl font-bold text-emerald-600">{product.trend_score}</p>
                  <p className="text-xs text-slate-500">Trend Score</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-indigo-50">
                  <Flame className="h-5 w-5 text-indigo-600 mx-auto mb-1" />
                  <p className="font-mono text-xl font-bold text-indigo-600">{formatCurrency(product.estimated_margin)}</p>
                  <p className="text-xs text-slate-500">Margin</p>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-sm font-semibold text-indigo-600">ViralScout</span>
                <span className="text-xs text-slate-400">Find Winning Products</span>
              </div>
            </div>
          </div>
          
          {/* Share Actions */}
          <div className="space-y-3">
            <p className="text-sm font-medium text-slate-700">Share on Social Media</p>
            <div className="flex gap-2">
              <Button 
                onClick={() => handleShare('twitter')}
                className="flex-1 bg-[#1DA1F2] hover:bg-[#1a8cd8]"
              >
                <Twitter className="h-4 w-4 mr-2" />
                Twitter
              </Button>
              <Button 
                onClick={() => handleShare('facebook')}
                className="flex-1 bg-[#4267B2] hover:bg-[#375695]"
              >
                <Facebook className="h-4 w-4 mr-2" />
                Facebook
              </Button>
              <Button 
                onClick={() => handleShare('linkedin')}
                className="flex-1 bg-[#0077B5] hover:bg-[#006399]"
              >
                <Linkedin className="h-4 w-4 mr-2" />
                LinkedIn
              </Button>
            </div>
          </div>
          
          {/* Copy Link & Download */}
          <div className="space-y-3">
            <p className="text-sm font-medium text-slate-700">Or share directly</p>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={handleCopyLink}
                className="flex-1"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4 mr-2 text-emerald-600" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Link2 className="h-4 w-4 mr-2" />
                    Copy Link
                  </>
                )}
              </Button>
              <Button 
                variant="outline" 
                onClick={handleDownloadCard}
                className="flex-1"
              >
                <Download className="h-4 w-4 mr-2" />
                Download Card
              </Button>
            </div>
          </div>
          
          {/* Referral Hint */}
          <div className="rounded-lg bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-100 p-4">
            <p className="text-sm text-amber-800">
              <span className="font-semibold">🎁 Earn free store builds!</span> Invite friends to ViralScout and unlock additional store creations.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
