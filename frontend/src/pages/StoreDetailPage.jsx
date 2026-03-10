import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, 
  Save, 
  Eye, 
  Download, 
  RefreshCw,
  Package,
  Palette,
  FileText,
  Settings,
  Trash2,
  Loader2,
  Check,
  ExternalLink,
  Copy,
  Rocket,
  Edit3,
  FileDown,
  CheckCircle2
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  getStore, 
  updateStore, 
  getStoreProducts, 
  updateStoreProduct,
  deleteStoreProduct,
  regenerateProductCopy,
  exportStore,
  updateStoreStatus
} from '@/services/storeService';

const TABS = [
  { id: 'overview', label: 'Overview', icon: Settings },
  { id: 'products', label: 'Products', icon: Package },
  { id: 'branding', label: 'Branding', icon: Palette },
  { id: 'content', label: 'Content', icon: FileText },
];

// Status configuration
const STATUS_CONFIG = {
  draft: { label: 'Draft', color: 'bg-slate-100 text-slate-600', nextStatus: 'ready', nextLabel: 'Mark Ready' },
  ready: { label: 'Ready', color: 'bg-blue-100 text-blue-700', nextStatus: 'exported', nextLabel: 'Export' },
  exported: { label: 'Exported', color: 'bg-amber-100 text-amber-700', nextStatus: 'published', nextLabel: 'Mark Published' },
  published: { label: 'Published', color: 'bg-emerald-100 text-emerald-700', nextStatus: null, nextLabel: null },
  archived: { label: 'Archived', color: 'bg-slate-100 text-slate-500', nextStatus: null, nextLabel: null },
};

// Launch progress steps
const LAUNCH_STEPS = [
  { id: 1, label: 'Create', icon: Edit3, status: 'draft', description: 'Store created with AI-generated content' },
  { id: 2, label: 'Review', icon: Check, status: 'ready', description: 'Review and customize your store' },
  { id: 3, label: 'Export', icon: FileDown, status: 'exported', description: 'Export to Shopify format' },
  { id: 4, label: 'Launch', icon: Rocket, status: 'published', description: 'Store is live!' },
];

export default function StoreDetailPage() {
  const { storeId } = useParams();
  const navigate = useNavigate();
  const { profile } = useAuth();
  const userId = profile?.id || 'demo-user-id';

  const [store, setStore] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [editedStore, setEditedStore] = useState({});
  const [editingProduct, setEditingProduct] = useState(null);

  useEffect(() => {
    loadStore();
  }, [storeId]);

  const loadStore = async () => {
    setLoading(true);
    const { data } = await getStore(storeId);
    if (data) {
      setStore(data);
      setEditedStore({
        name: data.name,
        tagline: data.tagline,
        headline: data.headline,
        status: data.status,
        branding: data.branding || {},
      });
      setProducts(data.products || []);
    }
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    const result = await updateStore(storeId, editedStore);
    if (result.success) {
      toast.success('Store updated successfully');
      setStore({ ...store, ...editedStore });
    } else {
      toast.error(result.error || 'Failed to update store');
    }
    setSaving(false);
  };

  const handleStatusChange = async (newStatus) => {
    const result = await updateStoreStatus(storeId, newStatus);
    if (result.success) {
      const statusLabels = {
        ready: 'Store marked as ready!',
        exported: 'Store exported!',
        published: 'Store published!',
        draft: 'Store reverted to draft',
      };
      toast.success(statusLabels[newStatus] || 'Status updated');
      setStore({ ...store, status: newStatus });
      setEditedStore({ ...editedStore, status: newStatus });
    } else {
      toast.error('Failed to update status');
    }
  };

  const handleExport = async () => {
    const exportData = await exportStore(storeId, 'shopify');
    if (exportData.error) {
      toast.error('Failed to export store');
      return;
    }
    
    // Download as JSON
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${store.name.replace(/\s+/g, '_')}_shopify_export.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('Store exported for Shopify');
    // Refresh store to get updated status
    loadStore();
  };

  const handleRegenerateCopy = async (productId) => {
    const result = await regenerateProductCopy(storeId, productId);
    if (result.success) {
      toast.success('Product copy regenerated');
      setProducts(products.map(p => p.id === productId ? result.product : p));
    } else {
      toast.error('Failed to regenerate copy');
    }
  };

  const handleDeleteProduct = async (productId) => {
    const result = await deleteStoreProduct(storeId, productId);
    if (result.success) {
      toast.success('Product removed');
      setProducts(products.filter(p => p.id !== productId));
    }
  };

  const handleProductUpdate = async (productId, updates) => {
    const result = await updateStoreProduct(storeId, productId, updates);
    if (result.success) {
      toast.success('Product updated');
      setProducts(products.map(p => p.id === productId ? result.product : p));
      setEditingProduct(null);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!store) {
    return (
      <DashboardLayout>
        <div className="text-center py-20">
          <h2 className="text-xl font-semibold text-slate-900">Store not found</h2>
          <Button onClick={() => navigate('/stores')} className="mt-4">
            Back to Stores
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/stores')}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="font-manrope text-2xl font-bold text-slate-900">
                  {store.name}
                </h1>
                <Badge className={STATUS_CONFIG[store.status]?.color || 'bg-slate-100 text-slate-600'}>
                  {STATUS_CONFIG[store.status]?.label || store.status}
                </Badge>
              </div>
              <p className="text-sm text-slate-500">{store.tagline}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => window.open(`/preview/${storeId}`, '_blank')}>
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </Button>
            <Button variant="outline" onClick={handleExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            {/* Dynamic status action button */}
            {STATUS_CONFIG[store.status]?.nextStatus && (
              <Button 
                onClick={() => handleStatusChange(STATUS_CONFIG[store.status].nextStatus)}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {STATUS_CONFIG[store.status].nextLabel}
              </Button>
            )}
            {store.status === 'published' && (
              <Button 
                variant="outline"
                onClick={() => handleStatusChange('draft')}
              >
                Unpublish
              </Button>
            )}
          </div>
        </div>

        {/* Launch Progress */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="text-sm font-medium text-slate-900 mb-4">Launch Progress</h3>
          <div className="flex items-start justify-between">
            {LAUNCH_STEPS.map((step, index) => {
              const currentProgress = Object.keys(STATUS_CONFIG).findIndex(s => s === store.status) + 1;
              const stepProgress = LAUNCH_STEPS.findIndex(s => s.status === store.status) + 1;
              const isComplete = index < stepProgress;
              const isCurrent = step.status === store.status;
              
              return (
                <React.Fragment key={step.id}>
                  <div className="flex flex-col items-center text-center flex-1">
                    <div 
                      className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 transition-all ${
                        isComplete 
                          ? 'bg-emerald-500 text-white' 
                          : isCurrent 
                            ? 'bg-indigo-500 text-white ring-4 ring-indigo-100' 
                            : 'bg-slate-100 text-slate-400'
                      }`}
                    >
                      {isComplete && !isCurrent ? (
                        <CheckCircle2 className="h-5 w-5" />
                      ) : (
                        <step.icon className="h-5 w-5" />
                      )}
                    </div>
                    <span className={`text-sm font-medium ${
                      isComplete || isCurrent ? 'text-slate-900' : 'text-slate-400'
                    }`}>
                      {step.label}
                    </span>
                    <span className="text-xs text-slate-500 mt-1 max-w-[120px]">
                      {step.description}
                    </span>
                  </div>
                  {index < LAUNCH_STEPS.length - 1 && (
                    <div className="flex-1 flex items-center pt-4">
                      <div 
                        className={`h-1 w-full rounded ${
                          isComplete ? 'bg-emerald-500' : 'bg-slate-200'
                        }`}
                      />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-slate-200">
          <nav className="flex gap-6">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-3 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Store Name</Label>
                  <Input
                    value={editedStore.name || ''}
                    onChange={(e) => setEditedStore({ ...editedStore, name: e.target.value })}
                    data-testid="store-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Input value={store.category} disabled className="bg-slate-50" />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Tagline</Label>
                <Input
                  value={editedStore.tagline || ''}
                  onChange={(e) => setEditedStore({ ...editedStore, tagline: e.target.value })}
                  placeholder="Your store tagline"
                />
              </div>

              <div className="space-y-2">
                <Label>Homepage Headline</Label>
                <Input
                  value={editedStore.headline || ''}
                  onChange={(e) => setEditedStore({ ...editedStore, headline: e.target.value })}
                  placeholder="Main headline for your store"
                />
              </div>

              <Button onClick={handleSave} disabled={saving}>
                {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Save Changes
              </Button>
            </div>
          )}

          {/* Products Tab */}
          {activeTab === 'products' && (
            <div className="space-y-4">
              {products.length === 0 ? (
                <p className="text-slate-500 text-center py-8">No products in this store</p>
              ) : (
                products.map((product) => (
                  <div 
                    key={product.id} 
                    className="border border-slate-200 rounded-xl p-4"
                    data-testid={`store-product-${product.id}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-slate-900">{product.title}</h4>
                          {product.is_featured && (
                            <Badge className="bg-indigo-100 text-indigo-700">Featured</Badge>
                          )}
                        </div>
                        <p className="text-sm text-slate-600 line-clamp-2 mb-3">
                          {product.description?.slice(0, 150)}...
                        </p>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="font-semibold text-slate-900">
                            £{product.price?.toFixed(2)}
                          </span>
                          {product.compare_at_price > product.price && (
                            <span className="text-slate-400 line-through">
                              £{product.compare_at_price?.toFixed(2)}
                            </span>
                          )}
                          <span className="text-slate-500">{product.category}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleRegenerateCopy(product.id)}
                        >
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="text-red-500 hover:text-red-600 hover:bg-red-50"
                          onClick={() => handleDeleteProduct(product.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    {/* Bullet Points */}
                    <div className="mt-4 pt-4 border-t border-slate-100">
                      <p className="text-xs font-medium text-slate-500 mb-2">Key Features</p>
                      <ul className="grid gap-1 text-sm text-slate-600">
                        {product.bullet_points?.slice(0, 3).map((point, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <Check className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))
              )}

              <Button variant="outline" onClick={() => navigate('/discover')} className="w-full">
                <Package className="h-4 w-4 mr-2" />
                Add More Products
              </Button>
            </div>
          )}

          {/* Branding Tab */}
          {activeTab === 'branding' && (
            <div className="space-y-6">
              <div className="grid gap-6 md:grid-cols-3">
                <div className="space-y-2">
                  <Label>Primary Color</Label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={editedStore.branding?.primary_color || '#0f172a'}
                      onChange={(e) => setEditedStore({
                        ...editedStore,
                        branding: { ...editedStore.branding, primary_color: e.target.value }
                      })}
                      className="w-12 h-10 rounded border cursor-pointer"
                    />
                    <Input
                      value={editedStore.branding?.primary_color || '#0f172a'}
                      onChange={(e) => setEditedStore({
                        ...editedStore,
                        branding: { ...editedStore.branding, primary_color: e.target.value }
                      })}
                      className="font-mono"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Secondary Color</Label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={editedStore.branding?.secondary_color || '#3b82f6'}
                      onChange={(e) => setEditedStore({
                        ...editedStore,
                        branding: { ...editedStore.branding, secondary_color: e.target.value }
                      })}
                      className="w-12 h-10 rounded border cursor-pointer"
                    />
                    <Input
                      value={editedStore.branding?.secondary_color || '#3b82f6'}
                      onChange={(e) => setEditedStore({
                        ...editedStore,
                        branding: { ...editedStore.branding, secondary_color: e.target.value }
                      })}
                      className="font-mono"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Accent Color</Label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={editedStore.branding?.accent_color || '#10b981'}
                      onChange={(e) => setEditedStore({
                        ...editedStore,
                        branding: { ...editedStore.branding, accent_color: e.target.value }
                      })}
                      className="w-12 h-10 rounded border cursor-pointer"
                    />
                    <Input
                      value={editedStore.branding?.accent_color || '#10b981'}
                      onChange={(e) => setEditedStore({
                        ...editedStore,
                        branding: { ...editedStore.branding, accent_color: e.target.value }
                      })}
                      className="font-mono"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Style</Label>
                <Input
                  value={editedStore.branding?.style_name || 'Modern Minimal'}
                  disabled
                  className="bg-slate-50"
                />
              </div>

              <div className="space-y-2">
                <Label>Font Family</Label>
                <Input
                  value={editedStore.branding?.font_family || 'Inter'}
                  disabled
                  className="bg-slate-50"
                />
              </div>

              <Button onClick={handleSave} disabled={saving}>
                {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Save Branding
              </Button>
            </div>
          )}

          {/* Content Tab */}
          {activeTab === 'content' && (
            <div className="space-y-6">
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">FAQ</h3>
                {store.faqs?.map((faq, i) => (
                  <div key={i} className="border border-slate-200 rounded-lg p-4">
                    <p className="font-medium text-slate-900">{faq.question}</p>
                    <p className="mt-1 text-sm text-slate-600">{faq.answer}</p>
                  </div>
                ))}
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">Policies</h3>
                <div className="space-y-2">
                  <Label>Shipping Policy</Label>
                  <Textarea
                    rows={6}
                    value={store.policies?.shipping_policy || ''}
                    readOnly
                    className="bg-slate-50 text-sm"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Return Policy</Label>
                  <Textarea
                    rows={6}
                    value={store.policies?.return_policy || ''}
                    readOnly
                    className="bg-slate-50 text-sm"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
