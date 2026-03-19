import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Package, Check, ChevronRight, ChevronLeft, Truck, DollarSign,
  Star, Loader2, Rocket, Store, Palette, FileText, Sparkles,
  ArrowRight, TrendingUp, ShoppingBag, RefreshCw, Info,
  Video, MessageSquare,
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { apiGet, apiPost } from '@/lib/api';
import { toast } from 'sonner';

const STEPS = [
  { id: 1, label: 'Product Intel', icon: Package, tip: 'Product intelligence and pricing strategy.' },
  { id: 2, label: 'Supplier', icon: Truck, tip: 'Verified supplier with cost analysis.' },
  { id: 3, label: 'Store Assets', icon: Store, tip: 'Product page, Shopify data, and store preview.' },
  { id: 4, label: 'Ad Pack', icon: Sparkles, tip: 'Ad creatives, scripts, and A/B test plan.' },
  { id: 5, label: 'Launch', icon: Rocket, tip: 'Review checklist and create your store package.' },
];

export default function ProductLaunchWizard() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [product, setProduct] = useState(null);
  const [suppliers, setSuppliers] = useState([]);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [storeData, setStoreData] = useState(null);
  const [adCreatives, setAdCreatives] = useState(null);
  const [launchResult, setLaunchResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (productId) loadProduct();
  }, [productId]);

  const loadProduct = async () => {
    setLoading(true);
    try {
      const res = await apiGet(`/api/products/${productId}`);
      if (res.ok) {
        const data = await res.json();
        setProduct(data.data || data);
        loadSuppliers();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadSuppliers = async () => {
    try {
      const res = await apiGet(`/api/suppliers/${productId}`);
      if (res.ok) {
        const data = await res.json();
        const list = data.suppliers || [];
        setSuppliers(list);
        if (list.length > 0) setSelectedSupplier(list[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerateStore = async () => {
    setActionLoading(true);
    try {
      // Use the store launch endpoint to generate preview
      const body = {
        product_id: productId,
        supplier_id: selectedSupplier?.id,
        store_name: product?.product_name,
        preview_only: true,
      };
      const res = await apiPost(`/api/stores/launch`, body);
      if (res.ok) {
        const data = await res.json();
        setStoreData(data);
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || 'Failed to generate store preview');
      }
    } catch (err) {
      toast.error('Store generation failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateAds = async () => {
    setActionLoading(true);
    try {
      const res = await apiPost(`/api/ad-creatives/generate/${productId}`);
      if (res.ok) {
        const data = await res.json();
        setAdCreatives(data);
      } else {
        toast.error('Failed to generate ad creatives');
      }
    } catch (err) {
      toast.error('Ad generation failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleLaunch = async () => {
    // If store was already created in step 3, just mark as launched
    if (storeData?.store_id || storeData?.id) {
      setLaunchResult(storeData);
      toast.success('Store package created! Connect Shopify to go live.');
      trackOutcome(storeData?.store_id || storeData?.id);
      return;
    }
    setActionLoading(true);
    try {
      const body = {
        product_id: productId,
        supplier_id: selectedSupplier?.id,
        store_name: storeData?.store?.name || product?.product_name,
      };
      const res = await apiPost(`/api/stores/launch`, body);
      if (res.ok) {
        const data = await res.json();
        setLaunchResult(data);
        toast.success('Store package created! Connect Shopify to go live.');
        trackOutcome(data.store_id || data.store?.id || data.id);
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || 'Launch failed');
      }
    } catch (err) {
      toast.error('Launch failed');
    } finally {
      setActionLoading(false);
    }
  };

  const trackOutcome = async (storeId) => {
    try {
      await apiPost('/api/outcomes/track', {
        product_id: productId,
        store_id: storeId,
      });
    } catch (e) {
      // Silent - non-critical
    }
  };

  const nextStep = () => {
    if (step === 2 && !storeData) handleGenerateStore();
    if (step === 3 && !adCreatives) handleGenerateAds();
    if (step === 4) handleLaunch();
    if (step < 5) setStep(step + 1);
  };

  const prevStep = () => step > 1 && setStep(step - 1);
  const progress = (step / 5) * 100;

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6" data-testid="launch-wizard">
        {/* Wizard Header */}
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center">
              <Rocket className="h-4 w-4 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 font-manrope">TrendScout LaunchPad</h1>
          </div>
          <p className="text-slate-500 mt-1">Everything you need to launch — product intel, store package, ads, and go-live checklist. Connect Shopify to push live.</p>
        </div>

        {/* Step Indicators */}
        <div className="relative">
          <Progress value={progress} className="h-1.5 mb-4" />
          <TooltipProvider>
            <div className="flex justify-between">
              {STEPS.map((s) => {
                const Icon = s.icon;
                const isActive = step === s.id;
                const isDone = step > s.id;
                return (
                  <Tooltip key={s.id}>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => s.id <= step && setStep(s.id)}
                        className={`flex flex-col items-center gap-1 transition-all ${
                          isActive ? 'scale-110' : isDone ? 'opacity-70' : 'opacity-40'
                        }`}
                        data-testid={`wizard-step-${s.id}`}
                      >
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                          isDone ? 'bg-emerald-100 text-emerald-600' :
                          isActive ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' :
                          'bg-slate-100 text-slate-400'
                        }`}>
                          {isDone ? <Check className="h-5 w-5" /> : <Icon className="h-5 w-5" />}
                        </div>
                        <span className={`text-xs font-medium ${isActive ? 'text-indigo-600' : 'text-slate-500'}`}>
                          {s.label}
                        </span>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent><p className="text-xs">{s.tip}</p></TooltipContent>
                  </Tooltip>
                );
              })}
            </div>
          </TooltipProvider>
        </div>

        {/* Step Content */}
        <Card className="border-0 shadow-lg">
          <CardContent className="p-8">
            {step === 1 && <Step1Product product={product} />}
            {step === 2 && (
              <Step2Supplier
                suppliers={suppliers}
                selected={selectedSupplier}
                onSelect={setSelectedSupplier}
                product={product}
              />
            )}
            {step === 3 && <Step3Store storeData={storeData} loading={actionLoading} />}
            {step === 4 && <Step4Ads adCreatives={adCreatives} loading={actionLoading} />}
            {step === 5 && <Step5Launch result={launchResult} loading={actionLoading} navigate={navigate} />}
          </CardContent>
        </Card>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={prevStep}
            disabled={step === 1}
            data-testid="wizard-prev-btn"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          {step < 5 && (
            <Button
              onClick={nextStep}
              disabled={actionLoading}
              className="bg-indigo-600 hover:bg-indigo-700"
              data-testid="wizard-next-btn"
            >
              {actionLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  Processing...
                </>
              ) : step === 4 ? (
                <>
                  <Rocket className="h-4 w-4 mr-1" />
                  Launch Product
                </>
              ) : (
                <>
                  Next Step
                  <ChevronRight className="h-4 w-4 ml-1" />
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

// ─── Step Components ─────────────────────────────────

function Step1Product({ product }) {
  if (!product) return <p className="text-slate-500">Product not found.</p>;
  const supplierCost = product.supplier_cost || product.estimated_supplier_cost || 0;
  const retailPrice = product.estimated_retail_price || supplierCost * 2.5;
  const margin = retailPrice - supplierCost;
  const marginPct = retailPrice > 0 ? ((margin / retailPrice) * 100).toFixed(0) : 0;

  return (
    <div data-testid="wizard-step1-content">
      <div className="flex items-center gap-2 mb-4">
        <Package className="h-5 w-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-slate-900">Product Intelligence</h3>
      </div>
      <p className="text-sm text-slate-500 mb-6">
        AI-analysed product data and recommended pricing strategy.
      </p>
      <div className="flex items-start gap-5">
        {product.image_url ? (
          <img src={product.image_url} alt={product.product_name} className="w-24 h-24 rounded-xl object-cover bg-slate-100" />
        ) : (
          <div className="w-24 h-24 rounded-xl bg-indigo-50 flex items-center justify-center">
            <Package className="h-10 w-10 text-indigo-300" />
          </div>
        )}
        <div className="flex-1">
          <h4 className="font-bold text-slate-900 text-lg">{product.product_name}</h4>
          <p className="text-sm text-slate-500 mt-1">{product.category}</p>
          <div className="grid grid-cols-3 gap-3 mt-4">
            <MetricBox label="Launch Score" value={product.launch_score || '—'} color="indigo" tooltip="A prediction of how likely this product is to succeed." />
            <MetricBox label="Success Prob." value={`${product.success_probability || 0}%`} color="emerald" tooltip="The estimated probability of this product being a winner." />
            <MetricBox label="Trend Stage" value={product.trend_stage || 'Unknown'} color="amber" tooltip="Where this product is in its lifecycle: Emerging, Rising, etc." />
          </div>
        </div>
      </div>

      {/* Pricing Strategy */}
      <div className="mt-6 bg-gradient-to-r from-indigo-50 to-violet-50 rounded-xl p-5 border border-indigo-100" data-testid="pricing-strategy">
        <div className="flex items-center gap-2 mb-3">
          <DollarSign className="h-4 w-4 text-indigo-600" />
          <h4 className="font-semibold text-slate-800 text-sm">Recommended Pricing Strategy</h4>
        </div>
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-xs text-slate-400 mb-1">Supplier Cost</p>
            <p className="font-bold text-slate-800">£{supplierCost.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-xs text-slate-400 mb-1">Recommended Price</p>
            <p className="font-bold text-indigo-600">£{retailPrice.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-xs text-slate-400 mb-1">Estimated Margin</p>
            <p className="font-bold text-emerald-600">£{margin.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-xs text-slate-400 mb-1">Margin %</p>
            <p className="font-bold text-amber-600">{marginPct}%</p>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-3">Based on competitor pricing, demand signals, and margin targets.</p>
      </div>
    </div>
  );
}

function Step2Supplier({ suppliers, selected, onSelect, product }) {
  return (
    <div data-testid="wizard-step2-content">
      <div className="flex items-center gap-2 mb-4">
        <Truck className="h-5 w-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-slate-900">Confirm Your Supplier</h3>
      </div>
      <p className="text-sm text-slate-500 mb-6">
        We've automatically matched the best supplier for this product. The supplier is where your product ships from — you don't need to hold any stock.
      </p>
      {suppliers.length === 0 ? (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-700">
          <Info className="h-4 w-4 inline mr-1" />
          No suppliers found yet. We'll auto-match the best supplier when you launch.
        </div>
      ) : (
        <div className="space-y-3">
          {suppliers.slice(0, 3).map((sup) => (
            <div
              key={sup.id}
              onClick={() => onSelect(sup)}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selected?.id === sup.id
                  ? 'border-indigo-500 bg-indigo-50/50 shadow-sm'
                  : 'border-slate-200 hover:border-indigo-200'
              }`}
              data-testid={`supplier-option-${sup.id}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-slate-900">{sup.supplier_name || sup.name || 'Supplier'}</p>
                  <div className="flex items-center gap-4 mt-1 text-sm text-slate-500">
                    <span className="flex items-center gap-1"><DollarSign className="h-3 w-3" /> £{sup.price?.toFixed(2) || '—'}</span>
                    <span className="flex items-center gap-1"><Truck className="h-3 w-3" /> {sup.shipping_time || sup.delivery_estimate || '7-15 days'}</span>
                  </div>
                </div>
                {selected?.id === sup.id && (
                  <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center">
                    <Check className="h-4 w-4 text-white" />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Step3Store({ storeData, loading }) {
  return (
    <div data-testid="wizard-step3-content">
      <div className="flex items-center gap-2 mb-4">
        <Store className="h-5 w-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-slate-900">Store Preview</h3>
      </div>
      <p className="text-sm text-slate-500 mb-6">
        We've automatically created your store — complete with product pages, branding, pricing, and policies. Review the preview below.
      </p>
      {loading ? (
        <div className="flex flex-col items-center justify-center py-12 text-slate-400">
          <Loader2 className="h-8 w-8 animate-spin mb-3 text-indigo-400" />
          <p className="font-medium">Generating your store...</p>
          <p className="text-xs mt-1">Creating product pages, branding, and policies</p>
        </div>
      ) : storeData?.store || storeData?.generation ? (
        <div className="space-y-4">
          <div className="bg-slate-50 rounded-lg p-5">
            <h4 className="font-bold text-slate-900 text-lg mb-1">
              {storeData.store?.name || storeData.generation?.selected_name || 'Your Store'}
            </h4>
            <div className="grid grid-cols-2 gap-3 mt-3">
              {(storeData.store?.branding?.colors || storeData.generation?.brand_colors) && (
                <div className="flex items-center gap-2">
                  <Palette className="h-4 w-4 text-slate-400" />
                  <span className="text-sm text-slate-600">Brand colors generated</span>
                  <div className="flex gap-1">
                    {(storeData.store?.branding?.colors || storeData.generation?.brand_colors || []).slice(0, 3).map((c, i) => (
                      <div key={i} className="w-4 h-4 rounded-full border" style={{ backgroundColor: c }} />
                    ))}
                  </div>
                </div>
              )}
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-slate-400" />
                <span className="text-sm text-slate-600">Product pages ready</span>
              </div>
              <div className="flex items-center gap-2">
                <ShoppingBag className="h-4 w-4 text-slate-400" />
                <span className="text-sm text-slate-600">Checkout configured</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="h-4 w-4 text-emerald-500" />
                <span className="text-sm text-slate-600">Policies generated</span>
              </div>
            </div>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-sm text-emerald-700">
            <Check className="h-4 w-4 inline mr-1" />
            Store preview ready. Proceed to generate ads.
          </div>
          {/* Shopify Export */}
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mt-3" data-testid="shopify-export">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShoppingBag className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">Shopify Import File</span>
              </div>
              <Badge className="bg-blue-100 text-blue-700 border-blue-200 text-[10px]">Ready to export</Badge>
            </div>
            <p className="text-xs text-blue-600 mt-1">Product data, variants, images, and SEO metadata formatted for Shopify CSV import.</p>
          </div>
        </div>
      ) : (
        <div className="bg-slate-50 rounded-lg p-8 text-center text-slate-400">
          <Store className="h-10 w-10 mx-auto mb-2 opacity-50" />
          <p>Store will be generated when you proceed</p>
        </div>
      )}
    </div>
  );
}

function Step4Ads({ adCreatives, loading }) {
  return (
    <div data-testid="wizard-step4-content">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="h-5 w-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-slate-900">Ad Creatives Generated</h3>
      </div>
      <p className="text-sm text-slate-500 mb-6">
        Our AI has created ready-to-use ad scripts and copy. You can use these on TikTok, Facebook, and Instagram to start driving traffic.
      </p>
      {loading ? (
        <div className="flex flex-col items-center justify-center py-12 text-slate-400">
          <Loader2 className="h-8 w-8 animate-spin mb-3 text-indigo-400" />
          <p className="font-medium">Creating your ad creatives...</p>
          <p className="text-xs mt-1">Generating scripts, hooks, and copy for all platforms</p>
        </div>
      ) : adCreatives?.creatives ? (
        <div className="space-y-3">
          {adCreatives.creatives.tiktok_scripts && (
            <CreativePreview icon={Video} title="TikTok Ad Scripts" count={adCreatives.creatives.tiktok_scripts.length} />
          )}
          {adCreatives.creatives.facebook_ads && (
            <CreativePreview icon={MessageSquare} title="Facebook Ad Copy" count={adCreatives.creatives.facebook_ads.length} />
          )}
          {adCreatives.creatives.instagram_captions && (
            <CreativePreview icon={Star} title="Instagram Captions" count={adCreatives.creatives.instagram_captions.length} />
          )}
          {adCreatives.creatives.video_storyboard && (
            <CreativePreview icon={Video} title="Video Storyboard" count={1} />
          )}
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-sm text-emerald-700 mt-4">
            <Check className="h-4 w-4 inline mr-1" />
            All ad creatives ready. Click "Launch Product" to go live.
          </div>

          {/* Ad Test Plan */}
          <div className="bg-violet-50 border border-violet-100 rounded-xl p-5 mt-4" data-testid="ad-test-plan">
            <div className="flex items-center gap-2 mb-3">
              <RefreshCw className="h-4 w-4 text-violet-600" />
              <h4 className="font-semibold text-violet-800 text-sm">A/B Test Plan</h4>
            </div>
            <div className="space-y-2 text-sm">
              {[
                { phase: 'Phase 1 — Testing (Day 1-3)', budget: '£20/day', desc: 'Run 3 ad variations across TikTok + Facebook. Kill underperformers at £5 CPA.' },
                { phase: 'Phase 2 — Validation (Day 4-7)', budget: '£40/day', desc: 'Scale winning ad. Test 2 new audiences. Target 2x ROAS.' },
                { phase: 'Phase 3 — Scale (Day 8+)', budget: '£100+/day', desc: 'Increase budget on proven winners. Add lookalike audiences.' },
              ].map((p, i) => (
                <div key={i} className="bg-white rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-800">{p.phase}</span>
                    <Badge className="bg-violet-100 text-violet-700 border-violet-200 text-[10px]">{p.budget}</Badge>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{p.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-slate-50 rounded-lg p-8 text-center text-slate-400">
          <Sparkles className="h-10 w-10 mx-auto mb-2 opacity-50" />
          <p>Ads will be generated when you proceed</p>
        </div>
      )}
    </div>
  );
}

function Step5Launch({ result, loading, navigate }) {
  const [checklist, setChecklist] = useState({
    product: true, supplier: true, store: true, ads: true,
    pricing: false, testPlan: false, tracking: false,
  });

  const toggleCheck = (key) => setChecklist(prev => ({ ...prev, [key]: !prev[key] }));
  const allChecked = Object.values(checklist).every(Boolean);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12" data-testid="wizard-step5-content">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-500 mb-3" />
        <p className="font-semibold text-slate-800">Creating your store package...</p>
        <p className="text-sm text-slate-500 mt-1">Generating product pages, branding, and supplier data</p>
      </div>
    );
  }

  if (result) {
    const storeId = result.store_id || result.store?.id || result.id;
    return (
      <div className="text-center py-8" data-testid="wizard-step5-content">
        <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
          <Check className="h-8 w-8 text-emerald-600" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-2">Store Package Ready!</h3>
        <p className="text-slate-500 mb-2">Your store has been created with product pages, branding, and supplier data.</p>
        <p className="text-sm text-amber-600 font-medium mb-6">
          To go live, connect your Shopify store and export from the store page.
        </p>
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6 max-w-md mx-auto text-left">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Next Steps</p>
          <div className="space-y-2.5">
            <div className="flex items-start gap-2.5">
              <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5 text-xs font-bold text-indigo-600">1</div>
              <p className="text-sm text-slate-700">Connect your Shopify store in <a href="/settings/connections" className="text-indigo-600 underline">Settings &rarr; Connections</a></p>
            </div>
            <div className="flex items-start gap-2.5">
              <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5 text-xs font-bold text-indigo-600">2</div>
              <p className="text-sm text-slate-700">View your store package and click <strong>"Export to Shopify"</strong></p>
            </div>
            <div className="flex items-start gap-2.5">
              <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5 text-xs font-bold text-indigo-600">3</div>
              <p className="text-sm text-slate-700">Products will be pushed to your Shopify store as drafts</p>
            </div>
          </div>
        </div>
        <div className="flex flex-wrap justify-center gap-3">
          <Button onClick={() => navigate(`/store/${storeId}`)} className="bg-indigo-600 hover:bg-indigo-700" data-testid="view-store-btn">
            <Store className="h-4 w-4 mr-2" /> View Store Package
          </Button>
          <Button variant="outline" onClick={() => navigate('/settings/connections')} data-testid="connect-shopify-btn">
            <ShoppingBag className="h-4 w-4 mr-2" /> Connect Shopify
          </Button>
          <Button variant="outline" onClick={() => navigate('/dashboard')} data-testid="back-to-dashboard-btn">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="wizard-step5-content">
      <div className="flex items-center gap-2 mb-4">
        <Rocket className="h-5 w-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-slate-900">Launch Checklist</h3>
      </div>
      <p className="text-sm text-slate-500 mb-6">
        Review all items before going live. Tick off each step to confirm you're ready.
      </p>
      <div className="space-y-2" data-testid="launch-checklist">
        {[
          { key: 'product', label: 'Product intelligence reviewed', auto: true },
          { key: 'supplier', label: 'Supplier confirmed and cost locked', auto: true },
          { key: 'store', label: 'Store pages and branding generated', auto: true },
          { key: 'ads', label: 'Ad creatives and scripts ready', auto: true },
          { key: 'pricing', label: 'Pricing strategy confirmed' },
          { key: 'testPlan', label: 'Ad test plan reviewed (budget & KPIs)' },
          { key: 'tracking', label: 'Pixel/tracking ready on store' },
        ].map(item => (
          <button
            key={item.key}
            onClick={() => !item.auto && toggleCheck(item.key)}
            className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all text-left ${
              checklist[item.key]
                ? 'border-emerald-200 bg-emerald-50/50'
                : 'border-slate-200 hover:border-slate-300'
            }`}
            data-testid={`checklist-${item.key}`}
          >
            <div className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 ${
              checklist[item.key] ? 'bg-emerald-500 text-white' : 'border-2 border-slate-300'
            }`}>
              {checklist[item.key] && <Check className="h-3 w-3" />}
            </div>
            <span className={`text-sm ${checklist[item.key] ? 'text-slate-700' : 'text-slate-500'}`}>
              {item.label}
            </span>
            {item.auto && <Badge className="ml-auto bg-slate-100 text-slate-500 border-slate-200 text-[9px]">Auto</Badge>}
          </button>
        ))}
      </div>
      {!allChecked && (
        <p className="text-xs text-amber-600 mt-3 flex items-center gap-1">
          <Info className="h-3 w-3" /> Complete all checklist items before launching.
        </p>
      )}
    </div>
  );
}

// ─── Helper Components ─────────────────────────────

function MetricBox({ label, value, color, tooltip }) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className={`bg-${color}-50 rounded-lg p-3 text-center cursor-help`}>
            <p className={`text-xl font-bold text-${color}-700 font-mono`}>{value}</p>
            <p className={`text-xs text-${color}-500 mt-0.5 flex items-center justify-center gap-1`}>
              {label} <Info className="h-2.5 w-2.5" />
            </p>
          </div>
        </TooltipTrigger>
        <TooltipContent><p className="text-xs max-w-[200px]">{tooltip}</p></TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

function CreativePreview({ icon: Icon, title, count }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
      <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
        <Icon className="h-4 w-4 text-indigo-600" />
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-slate-800">{title}</p>
        <p className="text-xs text-slate-500">{count} {count === 1 ? 'piece' : 'pieces'} generated</p>
      </div>
      <Check className="h-5 w-5 text-emerald-500" />
    </div>
  );
}
