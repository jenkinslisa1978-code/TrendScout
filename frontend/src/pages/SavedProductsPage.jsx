import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Bookmark, BookmarkX, Package, Eye, ArrowRight, Loader2,
  StickyNote, Rocket, FlaskConical, Ban, Search as SearchIcon,
  ChevronDown, Pencil, Check, X,
} from 'lucide-react';
import { getSavedProducts, unsaveProduct, updateProductNote, updateProductStatus } from '@/services/savedProductService';
import { useAuth } from '@/contexts/AuthContext';
import { formatCurrency, formatNumber, getTrendStageColor, getOpportunityColor, getTrendScoreColor } from '@/lib/utils';
import { toast } from 'sonner';

const STATUS_CONFIG = {
  researching: { label: 'Researching', icon: SearchIcon, color: 'bg-blue-50 text-blue-700 border-blue-200' },
  testing: { label: 'Testing', icon: FlaskConical, color: 'bg-amber-50 text-amber-700 border-amber-200' },
  launched: { label: 'Launched', icon: Rocket, color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  dropped: { label: 'Dropped', icon: Ban, color: 'bg-slate-100 text-slate-500 border-slate-200' },
};

function StatusBadge({ status, onClick }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.researching;
  const Icon = cfg.icon;
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors hover:opacity-80 ${cfg.color}`}
      data-testid={`status-badge-${status}`}
    >
      <Icon className="h-3 w-3" />
      {cfg.label}
      <ChevronDown className="h-3 w-3 ml-0.5" />
    </button>
  );
}

function StatusDropdown({ current, onSelect, onClose }) {
  return (
    <div className="absolute z-20 top-full mt-1 right-0 bg-white rounded-xl border border-slate-200 shadow-lg py-1 min-w-[160px]" data-testid="status-dropdown">
      {Object.entries(STATUS_CONFIG).map(([key, cfg]) => {
        const Icon = cfg.icon;
        return (
          <button
            key={key}
            onClick={() => { onSelect(key); onClose(); }}
            className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-50 transition-colors ${key === current ? 'font-semibold text-indigo-600' : 'text-slate-700'}`}
            data-testid={`status-option-${key}`}
          >
            <Icon className="h-4 w-4" />
            {cfg.label}
          </button>
        );
      })}
    </div>
  );
}

function NoteEditor({ note, productId, onSaved }) {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(note || '');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    const { error } = await updateProductNote(productId, text);
    setSaving(false);
    if (error) { toast.error('Failed to save note'); return; }
    onSaved(text);
    setEditing(false);
    toast.success('Note saved');
  };

  if (!editing) {
    return (
      <div className="mt-3">
        {note ? (
          <div
            className="text-xs text-slate-600 bg-amber-50/60 border border-amber-100 rounded-lg p-2.5 cursor-pointer hover:bg-amber-50 transition-colors"
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); setEditing(true); }}
            data-testid={`note-display-${productId}`}
          >
            <div className="flex items-center gap-1 mb-1 text-amber-700 font-medium">
              <StickyNote className="h-3 w-3" /> Note
            </div>
            <p className="whitespace-pre-wrap">{note}</p>
          </div>
        ) : (
          <button
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); setEditing(true); }}
            className="text-xs text-slate-400 hover:text-indigo-500 flex items-center gap-1 transition-colors"
            data-testid={`add-note-btn-${productId}`}
          >
            <Pencil className="h-3 w-3" /> Add note
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="mt-3" onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}>
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Add private notes about this product..."
        className="text-xs min-h-[60px] resize-none border-amber-200 focus:border-amber-300"
        autoFocus
        data-testid={`note-textarea-${productId}`}
      />
      <div className="flex gap-1.5 mt-1.5 justify-end">
        <Button
          size="sm"
          variant="ghost"
          onClick={() => { setText(note || ''); setEditing(false); }}
          className="h-7 text-xs"
        >
          <X className="h-3 w-3 mr-1" /> Cancel
        </Button>
        <Button
          size="sm"
          onClick={handleSave}
          disabled={saving}
          className="h-7 text-xs bg-amber-500 hover:bg-amber-600 text-white"
          data-testid={`save-note-btn-${productId}`}
        >
          {saving ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <Check className="h-3 w-3 mr-1" />}
          Save
        </Button>
      </div>
    </div>
  );
}

export default function SavedProductsPage() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');
  const [openDropdown, setOpenDropdown] = useState(null);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    const statusParam = activeFilter === 'all' ? null : activeFilter;
    const { data } = await getSavedProducts(user?.id, statusParam);
    setItems(data || []);
    setLoading(false);
  }, [user, activeFilter]);

  useEffect(() => { fetchItems(); }, [fetchItems]);

  const handleRemove = async (productId, e) => {
    e.preventDefault();
    e.stopPropagation();
    const { error } = await unsaveProduct(user?.id, productId);
    if (error) { toast.error('Failed to remove'); return; }
    setItems(prev => prev.filter(i => i.product_id !== productId));
    toast.success('Removed from workspace');
  };

  const handleStatusChange = async (productId, newStatus) => {
    const { error } = await updateProductStatus(productId, newStatus);
    if (error) { toast.error('Failed to update status'); return; }
    setItems(prev => prev.map(i =>
      i.product_id === productId ? { ...i, launch_status: newStatus } : i
    ));
  };

  const handleNoteSaved = (productId, newNote) => {
    setItems(prev => prev.map(i =>
      i.product_id === productId ? { ...i, note: newNote } : i
    ));
  };

  const counts = items.reduce((acc, i) => {
    acc[i.launch_status] = (acc[i.launch_status] || 0) + 1;
    return acc;
  }, {});

  return (
    <DashboardLayout>
      <div className="space-y-6" data-testid="workspace-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-manrope text-2xl font-bold text-slate-900">Product Workspace</h1>
            <p className="mt-1 text-slate-500">Save products, add notes, and track your launch experiments</p>
          </div>
          <Link to="/discover">
            <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="discover-more-btn">
              Discover More <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>

        {/* Status Filters */}
        <div className="flex flex-wrap gap-2" data-testid="workspace-filters">
          <Button
            variant={activeFilter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveFilter('all')}
            className={activeFilter === 'all' ? 'bg-indigo-600 text-white' : ''}
            data-testid="filter-all"
          >
            All ({items.length})
          </Button>
          {Object.entries(STATUS_CONFIG).map(([key, cfg]) => {
            const Icon = cfg.icon;
            return (
              <Button
                key={key}
                variant={activeFilter === key ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter(key)}
                className={activeFilter === key ? 'bg-indigo-600 text-white' : ''}
                data-testid={`filter-${key}`}
              >
                <Icon className="h-3.5 w-3.5 mr-1.5" />
                {cfg.label} ({counts[key] || 0})
              </Button>
            );
          })}
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : items.length === 0 ? (
          <Card className="border-slate-200 shadow-sm">
            <CardContent className="py-16 text-center">
              <Bookmark className="mx-auto h-12 w-12 text-slate-300" />
              <h3 className="mt-4 font-manrope text-lg font-semibold text-slate-900">
                {activeFilter === 'all' ? 'No saved products yet' : `No ${STATUS_CONFIG[activeFilter]?.label?.toLowerCase()} products`}
              </h3>
              <p className="mt-2 text-slate-500 max-w-md mx-auto">
                Start exploring products and save the ones you're interested in. They'll appear here for easy access.
              </p>
              <Link to="/discover" className="mt-6 inline-block">
                <Button className="bg-indigo-600 hover:bg-indigo-700">Browse Products</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3" data-testid="workspace-grid">
            {items.map((item) => {
              const product = item.product || {};
              const productId = item.product_id;
              return (
                <Link
                  key={item.id}
                  to={`/product/${productId}`}
                  data-testid={`workspace-item-${productId}`}
                >
                  <Card className="group border-slate-200 shadow-sm hover:border-indigo-200 hover:shadow-lg transition-all duration-300 h-full">
                    <CardContent className="p-0">
                      {/* Image */}
                      <div className="relative h-36 bg-slate-100 rounded-t-lg overflow-hidden">
                        {product.image_url ? (
                          <img
                            src={product.image_url}
                            alt={product.product_name}
                            className="w-full h-full object-cover"
                            loading="lazy"
                            onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                          />
                        ) : null}
                        <div className={`${product.image_url ? 'hidden' : 'flex'} w-full h-full items-center justify-center`}>
                          <Package className="h-10 w-10 text-slate-300" />
                        </div>
                        <div className="absolute top-3 left-3 z-10" onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}>
                          <div className="relative">
                            <StatusBadge
                              status={item.launch_status}
                              onClick={() => setOpenDropdown(openDropdown === productId ? null : productId)}
                            />
                            {openDropdown === productId && (
                              <StatusDropdown
                                current={item.launch_status}
                                onSelect={(s) => handleStatusChange(productId, s)}
                                onClose={() => setOpenDropdown(null)}
                              />
                            )}
                          </div>
                        </div>
                        <button
                          onClick={(e) => handleRemove(productId, e)}
                          className="absolute top-3 right-3 p-2 rounded-full bg-white/80 hover:bg-red-50 transition-colors"
                          data-testid={`remove-btn-${productId}`}
                        >
                          <BookmarkX className="h-4 w-4 text-slate-400 hover:text-red-500" />
                        </button>
                      </div>

                      {/* Content */}
                      <div className="p-4 space-y-3">
                        <div>
                          <h3 className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-1">
                            {product.product_name || 'Unknown Product'}
                          </h3>
                          <p className="text-sm text-slate-500 mt-0.5">{product.category}</p>
                        </div>

                        {/* Stats */}
                        <div className="flex items-center justify-between">
                          <div>
                            <p className={`font-mono text-xl font-bold ${getTrendScoreColor(product.launch_score)}`}>
                              {product.launch_score || '—'}
                            </p>
                            <p className="text-xs text-slate-400">Trend Score</p>
                          </div>
                          <div className="text-right">
                            <p className="font-mono text-lg font-semibold text-slate-900">
                              {product.estimated_margin ? formatCurrency(product.estimated_margin) : '—'}
                            </p>
                            <p className="text-xs text-slate-400">Est. Margin</p>
                          </div>
                        </div>

                        {/* TikTok Views */}
                        {product.tiktok_views > 0 && (
                          <div className="flex items-center gap-2 text-sm text-slate-500">
                            <Eye className="h-4 w-4" />
                            {formatNumber(product.tiktok_views)} TikTok views
                          </div>
                        )}

                        {/* Badges */}
                        <div className="flex flex-wrap gap-2">
                          {product.trend_stage && (
                            <Badge className={`${getTrendStageColor(product.trend_stage)} border text-xs`}>
                              {product.trend_stage}
                            </Badge>
                          )}
                          {product.opportunity_rating && (
                            <Badge className={`${getOpportunityColor(product.opportunity_rating)} border text-xs`}>
                              {product.opportunity_rating}
                            </Badge>
                          )}
                        </div>

                        {/* Note */}
                        <NoteEditor
                          note={item.note}
                          productId={productId}
                          onSaved={(newNote) => handleNoteSaved(productId, newNote)}
                        />
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
