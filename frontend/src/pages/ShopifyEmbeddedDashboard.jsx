import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp, Package, Zap, BarChart3, ArrowRight,
  Loader2, ExternalLink, Store, AlertTriangle, CheckCircle2,
  Radar, ShoppingBag,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

function ScoreBadge({ score }) {
  const color = score >= 80 ? 'bg-green-100 text-green-700 border-green-200'
    : score >= 60 ? 'bg-blue-100 text-blue-700 border-blue-200'
    : score >= 40 ? 'bg-amber-100 text-amber-700 border-amber-200'
    : 'bg-red-100 text-red-700 border-red-200';
  return (
    <Badge variant="outline" className={`font-mono text-xs font-bold ${color}`}>
      {score}
    </Badge>
  );
}

function TrendLabel({ label }) {
  const colors = {
    exploding: 'bg-red-50 text-red-600 border-red-200',
    rising: 'bg-amber-50 text-amber-600 border-amber-200',
    stable: 'bg-slate-50 text-slate-600 border-slate-200',
    declining: 'bg-blue-50 text-blue-600 border-blue-200',
  };
  return (
    <Badge variant="outline" className={`text-[10px] capitalize ${colors[label] || colors.stable}`}>
      {label || 'stable'}
    </Badge>
  );
}

function ProductRow({ product, onPush, pushing }) {
  return (
    <div className="flex items-center gap-3 p-3 border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors" data-testid={`embedded-product-${product.id}`}>
      {product.image_url ? (
        <img src={product.image_url} alt="" className="w-10 h-10 rounded-lg object-cover flex-shrink-0 bg-slate-100"  loading="lazy" /> 
      ) : (
        <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
          <Package className="h-4 w-4 text-slate-400" />
        </div>
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-900 truncate">{product.product_name}</p>
        <div className="flex items-center gap-2 mt-0.5">
          <ScoreBadge score={product.launch_score} />
          <TrendLabel label={product.early_trend_label} />
          <span className="text-[10px] text-slate-400">{product.category}</span>
        </div>
      </div>
      <Button
        size="sm"
        variant="outline"
        className="text-xs h-7 gap-1 flex-shrink-0"
        onClick={() => onPush(product.id)}
        disabled={pushing === product.id}
        data-testid={`push-btn-${product.id}`}
      >
        {pushing === product.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <Store className="h-3 w-3" />}
        Push
      </Button>
    </div>
  );
}

export default function ShopifyEmbeddedDashboard() {
  const [searchParams] = useSearchParams();
  const shop = searchParams.get('shop') || '';
  const host = searchParams.get('host') || '';

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pushing, setPushing] = useState(null);
  const [sessionToken, setSessionToken] = useState(null);
  const [error, setError] = useState(null);

  // Dynamically load Shopify App Bridge when inside iframe
  useEffect(() => {
    if (!shop || !host) return;
    // Only load if inside an iframe (actual Shopify Admin)
    const inIframe = window.self !== window.top;
    if (!inIframe) return;

    // Inject meta tag and script
    const meta = document.createElement('meta');
    meta.name = 'shopify-api-key';
    meta.content = process.env.REACT_APP_SHOPIFY_CLIENT_ID || '';
    document.head.appendChild(meta);

    const script = document.createElement('script');
    script.src = 'https://cdn.shopify.com/shopifycloud/app-bridge.js';
    script.onload = () => {
      // After App Bridge loads, initialize session
      initSession();
    };
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(meta);
      document.head.removeChild(script);
    };
  }, [shop, host]);

  // Initialize session from Shopify App Bridge
  async function initSession() {
    try {
      if (window.shopify) {
        const token = await window.shopify.idToken();
        const res = await fetch(`${API_URL}/api/shopify/app/session-token`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_token: token }),
        });
        if (res.ok) {
          const d = await res.json();
          setSessionToken(d.token);
        }
      }
    } catch {
      // App Bridge not available — proceed without session token
    }
  }

  // Fetch dashboard data
  useEffect(() => {
    async function fetchData() {
      if (!shop) { setLoading(false); return; }
      try {
        const res = await fetch(`${API_URL}/api/shopify/app/embedded/dashboard?shop=${encodeURIComponent(shop)}`);
        if (res.ok) {
          setData(await res.json());
        } else {
          setError('Failed to load dashboard data');
        }
      } catch {
        setError('Connection error');
      }
      setLoading(false);
    }
    fetchData();
  }, [shop]);

  // Push product to store
  const handlePush = useCallback(async (productId) => {
    if (!sessionToken) {
      toast.error('Please connect your TrendScout account first');
      return;
    }
    setPushing(productId);
    try {
      const res = await fetch(`${API_URL}/api/shopify/push-product`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionToken}`,
        },
        body: JSON.stringify({ product_id: productId }),
      });
      const d = await res.json();
      if (d.success) {
        toast.success(`Pushed to store as draft`);
      } else {
        toast.error(d.error || 'Push failed');
      }
    } catch {
      toast.error('Connection error');
    }
    setPushing(null);
  }, [sessionToken]);

  if (!shop) {
    return (
      <div className="p-8 text-center" data-testid="embedded-no-shop">
        <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-3" />
        <h2 className="font-semibold text-slate-900">No Shop Detected</h2>
        <p className="text-sm text-slate-500 mt-1">This page is designed to run inside Shopify Admin.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-16">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center" data-testid="embedded-error">
        <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-3" />
        <p className="text-sm text-slate-500">{error}</p>
      </div>
    );
  }

  const { trending_products = [], recent_exports = [], radar_detections = [], connected } = data || {};

  return (
    <div className="min-h-screen bg-white p-4 max-w-3xl mx-auto" data-testid="embedded-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-indigo-600" />
          <h1 className="text-lg font-bold text-slate-900">TrendScout</h1>
          <Badge className="bg-indigo-50 text-indigo-600 border-indigo-200 text-[10px]">for {shop.split('.')[0]}</Badge>
        </div>
        {!connected && (
          <a href={`${API_URL.replace('/api','')}/settings/connections`} target="_top">
            <Button size="sm" className="text-xs bg-indigo-600 hover:bg-indigo-700 gap-1" data-testid="connect-account-btn">
              Connect Account <ExternalLink className="h-3 w-3" />
            </Button>
          </a>
        )}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <Card className="border-slate-200">
          <CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-indigo-600" data-testid="stat-trending">{trending_products.length}</p>
            <p className="text-[10px] text-slate-500 mt-0.5">Trending Products</p>
          </CardContent>
        </Card>
        <Card className="border-slate-200">
          <CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-green-600" data-testid="stat-exports">{recent_exports.length}</p>
            <p className="text-[10px] text-slate-500 mt-0.5">Recent Exports</p>
          </CardContent>
        </Card>
        <Card className="border-slate-200">
          <CardContent className="p-3 text-center">
            <p className="text-2xl font-bold text-amber-600" data-testid="stat-radar">{radar_detections.length}</p>
            <p className="text-[10px] text-slate-500 mt-0.5">Radar Alerts</p>
          </CardContent>
        </Card>
      </div>

      {/* Trending Products */}
      <Card className="border-slate-200 mb-4">
        <div className="flex items-center justify-between p-3 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-1.5">
            <Zap className="h-4 w-4 text-indigo-500" /> Top Products to Launch
          </h2>
          <a href={`${API_URL.replace('/api','')}/discover`} target="_top">
            <Button variant="ghost" size="sm" className="text-xs text-indigo-600 h-7 gap-1">
              View All <ArrowRight className="h-3 w-3" />
            </Button>
          </a>
        </div>
        <CardContent className="p-0">
          {trending_products.length > 0 ? (
            trending_products.map(p => (
              <ProductRow key={p.id} product={p} onPush={handlePush} pushing={pushing} />
            ))
          ) : (
            <div className="p-6 text-center text-sm text-slate-400">No trending products found</div>
          )}
        </CardContent>
      </Card>

      {/* Radar Detections */}
      {radar_detections.length > 0 && (
        <Card className="border-slate-200 mb-4">
          <div className="flex items-center justify-between p-3 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-1.5">
              <Radar className="h-4 w-4 text-amber-500" /> Radar Detections
            </h2>
          </div>
          <CardContent className="p-0">
            {radar_detections.map(p => (
              <div key={p.id} className="flex items-center gap-3 p-3 border-b border-slate-100 last:border-0" data-testid={`radar-${p.id}`}>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 truncate">{p.product_name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <ScoreBadge score={p.launch_score} />
                    <span className="text-[10px] text-slate-400">{p.category}</span>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Recent Exports */}
      {recent_exports.length > 0 && (
        <Card className="border-slate-200">
          <div className="p-3 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-1.5">
              <ShoppingBag className="h-4 w-4 text-green-500" /> Recent Exports
            </h2>
          </div>
          <CardContent className="p-0">
            {recent_exports.map(e => (
              <div key={e.id} className="flex items-center justify-between p-3 border-b border-slate-100 last:border-0">
                <div>
                  <p className="text-sm text-slate-700">{e.product_id?.slice(0, 8)}...</p>
                  <p className="text-[10px] text-slate-400">{e.exported_at?.slice(0, 10)}</p>
                </div>
                <Badge variant="outline" className="text-[10px] bg-green-50 text-green-600 border-green-200">
                  <CheckCircle2 className="h-3 w-3 mr-1" /> {e.status || 'draft'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Footer */}
      <div className="mt-6 text-center">
        <a href={`${API_URL.replace('/api','')}/dashboard`} target="_top" className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
          Open Full TrendScout Dashboard
        </a>
      </div>
    </div>
  );
}
