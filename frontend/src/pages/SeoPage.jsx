import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import LandingLayout from '@/components/layouts/LandingLayout';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, Package, Lock, ArrowRight, TrendingUp, Sparkles } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const TREND_BADGE = {
  Exploding: 'bg-red-100 text-red-700 border-red-200',
  Emerging: 'bg-orange-100 text-orange-700 border-orange-200',
  Rising: 'bg-amber-100 text-amber-700 border-amber-200',
  Stable: 'bg-blue-100 text-blue-700 border-blue-200',
  Declining: 'bg-slate-100 text-slate-500 border-slate-200',
};

export default function SeoPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/api/public/seo/${slug}`)
      .then((r) => {
        if (!r.ok) throw new Error('Page not found');
        return r.json();
      })
      .then(setData)
      .catch(() => setError('Page not found'))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <LandingLayout>
        <div className="flex justify-center items-center min-h-[50vh]">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </LandingLayout>
    );
  }

  if (error || !data) {
    return (
      <LandingLayout>
        <div className="text-center py-24">
          <h1 className="text-2xl font-bold text-slate-900">Page Not Found</h1>
          <p className="text-slate-500 mt-2">The page you're looking for doesn't exist.</p>
        </div>
      </LandingLayout>
    );
  }

  return (
    <LandingLayout>
      <div className="mx-auto max-w-7xl px-6 py-16" data-testid="seo-page">
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto mb-12">
          <Badge className="bg-indigo-50 text-indigo-700 border-indigo-100 mb-4">
            <TrendingUp className="h-3 w-3 mr-1" /> Updated Daily
          </Badge>
          <h1 className="font-manrope text-3xl font-bold text-slate-900 sm:text-4xl">
            {data.title}
          </h1>
          <p className="mt-4 text-lg text-slate-600">{data.description}</p>
        </div>

        {/* Product Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.products.map((p, i) => (
            <div
              key={p.id}
              className="group bg-white rounded-2xl border border-slate-200 overflow-hidden hover:border-indigo-200 hover:shadow-lg transition-all duration-300"
              data-testid={`seo-product-${p.id}`}
            >
              {/* Image */}
              <div className="aspect-[4/3] bg-slate-100 relative overflow-hidden">
                {p.image_url ? (
                  <img src={p.image_url} alt={p.product_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <Package className="h-12 w-12 text-slate-300" />
                  </div>
                )}
                <Badge className={`absolute top-3 left-3 text-xs border ${TREND_BADGE[p.trend_stage] || TREND_BADGE.Stable}`}>
                  {p.trend_stage}
                </Badge>
              </div>
              {/* Content */}
              <div className="p-5">
                <h3 className="font-semibold text-slate-900 line-clamp-2 text-sm">{p.product_name}</h3>
                <p className="text-xs text-slate-500 mt-1">{p.category}</p>
                <div className="flex items-center justify-between mt-4">
                  <div>
                    <p className="text-2xl font-bold font-mono text-indigo-600">{p.launch_score}</p>
                    <p className="text-[10px] text-slate-400">Launch Score</p>
                  </div>
                  {/* Gated content */}
                  {i < 3 ? (
                    <div>
                      <p className="text-lg font-bold font-mono text-emerald-600">{p.success_probability}%</p>
                      <p className="text-[10px] text-slate-400">Success Prob.</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <Lock className="h-5 w-5 text-slate-300 mx-auto" />
                      <p className="text-[10px] text-slate-400">Sign up to see</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <div className="inline-block bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl p-8 sm:p-10">
            <Sparkles className="h-8 w-8 text-amber-300 mx-auto mb-3" />
            <h2 className="text-2xl font-bold text-white mb-2">
              Unlock Full Product Intelligence
            </h2>
            <p className="text-indigo-200 mb-6 max-w-md mx-auto">
              Get detailed profit estimates, supplier matches, and AI-generated ads for every product.
            </p>
            <Link to="/signup">
              <Button size="lg" className="bg-white text-indigo-700 hover:bg-indigo-50 font-semibold px-8" data-testid="seo-cta-btn">
                Start Free — No Credit Card
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </LandingLayout>
  );
}
