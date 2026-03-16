import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, Zap, Calendar, ArrowRight, Share2,
  Loader2, CheckCircle, Eye, Tag, Star, Copy, Twitter,
  ChevronRight, BookOpen,
} from 'lucide-react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

export default function WeeklyDigestPage() {
  const { digestId } = useParams();
  const [digest, setDigest] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const url = digestId
          ? `${API}/api/digest/${digestId}`
          : `${API}/api/digest/latest`;
        const res = await fetch(url);
        if (res.ok) setDigest(await res.json());
      } catch {}
      setLoading(false);
    })();
  }, [digestId]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
    </div>
  );

  if (!digest) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
      <BookOpen className="h-12 w-12 text-slate-300 mb-4" />
      <p className="text-slate-500">No weekly digest available yet.</p>
      <Link to="/trending" className="text-indigo-600 hover:underline text-sm mt-2">Browse trending products</Link>
    </div>
  );

  const shareUrl = `${window.location.origin}/weekly-digest`;
  const shareText = `${digest.title} — AI-scored trending products for dropshipping`;

  return (
    <>
      <Helmet>
        <title>{digest.seo?.title || digest.title}</title>
        <meta name="description" content={digest.seo?.description || digest.intro} />
        <meta property="og:title" content={digest.seo?.title || digest.title} />
        <meta property="og:description" content={digest.seo?.description || digest.intro} />
        {digest.seo?.og_image && <meta property="og:image" content={digest.seo.og_image} />}
        <link rel="canonical" href={shareUrl} />
      </Helmet>

      <div className="min-h-screen bg-slate-50" data-testid="weekly-digest-page">
        {/* Nav */}
        <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
          <Link to="/" className="text-lg font-bold text-slate-900">TrendScout</Link>
          <div className="flex items-center gap-3">
            <Link to="/trending" className="text-xs text-slate-500 hover:text-indigo-600">Trending</Link>
            <Link to="/weekly-digest/archive" className="text-xs text-slate-500 hover:text-indigo-600">Archive</Link>
            <Link to="/register">
              <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700" data-testid="digest-signup-btn">Start Free Trial</Button>
            </Link>
          </div>
        </nav>

        <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
          {/* Header */}
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-3">
              <Calendar className="h-4 w-4 text-indigo-500" />
              <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wide">{digest.week_label}</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-slate-900">{digest.title}</h1>
            <p className="text-sm text-slate-500 mt-3 max-w-2xl mx-auto">{digest.intro}</p>
            <div className="flex items-center justify-center gap-3 mt-4">
              <Badge className="bg-indigo-50 text-indigo-700 border-indigo-200">
                <Star className="h-3 w-3 mr-1" /> Avg Score: {digest.avg_score}/100
              </Badge>
              <Badge className="bg-slate-50 text-slate-600 border-slate-200">
                {digest.categories_featured?.length || 0} categories
              </Badge>
            </div>
          </div>

          {/* Share Bar */}
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => { window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`, '_blank'); }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-50 text-sky-700 border border-sky-200 text-xs font-medium hover:bg-sky-100 transition-colors"
              data-testid="share-twitter"
            >
              <Twitter className="h-3.5 w-3.5" /> Tweet
            </button>
            <button
              onClick={() => { navigator.clipboard.writeText(shareUrl); toast.success('Link copied!'); }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 text-slate-600 border border-slate-200 text-xs font-medium hover:bg-slate-100 transition-colors"
              data-testid="share-copy"
            >
              <Copy className="h-3.5 w-3.5" /> Copy Link
            </button>
          </div>

          {/* Products */}
          <div className="space-y-5" data-testid="digest-products">
            {(digest.products || []).map((p, idx) => (
              <Card key={p.id || idx} className="border-0 shadow-lg overflow-hidden hover:shadow-xl transition-shadow" data-testid="digest-product-card">
                <CardContent className="p-0">
                  <div className="flex flex-col sm:flex-row">
                    {/* Image */}
                    <div className="sm:w-56 h-48 sm:h-auto bg-slate-100 relative flex-shrink-0">
                      {p.image_url ? (
                        <img src={p.image_url} alt={p.product_name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Eye className="h-8 w-8 text-slate-300" />
                        </div>
                      )}
                      <div className={`absolute top-3 left-3 h-10 w-10 rounded-xl flex items-center justify-center text-sm font-black text-white ${
                        p.rank === 1 ? 'bg-amber-500' : p.rank === 2 ? 'bg-slate-500' : p.rank === 3 ? 'bg-orange-500' : 'bg-indigo-500'
                      }`}>
                        #{p.rank}
                      </div>
                    </div>
                    {/* Content */}
                    <div className="flex-1 p-5 space-y-3">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="text-base font-bold text-slate-900">{p.product_name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            {p.category && <Badge className="bg-slate-50 text-slate-600 border-slate-200 text-[10px]"><Tag className="h-3 w-3 mr-0.5" /> {p.category}</Badge>}
                            {p.trend_stage && <Badge className="bg-amber-50 text-amber-700 border-amber-200 text-[10px] capitalize">{p.trend_stage}</Badge>}
                            {p.verified_winner && <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px]"><CheckCircle className="h-3 w-3 mr-0.5" /> Winner</Badge>}
                          </div>
                        </div>
                        <div className={`text-2xl font-black ${p.launch_score >= 70 ? 'text-emerald-600' : p.launch_score >= 50 ? 'text-amber-600' : 'text-red-500'}`}>
                          {p.launch_score}
                        </div>
                      </div>
                      {p.ai_summary && <p className="text-xs text-slate-500 line-clamp-2">{p.ai_summary}</p>}
                      <p className="text-xs text-indigo-600 font-medium">{p.insight}</p>
                      <div className="flex items-center gap-4 text-xs text-slate-400">
                        {p.estimated_retail_price && <span>Est. ${p.estimated_retail_price}</span>}
                        {p.competition_level && <span>Competition: {p.competition_level}</span>}
                        {p.tiktok_views > 0 && <span>TikTok: {formatNum(p.tiktok_views)} views</span>}
                      </div>
                      <Link to={`/trending/${p.slug || p.id}`} className="inline-flex items-center gap-1 text-xs text-indigo-600 font-semibold hover:underline" data-testid={`view-product-${p.rank}`}>
                        View Full Analysis <ChevronRight className="h-3 w-3" />
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Bottom CTA */}
          <Card className="border-2 border-indigo-200 bg-indigo-50/50 shadow-none">
            <CardContent className="py-8 text-center">
              <h2 className="text-xl font-bold text-slate-900 mb-2">Get the full picture</h2>
              <p className="text-sm text-slate-500 mb-4">Access 7-signal breakdowns, profitability simulators, ad intelligence, and more.</p>
              <Link to="/register">
                <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="digest-bottom-cta">
                  <Zap className="h-4 w-4 mr-1.5" /> Start Free Trial
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Archive Link */}
          <div className="text-center">
            <Link to="/weekly-digest/archive" className="text-sm text-indigo-600 hover:underline font-medium" data-testid="view-archive-link">
              View past weekly digests <ArrowRight className="h-3 w-3 inline ml-1" />
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}

function formatNum(n) {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n?.toString() || '0';
}
