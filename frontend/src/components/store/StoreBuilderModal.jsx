import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  X, 
  Sparkles, 
  Store, 
  ArrowRight, 
  Check,
  Loader2,
  Palette,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { generateStore, createStore, getStoreLimits, getUserStores } from '@/services/storeService';

export default function StoreBuilderModal({ product, isOpen, onClose }) {
  const navigate = useNavigate();
  const { profile } = useAuth();
  const userId = profile?.id || 'demo-user-id';
  const userPlan = profile?.plan || 'elite';

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generation, setGeneration] = useState(null);
  const [selectedName, setSelectedName] = useState('');
  const [customName, setCustomName] = useState('');
  const [canCreate, setCanCreate] = useState(true);
  const [storesRemaining, setStoresRemaining] = useState('checking...');

  useEffect(() => {
    if (isOpen && product) {
      checkLimits();
      generateContent();
    }
  }, [isOpen, product]);

  const checkLimits = async () => {
    const limits = await getStoreLimits(userPlan);
    const { data: stores } = await getUserStores(userId);
    
    const limit = limits.limit === 'unlimited' ? Infinity : limits.limit;
    const count = stores.length;
    
    setCanCreate(count < limit);
    setStoresRemaining(limit === Infinity ? 'unlimited' : `${limit - count}`);
  };

  const generateContent = async () => {
    setGenerating(true);
    const result = await generateStore(product.id, userId, userPlan);
    
    if (result.success !== false) {
      setGeneration(result.generation);
      setSelectedName(result.generation.selected_name);
    } else {
      toast.error(result.error || 'Failed to generate store content');
    }
    setGenerating(false);
  };

  const handleRegenerate = async () => {
    setGenerating(true);
    const result = await generateStore(product.id, userId, userPlan, customName || null);
    
    if (result.success !== false) {
      setGeneration(result.generation);
      if (!customName) {
        setSelectedName(result.generation.selected_name);
      }
    }
    setGenerating(false);
  };

  const handleCreate = async () => {
    const storeName = customName || selectedName;
    
    if (!storeName.trim()) {
      toast.error('Please enter a store name');
      return;
    }
    
    setLoading(true);
    const result = await createStore(storeName, product.id, userId, userPlan);
    
    if (result.success) {
      toast.success('Store created successfully!');
      onClose();
      navigate(`/stores/${result.store.id}`);
    } else {
      toast.error(result.error || 'Failed to create store');
    }
    setLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-indigo-600 to-purple-600">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Build Your Shop</h2>
              <p className="text-sm text-white/80">AI-powered store creation</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center hover:bg-white/20 transition-colors"
          >
            <X className="h-5 w-5 text-white" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Limit Check */}
          {!canCreate ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 rounded-2xl bg-amber-100 flex items-center justify-center mx-auto mb-4">
                <Store className="h-8 w-8 text-amber-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Store Limit Reached</h3>
              <p className="text-slate-600 mb-4">
                Your {userPlan} plan allows a limited number of stores. 
                Upgrade to create more!
              </p>
              <Button onClick={onClose} variant="outline">Close</Button>
            </div>
          ) : generating ? (
            /* Generating State */
            <div className="text-center py-12">
              <Loader2 className="h-12 w-12 animate-spin text-indigo-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">
                Generating Your Store
              </h3>
              <p className="text-slate-600">
                Creating store name, tagline, product copy, and branding...
              </p>
            </div>
          ) : generation ? (
            /* Generation Result */
            <div className="space-y-6">
              {/* Product Info */}
              <div className="flex items-center gap-4 p-4 bg-slate-50 rounded-xl">
                <div className="w-16 h-16 rounded-lg bg-slate-200 flex items-center justify-center">
                  {product.image_url ? (
                    <img src={product.image_url} alt="" className="w-full h-full object-cover rounded-lg" />
                  ) : (
                    <Store className="h-6 w-6 text-slate-400" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-slate-900">{product.product_name}</p>
                  <p className="text-sm text-slate-500">{product.category}</p>
                </div>
                <Badge className="bg-indigo-100 text-indigo-700">
                  Score: {product.trend_score}
                </Badge>
              </div>

              {/* Step 1: Choose Name */}
              {step === 1 && (
                <div className="space-y-4">
                  <Label className="text-base font-semibold">Choose Your Store Name</Label>
                  
                  {/* Suggested Names */}
                  <div className="grid grid-cols-2 gap-2">
                    {generation.store_name_suggestions?.map((name) => (
                      <button
                        key={name}
                        onClick={() => {
                          setSelectedName(name);
                          setCustomName('');
                        }}
                        className={`p-3 rounded-lg border-2 text-left transition-all ${
                          selectedName === name && !customName
                            ? 'border-indigo-600 bg-indigo-50'
                            : 'border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        <p className="font-medium text-slate-900">{name}</p>
                      </button>
                    ))}
                  </div>

                  {/* Custom Name */}
                  <div className="space-y-2">
                    <Label className="text-sm text-slate-500">Or enter your own</Label>
                    <Input
                      placeholder="Enter custom store name"
                      value={customName}
                      onChange={(e) => setCustomName(e.target.value)}
                      className="h-12"
                    />
                  </div>

                  {/* Regenerate */}
                  <button
                    onClick={handleRegenerate}
                    disabled={generating}
                    className="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-700"
                  >
                    <RefreshCw className={`h-4 w-4 ${generating ? 'animate-spin' : ''}`} />
                    Generate new suggestions
                  </button>
                </div>
              )}

              {/* Step 2: Preview */}
              {step === 2 && (
                <div className="space-y-4">
                  <Label className="text-base font-semibold">Preview Your Store</Label>
                  
                  <div className="border rounded-xl overflow-hidden">
                    {/* Mini Preview Header */}
                    <div 
                      className="p-4 text-white"
                      style={{ backgroundColor: generation.branding?.primary_color || '#0f172a' }}
                    >
                      <h3 className="font-bold">{customName || selectedName}</h3>
                      <p className="text-sm text-white/80">{generation.tagline}</p>
                    </div>
                    
                    {/* Mini Preview Content */}
                    <div className="p-4 space-y-3">
                      <p className="font-semibold text-lg text-slate-900">
                        {generation.headline}
                      </p>
                      <div className="flex items-center gap-4">
                        <span className="text-2xl font-bold text-slate-900">
                          £{generation.product?.pricing?.suggested_price?.toFixed(2)}
                        </span>
                        <Badge 
                          style={{ 
                            backgroundColor: `${generation.branding?.accent_color}20`,
                            color: generation.branding?.accent_color 
                          }}
                        >
                          {generation.product?.category}
                        </Badge>
                      </div>
                      <ul className="space-y-1">
                        {generation.product?.bullet_points?.slice(0, 3).map((point, i) => (
                          <li key={i} className="flex items-center gap-2 text-sm text-slate-600">
                            <Check className="h-4 w-4 text-emerald-500" />
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Branding Preview */}
                  <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-xl">
                    <Palette className="h-5 w-5 text-slate-400" />
                    <span className="text-sm text-slate-600">
                      Style: {generation.branding?.style_name}
                    </span>
                    <div className="flex gap-1 ml-auto">
                      <div 
                        className="w-6 h-6 rounded-full border border-white shadow"
                        style={{ backgroundColor: generation.branding?.primary_color }}
                      />
                      <div 
                        className="w-6 h-6 rounded-full border border-white shadow"
                        style={{ backgroundColor: generation.branding?.secondary_color }}
                      />
                      <div 
                        className="w-6 h-6 rounded-full border border-white shadow"
                        style={{ backgroundColor: generation.branding?.accent_color }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t">
                <div className="text-sm text-slate-500">
                  {storesRemaining !== 'unlimited' && (
                    <span>{storesRemaining} stores remaining</span>
                  )}
                </div>
                <div className="flex gap-2">
                  {step === 2 && (
                    <Button variant="outline" onClick={() => setStep(1)}>
                      Back
                    </Button>
                  )}
                  {step === 1 ? (
                    <Button 
                      onClick={() => setStep(2)}
                      disabled={!selectedName && !customName}
                      className="bg-indigo-600 hover:bg-indigo-700"
                    >
                      Preview
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  ) : (
                    <Button 
                      onClick={handleCreate}
                      disabled={loading}
                      className="bg-emerald-600 hover:bg-emerald-700"
                      data-testid="create-store-confirm-btn"
                    >
                      {loading ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Store className="h-4 w-4 mr-2" />
                      )}
                      Create Store
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
