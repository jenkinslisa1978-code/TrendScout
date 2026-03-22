import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Store, Megaphone, Plus, Check, X, ExternalLink, Trash2,
  ShoppingBag, Globe, Loader2, AlertCircle, Link2, HeartPulse, Truck, KeyRound,
} from 'lucide-react';
import api, { apiGet, apiPost, apiDelete } from '@/lib/api';
import { toast } from 'sonner';

const STORE_ICONS = {
  shopify: '🟢',
  woocommerce: '🟣',
  etsy: '🟠',
  bigcommerce: '🔵',
  squarespace: '⬛',
};

const STORE_AUTOMATION = {
  shopify: { level: 'full', label: 'Full Automation', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  woocommerce: { level: 'full', label: 'Full Automation', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  etsy: { level: 'full', label: 'Full Automation', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  bigcommerce: { level: 'full', label: 'Full Automation', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  squarespace: { level: 'full', label: 'Full Automation', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
};

const AD_ICONS = {
  meta: '🔵',
  tiktok: '⬛',
  google: '🔴',
};

const AD_AUTOMATION = {
  meta: { level: 'full', label: 'Auto-Post Ads', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  tiktok: { level: 'full', label: 'Auto-Post Ads', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  google: { level: 'draft', label: 'Draft Only', color: 'bg-blue-100 text-blue-700 border-blue-200' },
};

export default function PlatformConnectionsPage() {
  const [platforms, setPlatforms] = useState({ stores: {}, ads: {} });
  const [connections, setConnections] = useState({ stores: [], ads: [] });
  const [loading, setLoading] = useState(true);
  const [connectModal, setConnectModal] = useState(null);
  const [formData, setFormData] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [healthResults, setHealthResults] = useState(null);
  const [healthChecking, setHealthChecking] = useState(false);

  const runHealthCheck = async () => {
    setHealthChecking(true);
    try {
      const res = await apiPost('/api/connections/health-check');
      const data = await res.json();
      setHealthResults(data);
    } catch {
      setHealthResults({ error: true, message: 'Health check failed' });
    }
    setHealthChecking(false);
  };

  const fetchData = useCallback(async () => {
    try {
      const [platformsRes, connectionsRes] = await Promise.all([
        apiGet('/api/connections/platforms'),
        apiGet('/api/connections/'),
      ]);
      const platformsData = await platformsRes.json();
      const connectionsData = await connectionsRes.json();
      setPlatforms(platformsData);
      setConnections(connectionsData);
    } catch (err) {
      console.error('Failed to fetch connections:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Check for Shopify OAuth callback success
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('shopify') === 'connected') {
      window.history.replaceState({}, '', window.location.pathname);
      fetchData();
    }
  }, [fetchData]);

  const openConnect = (type, platformKey, platformData) => {
    setConnectModal({ type, key: platformKey, ...platformData });
    setFormData({});
    setError('');
  };

  const handleConnect = async () => {
    setSaving(true);
    setError('');
    try {
      const typeMap = { store: '/api/connections/store', ads: '/api/connections/ads', supplier: '/api/connections/supplier', social: '/api/connections/social' };
      const endpoint = typeMap[connectModal.type] || '/api/connections/store';
      const body = { platform: connectModal.key, ...formData };
      const res = await apiPost(endpoint, body);
      const data = await res.json();
      if (data.success) {
        setConnectModal(null);
        fetchData();
      } else {
        setError(data.detail || 'Connection failed');
      }
    } catch (err) {
      setError('Connection failed. Please check your credentials.');
    } finally {
      setSaving(false);
    }
  };

  const handleDisconnect = async (type, platform) => {
    try {
      if (platform === 'shopify') {
        await apiDelete('/api/shopify/oauth/disconnect');
      }
      await apiDelete(`/api/connections/${type}/${platform}`);
      fetchData();
    } catch (err) {
      console.error('Disconnect failed:', err);
    }
  };

  const [shopifyDomain, setShopifyDomain] = useState('');
  const [shopifyAccessToken, setShopifyAccessToken] = useState('');
  const [shopifyLoading, setShopifyLoading] = useState(false);
  const [shopifyError, setShopifyError] = useState('');

  // OAuth state
  const [oauthPlatforms, setOauthPlatforms] = useState({});
  const [oauthModal, setOauthModal] = useState(null);
  const [oauthForm, setOauthForm] = useState({ client_id: '', client_secret: '', shop_domain: '' });
  const [oauthLoading, setOauthLoading] = useState(false);
  const [oauthError, setOauthError] = useState('');

  // Fetch OAuth platforms
  useEffect(() => {
    const fetchOAuth = async () => {
      try {
        const res = await apiGet('/api/oauth/platforms');
        const data = await res.json().catch(() => ({}));
        setOauthPlatforms(data.platforms || {});
      } catch {}
    };
    fetchOAuth();
  }, []);

  // Handle OAuth callback results from URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const oauthSuccess = params.get('oauth_success');
    const oauthError = params.get('oauth_error');
    const platform = params.get('platform');

    if (oauthSuccess) {
      toast.success(`${oauthSuccess} connected successfully via OAuth!`);
      window.history.replaceState({}, '', window.location.pathname);
      fetchData();
    } else if (oauthError) {
      toast.error(`OAuth failed for ${platform || 'platform'}: ${oauthError}`);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [fetchData]);

  const handleOAuthInit = async () => {
    if (!oauthForm.client_id || !oauthForm.client_secret) return;
    setOauthLoading(true);
    setOauthError('');
    try {
      const body = {
        client_id: oauthForm.client_id.trim(),
        client_secret: oauthForm.client_secret.trim(),
      };
      if (oauthModal?.requires_shop_domain && oauthForm.shop_domain) {
        let domain = oauthForm.shop_domain.trim().toLowerCase();
        if (!domain.endsWith('.myshopify.com')) {
          domain = `${domain}.myshopify.com`;
        }
        body.shop_domain = domain;
      }
      const res = await apiPost(`/api/oauth/${oauthModal.key}/init`, body);
      const data = await res.json().catch(() => ({}));
      if (data.oauth_url) {
        window.location.href = data.oauth_url;
      } else {
        setOauthError(data.detail || 'Failed to start OAuth flow');
      }
    } catch (err) {
      setOauthError('Failed to initiate OAuth. Please check your credentials.');
    } finally {
      setOauthLoading(false);
    }
  };

  const openOAuthModal = (platformKey) => {
    const config = oauthPlatforms[platformKey];
    if (!config) return;
    setOauthModal({ key: platformKey, ...config });
    setOauthForm({ client_id: '', client_secret: '', shop_domain: '' });
    setOauthError('');
  };

  const handleShopifyConnect = async () => {
    if (!shopifyDomain.trim() || !shopifyAccessToken.trim()) return;
    setShopifyLoading(true);
    setShopifyError('');
    try {
      let domain = shopifyDomain.trim().toLowerCase();
      if (!domain.endsWith('.myshopify.com')) {
        domain = `${domain}.myshopify.com`;
      }
      const response = await api.post('/api/connections/store', {
        platform: 'shopify',
        store_url: `https://${domain}`,
        access_token: shopifyAccessToken.trim(),
      });
      if (!response.ok || !response.data.success) {
        setShopifyError(response.data.detail || response.data.error?.message || 'Failed to connect Shopify store');
        return;
      }
      setShopifyDomain('');
      setShopifyAccessToken('');
      fetchData();
    } catch (err) {
      console.error('Shopify connect error:', err);
      setShopifyError('Failed to connect to Shopify. Please try again.');
    } finally {
      setShopifyLoading(false);
    }
  };

  const isConnected = (type, platform) => {
    const list = connections[type === 'store' ? 'stores' : type === 'ads' ? 'ads' : type === 'supplier' ? 'suppliers' : 'social'] || [];
    return list?.some((c) => c.platform === platform);
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8" data-testid="platform-connections">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 font-manrope">Platform Connections</h1>
            <p className="text-slate-500 mt-1">Connect your store and ad accounts to auto-publish products and post ads</p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={runHealthCheck}
            disabled={healthChecking}
            data-testid="health-check-btn"
          >
            {healthChecking ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <HeartPulse className="h-4 w-4 mr-1" />}
            {healthChecking ? 'Checking...' : 'Health Check'}
          </Button>
        </div>

        {/* Health Check Results */}
        {healthResults && !healthResults.error && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3" data-testid="health-check-results">
            <div className="flex items-center gap-2 mb-2">
              <HeartPulse className="h-4 w-4 text-indigo-500" />
              <span className="text-sm font-semibold text-slate-800">{healthResults.message}</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {healthResults.results?.map((r, i) => (
                <div key={i} className={`rounded-lg p-2 text-xs border ${
                  r.status === 'healthy' ? 'bg-emerald-50 border-emerald-200' :
                  r.status === 'draft' ? 'bg-blue-50 border-blue-200' :
                  'bg-red-50 border-red-200'
                }`}>
                  <p className="font-semibold capitalize">{r.platform}</p>
                  <p className={r.status === 'healthy' ? 'text-emerald-600' : r.status === 'draft' ? 'text-blue-600' : 'text-red-600'}>{r.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* E-Commerce Stores */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Store className="h-5 w-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-slate-900">E-Commerce Stores</h2>
          </div>
          <p className="text-sm text-slate-500 mb-4">Connect your online store so TrendScout can automatically publish products for you</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(platforms.stores || {}).map(([key, platform]) => {
              const connected = isConnected('store', key);
              const conn = connections.stores?.find((c) => c.platform === key);
              return (
                <Card key={key} className={`border ${connected ? 'border-emerald-200 bg-emerald-50/30' : 'border-slate-200'}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{STORE_ICONS[key] || '🔗'}</span>
                        <span className="font-semibold text-slate-900">{platform.name}</span>
                      </div>
                      {connected ? (
                        <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">Connected</Badge>
                      ) : (
                        <Badge variant="outline" className="text-slate-400">Not connected</Badge>
                      )}
                    </div>
                    {STORE_AUTOMATION[key] && (
                      <Badge className={`${STORE_AUTOMATION[key].color} text-[10px] mb-2`} data-testid={`automation-badge-${key}`}>
                        {STORE_AUTOMATION[key].label}
                      </Badge>
                    )}
                    {connected && conn && (
                      <p className="text-xs text-slate-500 mb-3 truncate">{conn.store_url}</p>
                    )}
                    <div className="flex gap-2">
                      {connected ? (
                        <>
                          <Button variant="outline" size="sm" className="flex-1 text-xs" disabled>
                            <Check className="h-3 w-3 mr-1" /> Connected
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700"
                            onClick={() => handleDisconnect('store', key)}
                            data-testid={`disconnect-${key}`}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </>
                      ) : key === 'shopify' ? (
                        <div className="w-full space-y-2">
                          <input
                            type="text"
                            placeholder="your-store.myshopify.com"
                            value={shopifyDomain}
                            onChange={(e) => setShopifyDomain(e.target.value)}
                            className="w-full text-xs border border-slate-200 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            data-testid="shopify-domain-input"
                          />
                          <input
                            type="password"
                            placeholder="Admin API access token"
                            value={shopifyAccessToken}
                            onChange={(e) => setShopifyAccessToken(e.target.value)}
                            className="w-full text-xs border border-slate-200 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            data-testid="shopify-access-token-input"
                          />
                          <p className="text-[10px] text-slate-400 leading-relaxed">
                            In your Shopify admin: <span className="font-medium text-slate-500">Settings &gt; Apps &gt; Develop apps &gt; Create app &gt; Configure Admin API scopes &gt; Install</span>, then copy the Admin API access token.
                          </p>
                          {shopifyError && (
                            <div className="bg-red-50 border border-red-200 rounded-md p-2 text-xs text-red-700" data-testid="shopify-error">
                              {shopifyError}
                            </div>
                          )}
                          <Button
                            size="sm"
                            className="w-full bg-emerald-600 hover:bg-emerald-700 text-xs"
                            onClick={handleShopifyConnect}
                            disabled={shopifyLoading || !shopifyDomain.trim() || !shopifyAccessToken.trim()}
                            data-testid="connect-shopify-btn"
                          >
                            {shopifyLoading ? (
                              <><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Connecting...</>
                            ) : (
                              <><Plus className="h-3 w-3 mr-1" /> Connect Shopify Store</>
                            )}
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-xs"
                          onClick={() => openConnect('store', key, platform)}
                          data-testid={`connect-${key}`}
                        >
                          <Plus className="h-3 w-3 mr-1" /> Connect
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Ad Platforms */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Megaphone className="h-5 w-5 text-purple-600" />
            <h2 className="text-lg font-semibold text-slate-900">Advertising Platforms</h2>
          </div>
          <p className="text-sm text-slate-500 mb-4">Connect your ad accounts so TrendScout can automatically post your ads</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(platforms.ads || {}).map(([key, platform]) => {
              const connected = isConnected('ads', key);
              const conn = connections.ads?.find((c) => c.platform === key);
              return (
                <Card key={key} className={`border ${connected ? 'border-emerald-200 bg-emerald-50/30' : 'border-slate-200'}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{AD_ICONS[key] || '📢'}</span>
                        <span className="font-semibold text-slate-900">{platform.name}</span>
                      </div>
                      {connected ? (
                        <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">Connected</Badge>
                      ) : (
                        <Badge variant="outline" className="text-slate-400">Not connected</Badge>
                      )}
                    </div>
                    {AD_AUTOMATION[key] && (
                      <Badge className={`${AD_AUTOMATION[key].color} text-[10px] mb-2`} data-testid={`automation-badge-${key}-ads`}>
                        {AD_AUTOMATION[key].label}
                      </Badge>
                    )}
                    {connected && conn && (
                      <p className="text-xs text-slate-500 mb-3">Account: {conn.account_id || 'Connected'}</p>
                    )}
                    <div className="flex gap-2">
                      {connected ? (
                        <>
                          <Button variant="outline" size="sm" className="flex-1 text-xs" disabled>
                            <Check className="h-3 w-3 mr-1" /> Connected
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700"
                            onClick={() => handleDisconnect('ads', key)}
                            data-testid={`disconnect-${key}-ads`}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </>
                      ) : (
                        <Button
                          size="sm"
                          className="flex-1 bg-purple-600 hover:bg-purple-700 text-xs"
                          onClick={() => openConnect('ads', key, platform)}
                          data-testid={`connect-${key}-ads`}
                        >
                          <Plus className="h-3 w-3 mr-1" /> Connect
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Social & Marketplace Platforms */}
        <div>
          <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <Globe className="h-5 w-5 text-violet-500" />
            Social & Marketplaces
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(platforms.social || {}).map(([key, platform]) => {
              const connected = isConnected('social', key);
              return (
                <Card key={key} className={`border ${connected ? 'border-violet-200 bg-violet-50/30' : 'border-slate-200'}`}>
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-slate-900 text-sm">{platform.name}</p>
                        <p className="text-xs text-slate-500">{connected ? 'Connected' : 'Not connected'}</p>
                      </div>
                      {connected && <div className="h-2.5 w-2.5 rounded-full bg-violet-500" />}
                    </div>
                    <div className="flex items-center gap-2">
                      {connected ? (
                        <>
                          <Button variant="outline" size="sm" className="flex-1 text-xs" disabled>
                            <Check className="h-3 w-3 mr-1" /> Connected
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700"
                            onClick={() => handleDisconnect('social', key)}
                            data-testid={`disconnect-${key}-social`}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </>
                      ) : (
                        <Button
                          size="sm"
                          className="flex-1 bg-violet-600 hover:bg-violet-700 text-xs"
                          onClick={() => openConnect('social', key, platform)}
                          data-testid={`connect-${key}-social`}
                        >
                          <Plus className="h-3 w-3 mr-1" /> Connect
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Supplier Platforms */}
        <div>
          <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
            <Truck className="h-5 w-5 text-amber-500" />
            Suppliers
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(platforms.suppliers || {}).map(([key, platform]) => {
              const connected = isConnected('supplier', key);
              return (
                <Card key={key} className={`border ${connected ? 'border-amber-200 bg-amber-50/30' : 'border-slate-200'}`}>
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-slate-900 text-sm">{platform.name}</p>
                        <p className="text-xs text-slate-500">{connected ? 'Connected' : 'Not connected'}</p>
                      </div>
                      {connected && <div className="h-2.5 w-2.5 rounded-full bg-amber-500" />}
                    </div>
                    <div className="flex items-center gap-2">
                      {connected ? (
                        <>
                          <Button variant="outline" size="sm" className="flex-1 text-xs" disabled>
                            <Check className="h-3 w-3 mr-1" /> Connected
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700"
                            onClick={() => handleDisconnect('supplier', key)}
                            data-testid={`disconnect-${key}-supplier`}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </>
                      ) : (
                        <Button
                          size="sm"
                          className="flex-1 bg-amber-600 hover:bg-amber-700 text-xs"
                          onClick={() => openConnect('supplier', key, platform)}
                          data-testid={`connect-${key}-supplier`}
                        >
                          <Plus className="h-3 w-3 mr-1" /> Connect
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* OAuth Connect Section */}
        {Object.keys(oauthPlatforms).length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <KeyRound className="h-5 w-5 text-teal-600" />
              <h2 className="text-lg font-semibold text-slate-900">OAuth Connections</h2>
              <Badge className="bg-teal-100 text-teal-700 border-teal-200 text-[10px]">Secure Login</Badge>
            </div>
            <p className="text-sm text-slate-500 mb-4">
              Connect platforms securely using OAuth. You'll be redirected to each platform to authorize access — no API keys stored on our end.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(oauthPlatforms).map(([key, config]) => {
                const connected = isConnected(config.connection_type, key);
                return (
                  <Card key={key} className={`border ${connected ? 'border-teal-200 bg-teal-50/30' : 'border-slate-200 hover:border-teal-200 transition-colors'}`}>
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-slate-900 text-sm">{config.name}</p>
                          <p className="text-[10px] text-slate-400 uppercase">{config.connection_type}</p>
                        </div>
                        {connected ? (
                          <Badge className="bg-teal-100 text-teal-700 border-teal-200">Connected</Badge>
                        ) : (
                          <Badge variant="outline" className="text-slate-400">Available</Badge>
                        )}
                      </div>
                      {!connected && (
                        <Button
                          size="sm"
                          className="w-full bg-teal-600 hover:bg-teal-700 text-xs"
                          onClick={() => openOAuthModal(key)}
                          data-testid={`oauth-connect-${key}`}
                        >
                          <KeyRound className="h-3 w-3 mr-1" /> Connect with OAuth
                        </Button>
                      )}
                      {connected && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="w-full text-red-500 hover:text-red-700 text-xs"
                          onClick={() => handleDisconnect(config.connection_type, key)}
                          data-testid={`oauth-disconnect-${key}`}
                        >
                          <Trash2 className="h-3 w-3 mr-1" /> Disconnect
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* How It Works */}
        <Card className="border-slate-200">
          <CardContent className="p-6">
            <h3 className="font-semibold text-slate-900 mb-4">How it works</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700 font-bold text-sm shrink-0">1</div>
                <div>
                  <p className="font-medium text-slate-800 text-sm">Connect your platforms</p>
                  <p className="text-xs text-slate-500">Link your Shopify/WooCommerce store and ad accounts above</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700 font-bold text-sm shrink-0">2</div>
                <div>
                  <p className="font-medium text-slate-800 text-sm">Pick a winning product</p>
                  <p className="text-xs text-slate-500">Use the Quick Launch on your dashboard to choose what to sell</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700 font-bold text-sm shrink-0">3</div>
                <div>
                  <p className="font-medium text-slate-800 text-sm">Auto-publish & auto-post</p>
                  <p className="text-xs text-slate-500">Products go live on your store and ads start running — automatically</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Connect Modal */}
      <Dialog open={!!connectModal} onOpenChange={() => setConnectModal(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Link2 className="h-5 w-5 text-indigo-600" />
              Connect {connectModal?.name}
            </DialogTitle>
            <DialogDescription>
              Enter your API credentials to connect. Your keys are stored securely.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-2">
            {/* Help text */}
            {connectModal?.help && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-xs text-blue-700">{connectModal.help}</p>
                    {connectModal.url && (
                      <a href={connectModal.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 underline flex items-center gap-1 mt-1">
                        Open {connectModal.name} <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Dynamic fields */}
            {connectModal?.fields?.includes('store_url') && (
              <div>
                <Label className="text-sm font-medium">Store URL</Label>
                <Input
                  placeholder="https://your-store.myshopify.com"
                  value={formData.store_url || ''}
                  onChange={(e) => setFormData({ ...formData, store_url: e.target.value })}
                  data-testid="connect-store-url"
                />
              </div>
            )}
            {connectModal?.fields?.includes('api_key') && (
              <div>
                <Label className="text-sm font-medium">API Key</Label>
                <Input
                  placeholder="Enter your API key"
                  value={formData.api_key || ''}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  data-testid="connect-api-key"
                />
              </div>
            )}
            {connectModal?.fields?.includes('api_secret') && (
              <div>
                <Label className="text-sm font-medium">API Secret</Label>
                <Input
                  type="password"
                  placeholder="Enter your API secret"
                  value={formData.api_secret || ''}
                  onChange={(e) => setFormData({ ...formData, api_secret: e.target.value })}
                  data-testid="connect-api-secret"
                />
              </div>
            )}
            {connectModal?.fields?.includes('access_token') && (
              <div>
                <Label className="text-sm font-medium">Access Token</Label>
                <Input
                  type="password"
                  placeholder="Enter your access token"
                  value={formData.access_token || ''}
                  onChange={(e) => setFormData({ ...formData, access_token: e.target.value })}
                  data-testid="connect-access-token"
                />
              </div>
            )}
            {connectModal?.fields?.includes('account_id') && (
              <div>
                <Label className="text-sm font-medium">Account / Advertiser ID</Label>
                <Input
                  placeholder="Enter your account ID"
                  value={formData.account_id || ''}
                  onChange={(e) => setFormData({ ...formData, account_id: e.target.value })}
                  data-testid="connect-account-id"
                />
              </div>
            )}
            {connectModal?.fields?.includes('pixel_id') && (
              <div>
                <Label className="text-sm font-medium">Pixel ID (optional)</Label>
                <Input
                  placeholder="Enter your pixel ID"
                  value={formData.pixel_id || ''}
                  onChange={(e) => setFormData({ ...formData, pixel_id: e.target.value })}
                  data-testid="connect-pixel-id"
                />
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">{error}</div>
            )}

            <Button
              onClick={handleConnect}
              disabled={saving}
              className="w-full bg-indigo-600 hover:bg-indigo-700"
              data-testid="connect-save-btn"
            >
              {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Check className="mr-2 h-4 w-4" />}
              {saving ? 'Connecting...' : 'Connect'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* OAuth Modal */}
      <Dialog open={!!oauthModal} onOpenChange={() => setOauthModal(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <KeyRound className="h-5 w-5 text-teal-600" />
              Connect {oauthModal?.name} via OAuth
            </DialogTitle>
            <DialogDescription>
              Enter your app credentials to securely connect via OAuth 2.0. You'll be redirected to authorize.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-2">
            {/* Setup Instructions */}
            {oauthModal?.instructions && (
              <div className="bg-teal-50 border border-teal-200 rounded-lg p-3">
                <p className="text-[11px] font-semibold text-teal-800 mb-1">Setup Instructions</p>
                <pre className="text-[10px] text-teal-700 whitespace-pre-wrap font-sans leading-relaxed">
                  {oauthModal.instructions}
                </pre>
                {oauthModal.setup_url && (
                  <a href={oauthModal.setup_url} target="_blank" rel="noopener noreferrer" className="text-xs text-teal-600 underline flex items-center gap-1 mt-2">
                    Open Developer Portal <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            )}

            {/* Redirect URI */}
            {oauthModal?.redirect_uri && (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                <p className="text-[10px] font-semibold text-slate-600 mb-1">Redirect URI (add this to your app)</p>
                <code className="text-[10px] bg-white border border-slate-200 rounded px-2 py-1 block break-all" data-testid="oauth-redirect-uri">
                  {oauthModal.redirect_uri}
                </code>
              </div>
            )}

            {/* Shop Domain (if required, e.g., Shopify) */}
            {oauthModal?.requires_shop_domain && (
              <div>
                <Label className="text-sm font-medium">Shop Domain</Label>
                <Input
                  placeholder="your-store.myshopify.com"
                  value={oauthForm.shop_domain}
                  onChange={(e) => setOauthForm({ ...oauthForm, shop_domain: e.target.value })}
                  data-testid="oauth-shop-domain"
                />
              </div>
            )}

            <div>
              <Label className="text-sm font-medium">Client ID / App Key</Label>
              <Input
                placeholder="Enter your Client ID"
                value={oauthForm.client_id}
                onChange={(e) => setOauthForm({ ...oauthForm, client_id: e.target.value })}
                data-testid="oauth-client-id"
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Client Secret / App Secret</Label>
              <Input
                type="password"
                placeholder="Enter your Client Secret"
                value={oauthForm.client_secret}
                onChange={(e) => setOauthForm({ ...oauthForm, client_secret: e.target.value })}
                data-testid="oauth-client-secret"
              />
            </div>

            {oauthError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700" data-testid="oauth-error">{oauthError}</div>
            )}

            <Button
              onClick={handleOAuthInit}
              disabled={oauthLoading || !oauthForm.client_id || !oauthForm.client_secret}
              className="w-full bg-teal-600 hover:bg-teal-700"
              data-testid="oauth-start-btn"
            >
              {oauthLoading ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Redirecting...</>
              ) : (
                <><KeyRound className="mr-2 h-4 w-4" /> Authorize with {oauthModal?.name}</>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
