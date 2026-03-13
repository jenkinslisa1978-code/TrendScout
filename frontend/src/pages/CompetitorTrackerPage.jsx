import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Radar, Plus, RefreshCw, Trash2, Store, Package, Tag,
  DollarSign, Clock, Loader2, ExternalLink, TrendingUp,
  TrendingDown, Minus, ArrowRight, X, AlertTriangle,
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';

export default function CompetitorTrackerPage() {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [addUrl, setAddUrl] = useState('');
  const [addName, setAddName] = useState('');
  const [adding, setAdding] = useState(false);
  const [refreshingId, setRefreshingId] = useState(null);

  useEffect(() => { fetchStores(); }, []);

  const fetchStores = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/competitor-stores');
      setStores(res.data.stores || []);
    } catch { toast.error('Failed to load stores'); }
    setLoading(false);
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!addUrl.trim()) return;
    setAdding(true);
    try {
      const res = await api.post('/api/competitor-stores', {
        url: addUrl.trim(),
        name: addName.trim() || undefined,
      });
      setStores(prev => [res.data, ...prev]);
      setAddUrl('');
      setAddName('');
      setShowAdd(false);
      toast.success('Store added and scanned!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add store');
    }
    setAdding(false);
  };

  const handleRefresh = async (storeId) => {
    setRefreshingId(storeId);
    try {
      const res = await api.post(`/api/competitor-stores/${storeId}/refresh`);
      setStores(prev => prev.map(s => s.id === storeId ? res.data : s));
      toast.success('Store rescanned!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Scan failed');
    }
    setRefreshingId(null);
  };

  const handleDelete = async (storeId) => {
    try {
      await api.delete(`/api/competitor-stores/${storeId}`);
      setStores(prev => prev.filter(s => s.id !== storeId));
      toast.success('Store removed');
    } catch { toast.error('Failed to remove'); }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="competitor-tracker-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">Competitor Tracker</h1>
            <p className="mt-1 text-slate-500 text-sm">Monitor competitor Shopify stores and track product changes</p>
          </div>
          <Button
            onClick={() => setShowAdd(!showAdd)}
            className="bg-indigo-600 hover:bg-indigo-700 rounded-xl font-semibold"
            data-testid="add-competitor-btn"
          >
            {showAdd ? <X className="h-4 w-4 mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
            {showAdd ? 'Cancel' : 'Add Store'}
          </Button>
        </div>

        {/* Add Form */}
        {showAdd && (
          <Card className="border-indigo-200 bg-indigo-50/30 animate-in slide-in-from-top-2 duration-300">
            <CardContent className="p-5">
              <form onSubmit={handleAdd} className="flex flex-col sm:flex-row gap-3" data-testid="add-store-form">
                <Input
                  value={addUrl}
                  onChange={(e) => setAddUrl(e.target.value)}
                  placeholder="Store URL (e.g. gymshark.com)"
                  className="flex-1 h-10 rounded-lg"
                  data-testid="add-store-url"
                  required
                />
                <Input
                  value={addName}
                  onChange={(e) => setAddName(e.target.value)}
                  placeholder="Store name (optional)"
                  className="sm:w-44 h-10 rounded-lg"
                  data-testid="add-store-name"
                />
                <Button
                  type="submit"
                  disabled={adding || !addUrl.trim()}
                  className="bg-indigo-600 hover:bg-indigo-700 h-10 px-5 rounded-lg font-semibold whitespace-nowrap"
                  data-testid="add-store-submit"
                >
                  {adding ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Plus className="h-4 w-4 mr-1.5" /> Track Store</>}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Stores List */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : stores.length === 0 ? (
          <Card className="border-slate-200">
            <CardContent className="py-16 text-center">
              <Radar className="mx-auto h-12 w-12 text-slate-300 mb-4" />
              <h3 className="font-manrope text-lg font-semibold text-slate-900">No competitors tracked yet</h3>
              <p className="mt-2 text-slate-500 max-w-md mx-auto text-sm">
                Add a Shopify store URL to start monitoring their product catalog, pricing, and new additions.
              </p>
              <Button onClick={() => setShowAdd(true)} className="mt-5 bg-indigo-600 hover:bg-indigo-700 rounded-xl" data-testid="empty-add-btn">
                <Plus className="h-4 w-4 mr-2" /> Add Your First Competitor
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {stores.map((store) => (
              <CompetitorStoreCard
                key={store.id}
                store={store}
                onRefresh={handleRefresh}
                onDelete={handleDelete}
                refreshing={refreshingId === store.id}
              />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

function CompetitorStoreCard({ store, onRefresh, onDelete, refreshing }) {
  const change = store.product_change || 0;
  const ChangeIcon = change > 0 ? TrendingUp : change < 0 ? TrendingDown : Minus;
  const changeColor = change > 0 ? 'text-emerald-600 bg-emerald-50' : change < 0 ? 'text-rose-600 bg-rose-50' : 'text-slate-500 bg-slate-50';

  const timeAgo = (d) => {
    try { return formatDistanceToNow(new Date(d), { addSuffix: true }); }
    catch { return '—'; }
  };

  return (
    <Card className="border-slate-200 hover:border-slate-300 transition-all" data-testid={`competitor-store-${store.id}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4 flex-1 min-w-0">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-slate-100 to-slate-50 border border-slate-200 flex items-center justify-center flex-shrink-0">
              <Store className="h-5 w-5 text-slate-500" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-slate-900 truncate">{store.name}</h3>
                <a href={store.url} target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-indigo-500 transition-colors">
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>
              <p className="text-xs text-slate-400 truncate">{store.domain}</p>

              {/* Metrics row */}
              <div className="flex items-center gap-4 mt-3 flex-wrap">
                <div className="flex items-center gap-1.5 text-sm">
                  <Package className="h-3.5 w-3.5 text-slate-400" />
                  <span className="font-semibold text-slate-700">{store.product_count}</span>
                  <span className="text-xs text-slate-400">products</span>
                </div>
                {store.categories?.length > 0 && (
                  <div className="flex items-center gap-1.5 text-sm">
                    <Tag className="h-3.5 w-3.5 text-slate-400" />
                    <span className="text-slate-600">{store.categories.length} categories</span>
                  </div>
                )}
                {store.price_range?.avg > 0 && (
                  <div className="flex items-center gap-1.5 text-sm">
                    <DollarSign className="h-3.5 w-3.5 text-slate-400" />
                    <span className="text-slate-600">${store.price_range.avg} avg</span>
                  </div>
                )}
                {change !== 0 && (
                  <Badge className={`${changeColor} border-0 rounded-full text-xs flex items-center gap-1`}>
                    <ChangeIcon className="h-3 w-3" />
                    {change > 0 ? '+' : ''}{change} products
                  </Badge>
                )}
              </div>

              {/* Categories */}
              {store.categories?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {store.categories.slice(0, 4).map(c => (
                    <Badge key={c.name} className="bg-slate-50 text-slate-500 border-slate-200 text-[10px] rounded-full">
                      {c.name} ({c.count})
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <div className="text-right mr-2">
              <div className="flex items-center gap-1 text-xs text-slate-400">
                <Clock className="h-3 w-3" />
                {timeAgo(store.last_scan_at)}
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onRefresh(store.id)}
              disabled={refreshing}
              className="h-8 px-3 rounded-lg"
              data-testid={`refresh-store-${store.id}`}
            >
              <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(store.id)}
              className="h-8 px-2 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50"
              data-testid={`delete-store-${store.id}`}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
