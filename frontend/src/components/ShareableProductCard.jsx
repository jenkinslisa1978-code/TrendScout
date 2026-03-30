import React, { useRef, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Share2, Download, Copy, Check, TrendingUp, Truck } from 'lucide-react';
import { toast } from 'sonner';
import { SourceTrustBadge } from '@/components/SourceTrustBadge';

function getTrendColor(stage) {
  switch (stage) {
    case 'exploding': return { bg: 'bg-red-500', text: 'text-red-600', badge: 'bg-red-100 text-red-700 border-red-200' };
    case 'rising': return { bg: 'bg-amber-500', text: 'text-amber-600', badge: 'bg-amber-100 text-amber-700 border-amber-200' };
    case 'emerging': return { bg: 'bg-emerald-500', text: 'text-emerald-600', badge: 'bg-emerald-100 text-emerald-700 border-emerald-200' };
    default: return { bg: 'bg-slate-500', text: 'text-slate-600', badge: 'bg-slate-100 text-slate-700 border-slate-200' };
  }
}

/**
 * ShareableProductCard — generates a visual product insight card
 * that can be exported as image or shared via link.
 */
export default function ShareableProductCard({ product, onClose }) {
  const cardRef = useRef(null);
  const [copied, setCopied] = useState(false);

  const launchScore = product.win_score || Math.round(
    (product.trend_score || 0) * 0.3 +
    (product.early_trend_score || 0) * 0.3 +
    (product.success_probability || 0) * 0.4
  );

  const supplierCost = product.supplier_cost || 0;
  const retailPrice = product.estimated_retail_price || product.recommended_price || 0;
  const margin = supplierCost > 0 && retailPrice > 0
    ? Math.round(((retailPrice - supplierCost) / retailPrice) * 100)
    : 0;

  const trendStage = product.early_trend_label || product.trend_stage || 'rising';
  const tc = getTrendColor(trendStage);

  const handleCopyLink = () => {
    const url = `${window.location.origin}/product/${product.id}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    toast.success('Link copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadImage = async () => {
    if (!cardRef.current) return;
    try {
      const html2canvas = (await import('html2canvas')).default;
      const canvas = await html2canvas(cardRef.current, {
        scale: 2,
        backgroundColor: '#ffffff',
        useCORS: true,
      });
      const link = document.createElement('a');
      link.download = `trendscout-${product.product_name?.replace(/\s+/g, '-').toLowerCase() || 'product'}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      toast.success('Image downloaded!');
    } catch (e) {
      toast.error('Failed to generate image. Try copying the link instead.');
    }
  };

  const handleShare = async () => {
    const url = `${window.location.origin}/product/${product.id}`;
    const text = `Check out this product on TrendScout: ${product.product_name} - Launch Score ${launchScore}, ${margin}% margin`;
    if (navigator.share) {
      try {
        await navigator.share({ title: 'TrendScout Product Insight', text, url });
      } catch (e) { /* cancelled */ }
    } else {
      handleCopyLink();
    }
  };

  return (
    <div className="space-y-3">
      {/* The shareable card */}
      <div
        ref={cardRef}
        className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-lg"
        style={{ maxWidth: 400 }}
        data-testid="shareable-card"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-900 to-slate-800 p-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-indigo-400" />
            <span className="text-xs font-bold text-indigo-400 tracking-wider uppercase">TrendScout Product Insight</span>
          </div>
        </div>

        {/* Product info */}
        <div className="p-5 space-y-4">
          <div className="flex items-start gap-3">
            {product.image_url && (
              <img
                src={product.image_url}
                alt={product.product_name}
                className="w-16 h-16 rounded-xl object-cover border border-slate-100"
                crossOrigin="anonymous"
              />
            )}
            <div className="flex-1 min-w-0">
              <h3 className="text-base font-bold text-slate-900 leading-tight">{product.product_name}</h3>
              <div className="flex items-center gap-2 mt-1">
                <Badge className={`text-[10px] ${tc.badge}`}>
                  {trendStage.charAt(0).toUpperCase() + trendStage.slice(1)}
                </Badge>
                {product.data_confidence && (
                  <SourceTrustBadge confidence={product.data_confidence} size="xs" showIcon={false} />
                )}
              </div>
            </div>
          </div>

          {/* Score grid */}
          <div className="grid grid-cols-4 gap-2">
            <div className="text-center bg-indigo-50 rounded-xl p-2.5">
              <p className="text-lg font-black text-indigo-700">{launchScore}</p>
              <p className="text-[9px] text-indigo-500 font-medium mt-0.5">Launch Score</p>
            </div>
            <div className="text-center bg-emerald-50 rounded-xl p-2.5">
              <p className="text-lg font-black text-emerald-700">{margin}%</p>
              <p className="text-[9px] text-emerald-500 font-medium mt-0.5">Margin</p>
            </div>
            <div className="text-center bg-amber-50 rounded-xl p-2.5">
              <p className="text-lg font-black text-amber-700">£{supplierCost.toFixed(0)}</p>
              <p className="text-[9px] text-amber-500 font-medium mt-0.5">Supplier</p>
            </div>
            <div className="text-center bg-violet-50 rounded-xl p-2.5">
              <p className="text-lg font-black text-violet-700">£{retailPrice.toFixed(0)}</p>
              <p className="text-[9px] text-violet-500 font-medium mt-0.5">Retail</p>
            </div>
          </div>

          {/* UK Shipping indicator */}
          {product.uk_shipping && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-100" data-testid="shareable-shipping-badge">
              <Truck className="h-3.5 w-3.5 text-slate-500" />
              <span className="text-xs text-slate-600">UK Delivery:</span>
              <span className={`inline-flex items-center gap-1 text-xs font-bold ${
                product.uk_shipping.tier === 'green' ? 'text-emerald-600' :
                product.uk_shipping.tier === 'yellow' ? 'text-amber-600' :
                'text-red-600'
              }`}>
                <span className={`h-1.5 w-1.5 rounded-full ${
                  product.uk_shipping.tier === 'green' ? 'bg-emerald-500' :
                  product.uk_shipping.tier === 'yellow' ? 'bg-amber-500' :
                  'bg-red-500'
                }`} />
                {product.uk_shipping.label}
              </span>
            </div>
          )}
        </div>

        {/* Watermark */}
        <div className="bg-slate-50 px-5 py-2 flex items-center justify-between border-t border-slate-100">
          <span className="text-[10px] text-slate-400">Powered by TrendScout AI</span>
          <span className="text-[10px] text-slate-400">trendscout.ai</span>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2">
        <Button
          size="sm"
          variant="outline"
          className="flex-1 text-xs"
          onClick={handleDownloadImage}
          data-testid="download-card-btn"
        >
          <Download className="h-3 w-3 mr-1" /> Download Image
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="flex-1 text-xs"
          onClick={handleCopyLink}
          data-testid="copy-link-btn"
        >
          {copied ? <Check className="h-3 w-3 mr-1" /> : <Copy className="h-3 w-3 mr-1" />}
          {copied ? 'Copied!' : 'Copy Link'}
        </Button>
        <Button
          size="sm"
          className="flex-1 text-xs bg-indigo-600 hover:bg-indigo-700"
          onClick={handleShare}
          data-testid="share-card-btn"
        >
          <Share2 className="h-3 w-3 mr-1" /> Share
        </Button>
      </div>
    </div>
  );
}
