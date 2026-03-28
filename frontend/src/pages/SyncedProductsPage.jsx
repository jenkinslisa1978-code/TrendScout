import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  RefreshCw, Package, ExternalLink, Loader2, ShoppingBag,
  Search, ArrowUpDown, Image as ImageIcon, Link2, Store,
  Filter,
} from 'lucide-react';
import { toast } from 'sonner';
import { apiGet, apiPost } from '@/lib/api';
import SyncHistory from '@/components/SyncHistory';

const PLATFORM_INFO = {
  shopify: { name: 'Shopify', color: 'emerald', icon: '🟢', syncEndpoint: '/api/shopify/sync-products' },
  etsy: { name: 'Etsy', color: 'orange', icon: '🟠', syncEndpoint: '/api/sync/etsy/products' },
  woocommerce: { name: 'WooCommerce', color: 'purple', icon: '🟣', syncEndpoint: '/api/sync/woocommerce/products' },
  amazon_seller: { name: 'Amazon', color: 'amber', icon: '🟠', syncEndpoint: '/api/sync/amazon/products' },
};

export default function SyncedProductsPage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [platformCounts, setPlatformCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(null);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('synced_at');
  const [filterPlatform, setFilterPlatform] = useState('all');

  const fetchProducts = useCallback(async () => {
    try {
      // Fetch from unified endpoint first
      const res = await apiGet('/api/sync/products');
      const data = await res.json();
      if (data.success) {
        setProducts(data.products || []);
        setPlatformCounts(data.by_platform || {});
        setLoading(false);
        return;
      }
    } catch {}

    // Fallback: fetch Shopify products
    try {
      const res = await apiGet('/api/shopify/synced-products');
      const data = await res.json();
      if (data.success) {
        const shopifyProducts = (data.products || []).map((p) => ({
          ...p,
          platform: 'shopify',
          platform_id: String(p.shopify_id),
        }));
        setProducts(shopifyProducts);
        setPlatformCounts({ shopify: shopifyProducts.length });
      }
    } catch {}

    setLoading(false);
  }, []);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const handleSync = async (platform) => {
    const info = PLATFORM_INFO[platform];
    if (!info) return;

    setSyncing(platform);
    try {
      const res = await apiPost(info.syncEndpoint);
      const data = await res.json();
      if (data.success) {
        toast.success(`Synced ${data.synced_count || 0} products from ${info.name}`);
        fetchProducts();
      } else {
        toast.error(data.detail || data.error || `${info.name} sync failed`);
      }
    } catch {
      toast.error(`Failed to sync from ${info.name}`);
    } finally {
      setSyncing(null);
    }
  };

  const filtered = products
    .filter((p) => filterPlatform === 'all' || p.platform === filterPlatform)
    .filter((p) =>
      !search ||
      p.title?.toLowerCase().includes(search.toLowerCase()) ||
      p.product_type?.toLowerCase().includes(search.toLowerCase()) ||
      p.platform?.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'price') return parseFloat(b.price || 0) - parseFloat(a.price || 0);
      if (sortBy === 'quantity') return (b.quantity || b.inventory_quantity || 0) - (a.quantity || a.inventory_quantity || 0);
      return (b.synced_at || '').localeCompare(a.synced_at || '');
    });

  const activePlatforms = Object.keys(platformCounts);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]" data-testid="synced-products-loading">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="synced-products-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Synced Products</h1>
            <p className="text-sm text-slate-500 mt-1">
              {products.length > 0
                ? `${products.length} products across ${activePlatforms.length} platform${activePlatforms.length !== 1 ? 's' : ''}`
                : 'Products from your connected stores'}
            </p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            {activePlatforms.map((plat) => {
              const info = PLATFORM_INFO[plat];
              if (!info) return null;
              return (
                <Button
                  key={plat}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSync(plat)}
                  disabled={syncing === plat}
                  data-testid={`sync-${plat}-btn`}
                >
                  {syncing === plat ? (
                    <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  ) : (
                    <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
                  )}
                  Sync {info.name}
                </Button>
              );
            })}
          </div>
        </div>

        {/* Platform summary cards */}
        {activePlatforms.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <button
              onClick={() => setFilterPlatform('all')}
              className={`rounded-lg border p-3 text-left transition-colors ${
                filterPlatform === 'all' ? 'border-indigo-300 bg-indigo-50' : 'border-slate-200 hover:border-slate-300'
              }`}
              data-testid="filter-all"
            >
              <Store className="h-4 w-4 text-indigo-600 mb-1" />
              <p className="text-lg font-bold text-slate-900">{products.length}</p>
              <p className="text-xs text-slate-500">All Platforms</p>
            </button>
            {activePlatforms.map((plat) => {
              const info = PLATFORM_INFO[plat];
              return (
                <button
                  key={plat}
                  onClick={() => setFilterPlatform(plat)}
                  className={`rounded-lg border p-3 text-left transition-colors ${
                    filterPlatform === plat ? 'border-indigo-300 bg-indigo-50' : 'border-slate-200 hover:border-slate-300'
                  }`}
                  data-testid={`filter-${plat}`}
                >
                  <span className="text-base">{info?.icon || '🔗'}</span>
                  <p className="text-lg font-bold text-slate-900">{platformCounts[plat] || 0}</p>
                  <p className="text-xs text-slate-500">{info?.name || plat}</p>
                </button>
              );
            })}
          </div>
        )}

        {/* Sync History */}
        <SyncHistory />

        {/* No products state */}
        {products.length === 0 && (
          <Card className="border-dashed border-2 border-slate-200">
            <CardContent className="p-12 text-center">
              <div className="mx-auto w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mb-4">
                <Package className="h-8 w-8 text-indigo-600" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900 mb-2">No Synced Products</h2>
              <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">
                Connect a store and sync your products to manage them all from one place.
              </p>
              <Button
                onClick={() => navigate('/settings/connections')}
                className="bg-indigo-600 hover:bg-indigo-700"
                data-testid="go-to-connections-btn"
              >
                <Link2 className="h-4 w-4 mr-2" /> Connect a Store
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Products list */}
        {products.length > 0 && (
          <>
            {/* Search and sort */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  data-testid="search-synced-products"
                />
              </div>
              <div className="flex items-center gap-2">
                <ArrowUpDown className="h-4 w-4 text-slate-400" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  data-testid="sort-synced-products"
                >
                  <option value="synced_at">Recently Synced</option>
                  <option value="price">Price (High to Low)</option>
                  <option value="quantity">Stock (High to Low)</option>
                </select>
              </div>
            </div>

            {/* Product grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filtered.map((product) => {
                const platInfo = PLATFORM_INFO[product.platform];
                const productId = product.platform_id || product.shopify_id || product.id;
                return (
                  <Card
                    key={`${product.platform}-${productId}`}
                    className="group hover:shadow-md transition-shadow border-slate-200"
                    data-testid={`synced-product-${productId}`}
                  >
                    <CardContent className="p-0">
                      {/* Image */}
                      <div className="aspect-square bg-slate-50 rounded-t-lg overflow-hidden relative">
                        {product.image_url ? (
                          <img
                            src={product.image_url}
                            alt={product.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            loading="lazy"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <ImageIcon className="h-12 w-12 text-slate-300" />
                          </div>
                        )}
                        <div className="absolute top-2 left-2">
                          <Badge className="bg-white/90 text-slate-700 border text-[10px] backdrop-blur-sm">
                            {platInfo?.icon} {platInfo?.name || product.platform}
                          </Badge>
                        </div>
                        <div className="absolute top-2 right-2">
                          <Badge className={`text-[10px] ${
                            (product.status === 'active' || product.status === 'publish')
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-slate-100 text-slate-600'
                          }`}>
                            {product.status || 'active'}
                          </Badge>
                        </div>
                      </div>

                      {/* Details */}
                      <div className="p-3 space-y-2">
                        <h3 className="font-medium text-sm text-slate-900 line-clamp-2 leading-tight">
                          {product.title}
                        </h3>
                        <div className="flex items-center justify-between">
                          {product.price && (
                            <span className="text-base font-bold text-slate-900">
                              {product.currency === 'USD' ? '$' : '£'}{parseFloat(product.price).toFixed(2)}
                            </span>
                          )}
                          <span className="flex items-center gap-1 text-xs text-slate-500">
                            <Package className="h-3 w-3" />
                            {product.quantity ?? product.inventory_quantity ?? '—'}
                          </span>
                        </div>
                        {product.url && (
                          <a
                            href={product.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 pt-1"
                          >
                            <ExternalLink className="h-3 w-3" /> View on {platInfo?.name || 'Store'}
                          </a>
                        )}
                        {!product.url && product.shop_domain && (
                          <a
                            href={`https://${product.shop_domain}/admin/products/${product.shopify_id || productId}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 pt-1"
                          >
                            <ExternalLink className="h-3 w-3" /> View on {platInfo?.name || 'Store'}
                          </a>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {filtered.length === 0 && search && (
              <div className="text-center py-12 text-slate-500">
                <Search className="h-8 w-8 mx-auto mb-3 text-slate-300" />
                <p className="text-sm">No products match "{search}"</p>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
