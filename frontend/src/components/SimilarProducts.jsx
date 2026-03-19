import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Package, TrendingUp, ArrowRight } from 'lucide-react';
import { API_URL } from '@/lib/config';

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return 'just now';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return '1 day ago';
  if (days < 7) return `${days} days ago`;
  return `${Math.floor(days / 7)}w ago`;
}

export default function SimilarProducts({ productId, productName }) {
  const [similar, setSimilar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    (async () => {
      try {
        const token = localStorage.getItem('trendscout_token');
        const res = await fetch(`${API_URL}/api/products/${productId}/similar?limit=6`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (res.ok) {
          const data = await res.json();
          setSimilar(data.similar_products || []);
        }
      } catch {
      } finally {
        setLoading(false);
      }
    })();
  }, [productId]);

  if (loading || similar.length === 0) return null;

  return (
    <Card className="border-slate-200 shadow-sm" data-testid="similar-products">
      <CardHeader className="border-b border-slate-100 pb-4">
        <CardTitle className="font-manrope text-lg font-semibold text-slate-900 flex items-center gap-2">
          <Package className="h-5 w-5 text-indigo-600" />
          Similar Products
        </CardTitle>
        <p className="text-sm text-slate-500 mt-1">Products related to {productName}</p>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {similar.map((p) => (
            <Link
              key={p.id}
              to={`/trending/${p.slug || slugify(p.product_name)}`}
              className="group block rounded-xl border border-slate-100 overflow-hidden hover:border-indigo-200 hover:shadow-md transition-all duration-200"
              data-testid={`similar-product-${p.id}`}
            >
              <div className="relative h-28 bg-slate-50 overflow-hidden">
                {p.image_url ? (
                  <img
                    src={p.image_url}
                    alt={p.product_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Package className="h-8 w-8 text-slate-200" />
                  </div>
                )}
                <div className="absolute top-1.5 left-1.5 bg-white/90 backdrop-blur-sm rounded-md px-1.5 py-0.5 shadow-sm">
                  <span className="font-mono text-xs font-bold text-indigo-600">{p.launch_score}</span>
                </div>
              </div>
              <div className="p-2.5">
                <h4 className="text-xs font-semibold text-slate-800 line-clamp-2 group-hover:text-indigo-600 transition-colors leading-tight">
                  {p.product_name}
                </h4>
                <div className="flex items-center justify-between mt-1.5">
                  <span className="text-[10px] text-slate-400">{p.category}</span>
                  <Badge className="text-[9px] bg-emerald-50 text-emerald-600 border-emerald-200">
                    {p.margin_percent}% margin
                  </Badge>
                </div>
                {p.last_updated && (
                  <p className="text-[9px] text-slate-300 mt-1">{timeAgo(p.last_updated)}</p>
                )}
              </div>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
