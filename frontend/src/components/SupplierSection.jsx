import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Package, ExternalLink, Check, Truck, Clock, AlertCircle, RefreshCw, Star } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function SupplierSection({ productId, productName }) {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selecting, setSelecting] = useState(null);

  const fetchSuppliers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/suppliers/${productId}`);
      const data = await res.json();
      setSuppliers(data.suppliers || []);
    } catch (err) {
      console.error('Failed to fetch suppliers:', err);
    } finally {
      setLoading(false);
    }
  }, [productId]);

  useEffect(() => { fetchSuppliers(); }, [fetchSuppliers]);

  const handleSelect = async (supplierId) => {
    setSelecting(supplierId);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/api/suppliers/${productId}/select/${supplierId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setSuppliers(prev => prev.map(s => ({ ...s, is_selected: s.id === supplierId })));
      }
    } catch (err) {
      console.error('Failed to select supplier:', err);
    } finally {
      setSelecting(null);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/suppliers/${productId}/find`, { method: 'POST' });
      const data = await res.json();
      setSuppliers(data.suppliers || []);
    } catch (err) {
      console.error('Refresh failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence === 'scraped') return <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-xs">Verified</Badge>;
    if (confidence === 'verified') return <Badge className="bg-blue-50 text-blue-700 border-blue-200 text-xs">Matched</Badge>;
    return <Badge className="bg-amber-50 text-amber-700 border-amber-200 text-xs">Estimated</Badge>;
  };

  if (loading) {
    return (
      <Card className="border-slate-200" data-testid="supplier-section-loading">
        <CardContent className="p-8 text-center text-slate-400">
          <Package className="h-6 w-6 mx-auto mb-2 animate-pulse" />
          Finding suppliers...
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-200 shadow-sm" data-testid="supplier-section">
      <CardHeader className="border-b border-slate-100 pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="font-manrope text-lg font-semibold text-slate-900 flex items-center gap-2">
            <Package className="h-5 w-5 text-sky-500" />
            Supplier Listings
            <Badge variant="outline" className="text-xs ml-2">{suppliers.length} found</Badge>
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={handleRefresh} data-testid="refresh-suppliers-btn">
            <RefreshCw className="h-4 w-4 mr-1" /> Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        {suppliers.length === 0 ? (
          <div className="text-center py-6 text-slate-400" data-testid="no-suppliers">
            <AlertCircle className="h-6 w-6 mx-auto mb-2" />
            <p className="text-sm">No suppliers found for this product</p>
          </div>
        ) : (
          suppliers.map((supplier) => (
            <div
              key={supplier.id}
              className={`relative border rounded-lg p-4 transition-all ${
                supplier.is_selected
                  ? 'border-emerald-300 bg-emerald-50/50 ring-1 ring-emerald-200'
                  : 'border-slate-200 hover:border-slate-300 bg-white'
              }`}
              data-testid={`supplier-card-${supplier.source}`}
            >
              {supplier.is_selected && (
                <div className="absolute top-3 right-3">
                  <Badge className="bg-emerald-500 text-white text-xs flex items-center gap-1">
                    <Check className="h-3 w-3" /> Selected
                  </Badge>
                </div>
              )}

              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center">
                  {supplier.source === 'aliexpress' ? (
                    <span className="text-orange-500 font-bold text-xs">AE</span>
                  ) : (
                    <span className="text-blue-500 font-bold text-xs">CJ</span>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-semibold text-slate-900 truncate">{supplier.supplier_name}</h4>
                    {getConfidenceBadge(supplier.confidence)}
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
                    <div>
                      <p className="text-xs text-slate-400 uppercase tracking-wide">Cost</p>
                      <p className="text-sm font-mono font-bold text-slate-900">
                        {supplier.supplier_cost > 0 ? `$${supplier.supplier_cost.toFixed(2)}` : 'Unknown'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 uppercase tracking-wide">Shipping</p>
                      <p className="text-sm font-mono text-slate-700">
                        {supplier.estimated_shipping_cost > 0 ? `+$${supplier.estimated_shipping_cost.toFixed(2)}` : 'Free'}
                      </p>
                    </div>
                    <div className="flex items-start gap-1">
                      <Truck className="h-3.5 w-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-xs text-slate-400">Delivery</p>
                        <p className="text-sm text-slate-700">{supplier.shipping_days_min}-{supplier.shipping_days_max} days</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-1">
                      <Clock className="h-3.5 w-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-xs text-slate-400">Origin</p>
                        <p className="text-sm text-slate-700">{supplier.shipping_origin}</p>
                      </div>
                    </div>
                  </div>

                  {(supplier.supplier_rating || supplier.supplier_orders) && (
                    <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                      {supplier.supplier_rating && (
                        <span className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-amber-400 fill-amber-400" />
                          {supplier.supplier_rating}
                        </span>
                      )}
                      {supplier.supplier_orders && (
                        <span>{supplier.supplier_orders.toLocaleString()}+ sold</span>
                      )}
                    </div>
                  )}

                  {supplier.confidence_note && (
                    <p className="text-xs text-slate-400 mt-2 italic">{supplier.confidence_note}</p>
                  )}

                  <div className="flex items-center gap-2 mt-3">
                    {!supplier.is_selected && (
                      <Button
                        size="sm"
                        onClick={() => handleSelect(supplier.id)}
                        disabled={selecting === supplier.id}
                        data-testid={`select-supplier-${supplier.source}`}
                        className="bg-slate-900 hover:bg-slate-800 text-white text-xs"
                      >
                        {selecting === supplier.id ? 'Selecting...' : 'Select Supplier'}
                      </Button>
                    )}
                    <a href={supplier.supplier_url} target="_blank" rel="noopener noreferrer">
                      <Button variant="outline" size="sm" className="text-xs" data-testid={`view-supplier-${supplier.source}`}>
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View on {supplier.source === 'aliexpress' ? 'AliExpress' : 'CJ'}
                      </Button>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
