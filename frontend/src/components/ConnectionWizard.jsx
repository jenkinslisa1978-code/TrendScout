import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  ChevronRight, ChevronLeft, Check, Copy, ExternalLink,
  Loader2, AlertCircle, Sparkles, Link2, ShieldCheck,
} from 'lucide-react';
import { apiGet, apiPost } from '@/lib/api';
import { toast } from 'sonner';

const PLATFORM_META = {
  shopify: { icon: '🟢', color: 'emerald', type: 'store' },
  etsy: { icon: '🟠', color: 'orange', type: 'store' },
  woocommerce: { icon: '🟣', color: 'purple', type: 'store' },
  bigcommerce: { icon: '🔵', color: 'blue', type: 'store' },
  squarespace: { icon: '⬛', color: 'slate', type: 'store' },
  meta: { icon: '🔵', color: 'blue', type: 'ads' },
  tiktok: { icon: '⬛', color: 'slate', type: 'ads' },
  google: { icon: '🔴', color: 'red', type: 'ads' },
  tiktok_shop: { icon: '⬛', color: 'slate', type: 'social' },
  instagram_shopping: { icon: '🟣', color: 'purple', type: 'social' },
  amazon_seller: { icon: '🟠', color: 'orange', type: 'social' },
};

const STEPS = ['select', 'setup', 'credentials', 'connect'];
const STEP_LABELS = ['Choose Platform', 'Setup Guide', 'Enter Credentials', 'Connect'];

export default function ConnectionWizard({ open, onClose, platforms, onConnected }) {
  const [step, setStep] = useState(0);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [selectedType, setSelectedType] = useState(null);
  const [oauthPlatformData, setOauthPlatformData] = useState(null);
  const [form, setForm] = useState({});
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [copied, setCopied] = useState(false);

  // Reset on open/close
  useEffect(() => {
    if (open) {
      setStep(0);
      setSelectedPlatform(null);
      setSelectedType(null);
      setForm({});
      setError('');
      setSuccess(false);
      setOauthPlatformData(null);
    }
  }, [open]);

  // Fetch OAuth platform setup info when a platform is selected
  useEffect(() => {
    if (!selectedPlatform) return;
    const fetchSetup = async () => {
      try {
        const oauthKey = mapPlatformToOAuth(selectedPlatform, selectedType);
        if (oauthKey) {
          const res = await apiGet(`/api/oauth/${oauthKey}/setup`);
          const data = await res.json();
          if (data.redirect_uri) setOauthPlatformData(data);
        }
      } catch {}
    };
    fetchSetup();
  }, [selectedPlatform, selectedType]);

  function mapPlatformToOAuth(key, type) {
    const map = {
      shopify: 'shopify', etsy: 'etsy', meta: 'meta',
      tiktok: 'tiktok_ads', google: 'google_ads',
      tiktok_shop: 'tiktok_shop', amazon_seller: 'amazon_seller',
    };
    return map[key] || null;
  }

  const allPlatforms = [];
  if (platforms.stores) {
    Object.entries(platforms.stores).forEach(([k, v]) => {
      allPlatforms.push({ key: k, type: 'store', ...v, ...PLATFORM_META[k] });
    });
  }
  if (platforms.ads) {
    Object.entries(platforms.ads).forEach(([k, v]) => {
      allPlatforms.push({ key: k, type: 'ads', ...v, ...PLATFORM_META[k] });
    });
  }
  if (platforms.social) {
    Object.entries(platforms.social).forEach(([k, v]) => {
      allPlatforms.push({ key: k, type: 'social', ...v, ...PLATFORM_META[k] });
    });
  }

  const currentPlatformData = allPlatforms.find(
    (p) => p.key === selectedPlatform && p.type === selectedType
  );

  const handleSelect = (platform) => {
    setSelectedPlatform(platform.key);
    setSelectedType(platform.type);
    setForm({});
    setError('');

    // If oauth_ready, skip to credentials step (just need shop domain for Shopify)
    if (platform.oauth_ready && platform.key === 'shopify') {
      setStep(2); // go to credentials for shop domain
    } else if (platform.oauth_ready) {
      // One-click connect — skip straight to connect
      setStep(3);
    } else {
      setStep(1); // show setup guide
    }
  };

  const handleConnect = async () => {
    setConnecting(true);
    setError('');
    try {
      const platformData = currentPlatformData;
      if (!platformData) throw new Error('Platform not found');

      // OAuth-ready platforms
      if (platformData.oauth_ready) {
        const oauthKey = platformData.oauth_key || mapPlatformToOAuth(selectedPlatform, selectedType);
        if (selectedPlatform === 'shopify') {
          // Shopify needs shop domain
          const domain = form.shop_domain?.trim();
          if (!domain) { setError('Shop domain is required'); setConnecting(false); return; }
          const res = await apiPost('/api/shopify/oauth/init', { shop_domain: domain });
          const data = await res.json();
          if (data.oauth_url) { window.location.href = data.oauth_url; return; }
          setError(data.detail || 'Failed to start OAuth');
        } else if (oauthKey) {
          const res = await apiPost(`/api/oauth/${oauthKey}/init`, {});
          const data = await res.json();
          if (data.oauth_url) { window.location.href = data.oauth_url; return; }
          setError(data.detail || 'Failed to start OAuth');
        }
      } else {
        // Manual credentials
        const typeMap = { store: '/api/connections/store', ads: '/api/connections/ads', supplier: '/api/connections/supplier', social: '/api/connections/social' };
        const endpoint = typeMap[selectedType] || '/api/connections/store';
        const body = { platform: selectedPlatform, ...form };
        const res = await apiPost(endpoint, body);
        const data = await res.json();
        if (data.success) {
          setSuccess(true);
          toast.success(`${platformData.name} connected successfully!`);
          setTimeout(() => { onConnected?.(); onClose(); }, 1500);
          return;
        }
        setError(data.detail || data.error?.message || 'Connection failed');
      }
    } catch (err) {
      setError('Connection failed. Please check your credentials.');
    } finally {
      setConnecting(false);
    }
  };

  const copyRedirectUri = () => {
    if (oauthPlatformData?.redirect_uri) {
      navigator.clipboard.writeText(oauthPlatformData.redirect_uri);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg p-0 overflow-hidden" data-testid="connection-wizard">
        {/* Progress bar */}
        <div className="flex border-b border-slate-100">
          {STEP_LABELS.map((label, i) => (
            <div key={i} className="flex-1 relative">
              <div className={`h-1 ${i <= step ? 'bg-indigo-500' : 'bg-slate-100'} transition-colors`} />
              <p className={`text-[9px] text-center py-1.5 ${
                i === step ? 'text-indigo-600 font-semibold' : i < step ? 'text-emerald-600' : 'text-slate-400'
              }`}>
                {i < step ? <Check className="h-2.5 w-2.5 inline mr-0.5" /> : null}
                {label}
              </p>
            </div>
          ))}
        </div>

        <div className="px-6 pb-6 pt-2">
          {/* Step 1: Select Platform */}
          {step === 0 && (
            <div data-testid="wizard-step-select">
              <DialogHeader className="mb-4">
                <DialogTitle className="text-lg flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-indigo-500" />
                  Connect a Platform
                </DialogTitle>
                <DialogDescription>
                  Choose which platform you'd like to connect to TrendScout.
                </DialogDescription>
              </DialogHeader>

              {['store', 'ads', 'social'].map((type) => {
                const items = allPlatforms.filter((p) => p.type === type);
                if (items.length === 0) return null;
                const label = type === 'store' ? 'E-Commerce Stores' : type === 'ads' ? 'Advertising' : 'Marketplaces';
                return (
                  <div key={type} className="mb-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase mb-2">{label}</p>
                    <div className="grid grid-cols-2 gap-2">
                      {items.map((p) => (
                        <button
                          key={p.key}
                          className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 transition-all text-left group"
                          onClick={() => handleSelect(p)}
                          data-testid={`wizard-select-${p.key}`}
                        >
                          <span className="text-lg">{p.icon || '🔗'}</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-900 truncate">{p.name}</p>
                            {p.oauth_ready && (
                              <span className="text-[9px] text-emerald-600 font-medium">One-click connect</span>
                            )}
                          </div>
                          <ChevronRight className="h-3.5 w-3.5 text-slate-300 group-hover:text-indigo-400 transition-colors" />
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Step 2: Setup Guide */}
          {step === 1 && currentPlatformData && (
            <div data-testid="wizard-step-setup">
              <DialogHeader className="mb-4">
                <DialogTitle className="text-lg flex items-center gap-2">
                  <span className="text-xl">{currentPlatformData.icon}</span>
                  Setup {currentPlatformData.name}
                </DialogTitle>
                <DialogDescription>
                  Follow these steps to get your API credentials.
                </DialogDescription>
              </DialogHeader>

              {/* Setup Instructions */}
              {(oauthPlatformData?.instructions || currentPlatformData.help) && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-4">
                  <pre className="text-xs text-slate-700 whitespace-pre-wrap font-sans leading-relaxed">
                    {oauthPlatformData?.instructions || currentPlatformData.help}
                  </pre>
                </div>
              )}

              {/* Redirect URI */}
              {oauthPlatformData?.redirect_uri && (
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3 mb-4">
                  <p className="text-[10px] font-semibold text-indigo-700 mb-1">Redirect URI (copy this into your app settings)</p>
                  <div className="flex items-center gap-2">
                    <code className="text-[11px] bg-white border border-indigo-200 rounded px-2 py-1 flex-1 break-all font-mono" data-testid="wizard-redirect-uri">
                      {oauthPlatformData.redirect_uri}
                    </code>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="shrink-0 h-7 text-xs"
                      onClick={copyRedirectUri}
                      data-testid="wizard-copy-uri"
                    >
                      {copied ? <Check className="h-3 w-3 text-emerald-500" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>
              )}

              {/* Developer Portal Link */}
              {(oauthPlatformData?.setup_url || currentPlatformData.url) && (
                <a
                  href={oauthPlatformData?.setup_url || currentPlatformData.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-sm text-indigo-600 hover:text-indigo-800 mb-4"
                >
                  Open Developer Portal <ExternalLink className="h-3.5 w-3.5" />
                </a>
              )}

              <div className="flex justify-between mt-4">
                <Button variant="ghost" size="sm" onClick={() => setStep(0)} data-testid="wizard-back-btn">
                  <ChevronLeft className="h-3.5 w-3.5 mr-1" /> Back
                </Button>
                <Button size="sm" onClick={() => setStep(2)} className="bg-indigo-600 hover:bg-indigo-700" data-testid="wizard-next-btn">
                  I've done this <ChevronRight className="h-3.5 w-3.5 ml-1" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Enter Credentials */}
          {step === 2 && currentPlatformData && (
            <div data-testid="wizard-step-credentials">
              <DialogHeader className="mb-4">
                <DialogTitle className="text-lg flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5 text-indigo-500" />
                  Enter Credentials
                </DialogTitle>
                <DialogDescription>
                  {currentPlatformData.oauth_ready
                    ? `Just enter your ${currentPlatformData.name} details to connect.`
                    : 'Paste the credentials from the previous step.'}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-3">
                {/* Shopify: just shop domain */}
                {selectedPlatform === 'shopify' && currentPlatformData.oauth_ready && (
                  <div>
                    <Label className="text-sm">Shop Domain</Label>
                    <Input
                      placeholder="your-store.myshopify.com"
                      value={form.shop_domain || ''}
                      onChange={(e) => setForm({ ...form, shop_domain: e.target.value })}
                      data-testid="wizard-shop-domain"
                    />
                    <p className="text-[10px] text-slate-400 mt-1">You'll be redirected to Shopify to authorize access</p>
                  </div>
                )}

                {/* Non-OAuth: show fields */}
                {!currentPlatformData.oauth_ready && (
                  <>
                    {currentPlatformData.fields?.includes('store_url') && (
                      <div>
                        <Label className="text-sm">Store URL</Label>
                        <Input
                          placeholder={`https://your-${selectedPlatform}-store.com`}
                          value={form.store_url || ''}
                          onChange={(e) => setForm({ ...form, store_url: e.target.value })}
                          data-testid="wizard-store-url"
                        />
                      </div>
                    )}
                    {currentPlatformData.fields?.includes('api_key') && (
                      <div>
                        <Label className="text-sm">API Key</Label>
                        <Input
                          placeholder="Your API key"
                          value={form.api_key || ''}
                          onChange={(e) => setForm({ ...form, api_key: e.target.value })}
                          data-testid="wizard-api-key"
                        />
                      </div>
                    )}
                    {currentPlatformData.fields?.includes('api_secret') && (
                      <div>
                        <Label className="text-sm">API Secret</Label>
                        <Input
                          type="password"
                          placeholder="Your API secret"
                          value={form.api_secret || ''}
                          onChange={(e) => setForm({ ...form, api_secret: e.target.value })}
                          data-testid="wizard-api-secret"
                        />
                      </div>
                    )}
                    {currentPlatformData.fields?.includes('access_token') && (
                      <div>
                        <Label className="text-sm">Access Token</Label>
                        <Input
                          type="password"
                          placeholder="Your access token"
                          value={form.access_token || ''}
                          onChange={(e) => setForm({ ...form, access_token: e.target.value })}
                          data-testid="wizard-access-token"
                        />
                      </div>
                    )}
                    {currentPlatformData.fields?.includes('account_id') && (
                      <div>
                        <Label className="text-sm">Account / Advertiser ID</Label>
                        <Input
                          placeholder="Your account ID"
                          value={form.account_id || ''}
                          onChange={(e) => setForm({ ...form, account_id: e.target.value })}
                          data-testid="wizard-account-id"
                        />
                      </div>
                    )}
                    {currentPlatformData.fields?.includes('pixel_id') && (
                      <div>
                        <Label className="text-sm">Pixel ID (optional)</Label>
                        <Input
                          placeholder="Your pixel ID"
                          value={form.pixel_id || ''}
                          onChange={(e) => setForm({ ...form, pixel_id: e.target.value })}
                          data-testid="wizard-pixel-id"
                        />
                      </div>
                    )}
                  </>
                )}

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 flex items-start gap-2" data-testid="wizard-error">
                    <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                    {error}
                  </div>
                )}
              </div>

              <div className="flex justify-between mt-5">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setStep(currentPlatformData.oauth_ready ? 0 : 1)}
                  data-testid="wizard-back-creds"
                >
                  <ChevronLeft className="h-3.5 w-3.5 mr-1" /> Back
                </Button>
                <Button
                  size="sm"
                  className="bg-indigo-600 hover:bg-indigo-700"
                  onClick={() => setStep(3)}
                  data-testid="wizard-next-connect"
                >
                  Continue <ChevronRight className="h-3.5 w-3.5 ml-1" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 4: Connect */}
          {step === 3 && currentPlatformData && (
            <div data-testid="wizard-step-connect">
              {success ? (
                <div className="text-center py-8">
                  <div className="h-16 w-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4 animate-in zoom-in duration-300">
                    <Check className="h-8 w-8 text-emerald-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-1">{currentPlatformData.name} Connected!</h3>
                  <p className="text-sm text-slate-500">Your account is now linked to TrendScout.</p>
                </div>
              ) : (
                <>
                  <DialogHeader className="mb-4">
                    <DialogTitle className="text-lg flex items-center gap-2">
                      <Link2 className="h-5 w-5 text-indigo-500" />
                      Ready to Connect
                    </DialogTitle>
                    <DialogDescription>
                      {currentPlatformData.oauth_ready
                        ? `Click below to securely connect your ${currentPlatformData.name} account.`
                        : `Review your details and connect.`}
                    </DialogDescription>
                  </DialogHeader>

                  {/* Summary */}
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-4">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-2xl">{currentPlatformData.icon}</span>
                      <div>
                        <p className="font-semibold text-slate-900">{currentPlatformData.name}</p>
                        <p className="text-xs text-slate-500 capitalize">{selectedType} connection</p>
                      </div>
                      {currentPlatformData.oauth_ready && (
                        <Badge className="ml-auto bg-emerald-100 text-emerald-700 border-emerald-200 text-[10px]">
                          Secure OAuth
                        </Badge>
                      )}
                    </div>
                    {currentPlatformData.oauth_ready && (
                      <p className="text-xs text-slate-500">
                        You'll be redirected to {currentPlatformData.name} to authorize. No credentials are stored on our servers.
                      </p>
                    )}
                  </div>

                  {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 mb-4 flex items-start gap-2" data-testid="wizard-connect-error">
                      <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                      {error}
                    </div>
                  )}

                  <div className="flex justify-between">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setStep(currentPlatformData.oauth_ready && selectedPlatform !== 'shopify' ? 0 : 2)}
                      data-testid="wizard-back-connect"
                    >
                      <ChevronLeft className="h-3.5 w-3.5 mr-1" /> Back
                    </Button>
                    <Button
                      className="bg-indigo-600 hover:bg-indigo-700"
                      onClick={handleConnect}
                      disabled={connecting}
                      data-testid="wizard-connect-btn"
                    >
                      {connecting ? (
                        <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Connecting...</>
                      ) : (
                        <><Link2 className="h-4 w-4 mr-2" /> Connect {currentPlatformData.name}</>
                      )}
                    </Button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
