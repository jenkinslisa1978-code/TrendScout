import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Search, Package, Loader2, TrendingUp, Import, CheckCircle2,
  ShoppingBag, Truck, Star, ExternalLink, AlertTriangle,
  X, ChevronLeft, ChevronRight, Eye, DollarSign, Boxes,
  Globe, Weight, ImageIcon, Tag, BarChart3, Clock,
} from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

function PriceBadge({ price, label }) {
  return (
    <div>
      {label && <p className="text-[10px] text-slate-400 uppercase tracking-wide">{label}</p>}
      <span className="font-mono text-sm font-bold text-slate-900">${Number(price).toFixed(2)}</span>
    </div>
  );
}

function StockBadge({ status }) {
  const isInStock = status === 'in_stock';
  return (
    <Badge
      variant="outline"
      className={`text-[10px] ${isInStock ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}
      data-testid="stock-badge"
    >
      {isInStock ? 'In Stock' : 'Limited'}
    </Badge>
  );
}

function CJProductCard({ product, onImport, onViewDetail, importing }) {
  const isImporting = importing === product.cj_pid;
  const retailPrice = (product.sell_price * 2.5).toFixed(2);
  const margin = product.sell_price > 0
    ? Math.round(((retailPrice - product.sell_price) / retailPrice) * 100)
    : 0;

  return (
    <Card
      className="border border-slate-200/60 hover:shadow-md hover:border-slate-300 transition-all cursor-pointer group"
      data-testid={`cj-product-${product.cj_pid}`}
      onClick={() => onViewDetail(product.cj_pid)}
    >
      <CardContent className="p-0">
        <div className="flex gap-4 p-4">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt=""
              className="w-24 h-24 rounded-xl object-cover bg-slate-100 flex-shrink-0 group-hover:scale-[1.02] transition-transform"
              loading="lazy"
            />
          ) : (
            <div className="w-24 h-24 rounded-xl bg-slate-100 flex items-center justify-center flex-shrink-0">
              <Package className="h-8 w-8 text-slate-300" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-sm text-slate-900 line-clamp-2 leading-snug group-hover:text-indigo-700 transition-colors">
              {product.product_name}
            </h3>
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              <Badge variant="outline" className="text-[10px] bg-slate-50">{product.category || 'General'}</Badge>
              <StockBadge status={product.stock_status} />
              {product.variants_count > 1 && (
                <span className="text-[10px] text-slate-400">{product.variants_count} variants</span>
              )}
            </div>
            <div className="flex items-center gap-5 mt-2.5">
              <PriceBadge price={product.supplier_cost || product.sell_price} label="Supplier" />
              <PriceBadge price={retailPrice} label="Est. Retail" />
              <div>
                <p className="text-[10px] text-slate-400 uppercase tracking-wide">Margin</p>
                <span className={`text-sm font-bold ${margin >= 50 ? 'text-emerald-600' : margin >= 30 ? 'text-amber-600' : 'text-red-600'}`}>
                  {margin}%
                </span>
              </div>
            </div>
          </div>
          <div className="flex flex-col gap-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
            <Button
              size="sm"
              onClick={() => onImport(product.cj_pid)}
              disabled={isImporting}
              className="text-xs gap-1.5 bg-indigo-600 hover:bg-indigo-700"
              data-testid={`import-btn-${product.cj_pid}`}
            >
              {isImporting ? <Loader2 className="h-3 w-3 animate-spin" /> : <Import className="h-3 w-3" />}
              Import
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-xs gap-1"
              onClick={() => onViewDetail(product.cj_pid)}
              data-testid={`view-btn-${product.cj_pid}`}
            >
              <Eye className="h-3 w-3" /> Details
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ProductDetailModal({ pid, open, onClose, onImport, importing }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeImage, setActiveImage] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (!pid || !open) return;
    setLoading(true);
    setError('');
    setActiveImage(0);
    api.get(`/api/cj/product/${pid}`).then(res => {
      if (res.ok && res.data?.product) {
        setProduct(res.data.product);
      } else {
        setError(res.data?.detail || res.data?.error || 'Failed to load product');
      }
      setLoading(false);
    }).catch(() => {
      setError('Connection error');
      setLoading(false);
    });
  }, [pid, open]);

  const handleImport = async () => {
    const result = await onImport(pid);
    if (result?.product_id && !result?.already_existed) {
      toast.success('Imported! Redirecting to analysis...');
      setTimeout(() => navigate(`/product/${result.product_id}`), 1200);
    }
  };

  const images = product?.images?.length > 0 ? product.images : (product?.image_url ? [product.image_url] : []);
  const retailPrice = product ? (product.sell_price * 2.5).toFixed(2) : 0;
  const margin = product?.sell_price > 0 ? Math.round(((retailPrice - product.sell_price) / retailPrice) * 100) : 0;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto" data-testid="cj-product-detail-modal">
        <DialogHeader>
          <DialogTitle className="text-lg flex items-center gap-2">
            <Package className="h-5 w-5 text-indigo-600" />
            Product Details
            <Badge className="bg-green-50 text-green-700 border-green-200 text-[10px] ml-2">CJ Dropshipping</Badge>
          </DialogTitle>
        </DialogHeader>

        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {!loading && product && (
          <div className="space-y-5">
            {/* Image gallery */}
            {images.length > 0 && (
              <div className="space-y-2">
                <div className="relative rounded-xl overflow-hidden bg-slate-50 h-64 flex items-center justify-center">
                  <img
                    src={images[activeImage]}
                    alt=""
                    className="max-h-full max-w-full object-contain"
                    data-testid="product-detail-image"
                   loading="lazy" />
                  {images.length > 1 && (
                    <>
                      <button
                        onClick={() => setActiveImage((prev) => (prev - 1 + images.length) % images.length)}
                        className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full p-1.5 shadow"
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setActiveImage((prev) => (prev + 1) % images.length)}
                        className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full p-1.5 shadow"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </>
                  )}
                </div>
                {images.length > 1 && (
                  <div className="flex gap-1.5 overflow-x-auto pb-1">
                    {images.slice(0, 8).map((img, i) => (
                      <button
                        key={i}
                        onClick={() => setActiveImage(i)}
                        className={`flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden border-2 transition-all ${
                          i === activeImage ? 'border-indigo-500 ring-1 ring-indigo-200' : 'border-transparent opacity-60 hover:opacity-100'
                        }`}
                      >
                        <img src={img} alt="" className="w-full h-full object-cover"  loading="lazy" />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Title & Category */}
            <div>
              <h2 className="text-lg font-semibold text-slate-900" data-testid="product-detail-name">{product.product_name}</h2>
              <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                <Badge variant="outline" className="text-xs">{product.category || 'General'}</Badge>
                <StockBadge status={product.stock_status} />
                {product.variants_count > 0 && (
                  <Badge variant="outline" className="text-xs bg-slate-50">
                    <Boxes className="h-3 w-3 mr-1" />{product.variants_count} variants
                  </Badge>
                )}
              </div>
            </div>

            {/* Pricing Grid */}
            <div className="grid grid-cols-3 gap-3" data-testid="product-detail-pricing">
              <div className="bg-slate-50 rounded-xl p-3 text-center">
                <p className="text-[10px] text-slate-400 uppercase tracking-wide">Supplier Cost</p>
                <p className="text-xl font-bold font-mono text-slate-900 mt-0.5">${product.sell_price.toFixed(2)}</p>
              </div>
              <div className="bg-slate-50 rounded-xl p-3 text-center">
                <p className="text-[10px] text-slate-400 uppercase tracking-wide">Est. Retail (2.5x)</p>
                <p className="text-xl font-bold font-mono text-slate-900 mt-0.5">${retailPrice}</p>
              </div>
              <div className={`rounded-xl p-3 text-center ${margin >= 50 ? 'bg-emerald-50' : margin >= 30 ? 'bg-amber-50' : 'bg-red-50'}`}>
                <p className="text-[10px] text-slate-400 uppercase tracking-wide">Est. Margin</p>
                <p className={`text-xl font-bold font-mono mt-0.5 ${margin >= 50 ? 'text-emerald-700' : margin >= 30 ? 'text-amber-700' : 'text-red-700'}`}>
                  {margin}%
                </p>
              </div>
            </div>

            {/* Variants */}
            {product.variants && product.variants.length > 0 && (
              <div data-testid="product-detail-variants">
                <h3 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-1.5">
                  <Tag className="h-4 w-4 text-indigo-500" /> Variants ({product.variants.length})
                </h3>
                <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
                  {product.variants.map((v, i) => (
                    <div key={v.vid || i} className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2">
                      <div className="flex items-center gap-2 min-w-0">
                        {v.image && (
                          <img src={v.image} alt="" className="w-8 h-8 rounded object-cover flex-shrink-0"  loading="lazy" />
                        )}
                        <span className="text-sm text-slate-700 truncate">{v.name || v.sku || `Variant ${i + 1}`}</span>
                      </div>
                      <div className="flex items-center gap-3 flex-shrink-0">
                        <span className="font-mono text-sm font-semibold text-slate-900">${v.price.toFixed(2)}</span>
                        {v.stock > 0 && (
                          <span className="text-[10px] text-slate-400">{v.stock} in stock</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Properties */}
            {product.properties && product.properties.length > 0 && (
              <div data-testid="product-detail-properties">
                <h3 className="text-sm font-semibold text-slate-700 mb-2">Properties</h3>
                <div className="flex flex-wrap gap-2">
                  {product.properties.map((p, i) => (
                    <Badge key={i} variant="outline" className="text-xs bg-slate-50">
                      {p.name}: {p.value}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Description */}
            {product.description && (
              <div data-testid="product-detail-description">
                <h3 className="text-sm font-semibold text-slate-700 mb-1">Description</h3>
                {product.description.includes('<') ? (
                  <div
                    className="text-sm text-slate-500 leading-relaxed line-clamp-6 [&_b]:font-semibold [&_br]:hidden"
                    dangerouslySetInnerHTML={{ __html: product.description.replace(/<br\s*\/?>/gi, ' ').replace(/<(?!b|\/b|strong|\/strong)[^>]+>/gi, '') }}
                  />
                ) : (
                  <p className="text-sm text-slate-500 leading-relaxed line-clamp-4">{product.description}</p>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-3 pt-2 border-t border-slate-100">
              <Button
                onClick={handleImport}
                disabled={importing === pid}
                className="flex-1 gap-2 bg-indigo-600 hover:bg-indigo-700"
                data-testid="modal-import-btn"
              >
                {importing === pid ? <Loader2 className="h-4 w-4 animate-spin" /> : <Import className="h-4 w-4" />}
                Import to TrendScout
              </Button>
              <a href={product.source_url} target="_blank" rel="noopener noreferrer" className="flex-shrink-0">
                <Button variant="outline" className="gap-1.5">
                  <ExternalLink className="h-4 w-4" /> View on CJ
                </Button>
              </a>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

const SOURCE_COLORS = {
  cj_dropshipping: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', label: 'CJ Dropshipping' },
  aliexpress: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200', label: 'AliExpress' },
  zendrop: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', label: 'Zendrop' },
};

function SupplierComparisonCard({ supplier }) {
  const colors = SOURCE_COLORS[supplier.source] || SOURCE_COLORS.cj_dropshipping;
  const isEstimation = supplier.mode !== 'live';

  return (
    <Card className="border border-slate-200/60 hover:shadow-md transition-all" data-testid={`supplier-${supplier.source}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {supplier.image_url ? (
            <img src={supplier.image_url} alt="" className="w-16 h-16 rounded-lg object-cover bg-slate-100 flex-shrink-0"  loading="lazy" />
          ) : (
            <div className="w-16 h-16 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
              <Package className="h-6 w-6 text-slate-300" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Badge className={`text-[10px] ${colors.bg} ${colors.text} ${colors.border}`}>
                {colors.label}
              </Badge>
              <Badge variant="outline" className={`text-[10px] ${isEstimation ? 'bg-slate-50 text-slate-500 border-slate-200' : 'bg-emerald-50 text-emerald-600 border-emerald-200'}`}>
                {isEstimation ? 'Compare externally' : 'Live'}
              </Badge>
            </div>
            <h3 className="text-sm font-semibold text-slate-900 line-clamp-1">{supplier.product_name}</h3>
            <div className="grid grid-cols-4 gap-3 mt-2">
              <div>
                <p className="text-[10px] text-slate-400 uppercase">Cost</p>
                <p className="font-mono text-sm font-bold text-slate-900">
                  {supplier.supplier_cost > 0 ? `$${supplier.supplier_cost.toFixed(2)}` : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-slate-400 uppercase">Retail</p>
                <p className="font-mono text-sm font-bold text-slate-900">
                  {supplier.estimated_retail > 0 ? `$${supplier.estimated_retail.toFixed(2)}` : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-slate-400 uppercase">Margin</p>
                <p className={`text-sm font-bold ${supplier.margin_pct >= 50 ? 'text-emerald-600' : supplier.margin_pct >= 30 ? 'text-amber-600' : 'text-red-600'}`}>
                  {supplier.margin_pct}%
                </p>
              </div>
              <div>
                <p className="text-[10px] text-slate-400 uppercase">Shipping</p>
                <p className="text-sm font-semibold text-slate-700 flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {supplier.shipping_days}d
                </p>
              </div>
            </div>
            {supplier.note && (
              <p className="text-[10px] text-slate-500 mt-1.5 flex items-center gap-1">
                <ExternalLink className="h-3 w-3" /> {supplier.note}
              </p>
            )}
          </div>
          {supplier.source_url && (
            <a href={supplier.source_url} target="_blank" rel="noopener noreferrer" className="flex-shrink-0">
              <Button variant="outline" size="sm" className="text-xs gap-1">
                <ExternalLink className="h-3 w-3" /> View
              </Button>
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function SupplierComparisonView({ query, active }) {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const handleCompare = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/api/cj/supplier-comparison?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        setSuppliers(res.data.suppliers || []);
      } else {
        setError(res.data?.error || 'Comparison failed');
      }
    } catch {
      setError('Connection error');
    }
    setLoading(false);
    setSearched(true);
  }, [query]);

  useEffect(() => {
    if (active && query.trim() && !searched) {
      handleCompare();
    }
  }, [active, query, searched, handleCompare]);

  if (!active) return null;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        <p className="text-sm text-slate-400">Comparing suppliers...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-amber-200 bg-amber-50">
        <CardContent className="p-3 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-600" />
          <p className="text-sm text-amber-700">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!searched) {
    return (
      <Card className="border-0 shadow-sm">
        <CardContent className="text-center py-12">
          <BarChart3 className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <p className="text-lg font-semibold text-slate-700">Search to compare suppliers</p>
          <p className="text-sm text-slate-500 mt-1">Enter a product name above to see pricing across CJ, AliExpress, and Zendrop</p>
        </CardContent>
      </Card>
    );
  }

  if (suppliers.length === 0) {
    return (
      <Card className="border-0 shadow-sm">
        <CardContent className="text-center py-12">
          <Package className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <p className="text-lg font-semibold text-slate-700">No supplier data found</p>
        </CardContent>
      </Card>
    );
  }

  // Group by source
  const grouped = {};
  for (const s of suppliers) {
    if (!grouped[s.source]) grouped[s.source] = [];
    grouped[s.source].push(s);
  }

  return (
    <div className="space-y-4" data-testid="supplier-comparison-results">
      <p className="text-sm text-slate-500">
        <strong>{suppliers.length}</strong> results across {Object.keys(grouped).length} suppliers
      </p>
      {Object.entries(grouped).map(([source, items]) => (
        <div key={source}>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            {SOURCE_COLORS[source]?.label || source} ({items.length})
          </h3>
          <div className="space-y-2">
            {items.map((s, i) => (
              <SupplierComparisonCard key={`${source}-${i}`} supplier={s} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function AvasamProductCard({ product, onImport, importing }) {
  const isImporting = importing === product.avasam_pid;
  const retailPrice = product.sell_price > 0 ? product.sell_price : (product.supplier_cost * 2.5);
  const margin = product.supplier_cost > 0
    ? Math.round(((retailPrice - product.supplier_cost) / retailPrice) * 100)
    : 0;

  return (
    <Card className="border border-slate-200/60 hover:shadow-md hover:border-slate-300 transition-all">
      <CardContent className="p-0">
        <div className="flex gap-4 p-4">
          {product.image_url ? (
            <img src={product.image_url} alt={product.product_name} className="w-16 h-16 rounded-lg object-cover bg-slate-100 flex-shrink-0" loading="lazy" />
          ) : (
            <div className="w-16 h-16 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
              <Package className="h-6 w-6 text-slate-300" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="font-semibold text-slate-900 text-sm line-clamp-2 leading-snug">{product.product_name}</p>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <Badge className="bg-violet-50 text-violet-700 border-violet-200 text-[10px]">Avasam</Badge>
                  {product.category && <Badge variant="outline" className="text-[10px]">{product.category}</Badge>}
                  <StockBadge status={product.stock_status} />
                </div>
              </div>
              <div className="flex-shrink-0 text-right">
                <PriceBadge price={product.supplier_cost} label="Cost" />
                {margin > 0 && <p className="text-xs font-semibold text-emerald-600 mt-0.5">{margin}% margin</p>}
              </div>
            </div>
            <div className="flex items-center justify-between mt-3">
              <div className="flex items-center gap-3 text-xs text-slate-400">
                {product.sku && <span>SKU: {product.sku}</span>}
                {product.brand && <span>{product.brand}</span>}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => window.open(product.source_url, '_blank')}
                >
                  <ExternalLink className="h-3 w-3 mr-1" /> View
                </Button>
                <Button
                  size="sm"
                  className="h-7 text-xs bg-violet-600 hover:bg-violet-700"
                  disabled={isImporting}
                  onClick={() => onImport(product.avasam_pid, product)}
                >
                  {isImporting ? <Loader2 className="h-3 w-3 animate-spin" /> : <><Import className="h-3 w-3 mr-1" /> Import</>}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function AvasamSearchView({ query, onQueryChange }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(null);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/api/avasam/search?q=${encodeURIComponent(query)}&page_size=20`);
      if (res.ok) {
        setProducts(res.data.products || []);
      } else {
        setError(res.data?.error || 'Avasam search failed. Check your credentials in Settings → Connections.');
      }
    } catch {
      setError('Connection error');
    }
    setLoading(false);
    setSearched(true);
  }, [query]);

  const handleImport = useCallback(async (avasamPid, product) => {
    setImporting(avasamPid);
    try {
      const res = await api.post(`/api/avasam/import/${avasamPid}`);
      if (res.ok) {
        toast.success(`Imported: ${product.product_name}`);
      } else {
        toast.error(res.data?.detail || 'Import failed');
      }
    } catch {
      toast.error('Connection error');
    }
    setImporting(null);
  }, []);

  return (
    <div>
      <div className="flex gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search Avasam UK suppliers (e.g. phone case, kitchen gadget)"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="pl-10 h-11"
          />
        </div>
        <Button onClick={handleSearch} disabled={loading || !query.trim()} className="h-11 px-6 bg-violet-600 hover:bg-violet-700">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Search className="h-4 w-4 mr-2" /> Search</>}
        </Button>
      </div>

      {error && (
        <Card className="border-amber-200 bg-amber-50 mb-4">
          <CardContent className="p-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-600 flex-shrink-0" />
            <p className="text-sm text-amber-700">{error}</p>
          </CardContent>
        </Card>
      )}
      {loading && (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-violet-500" />
          <p className="text-sm text-slate-400">Searching Avasam UK suppliers...</p>
        </div>
      )}
      {!loading && searched && products.length === 0 && !error && (
        <Card className="border-0 shadow-sm">
          <CardContent className="text-center py-12">
            <Package className="h-12 w-12 text-slate-300 mx-auto mb-3" />
            <p className="text-lg font-semibold text-slate-700">No products found</p>
            <p className="text-sm text-slate-500 mt-1">Try a different search term or check your Avasam catalogue</p>
          </CardContent>
        </Card>
      )}
      {!loading && products.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-slate-500"><strong>{products.length}</strong> products found</p>
          {products.map((p) => (
            <AvasamProductCard key={p.avasam_pid} product={p} onImport={handleImport} importing={importing} />
          ))}
        </div>
      )}
      {!searched && (
        <div className="space-y-6 mt-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { icon: ShoppingBag, title: 'UK-Based Suppliers', desc: 'Source from Avasam\'s network of verified UK wholesalers and dropshippers' },
              { icon: Truck, title: 'Fast UK Shipping', desc: 'UK suppliers mean faster delivery times and lower shipping costs for your customers' },
              { icon: Star, title: 'One-Click Import', desc: 'Import Avasam products directly into TrendScout for instant launch analysis' },
            ].map(f => (
              <Card key={f.title} className="border-slate-200/60">
                <CardContent className="p-5">
                  <div className="h-9 w-9 rounded-lg bg-violet-50 flex items-center justify-center mb-3">
                    <f.icon className="h-5 w-5 text-violet-500" />
                  </div>
                  <h3 className="font-semibold text-sm text-slate-900">{f.title}</h3>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">{f.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function CJSourcingPage() {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);
  const [detailPid, setDetailPid] = useState(null);
  const [activeTab, setActiveTab] = useState('search');

  const handleSearch = useCallback(async (pageNum = 1) => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/api/cj/search?q=${encodeURIComponent(query)}&page=${pageNum}&page_size=20`);
      if (res.ok) {
        setProducts(res.data.products || []);
        setTotal(res.data.total || 0);
        setPage(pageNum);
      } else {
        setError(res.data?.error || 'Search failed. The CJ API may be rate-limited — please try again in a moment.');
      }
    } catch {
      setError('Connection error');
    }
    setLoading(false);
    setSearched(true);
  }, [query]);

  const handleImport = useCallback(async (cjPid) => {
    setImporting(cjPid);
    let result = null;
    try {
      const res = await api.post(`/api/cj/import/${cjPid}`);
      if (res.ok) {
        result = res.data;
        if (result.already_existed) {
          toast.info('Product already in your catalogue');
        } else {
          toast.success(`Imported! Launch score: ${result.launch_score}`);
        }
      } else {
        toast.error(res.data?.detail || 'Import failed');
      }
    } catch {
      toast.error('Connection error');
    }
    setImporting(null);
    return result;
  }, []);

  const totalPages = Math.ceil(total / 20);

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto" data-testid="cj-sourcing-page">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2.5 mb-1">
            <div className="h-9 w-9 rounded-lg bg-indigo-100 flex items-center justify-center">
              <Truck className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Product Sourcing</h1>
              <p className="text-sm text-slate-500">Search real supplier inventory with live pricing across multiple platforms</p>
            </div>
            <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px] ml-auto">Live API</Badge>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-5 bg-slate-100 rounded-lg p-1 w-fit" data-testid="sourcing-tabs">
          <button
            onClick={() => setActiveTab('search')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'search' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            }`}
            data-testid="tab-search"
          >
            CJ Search
          </button>
          <button
            onClick={() => setActiveTab('avasam')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'avasam' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            }`}
            data-testid="tab-avasam"
          >
            Avasam UK
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'compare' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            }`}
            data-testid="tab-compare"
          >
            Compare Suppliers
          </button>
        </div>

        {/* CJ Search bar — only shown on CJ and compare tabs */}
        {activeTab !== 'avasam' && (
          <div className="flex gap-3 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search products (e.g. LED strip lights, phone case, yoga mat)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (activeTab === 'search' ? handleSearch() : null)}
                className="pl-10 h-11"
                data-testid="cj-search-input"
              />
            </div>
            <Button
              onClick={() => activeTab === 'search' ? handleSearch() : null}
              disabled={loading || !query.trim()}
              className="h-11 px-6 bg-indigo-600 hover:bg-indigo-700"
              data-testid="cj-search-btn"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Search className="h-4 w-4 mr-2" /> Search</>}
            </Button>
          </div>
        )}

        {/* Avasam Tab */}
        {activeTab === 'avasam' && (
          <AvasamSearchView query={query} onQueryChange={setQuery} />
        )}

        {/* Compare Suppliers Tab */}
        {activeTab === 'compare' && (
          <SupplierComparisonView query={query} active={activeTab === 'compare'} />
        )}

        {/* CJ Search Tab */}
        {activeTab === 'search' && (
          <>
        {/* Error */}
        {error && (
          <Card className="border-amber-200 bg-amber-50 mb-4">
            <CardContent className="p-3 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-600 flex-shrink-0" />
              <p className="text-sm text-amber-700">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
            <p className="text-sm text-slate-400">Searching CJ Dropshipping...</p>
          </div>
        )}

        {/* No results */}
        {!loading && searched && products.length === 0 && !error && (
          <Card className="border-0 shadow-sm">
            <CardContent className="text-center py-12">
              <Package className="h-12 w-12 text-slate-300 mx-auto mb-3" />
              <p className="text-lg font-semibold text-slate-700">No products found</p>
              <p className="text-sm text-slate-500 mt-1">Try a different search term or broader keywords</p>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {!loading && products.length > 0 && (
          <>
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm text-slate-500" data-testid="cj-result-count">
                <strong>{total.toLocaleString()}</strong> products found
              </p>
              <p className="text-xs text-slate-400">Page {page} of {totalPages || 1}</p>
            </div>
            <div className="space-y-3">
              {products.map((p) => (
                <CJProductCard
                  key={p.cj_pid}
                  product={p}
                  onImport={handleImport}
                  onViewDetail={setDetailPid}
                  importing={importing}
                />
              ))}
            </div>
            {total > 20 && (
              <div className="flex justify-center gap-3 mt-6">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => handleSearch(page - 1)}
                  data-testid="cj-prev-page"
                >
                  <ChevronLeft className="h-4 w-4 mr-1" /> Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => handleSearch(page + 1)}
                  data-testid="cj-next-page"
                >
                  Next <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            )}
          </>
        )}

        {/* Initial state — feature cards */}
        {!searched && (
          <div className="space-y-6 mt-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[
                { icon: ShoppingBag, title: 'Real Suppliers', desc: 'Browse products from CJ Dropshipping with live stock levels and pricing' },
                { icon: TrendingUp, title: 'One-Click Import', desc: 'Import any product into TrendScout for instant launch score analysis' },
                { icon: Star, title: 'Live Data', desc: 'Real supplier costs, variants, shipping weights, and availability' },
              ].map(f => (
                <Card key={f.title} className="border-slate-200/60 hover:shadow-sm transition-shadow">
                  <CardContent className="p-5">
                    <div className="h-9 w-9 rounded-lg bg-indigo-50 flex items-center justify-center mb-3">
                      <f.icon className="h-5 w-5 text-indigo-500" />
                    </div>
                    <h3 className="font-semibold text-sm text-slate-900">{f.title}</h3>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">{f.desc}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Quick search suggestions */}
            <div className="text-center">
              <p className="text-xs text-slate-400 mb-2">Popular searches</p>
              <div className="flex flex-wrap justify-center gap-2">
                {['LED strip lights', 'phone case', 'yoga mat', 'kitchen gadget', 'pet toy', 'wireless earbuds'].map(term => (
                  <button
                    key={term}
                    onClick={() => { setQuery(term); }}
                    className="text-xs px-3 py-1.5 rounded-full bg-slate-100 text-slate-600 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                    data-testid={`quick-search-${term.replace(/\s+/g, '-')}`}
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
          </>
        )}
      </div>

      {/* Product Detail Modal */}
      <ProductDetailModal
        pid={detailPid}
        open={!!detailPid}
        onClose={() => setDetailPid(null)}
        onImport={handleImport}
        importing={importing}
      />
    </DashboardLayout>
  );
}
