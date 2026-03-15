import React from 'react';
import { Button } from '@/components/ui/button';
import { Share2, Twitter, Link2, Check } from 'lucide-react';

export default function ShareSnippet({ productName, score, category, productId }) {
  const [copied, setCopied] = React.useState(false);
  const siteUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
  const shareUrl = `${siteUrl}/p/${productId}`;
  const shareText = `${productName} scored ${score}/100 on TrendScout's 7-Signal Launch Score! ${category ? `Category: ${category}` : ''} Check it out:`;

  const shareTwitter = () => {
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`, '_blank');
  };

  const copyLink = () => {
    navigator.clipboard.writeText(`${shareText} ${shareUrl}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-2" data-testid="share-snippet">
      <Button
        size="sm"
        variant="outline"
        onClick={shareTwitter}
        className="text-xs border-slate-200 text-slate-600 hover:bg-sky-50 hover:text-sky-600 hover:border-sky-200"
        data-testid="share-twitter"
      >
        <Twitter className="h-3 w-3 mr-1" /> Tweet
      </Button>
      <Button
        size="sm"
        variant="outline"
        onClick={copyLink}
        className="text-xs border-slate-200 text-slate-600 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200"
        data-testid="share-copy-link"
      >
        {copied ? <><Check className="h-3 w-3 mr-1" /> Copied!</> : <><Link2 className="h-3 w-3 mr-1" /> Copy Link</>}
      </Button>
    </div>
  );
}
