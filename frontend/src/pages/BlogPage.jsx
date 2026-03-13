import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Badge } from '@/components/ui/badge';
import {
  BookOpen, Clock, Tag, ArrowRight, Loader2, Sparkles, TrendingUp,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function BlogPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/blog/posts`)
      .then(r => r.json())
      .then(d => { setPosts(d.posts || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <LandingLayout>
      <Helmet>
        <title>TrendScout Blog — Trending Product Insights & Ecommerce Intelligence</title>
        <meta name="description" content="Weekly AI-curated insights on trending ecommerce products. Discover winning dropshipping products, TikTok viral trends, and market analysis." />
        <meta property="og:title" content="TrendScout Blog — Trending Product Intelligence" />
        <meta property="og:type" content="blog" />
        <link rel="canonical" href="https://www.trendscout.click/blog" />
      </Helmet>

      <div className="mx-auto max-w-4xl px-6 py-12" data-testid="blog-page">
        {/* Hero */}
        <div className="text-center mb-12">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-200/50">
            <BookOpen className="h-7 w-7 text-white" />
          </div>
          <h1 className="font-manrope text-4xl font-extrabold text-slate-900">
            Trend Intelligence Blog
          </h1>
          <p className="mt-3 text-slate-500 max-w-lg mx-auto">
            AI-curated weekly insights on the hottest ecommerce products and emerging market trends.
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <h3 className="font-manrope text-lg font-semibold text-slate-900">No posts yet</h3>
            <p className="text-slate-500 mt-2">Fresh trend intelligence articles are coming soon.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {posts.map((post, i) => (
              <Link
                key={post.id}
                to={`/blog/${post.slug}`}
                className="block group"
                data-testid={`blog-post-card-${i}`}
              >
                <article className={`rounded-2xl border overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                  i === 0 ? 'border-indigo-200 bg-gradient-to-r from-indigo-50/50 to-violet-50/30' : 'border-slate-200 bg-white'
                }`}>
                  <div className="p-6 sm:p-8">
                    {/* Category & Date */}
                    <div className="flex items-center gap-3 mb-3">
                      <Badge className="bg-indigo-100 text-indigo-700 border-0 rounded-full text-xs">
                        <Tag className="h-3 w-3 mr-1" />{post.category}
                      </Badge>
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatTimeAgo(post.published_at)}
                      </span>
                      {post.ai_generated && (
                        <Badge className="bg-violet-100 text-violet-700 border-0 rounded-full text-xs">
                          <Sparkles className="h-3 w-3 mr-1" />AI Generated
                        </Badge>
                      )}
                    </div>

                    {/* Title */}
                    <h2 className={`font-manrope font-bold text-slate-900 group-hover:text-indigo-600 transition-colors ${
                      i === 0 ? 'text-2xl' : 'text-xl'
                    }`}>
                      {post.title}
                    </h2>

                    {/* Description */}
                    <p className="mt-2 text-slate-500 text-sm line-clamp-2">
                      {post.meta_description}
                    </p>

                    {/* Product thumbnails */}
                    {post.products && post.products.length > 0 && (
                      <div className="flex items-center gap-2 mt-4">
                        <div className="flex -space-x-2">
                          {post.products.slice(0, 4).map((p, j) => (
                            <div key={j} className="w-8 h-8 rounded-lg border-2 border-white overflow-hidden bg-slate-100">
                              {p.image_url ? (
                                <img src={p.image_url} alt="" className="w-full h-full object-cover" />
                              ) : null}
                            </div>
                          ))}
                        </div>
                        <span className="text-xs text-slate-400 ml-1">{post.products.length} products featured</span>
                      </div>
                    )}

                    {/* Tags */}
                    {post.tags && post.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {post.tags.slice(0, 4).map(tag => (
                          <span key={tag} className="text-[10px] text-slate-400 bg-slate-50 px-2 py-0.5 rounded-full">#{tag}</span>
                        ))}
                      </div>
                    )}

                    {/* Read more */}
                    <div className="flex items-center gap-1 mt-4 text-indigo-600 text-sm font-semibold group-hover:gap-2 transition-all">
                      Read full analysis <ArrowRight className="h-4 w-4" />
                    </div>
                  </div>
                </article>
              </Link>
            ))}
          </div>
        )}
      </div>
    </LandingLayout>
  );
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return '';
  try {
    return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
  } catch {
    return '';
  }
}
