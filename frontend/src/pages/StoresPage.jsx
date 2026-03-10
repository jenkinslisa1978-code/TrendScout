import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Store, 
  Plus, 
  ExternalLink, 
  Settings, 
  Trash2, 
  Package,
  Eye,
  MoreVertical,
  Loader2,
  Sparkles,
  Lock,
  Check,
  FileDown,
  Rocket,
  Edit3
} from 'lucide-react';
import { toast } from 'sonner';
import { getUserStores, deleteStore, getStoreLimits } from '@/services/storeService';

// Status configuration with colors and progress
const STATUS_CONFIG = {
  draft: { 
    label: 'Draft', 
    color: 'bg-slate-100 text-slate-600',
    progress: 1,
    description: 'Store created, needs review'
  },
  ready: { 
    label: 'Ready', 
    color: 'bg-blue-100 text-blue-700',
    progress: 2,
    description: 'Ready to export'
  },
  exported: { 
    label: 'Exported', 
    color: 'bg-amber-100 text-amber-700',
    progress: 3,
    description: 'Exported to Shopify'
  },
  published: { 
    label: 'Published', 
    color: 'bg-emerald-100 text-emerald-700',
    progress: 4,
    description: 'Live on Shopify'
  },
  archived: { 
    label: 'Archived', 
    color: 'bg-slate-100 text-slate-500',
    progress: 0,
    description: 'No longer active'
  },
};

// Progress steps for the launch flow
const LAUNCH_STEPS = [
  { id: 1, label: 'Create', icon: Edit3, status: 'draft' },
  { id: 2, label: 'Review', icon: Check, status: 'ready' },
  { id: 3, label: 'Export', icon: FileDown, status: 'exported' },
  { id: 4, label: 'Launch', icon: Rocket, status: 'published' },
];

// Progress indicator component
const LaunchProgress = ({ currentStatus }) => {
  const currentProgress = STATUS_CONFIG[currentStatus]?.progress || 0;
  
  return (
    <div className="flex items-center gap-1 mt-3">
      {LAUNCH_STEPS.map((step, index) => {
        const isComplete = currentProgress >= step.id;
        const isCurrent = currentProgress === step.id;
        
        return (
          <React.Fragment key={step.id}>
            <div className="flex flex-col items-center">
              <div 
                className={`w-6 h-6 rounded-full flex items-center justify-center transition-all ${
                  isComplete 
                    ? 'bg-emerald-500 text-white' 
                    : isCurrent 
                      ? 'bg-indigo-500 text-white ring-2 ring-indigo-200' 
                      : 'bg-slate-100 text-slate-400'
                }`}
              >
                {isComplete && currentProgress > step.id ? (
                  <Check className="h-3 w-3" />
                ) : (
                  <step.icon className="h-3 w-3" />
                )}
              </div>
              <span className={`text-[10px] mt-1 ${
                isComplete ? 'text-slate-700 font-medium' : 'text-slate-400'
              }`}>
                {step.label}
              </span>
            </div>
            {index < LAUNCH_STEPS.length - 1 && (
              <div 
                className={`flex-1 h-0.5 mb-4 ${
                  currentProgress > step.id ? 'bg-emerald-500' : 'bg-slate-200'
                }`}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

export default function StoresPage() {
  const { profile, isDemoMode } = useAuth();
  const navigate = useNavigate();
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [limits, setLimits] = useState({ limit: 1, plan: 'starter' });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);

  const userId = profile?.id || 'demo-user-id';
  const userPlan = profile?.plan || 'elite';

  useEffect(() => {
    loadStores();
    loadLimits();
  }, [userId, userPlan]);

  const loadStores = async () => {
    setLoading(true);
    const { data } = await getUserStores();
    setStores(data);
    setLoading(false);
  };

  const loadLimits = async () => {
    const data = await getStoreLimits(userPlan);
    setLimits(data);
  };

  const handleDelete = async (storeId) => {
    const result = await deleteStore(storeId);
    if (result.success) {
      toast.success('Store deleted successfully');
      setStores(stores.filter(s => s.id !== storeId));
    } else {
      toast.error(result.error || 'Failed to delete store');
    }
    setShowDeleteConfirm(null);
  };

  const canCreateMore = () => {
    if (limits.limit === 'unlimited') return true;
    return stores.length < limits.limit;
  };

  const storesRemaining = () => {
    if (limits.limit === 'unlimited') return 'unlimited';
    return Math.max(0, limits.limit - stores.length);
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-manrope text-3xl font-bold text-slate-900">My Stores</h1>
            <p className="mt-1 text-slate-600">
              Manage your stores and launch new shops from trending products
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="text-right mr-4">
              <p className="text-sm text-slate-500">
                {stores.length} / {limits.limit === 'unlimited' ? '∞' : limits.limit} stores
              </p>
              <p className="text-xs text-slate-400 capitalize">{userPlan} Plan</p>
            </div>
            
            {canCreateMore() ? (
              <Button 
                onClick={() => navigate('/discover')}
                data-testid="create-store-btn"
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Store
              </Button>
            ) : (
              <Button variant="outline" disabled className="gap-2">
                <Lock className="h-4 w-4" />
                Limit Reached
              </Button>
            )}
          </div>
        </div>

        {/* Limit Warning */}
        {!canCreateMore() && (
          <div className="rounded-xl bg-amber-50 border border-amber-200 p-4">
            <div className="flex items-start gap-3">
              <Lock className="h-5 w-5 text-amber-600 mt-0.5" />
              <div>
                <p className="font-medium text-amber-800">Store limit reached</p>
                <p className="text-sm text-amber-700 mt-1">
                  Your {userPlan} plan allows {limits.limit} store{limits.limit !== 1 ? 's' : ''}. 
                  Upgrade to Pro (5 stores) or Elite (unlimited) to create more.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : stores.length === 0 ? (
          /* Empty State */
          <div className="rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center">
            <div className="mx-auto w-16 h-16 rounded-2xl bg-indigo-100 flex items-center justify-center mb-4">
              <Store className="h-8 w-8 text-indigo-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">No stores yet</h3>
            <p className="mt-2 text-slate-600 max-w-md mx-auto">
              Create your first store by finding a trending product and clicking "Build Shop"
            </p>
            <Button 
              onClick={() => navigate('/discover')}
              className="mt-6 bg-indigo-600 hover:bg-indigo-700"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Find Products to Sell
            </Button>
          </div>
        ) : (
          /* Store Grid */
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {stores.map((store) => {
              const statusConfig = STATUS_CONFIG[store.status] || STATUS_CONFIG.draft;
              
              return (
                <div
                  key={store.id}
                  data-testid={`store-card-${store.id}`}
                  className="group relative rounded-2xl border border-slate-200 bg-white p-6 transition-all hover:shadow-lg hover:border-slate-300"
                >
                  {/* Store Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div 
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg"
                      style={{ backgroundColor: store.branding?.primary_color || '#6366f1' }}
                    >
                      {store.name?.charAt(0) || 'S'}
                    </div>
                    <Badge className={statusConfig.color}>
                      {statusConfig.label}
                    </Badge>
                  </div>

                  {/* Store Info */}
                  <h3 className="font-semibold text-lg text-slate-900 mb-1">{store.name}</h3>
                  <p className="text-sm text-slate-500 mb-2 line-clamp-2">
                    {store.tagline || 'No tagline set'}
                  </p>

                  {/* Stats */}
                  <div className="flex items-center gap-4 text-sm text-slate-600 mb-2">
                    <div className="flex items-center gap-1">
                      <Package className="h-4 w-4" />
                      <span>{store.product_count || 0} products</span>
                    </div>
                    <div className="text-slate-300">|</div>
                    <div className="capitalize">{store.category}</div>
                  </div>

                  {/* Launch Progress */}
                  <LaunchProgress currentStatus={store.status} />

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-4 mt-4 border-t border-slate-100">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigate(`/stores/${store.id}`)}
                      className="flex-1"
                    >
                      <Settings className="h-4 w-4 mr-1" />
                      Manage
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(`/preview/${store.id}`, '_blank')}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowDeleteConfirm(store.id)}
                      className="text-red-500 hover:text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Delete Confirmation */}
                  {showDeleteConfirm === store.id && (
                    <div className="absolute inset-0 bg-white/95 backdrop-blur-sm rounded-2xl flex flex-col items-center justify-center p-6 z-10">
                      <p className="text-sm text-slate-600 mb-4 text-center">
                        Delete "{store.name}"? This cannot be undone.
                      </p>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowDeleteConfirm(null)}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(store.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Quick Tips */}
        <div className="rounded-xl bg-slate-50 p-6">
          <h3 className="font-semibold text-slate-900 mb-3">Quick Tips</h3>
          <ul className="space-y-2 text-sm text-slate-600">
            <li className="flex items-start gap-2">
              <span className="text-indigo-600">1.</span>
              Find trending products in the Discover tab
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-600">2.</span>
              Click "Build Shop" to generate a store with AI-powered copy
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-600">3.</span>
              Edit your store details and preview the storefront
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-600">4.</span>
              Export to Shopify when ready to launch
            </li>
          </ul>
        </div>
      </div>
    </DashboardLayout>
  );
}
