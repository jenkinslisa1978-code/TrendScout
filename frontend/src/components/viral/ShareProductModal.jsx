import React, { useState, useRef } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogDescription
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Share2, 
  Copy, 
  Twitter, 
  Linkedin, 
  Download,
  Check,
  MessageCircle,
  ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';
import { getMarketOpportunityInfo, formatCurrency } from '@/lib/utils';
import html2canvas from 'html2canvas';

export default function ShareProductModal({ 
  isOpen, 
  onClose, 
  product,
  shareData 
}) {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const cardRef = useRef(null);

  if (!product || !shareData) return null;

  const marketInfo = getMarketOpportunityInfo(shareData.card_data?.market_label || 'competitive');
  const shareUrl = `${window.location.origin}/discover/product/${product.id}`;
  
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      toast.success('Link copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy link');
    }
  };

  const handleCopyText = async () => {
    try {
      await navigator.clipboard.writeText(shareData.share_text + '\n\n' + shareUrl);
      toast.success('Share text copied!');
    } catch (err) {
      toast.error('Failed to copy text');
    }
  };

  const handleTwitterShare = () => {
    const text = encodeURIComponent(shareData.share_text);
    const url = encodeURIComponent(shareUrl);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  };

  const handleLinkedInShare = () => {
    const url = encodeURIComponent(shareUrl);
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank');
  };

  const handleWhatsAppShare = () => {
    const text = encodeURIComponent(shareData.share_text + '\n\n' + shareUrl);
    window.open(`https://wa.me/?text=${text}`, '_blank');
  };

  const handleDownloadCard = async () => {
    if (!cardRef.current) return;
    
    setDownloading(true);
    try {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#ffffff',
        scale: 2,
      });
      
      const link = document.createElement('a');
      link.download = `viralscout-${product.product_name.toLowerCase().replace(/\s+/g, '-')}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      
      toast.success('Card downloaded!');
    } catch (err) {
      toast.error('Failed to download card');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5 text-indigo-600" />
            Share Winning Product
          </DialogTitle>
          <DialogDescription>
            Share this product insight with your network
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Shareable Card Preview */}
          <div className="border rounded-xl overflow-hidden bg-white">
            <div 
              ref={cardRef}
              className="p-6 bg-gradient-to-br from-indigo-50 via-white to-purple-50"
              data-testid="share-card"
            >
              {/* ViralScout Branding */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center">
                    <span className="text-white font-bold text-sm">VS</span>
                  </div>
                  <div>
                    <p className="font-bold text-slate-900">ViralScout</p>
                    <p className="text-xs text-slate-500">Find winning products before they go viral</p>
                  </div>
                </div>
                <Badge className={`${marketInfo.color} border text-xs font-semibold`}>
                  {marketInfo.text}
                </Badge>
              </div>

              {/* Product Info */}
              <div className="flex gap-4">
                {product.image_url && (
                  <img 
                    src={product.image_url} 
                    alt={product.product_name}
                    className="w-20 h-20 rounded-lg object-cover"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-lg text-slate-900 truncate">
                    {product.product_name}
                  </h3>
                  <p className="text-sm text-slate-500">{product.category}</p>
                  
                  {/* Scores */}
                  <div className="flex items-center gap-4 mt-3">
                    <div>
                      <p className="text-2xl font-bold text-indigo-600">
                        {shareData.card_data?.market_score || 0}
                      </p>
                      <p className="text-xs text-slate-500">Market Score</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-emerald-600">
                        {shareData.card_data?.trend_score || 0}
                      </p>
                      <p className="text-xs text-slate-500">Trend Score</p>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-slate-700">
                        {shareData.card_data?.margin_range || '£20+'}
                      </p>
                      <p className="text-xs text-slate-500">Est. Margin</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Badges */}
              <div className="flex flex-wrap gap-2 mt-4">
                <Badge className="bg-slate-100 text-slate-700 border-slate-200 text-xs">
                  {shareData.card_data?.trend_stage?.charAt(0).toUpperCase() + shareData.card_data?.trend_stage?.slice(1) || 'Rising'}
                </Badge>
                {shareData.card_data?.early_trend_label && shareData.card_data.early_trend_label !== 'stable' && (
                  <Badge className="bg-amber-50 text-amber-700 border-amber-200 text-xs">
                    {shareData.card_data.early_trend_label === 'exploding' ? '🔥 Exploding' : 
                     shareData.card_data.early_trend_label === 'rising' ? '📈 Rising' : 
                     '🌱 Early Trend'}
                  </Badge>
                )}
              </div>

              {/* Footer */}
              <div className="mt-4 pt-4 border-t border-slate-200 flex items-center justify-between">
                <p className="text-xs text-slate-400">viralscout.com</p>
                <p className="text-xs text-indigo-600 font-medium">
                  Discover more winning products →
                </p>
              </div>
            </div>
          </div>

          {/* Share Options */}
          <div className="space-y-3">
            <p className="text-sm font-medium text-slate-700">Share via</p>
            <div className="grid grid-cols-2 gap-3">
              <Button 
                variant="outline" 
                className="h-12"
                onClick={handleTwitterShare}
                data-testid="share-twitter"
              >
                <Twitter className="h-5 w-5 mr-2 text-[#1DA1F2]" />
                Twitter / X
              </Button>
              <Button 
                variant="outline" 
                className="h-12"
                onClick={handleLinkedInShare}
                data-testid="share-linkedin"
              >
                <Linkedin className="h-5 w-5 mr-2 text-[#0A66C2]" />
                LinkedIn
              </Button>
              <Button 
                variant="outline" 
                className="h-12"
                onClick={handleWhatsAppShare}
                data-testid="share-whatsapp"
              >
                <MessageCircle className="h-5 w-5 mr-2 text-[#25D366]" />
                WhatsApp
              </Button>
              <Button 
                variant="outline" 
                className="h-12"
                onClick={handleCopyText}
                data-testid="share-copy-text"
              >
                <Copy className="h-5 w-5 mr-2" />
                Copy Text
              </Button>
            </div>
          </div>

          {/* Copy Link & Download */}
          <div className="flex gap-3">
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={handleCopyLink}
              data-testid="share-copy-link"
            >
              {copied ? (
                <Check className="h-4 w-4 mr-2 text-emerald-600" />
              ) : (
                <ExternalLink className="h-4 w-4 mr-2" />
              )}
              {copied ? 'Copied!' : 'Copy Link'}
            </Button>
            <Button 
              className="flex-1 bg-indigo-600 hover:bg-indigo-700"
              onClick={handleDownloadCard}
              disabled={downloading}
              data-testid="share-download"
            >
              <Download className="h-4 w-4 mr-2" />
              {downloading ? 'Downloading...' : 'Download Card'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
