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
  ShoppingBag, Globe, Loader2, AlertCircle, Link2,
} from 'lucide-react';
import { apiGet, apiPost, apiDelete } from '@/lib/api';

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
  etsy: { level: 'manual', label: 'Manual Import', color: 'bg-amber-100 text-amber-700 border-amber-200' },
  bigcommerce: { level: 'manual', label: 'Manual Import', color: 'bg-amber-100 text-amber-700 border-amber-200' },
  squarespace: { level: 'manual', label: 'Manual Import', color: 'bg-amber-100 text-amber-700 border-amber-200' },
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

  const openConnect = (type, platformKey, platformData) => {
    setConnectModal({ type, key: platformKey, ...platformData });
    setFormData({});
    setError('');
  };

  const handleConnect = async () => {
    setSaving(true);
    setError('');
    try {
      const endpoint = connectModal.type === 'store' ? '/api/connections/store' : '/api/connections/ads';
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
      await apiDelete(`/api/connections/${type}/${platform}`);
      fetchData();
    } catch (err) {
      console.error('Disconnect failed:', err);
    }
  };

  const isConnected = (type, platform) => {
    const list = type === 'store' ? connections.stores : connections.ads;
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
        <div>
          <h1 className="text-2xl font-bold text-slate-900 font-manrope">Platform Connections</h1>
          <p className="text-slate-500 mt-1">Connect your store and ad accounts to auto-publish products and post ads</p>
        </div>

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
    </DashboardLayout>
  );
}
