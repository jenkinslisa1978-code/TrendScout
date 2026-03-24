import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  RefreshCw, Package, ExternalLink, Loader2, ShoppingBag,
  AlertCircle, Link2, Search, ArrowUpDown, Image as ImageIcon,
} from 'lucide-react';
import { toast } from 'sonner';
import { apiGet, apiPost } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

function ShopifyProductsPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [connected, setConnected] = useState(null);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('synced_at');

  const fetchProducts = useCallback(async () => {
    try {
      const res = await apiGet('/api/shopify/synced-products');
      const data = await res.json();
      if (data.success) {
        setProducts(data.products || []);
        setConnected(true);
      } else {
        setConnected(false);
      }
    } catch {
      setConnected(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      const res = await apiPost('/api/shopify/sync-products');
      const data = await res.json();
      if (data.success) {
        toast.success(`Synced ${data.synced_count} products from ${data.shop}`);
        fetchProducts();
      } else {
        toast.error(data.error || 'Sync failed');
      }
    } catch {
      toast.error('Failed to sync products');
    } finally {
      setSyncing(false);
    }
  };

  const filtered = products
    .filter(p => !search || p.title?.toLowerCase().includes(search.toLowerCase()) || p.product_type?.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'price') return parseFloat(b.price || 0) - parseFloat(a.price || 0);
      if (sortBy === 'inventory') return (b.inventory_quantity || 0) - (a.inventory_quantity || 0);
      return (b.synced_at || '').localeCompare(a.synced_at || '');
    });

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="shopify-products-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Shopify Products</h1>
            <p className="text-sm text-slate-500 mt-1">
              {connected && products.length > 0
                ? `${products.length} products synced from your Shopify store`
                : 'Products from your connected Shopify store'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {connected && (
              <Button
                onClick={handleSync}
                disabled={syncing}
                className="bg-indigo-600 hover:bg-indigo-700"
                data-testid="sync-products-btn"
              >
                {syncing ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Syncing...</>
                ) : (
                  <><RefreshCw className="h-4 w-4 mr-2" /> Sync Now</>
                )}
              </Button>
            )}
          </div>
        </div>

        {/* No connection state */}
        {connected === false && (
          <Card className="border-dashed border-2 border-slate-200">
            <CardContent className="p-12 text-center">
              <div className="mx-auto w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mb-4">
                <Link2 className="h-8 w-8 text-emerald-600" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900 mb-2">Connect Your Shopify Store</h2>
              <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">
                Connect your Shopify store to sync your products into TrendScout. Analyse performance, spot trends, and manage everything in one place.
              </p>
              <Button
                onClick={() => navigate('/settings/connections')}
                className="bg-emerald-600 hover:bg-emerald-700"
                data-testid="go-to-connections-btn"
              >
                <Link2 className="h-4 w-4 mr-2" /> Go to Connections
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Connected but no products */}
        {connected && products.length === 0 && (
          <Card className="border-dashed border-2 border-slate-200">
            <CardContent className="p-12 text-center">
              <div className="mx-auto w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mb-4">
                <Package className="h-8 w-8 text-indigo-600" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900 mb-2">No Products Synced Yet</h2>
              <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">
                Your Shopify store is connected. Click "Sync Now" to pull your products into TrendScout.
              </p>
              <Button
                onClick={handleSync}
                disabled={syncing}
                className="bg-indigo-600 hover:bg-indigo-700"
                data-testid="first-sync-btn"
              >
                {syncing ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Syncing...</>
                ) : (
                  <><RefreshCw className="h-4 w-4 mr-2" /> Sync Products</>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Products list */}
        {connected && products.length > 0 && (
          <>
            {/* Search and sort bar */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  data-testid="search-products-input"
                />
              </div>
              <div className="flex items-center gap-2">
                <ArrowUpDown className="h-4 w-4 text-slate-400" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  data-testid="sort-products-select"
                >
                  <option value="synced_at">Recently Synced</option>
                  <option value="price">Price (High to Low)</option>
                  <option value="inventory">Inventory (High to Low)</option>
                </select>
              </div>
            </div>

            {/* Product grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filtered.map((product) => (
                <Card key={product.shopify_id} className="group hover:shadow-md transition-shadow border-slate-200" data-testid={`product-card-${product.shopify_id}`}>
                  <CardContent className="p-0">
                    {/* Product image */}
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
                      <div className="absolute top-2 right-2">
                        <Badge className={`text-[10px] ${product.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>
                          {product.status || 'active'}
                        </Badge>
                      </div>
                    </div>

                    {/* Product details */}
                    <div className="p-3 space-y-2">
                      <h3 className="font-medium text-sm text-slate-900 line-clamp-2 leading-tight" title={product.title}>
                        {product.title}
                      </h3>

                      <div className="flex items-center justify-between">
                        {product.price && (
                          <span className="text-base font-bold text-slate-900">
                            £{parseFloat(product.price).toFixed(2)}
                          </span>
                        )}
                        {product.variants_count > 1 && (
                          <span className="text-xs text-slate-400">{product.variants_count} variants</span>
                        )}
                      </div>

                      <div className="flex items-center justify-between text-xs text-slate-500">
                        {product.product_type && (
                          <span className="truncate">{product.product_type}</span>
                        )}
                        <span className="flex items-center gap-1">
                          <Package className="h-3 w-3" />
                          {product.inventory_quantity ?? '—'}
                        </span>
                      </div>

                      {product.vendor && (
                        <p className="text-xs text-slate-400 truncate">by {product.vendor}</p>
                      )}

                      <a
                        href={`https://${product.shop_domain}/admin/products/${product.shopify_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 pt-1"
                        data-testid={`view-on-shopify-${product.shopify_id}`}
                      >
                        <ExternalLink className="h-3 w-3" /> View on Shopify
                      </a>
                    </div>
                  </CardContent>
                </Card>
              ))}
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

export default ShopifyProductsPage;
