import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  ArrowLeft, Clock, Tag, Sparkles, TrendingUp, Package, ChevronRight,
  Loader2, BookOpen, Share2, Zap,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function BlogPostPage() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/blog/posts/${slug}`)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(d => { setPost(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [slug]);

  // Add JSON-LD structured data
  useEffect(() => {
    if (!post) return;
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": post.title,
      "description": post.meta_description || '',
      "datePublished": post.published_at,
      "author": { "@type": "Organization", "name": "TrendScout" },
      "publisher": { "@type": "Organization", "name": "TrendScout" },
      "url": `https://www.trendscout.click/blog/${slug}`,
    });
    document.head.appendChild(script);
    return () => document.head.removeChild(script);
  }, [post, slug]);

  if (loading) {
    return (
      <LandingLayout>
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </LandingLayout>
    );
  }

  if (!post) {
    return (
      <LandingLayout>
        <div className="text-center py-20 max-w-lg mx-auto px-6">
          <BookOpen className="h-12 w-12 text-slate-300 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-slate-900">Post not found</h1>
          <Link to="/blog" className="text-indigo-600 text-sm mt-2 block">Back to Blog</Link>
        </div>
      </LandingLayout>
    );
  }

  const content = post.content || {};
  const canonicalUrl = `https://www.trendscout.click/blog/${slug}`;

  return (
    <LandingLayout>
      <Helmet>
        <title>{`${post.title} — TrendScout Blog`}</title>
        <meta name="description" content={post.meta_description || ''} />
        <meta property="og:title" content={post.title} />
        <meta property="og:description" content={post.meta_description || ''} />
        <meta property="og:type" content="article" />
        <meta property="og:url" content={canonicalUrl} />
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:title" content={post.title} />
        <link rel="canonical" href={canonicalUrl} />
      </Helmet>

      <article className="mx-auto max-w-3xl px-6 py-12" data-testid="blog-post-page">
        {/* Back */}
        <Link to="/blog" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-600 mb-6 transition-colors">
          <ArrowLeft className="h-4 w-4" /> Back to Blog
        </Link>

        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center gap-3 mb-4 flex-wrap">
            <Badge className="bg-indigo-100 text-indigo-700 border-0 rounded-full text-xs">
              <Tag className="h-3 w-3 mr-1" />{post.category}
            </Badge>
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {post.published_at ? formatDistanceToNow(new Date(post.published_at), { addSuffix: true }) : ''}
            </span>
            {post.ai_generated && (
              <Badge className="bg-violet-100 text-violet-700 border-0 rounded-full text-xs">
                <Sparkles className="h-3 w-3 mr-1" />AI Generated
              </Badge>
            )}
          </div>
          <h1 className="font-manrope text-3xl sm:text-4xl font-extrabold text-slate-900 leading-tight">
            {post.title}
          </h1>
        </header>

        {/* Intro */}
        {content.intro && (
          <p className="text-lg text-slate-600 leading-relaxed mb-8 border-l-4 border-indigo-300 pl-4"
             dangerouslySetInnerHTML={{ __html: content.intro.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
        )}

        {/* Featured Products */}
        {post.products && post.products.length > 0 && (
          <div className="mb-10">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-indigo-500" />
              Featured Products
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {post.products.map((p) => (
                <Link
                  key={p.id}
                  to={`/trending/${p.slug}`}
                  className="group block rounded-xl border border-slate-100 overflow-hidden hover:border-indigo-200 hover:shadow-lg transition-all"
                  data-testid={`blog-product-${p.id}`}
                >
                  <div className="h-28 bg-slate-50 overflow-hidden">
                    {p.image_url ? (
                      <img src={p.image_url} alt={p.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center"><Package className="h-8 w-8 text-slate-300" /></div>
                    )}
                  </div>
                  <div className="p-3">
                    <h3 className="text-sm font-semibold text-slate-900 line-clamp-1 group-hover:text-indigo-600 transition-colors">{p.product_name}</h3>
                    <div className="flex items-center justify-between mt-2">
                      <Badge className={`text-[10px] rounded-full border-0 ${
                        p.launch_score >= 70 ? 'bg-emerald-50 text-emerald-700' : p.launch_score >= 50 ? 'bg-amber-50 text-amber-700' : 'bg-slate-50 text-slate-600'
                      }`}>
                        Score: {p.launch_score}
                      </Badge>
                      <span className="text-xs text-emerald-600 font-semibold">{p.margin_percent}% margin</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Article Sections */}
        {content.sections && content.sections.map((section, i) => (
          <section key={i} className="mb-8" data-testid={`blog-section-${i}`}>
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-3">{section.heading}</h2>
            <div className="text-slate-600 leading-relaxed space-y-3 prose-sm">
              {section.content.split('\n').filter(Boolean).map((para, j) => (
                <p key={j} dangerouslySetInnerHTML={{ __html: para.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
              ))}
            </div>
          </section>
        ))}

        {/* Product Highlights */}
        {content.product_highlights && content.product_highlights.length > 0 && (
          <div className="mb-8">
            <h2 className="font-manrope text-xl font-bold text-slate-900 mb-4">Product Highlights</h2>
            <div className="space-y-3">
              {content.product_highlights.map((ph, i) => (
                <Card key={i} className="border-slate-200">
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-slate-900 text-sm">{ph.name}</h3>
                    <p className="text-xs text-indigo-600 mt-1">{ph.why_trending}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{ph.opportunity}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Conclusion */}
        {content.conclusion && (
          <div className="p-6 bg-gradient-to-r from-indigo-50 to-violet-50 rounded-2xl border border-indigo-100 mb-8">
            <p className="text-slate-700 leading-relaxed">{content.conclusion}</p>
          </div>
        )}

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-8">
            {post.tags.map(tag => (
              <span key={tag} className="text-xs text-slate-500 bg-slate-100 px-3 py-1 rounded-full">#{tag}</span>
            ))}
          </div>
        )}

        {/* CTA */}
        <div className="text-center py-10 bg-gradient-to-r from-slate-50 to-indigo-50 rounded-2xl">
          <h3 className="font-manrope text-xl font-bold text-slate-900 mb-2">Want deeper product intelligence?</h3>
          <p className="text-slate-500 text-sm mb-5 max-w-md mx-auto">
            Get AI launch simulations, supplier data, ad creatives, and trend alerts for every product.
          </p>
          <Link to="/signup" className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold px-6 py-2.5 rounded-xl hover:shadow-lg transition-shadow" data-testid="blog-cta">
            <Zap className="h-4 w-4" /> Start Free Trial
          </Link>
        </div>
      </article>
    </LandingLayout>
  );
}
