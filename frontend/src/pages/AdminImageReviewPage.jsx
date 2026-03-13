import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Image, CheckCircle2, XCircle, AlertTriangle, Pin, PinOff,
  Loader2, Eye, ChevronLeft, ChevronRight, Search, Package,
  BarChart3, Clock, Shield, Check, X, ExternalLink,
  Copy, Trash2, RefreshCw, Filter, ArrowLeft,
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

const STATUS_CONFIG = {
  needs_review: { label: 'Needs Review', color: 'bg-amber-100 text-amber-700 border-amber-200', icon: AlertTriangle },
  pending: { label: 'Pending', color: 'bg-slate-100 text-slate-600 border-slate-200', icon: Clock },
  approved: { label: 'Approved', color: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: CheckCircle2 },
  rejected: { label: 'Rejected', color: 'bg-red-100 text-red-700 border-red-200', icon: XCircle },
  placeholder: { label: 'Placeholder', color: 'bg-violet-100 text-violet-700 border-violet-200', icon: Image },
};

export default function AdminImageReviewPage() {
  const [metrics, setMetrics] = useState(null);
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('needs_review');
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [detailProduct, setDetailProduct] = useState(null);
  const [bulkLoading, setBulkLoading] = useState(false);

  const fetchMetrics = useCallback(async () => {
    try {
      const { data } = await api.get('/api/admin/image-review/metrics');
      setMetrics(data);
    } catch {}
  }, []);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, limit: 20 });
      if (statusFilter) params.set('status', statusFilter);
      const { data } = await api.get(`/api/admin/image-review/products?${params}`);
      setProducts(data.products || []);
      setTotal(data.total || 0);
    } catch (e) {
      toast.error('Failed to load products');
    }
    setLoading(false);
  }, [page, statusFilter]);

  useEffect(() => { fetchMetrics(); }, [fetchMetrics]);
  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const toggleSelect = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    if (selectedIds.size === products.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(products.map(p => p.id)));
    }
  };

  const handleBulkAction = async (action) => {
    if (selectedIds.size === 0) return;
    setBulkLoading(true);
    try {
      await api.post('/api/admin/image-review/bulk', {
        action,
        product_ids: Array.from(selectedIds),
      });
      toast.success(`Bulk ${action}: ${selectedIds.size} products updated`);
      setSelectedIds(new Set());
      fetchProducts();
      fetchMetrics();
    } catch {
      toast.error('Bulk action failed');
    }
    setBulkLoading(false);
  };

  const handleSingleAction = async (productId, action, extra = {}) => {
    try {
      await api.put(`/api/admin/image-review/products/${productId}/${action}`, extra);
      toast.success(`Image ${action}d`);
      fetchProducts();
      fetchMetrics();
      if (detailProduct?.id === productId) {
        const { data } = await api.get(`/api/admin/image-review/products/${productId}`);
        setDetailProduct(data);
      }
    } catch (e) {
      toast.error(`Failed to ${action}`);
    }
  };

  const totalPages = Math.ceil(total / 20);

  // Detail view
  if (detailProduct) {
    return (
      <DashboardLayout>
        <ImageDetailView
          product={detailProduct}
          onBack={() => setDetailProduct(null)}
          onAction={handleSingleAction}
          onRefresh={async () => {
            const { data } = await api.get(`/api/admin/image-review/products/${detailProduct.id}`);
            setDetailProduct(data);
            fetchMetrics();
          }}
        />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="image-review-page">
        {/* Header */}
        <div>
          <h1 className="font-manrope text-2xl font-bold text-slate-900">Image Review Dashboard</h1>
          <p className="mt-1 text-slate-500">Review and validate product images across the catalogue</p>
        </div>

        {/* QA Metrics */}
        {metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3" data-testid="image-metrics">
            {[
              { label: 'Total', value: metrics.total_products, icon: Package, color: 'text-slate-600 bg-slate-50' },
              { label: 'Needs Review', value: metrics.needs_review, icon: AlertTriangle, color: 'text-amber-600 bg-amber-50' },
              { label: 'Pending', value: metrics.pending, icon: Clock, color: 'text-slate-500 bg-slate-50' },
              { label: 'Approved', value: metrics.approved, icon: CheckCircle2, color: 'text-emerald-600 bg-emerald-50' },
              { label: 'Rejected', value: metrics.rejected, icon: XCircle, color: 'text-red-600 bg-red-50' },
              { label: 'Placeholder', value: metrics.placeholder, icon: Image, color: 'text-violet-600 bg-violet-50' },
              { label: 'Pinned', value: metrics.pinned, icon: Pin, color: 'text-indigo-600 bg-indigo-50' },
            ].map(m => {
              const Icon = m.icon;
              return (
                <Card key={m.label} className="border-slate-200 shadow-sm">
                  <CardContent className="p-4 text-center">
                    <div className={`inline-flex h-8 w-8 items-center justify-center rounded-lg ${m.color} mb-2`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <p className="text-2xl font-bold text-slate-900">{m.value}</p>
                    <p className="text-xs text-slate-500">{m.label}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Filters & Bulk Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5">
            <Filter className="h-4 w-4 text-slate-400" />
            {[null, 'needs_review', 'pending', 'approved', 'rejected', 'placeholder'].map(s => (
              <Button
                key={s || 'all'}
                size="sm"
                variant={statusFilter === s ? 'default' : 'outline'}
                onClick={() => { setStatusFilter(s); setPage(1); setSelectedIds(new Set()); }}
                className={`text-xs ${statusFilter === s ? 'bg-indigo-600' : ''}`}
                data-testid={`filter-${s || 'all'}`}
              >
                {s ? STATUS_CONFIG[s]?.label : 'All'}
              </Button>
            ))}
          </div>

          {selectedIds.size > 0 && (
            <div className="flex items-center gap-2 ml-auto" data-testid="bulk-actions">
              <span className="text-xs text-slate-500">{selectedIds.size} selected</span>
              <Button size="sm" variant="outline" className="text-xs text-emerald-600 border-emerald-200"
                onClick={() => handleBulkAction('approve')} disabled={bulkLoading} data-testid="bulk-approve">
                <Check className="h-3 w-3 mr-1" /> Approve
              </Button>
              <Button size="sm" variant="outline" className="text-xs text-red-600 border-red-200"
                onClick={() => handleBulkAction('reject')} disabled={bulkLoading} data-testid="bulk-reject">
                <X className="h-3 w-3 mr-1" /> Reject
              </Button>
              <Button size="sm" variant="outline" className="text-xs"
                onClick={() => handleBulkAction('mark_needs_review')} disabled={bulkLoading} data-testid="bulk-review">
                <RefreshCw className="h-3 w-3 mr-1" /> Re-review
              </Button>
            </div>
          )}
        </div>

        {/* Product Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : products.length === 0 ? (
          <Card className="border-slate-200">
            <CardContent className="py-16 text-center">
              <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-300" />
              <h3 className="mt-4 font-semibold text-slate-900">No products to review</h3>
              <p className="mt-2 text-slate-500">All images in this category have been reviewed.</p>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Select All */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedIds.size === products.length && products.length > 0}
                onChange={selectAll}
                className="h-4 w-4 rounded border-slate-300"
                data-testid="select-all"
              />
              <span className="text-xs text-slate-500">Select all on page ({products.length})</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4" data-testid="review-grid">
              {products.map(p => {
                const statusCfg = STATUS_CONFIG[p.image_status] || STATUS_CONFIG.pending;
                const StatusIcon = statusCfg.icon;
                const isSelected = selectedIds.has(p.id);

                return (
                  <div
                    key={p.id}
                    className={`group relative bg-white rounded-xl border transition-all duration-200 cursor-pointer overflow-hidden hover:shadow-md ${
                      isSelected ? 'border-indigo-400 ring-2 ring-indigo-100' : 'border-slate-200'
                    }`}
                    data-testid={`review-item-${p.id}`}
                  >
                    {/* Checkbox */}
                    <div className="absolute top-2 left-2 z-10">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleSelect(p.id)}
                        className="h-4 w-4 rounded border-slate-300"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </div>

                    {/* Status Badge */}
                    <div className="absolute top-2 right-2 z-10">
                      <Badge className={`text-[10px] border ${statusCfg.color}`}>
                        <StatusIcon className="h-2.5 w-2.5 mr-0.5" />
                        {statusCfg.label}
                      </Badge>
                    </div>

                    {/* Image */}
                    <div className="aspect-square bg-slate-50 overflow-hidden" onClick={() => setDetailProduct(p)}>
                      {p.image_url ? (
                        <img src={p.image_url} alt={p.product_name} className="w-full h-full object-cover" loading="lazy" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Package className="h-10 w-10 text-slate-300" />
                        </div>
                      )}
                    </div>

                    {/* Info */}
                    <div className="p-3" onClick={() => setDetailProduct(p)}>
                      <p className="text-xs font-medium text-slate-800 line-clamp-1">{p.product_name}</p>
                      <div className="flex items-center justify-between mt-1.5">
                        <span className="text-[10px] text-slate-400">{p.category}</span>
                        <span className="text-[10px] font-mono text-slate-500">
                          {((p.image_confidence || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                      {p.image_pinned && (
                        <Pin className="h-3 w-3 text-indigo-500 mt-1" />
                      )}
                    </div>

                    {/* Quick Actions */}
                    <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-t border-slate-100 flex opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleSingleAction(p.id, 'approve'); }}
                        className="flex-1 py-1.5 text-[11px] text-emerald-600 hover:bg-emerald-50 transition-colors flex items-center justify-center gap-1"
                        data-testid={`quick-approve-${p.id}`}
                      >
                        <Check className="h-3 w-3" /> Approve
                      </button>
                      <div className="w-px bg-slate-100" />
                      <button
                        onClick={(e) => { e.stopPropagation(); handleSingleAction(p.id, 'reject', { reason: 'Image mismatch' }); }}
                        className="flex-1 py-1.5 text-[11px] text-red-600 hover:bg-red-50 transition-colors flex items-center justify-center gap-1"
                        data-testid={`quick-reject-${p.id}`}
                      >
                        <X className="h-3 w-3" /> Reject
                      </button>
                      <div className="w-px bg-slate-100" />
                      <button
                        onClick={(e) => { e.stopPropagation(); setDetailProduct(p); }}
                        className="flex-1 py-1.5 text-[11px] text-slate-600 hover:bg-slate-50 transition-colors flex items-center justify-center gap-1"
                      >
                        <Eye className="h-3 w-3" /> Detail
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm text-slate-600">Page {page} of {totalPages}</span>
                <Button size="sm" variant="outline" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

/* ── Image Detail View ── */
function ImageDetailView({ product, onBack, onAction, onRefresh }) {
  const [customUrl, setCustomUrl] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [saving, setSaving] = useState(false);

  const statusCfg = STATUS_CONFIG[product.image_status] || STATUS_CONFIG.pending;
  const StatusIcon = statusCfg.icon;

  const handleSetUrl = async () => {
    if (!customUrl.trim()) return;
    setSaving(true);
    try {
      await api.put(`/api/admin/image-review/products/${product.id}/url`, { url: customUrl.trim() });
      toast.success('Image URL updated');
      setCustomUrl('');
      onRefresh();
    } catch {
      toast.error('Failed to set URL');
    }
    setSaving(false);
  };

  const handlePin = async () => {
    await api.put(`/api/admin/image-review/products/${product.id}/pin`, { pinned: !product.image_pinned });
    toast.success(product.image_pinned ? 'Image unpinned' : 'Image pinned');
    onRefresh();
  };

  return (
    <div className="space-y-6" data-testid="image-detail-view">
      {/* Back button */}
      <Button variant="ghost" onClick={onBack} className="text-slate-600" data-testid="back-to-list">
        <ArrowLeft className="h-4 w-4 mr-2" /> Back to Review Queue
      </Button>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left: Image */}
        <Card className="border-slate-200 shadow-sm overflow-hidden">
          <div className="aspect-square bg-slate-50">
            {product.image_url ? (
              <img src={product.image_url} alt={product.product_name} className="w-full h-full object-contain" />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Package className="h-20 w-20 text-slate-200" />
                <p className="text-slate-400 mt-4">No image</p>
              </div>
            )}
          </div>
        </Card>

        {/* Right: Details & Actions */}
        <div className="space-y-4">
          <Card className="border-slate-200 shadow-sm">
            <CardContent className="p-5 space-y-4">
              <div>
                <h2 className="font-manrope text-xl font-bold text-slate-900" data-testid="detail-product-name">
                  {product.product_name}
                </h2>
                <p className="text-sm text-slate-500 mt-1">{product.category}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-400">Status</p>
                  <Badge className={`mt-1 text-xs border ${statusCfg.color}`}>
                    <StatusIcon className="h-3 w-3 mr-1" />
                    {statusCfg.label}
                  </Badge>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-400">Confidence</p>
                  <p className="mt-1 font-mono text-lg font-bold text-slate-900">
                    {((product.image_confidence || 0) * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-400">Pinned</p>
                  <p className="mt-1 text-sm font-medium">{product.image_pinned ? 'Yes' : 'No'}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-400">Trend Score</p>
                  <p className="mt-1 font-mono text-lg font-bold text-indigo-600">{product.launch_score || '—'}</p>
                </div>
              </div>

              {product.image_mismatch_reason && (
                <div className="bg-red-50 border border-red-100 rounded-lg p-3">
                  <p className="text-xs font-medium text-red-700">Mismatch Reason</p>
                  <p className="text-sm text-red-600 mt-1">{product.image_mismatch_reason}</p>
                </div>
              )}

              {product.image_detected_object && (
                <div className="bg-amber-50 border border-amber-100 rounded-lg p-3">
                  <p className="text-xs font-medium text-amber-700">Detected Object</p>
                  <p className="text-sm text-amber-600 mt-1">{product.image_detected_object}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700"
                  onClick={() => onAction(product.id, 'approve')} data-testid="detail-approve">
                  <CheckCircle2 className="h-4 w-4 mr-1" /> Approve
                </Button>
                <Button size="sm" variant="destructive"
                  onClick={() => onAction(product.id, 'reject', { reason: rejectReason || 'Manual rejection' })} data-testid="detail-reject">
                  <XCircle className="h-4 w-4 mr-1" /> Reject
                </Button>
                <Button size="sm" variant="outline" onClick={handlePin} data-testid="detail-pin">
                  {product.image_pinned ? <PinOff className="h-4 w-4 mr-1" /> : <Pin className="h-4 w-4 mr-1" />}
                  {product.image_pinned ? 'Unpin' : 'Pin'}
                </Button>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-600">Rejection Reason</label>
                <Input
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="e.g. Wrong product, accessory image..."
                  className="text-sm mt-1"
                  data-testid="reject-reason-input"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-600">Set Custom Image URL</label>
                <div className="flex gap-2 mt-1">
                  <Input
                    value={customUrl}
                    onChange={(e) => setCustomUrl(e.target.value)}
                    placeholder="https://..."
                    className="text-sm flex-1"
                    data-testid="custom-url-input"
                  />
                  <Button size="sm" onClick={handleSetUrl} disabled={saving || !customUrl.trim()} data-testid="set-url-btn">
                    {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Set'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Candidates */}
          {product.image_candidates?.length > 0 && (
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Candidate Images ({product.image_candidates.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-2">
                  {product.image_candidates.map((c, i) => (
                    <div key={i} className="relative group rounded-lg overflow-hidden border border-slate-200">
                      <img src={c.url || c} alt="" className="aspect-square object-cover w-full" />
                      <button
                        onClick={() => onAction(product.id, 'select-candidate', { url: c.url || c })}
                        className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                      >
                        <span className="text-white text-xs font-medium">Select</span>
                      </button>
                      {c.confidence && (
                        <span className="absolute bottom-1 right-1 bg-black/70 text-white text-[10px] px-1.5 py-0.5 rounded">
                          {(c.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
