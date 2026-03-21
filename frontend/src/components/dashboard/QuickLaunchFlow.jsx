import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Rocket, Store, Megaphone, ArrowRight, CheckCircle2, Loader2, Sparkles, Link2, AlertCircle } from 'lucide-react';
import { apiGet, apiPost } from '@/lib/api';

export default function QuickLaunchFlow() {
  const navigate = useNavigate();
  const [topProduct, setTopProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);
  const [storeCreated, setStoreCreated] = useState(null);
  const [adsGenerated, setAdsGenerated] = useState(false);
  const [adsPosted, setAdsPosted] = useState(null);
  const [connections, setConnections] = useState({ stores: [], ads: [] });
  const [step, setStep] = useState(1);

  useEffect(() => {
    const fetchTop = async () => {
      try {
        const [prodRes, connRes] = await Promise.all([
          apiGet('/api/products?page=1&limit=10&sort_by=launch_score&sort_order=desc'),
          apiGet('/api/connections/').catch(() => null),
        ]);
        const res = await prodRes.json();
        const products = res?.data || res?.products || [];
        if (products.length > 0) {
          const best = products.sort((a, b) => (b.launch_score || 0) - (a.launch_score || 0))[0];
          setTopProduct(best);
        }
        if (connRes) {
          const connData = await connRes.json();
          setConnections(connData);
        }
      } catch (err) {
        console.error('Failed to fetch top product:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTop();
  }, []);

  const hasStoreConnection = connections.stores?.length > 0;
  const hasAdConnection = connections.ads?.length > 0;

  const handleSetUpShop = async () => {
    if (!topProduct) return;
    setLaunching(true);
    try {
      // Create the store
      const response = await apiPost('/api/stores/launch', {
        product_id: topProduct.id,
        store_name: `${topProduct.product_name.split(' ').slice(0, 3).join(' ')} Store`,
      });
      const res = await response.json();
      if (res?.store) {
        setStoreCreated(res.store);

        // Auto-publish if connected
        if (hasStoreConnection) {
          try {
            const pubRes = await apiPost(`/api/connections/publish/${res.store.id}`);
            const pubData = await pubRes.json();
            if (pubData.success) {
              setStoreCreated({ ...res.store, published: true, platform: pubData.platform, store_url: pubData.store_url });
            }
          } catch (pubErr) {
            console.error('Auto-publish failed:', pubErr);
          }
        }
        setStep(3);
      }
    } catch (err) {
      console.error('Store creation failed:', err);
    } finally {
      setLaunching(false);
    }
  };

  const handleMakeAds = async () => {
    if (!topProduct) return;
    setLaunching(true);
    try {
      // Generate the ad creatives
      const response = await apiPost(`/api/ad-creatives/generate/${topProduct.id}`);
      await response.json();
      setAdsGenerated(true);

      // Auto-post if connected
      if (hasAdConnection) {
        try {
          const postRes = await apiPost(`/api/connections/post-ads/${topProduct.id}`);
          const postData = await postRes.json();
          if (postData.success) {
            setAdsPosted(postData);
          }
        } catch (postErr) {
          console.error('Auto-post failed:', postErr);
        }
      }
      setStep(4);
    } catch (err) {
      console.error('Ad generation failed:', err);
    } finally {
      setLaunching(false);
    }
  };

  if (loading) return null;
  if (!topProduct) return null;

  const margin = ((topProduct.estimated_retail_price || 0) - (topProduct.supplier_cost || 0)).toFixed(2);

  return (
    <Card className="border-2 border-indigo-200 shadow-lg overflow-hidden" data-testid="quick-launch-flow">
      <div className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
            <Rocket className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white font-manrope">Launch a Product in 3 Clicks</h2>
            <p className="text-sm text-white/80">We've found your best product. Set up shop and make ads — all from here.</p>
          </div>
        </div>
      </div>

      <CardContent className="p-6">
        {/* Progress Steps */}
        <div className="flex items-center gap-2 mb-6">
          {[
            { num: 1, label: 'Pick a winner' },
            { num: 2, label: 'Set up shop' },
            { num: 3, label: 'Make ads' },
          ].map((s, i) => (
            <React.Fragment key={s.num}>
              <div className={`flex items-center gap-2 ${step > s.num ? 'text-emerald-600' : step === s.num ? 'text-indigo-600' : 'text-slate-300'}`}>
                <div className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
                  step > s.num ? 'bg-emerald-100 text-emerald-700' : step === s.num ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-400'
                }`}>
                  {step > s.num ? <CheckCircle2 className="h-4 w-4" /> : s.num}
                </div>
                <span className="text-sm font-medium hidden sm:inline">{s.label}</span>
              </div>
              {i < 2 && <div className={`flex-1 h-0.5 ${step > s.num + 1 ? 'bg-emerald-300' : 'bg-slate-200'}`} />}
            </React.Fragment>
          ))}
        </div>

        {/* Step 1: Product Recommendation */}
        <div className={`rounded-xl border p-4 mb-4 ${step >= 1 ? 'border-indigo-200 bg-indigo-50/30' : 'border-slate-200 bg-slate-50'}`}>
          <div className="flex items-start gap-4">
            {topProduct.image_url ? (
              <img src={topProduct.image_url} alt="" className="w-16 h-16 rounded-lg object-cover flex-shrink-0"  loading="lazy" /> 
            ) : (
              <div className="w-16 h-16 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-6 w-6 text-indigo-400" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200 text-xs">Our #1 Pick</Badge>
                <Badge variant="outline" className="text-xs">{topProduct.category}</Badge>
              </div>
              <h3 className="font-semibold text-slate-900 truncate" data-testid="quick-launch-product-name">
                {topProduct.product_name}
              </h3>
              <div className="flex items-center gap-4 mt-2 text-sm">
                <span className="text-emerald-600 font-semibold">£{margin} profit per sale</span>
                <span className="text-slate-400">|</span>
                <span className="text-slate-600">Supplier: £{(topProduct.supplier_cost || 0).toFixed(2)}</span>
                <span className="text-slate-400">|</span>
                <span className="text-slate-600">Sell for: £{(topProduct.estimated_retail_price || 0).toFixed(2)}</span>
              </div>
              <div className="flex items-center gap-3 mt-2">
                <div className="flex items-center gap-1 text-xs">
                  <span className="text-slate-500">Launch Score:</span>
                  <span className="font-bold text-indigo-600">{topProduct.launch_score || 0}/100</span>
                  <span className="text-slate-400 ml-1">— How ready this product is to sell</span>
                </div>
              </div>
            </div>
            {step === 1 && (
              <Button
                onClick={() => setStep(2)}
                className="bg-indigo-600 hover:bg-indigo-700 shrink-0"
                data-testid="quick-launch-pick-btn"
              >
                Pick This
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            )}
            {step > 1 && (
              <div className="flex items-center gap-1 text-emerald-600 shrink-0">
                <CheckCircle2 className="h-5 w-5" />
                <span className="text-sm font-medium">Selected</span>
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Set Up Shop */}
        {step >= 2 && (
          <div className={`rounded-xl border p-4 mb-4 ${step === 2 ? 'border-indigo-200 bg-indigo-50/30' : 'border-slate-200 bg-slate-50'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${step > 2 ? 'bg-emerald-100' : 'bg-indigo-100'}`}>
                  <Store className={`h-5 w-5 ${step > 2 ? 'text-emerald-600' : 'text-indigo-600'}`} />
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">Set Up Your Shop</h4>
                  <p className="text-sm text-slate-500">
                    {storeCreated?.published
                      ? `Published to your ${storeCreated.platform} store`
                      : storeCreated
                      ? `"${storeCreated.name}" created as draft`
                      : hasStoreConnection
                      ? 'Auto-publish to your connected store'
                      : 'Create a store with this product ready to sell'}
                  </p>
                  {!hasStoreConnection && step === 2 && !storeCreated && (
                    <button onClick={() => navigate('/settings/connections')} className="text-xs text-indigo-600 hover:underline mt-1">
                      Connect your Shopify/WooCommerce for auto-publish
                    </button>
                  )}
                </div>
              </div>
              {step === 2 && !storeCreated && (
                <Button
                  onClick={handleSetUpShop}
                  disabled={launching}
                  className="bg-indigo-600 hover:bg-indigo-700"
                  data-testid="quick-launch-shop-btn"
                >
                  {launching ? <Loader2 className="mr-1 h-4 w-4 animate-spin" /> : <Store className="mr-1 h-4 w-4" />}
                  {launching ? 'Creating...' : 'Create Shop'}
                </Button>
              )}
              {step > 2 && (
                <div className="flex items-center gap-1 text-emerald-600">
                  <CheckCircle2 className="h-5 w-5" />
                  <span className="text-sm font-medium">Shop Created</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Make Ads */}
        {step >= 3 && (
          <div className={`rounded-xl border p-4 mb-4 ${step === 3 ? 'border-indigo-200 bg-indigo-50/30' : 'border-slate-200 bg-slate-50'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${step > 3 ? 'bg-emerald-100' : 'bg-indigo-100'}`}>
                  <Megaphone className={`h-5 w-5 ${step > 3 ? 'text-emerald-600' : 'text-indigo-600'}`} />
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">Generate Your Ads</h4>
                  <p className="text-sm text-slate-500">
                    {adsPosted
                      ? `Ads submitted to ${adsPosted.posted_to?.map(p => p.name).join(', ')}`
                      : adsGenerated
                      ? 'Ad concepts ready — view them in Ad Tests'
                      : hasAdConnection
                      ? 'Auto-post ads to your connected platforms'
                      : 'AI will create ad concepts for TikTok, Facebook & Instagram'}
                  </p>
                  {!hasAdConnection && step === 3 && !adsGenerated && (
                    <button onClick={() => navigate('/settings/connections')} className="text-xs text-indigo-600 hover:underline mt-1">
                      Connect your ad accounts for auto-posting
                    </button>
                  )}
                </div>
              </div>
              {step === 3 && !adsGenerated && (
                <div className="flex items-center gap-2">
                  <Button
                    onClick={handleMakeAds}
                    disabled={launching}
                    className="bg-indigo-600 hover:bg-indigo-700"
                    data-testid="quick-launch-ads-btn"
                  >
                    {launching ? <Loader2 className="mr-1 h-4 w-4 animate-spin" /> : <Megaphone className="mr-1 h-4 w-4" />}
                    {launching ? 'Generating...' : 'Make Ads'}
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => { setAdsGenerated(false); setStep(4); }}
                    className="text-slate-500 text-sm"
                    data-testid="quick-launch-skip-ads-btn"
                  >
                    Skip, I'll do my own
                  </Button>
                </div>
              )}
              {step > 3 && (
                <div className="flex items-center gap-1 text-emerald-600">
                  <CheckCircle2 className="h-5 w-5" />
                  <span className="text-sm font-medium">Ads Generated</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Completion */}
        {step === 4 && (
          <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-center">
            <CheckCircle2 className="h-8 w-8 text-emerald-600 mx-auto mb-2" />
            <h4 className="font-bold text-emerald-900 text-lg">
              {adsGenerated ? "You're Ready to Launch!" : "Shop Created!"}
            </h4>
            <p className="text-sm text-emerald-700 mb-3">
              {adsGenerated
                ? storeCreated?.published
                  ? `Published to ${storeCreated.platform} and ads submitted. You're live!`
                  : 'Your shop and ads are set up. View your store to customise and publish.'
                : 'Your shop is ready. You can create ads later from the Ad Tests page.'}
            </p>
            <div className="flex items-center justify-center gap-3">
              {storeCreated && (
                <Button
                  onClick={() => navigate(`/stores/${storeCreated.id}`)}
                  className="bg-emerald-600 hover:bg-emerald-700"
                  data-testid="quick-launch-view-store-btn"
                >
                  View My Shop
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Button>
              )}
              <Button
                variant="outline"
                onClick={() => navigate(`/product/${topProduct.id}`)}
                data-testid="quick-launch-view-product-btn"
              >
                See Full Analysis
              </Button>
            </div>
          </div>
        )}

        {/* Not interested link */}
        {step === 1 && (
          <button
            onClick={() => navigate('/discover')}
            className="text-xs text-slate-400 hover:text-slate-600 mt-2 block mx-auto"
            data-testid="quick-launch-browse-more"
          >
            Not interested? Browse all products instead
          </button>
        )}
      </CardContent>
    </Card>
  );
}
