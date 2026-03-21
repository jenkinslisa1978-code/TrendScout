import React, { useState } from 'react';
import { trackEvent } from '@/services/analytics';
import { Share2, Copy, Check, Twitter } from 'lucide-react';

/**
 * Share button for calculator results.
 * Provides native share (mobile), copy-to-clipboard, and X/Twitter share.
 */
export default function ShareResult({ tool, resultText, detail }) {
  const [copied, setCopied] = useState(false);

  const shareText = `${resultText}${detail ? ` — ${detail}` : ''}\n\nCalculated with TrendScout free tools`;
  const shareUrl = `${window.location.origin}/tools`;

  const handleNativeShare = async () => {
    trackEvent('share_result', { tool, method: 'native' });
    if (navigator.share) {
      try {
        await navigator.share({ title: `My UK ${tool} result`, text: shareText, url: shareUrl });
      } catch {}
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(`${shareText}\n${shareUrl}`);
    setCopied(true);
    trackEvent('share_result', { tool, method: 'copy' });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTwitter = () => {
    trackEvent('share_result', { tool, method: 'twitter' });
    const text = encodeURIComponent(shareText);
    const url = encodeURIComponent(shareUrl);
    window.open(`https://x.com/intent/tweet?text=${text}&url=${url}`, '_blank', 'width=550,height=420');
  };

  return (
    <div className="flex items-center gap-2 mt-3 pt-3 border-t border-slate-100" data-testid="share-result">
      <span className="text-xs text-slate-400 mr-1">Share:</span>
      {typeof navigator.share === 'function' && (
        <button onClick={handleNativeShare} className="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-slate-700 transition-colors" title="Share" data-testid="share-native-btn">
          <Share2 className="h-3.5 w-3.5" />
        </button>
      )}
      <button onClick={handleCopy} className="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-slate-700 transition-colors" title="Copy" data-testid="share-copy-btn">
        {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
      </button>
      <button onClick={handleTwitter} className="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-slate-700 transition-colors" title="Share on X" data-testid="share-twitter-btn">
        <Twitter className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
