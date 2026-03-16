import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Key, Plus, Trash2, Copy, Loader2, Shield,
  Code, Terminal, Clock, Zap, CheckCircle, AlertTriangle,
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function ApiDocsPage() {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newKeyName, setNewKeyName] = useState('');
  const [creating, setCreating] = useState(false);
  const [newKey, setNewKey] = useState(null);

  useEffect(() => { fetchKeys(); }, []);

  const fetchKeys = async () => {
    try {
      const res = await api.get('/api/api-keys/');
      if (res.ok) setKeys(res.data.keys || []);
    } catch {}
    setLoading(false);
  };

  const generateKey = async () => {
    if (!newKeyName.trim()) return;
    setCreating(true);
    try {
      const res = await api.post('/api/api-keys/generate', { name: newKeyName.trim() });
      if (res.ok) {
        setNewKey(res.data.key);
        setNewKeyName('');
        fetchKeys();
        toast.success('API key generated');
      } else {
        toast.error(res.data?.detail || 'Failed to generate key');
      }
    } catch { toast.error('Failed'); }
    setCreating(false);
  };

  const revokeKey = async (id) => {
    try {
      await api.delete(`/api/api-keys/${id}`);
      setKeys(prev => prev.filter(k => k.id !== id));
      toast.success('Key revoked');
    } catch { toast.error('Failed to revoke'); }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto p-6 space-y-6" data-testid="api-docs-page">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">API Access</h1>
          <p className="text-sm text-slate-500 mt-1">Programmatic access to TrendScout data. Search products, scores, and trends via REST API.</p>
        </div>

        {/* Key Management */}
        <Card className="border-0 shadow-lg" data-testid="api-keys-section">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <Key className="h-4 w-4 text-indigo-600" /> Your API Keys
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Generate */}
            <div className="flex gap-2">
              <Input
                value={newKeyName}
                onChange={e => setNewKeyName(e.target.value)}
                placeholder="Key name (e.g., Production, Staging)"
                data-testid="api-key-name-input"
              />
              <Button onClick={generateKey} disabled={creating || !newKeyName.trim()} className="bg-indigo-600 hover:bg-indigo-700" data-testid="generate-key-btn">
                {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Plus className="h-4 w-4 mr-1" /> Generate</>}
              </Button>
            </div>

            {/* New Key Reveal */}
            {newKey && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4" data-testid="new-key-reveal">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="h-4 w-4 text-emerald-600" />
                  <span className="text-sm font-semibold text-emerald-700">New API Key Created</span>
                </div>
                <div className="flex items-center gap-2">
                  <code className="flex-1 bg-white px-3 py-2 rounded-lg border border-emerald-200 text-xs font-mono text-slate-800 break-all">{newKey}</code>
                  <Button variant="outline" size="sm" onClick={() => copyToClipboard(newKey)} data-testid="copy-new-key">
                    <Copy className="h-3.5 w-3.5" />
                  </Button>
                </div>
                <p className="text-[10px] text-amber-600 mt-2 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" /> Save this key now — it won't be shown again.
                </p>
              </div>
            )}

            {/* Key List */}
            {keys.length === 0 ? (
              <p className="text-sm text-slate-400 py-3 text-center">No API keys yet.</p>
            ) : (
              <div className="space-y-2">
                {keys.map(k => (
                  <div key={k.id} className={`flex items-center justify-between p-3 rounded-lg border ${k.active ? 'bg-white border-slate-200' : 'bg-slate-50 border-slate-100 opacity-60'}`} data-testid="api-key-item">
                    <div className="flex items-center gap-3">
                      <Shield className={`h-4 w-4 ${k.active ? 'text-emerald-500' : 'text-slate-400'}`} />
                      <div>
                        <p className="text-sm font-semibold text-slate-800">{k.name}</p>
                        <p className="text-xs text-slate-400">
                          {k.key_prefix} &middot; {k.total_calls || 0} calls
                          {k.last_used && ` · Last used ${new Date(k.last_used).toLocaleDateString()}`}
                        </p>
                      </div>
                    </div>
                    {k.active && (
                      <button onClick={() => revokeKey(k.id)} className="text-slate-400 hover:text-red-500" data-testid={`revoke-key-${k.id}`}>
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                    {!k.active && <Badge className="bg-red-50 text-red-600 border-red-200 text-[10px]">Revoked</Badge>}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* API Documentation */}
        <Card className="border-0 shadow-lg" data-testid="api-docs-section">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <Code className="h-4 w-4 text-purple-600" /> API Reference
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase mb-2">Authentication</p>
              <p className="text-sm text-slate-600">Include your API key in the <code className="bg-white px-1.5 py-0.5 rounded text-indigo-600 text-xs">X-API-Key</code> header with every request.</p>
              <div className="mt-3 bg-slate-900 rounded-lg p-3">
                <code className="text-xs text-green-400">curl -H "X-API-Key: ts_your_key_here" \</code><br />
                <code className="text-xs text-slate-400">&nbsp;&nbsp;{window.location.origin}/api/v1/products/search?q=wireless</code>
              </div>
            </div>

            <Endpoint
              method="GET"
              path="/api/v1/products/search"
              desc="Search products by name, category, and minimum score."
              params={[
                { name: 'q', type: 'string', desc: 'Search query' },
                { name: 'category', type: 'string', desc: 'Filter by category' },
                { name: 'min_score', type: 'int', desc: 'Minimum launch score (0-100)' },
                { name: 'limit', type: 'int', desc: 'Max results (default 20, max 50)' },
              ]}
            />
            <Endpoint
              method="GET"
              path="/api/v1/products/{product_id}/score"
              desc="Get detailed 7-signal launch score breakdown."
              params={[
                { name: 'product_id', type: 'string', desc: 'Product ID' },
              ]}
            />
            <Endpoint
              method="GET"
              path="/api/v1/trends/top"
              desc="Get top trending products ranked by launch score."
              params={[
                { name: 'limit', type: 'int', desc: 'Max results (default 10)' },
                { name: 'category', type: 'string', desc: 'Filter by category' },
              ]}
            />
            <Endpoint
              method="GET"
              path="/api/v1/trends/categories"
              desc="Get trending categories with average scores and product counts."
              params={[]}
            />

            <div className="bg-amber-50 rounded-xl p-4 border border-amber-200 flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-amber-700">Rate Limits</p>
                <p className="text-xs text-amber-600 mt-1">100 requests per minute per API key. Rate limit headers are included in every response.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

function Endpoint({ method, path, desc, params }) {
  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      <div className="bg-slate-50 px-4 py-2.5 flex items-center gap-3 border-b border-slate-200">
        <Badge className={`text-[10px] font-mono ${method === 'GET' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-blue-50 text-blue-700 border-blue-200'}`}>
          {method}
        </Badge>
        <code className="text-xs font-mono text-slate-700">{path}</code>
      </div>
      <div className="p-4 space-y-3">
        <p className="text-sm text-slate-600">{desc}</p>
        {params.length > 0 && (
          <div>
            <p className="text-[10px] font-semibold text-slate-400 uppercase mb-1.5">Parameters</p>
            <div className="space-y-1">
              {params.map(p => (
                <div key={p.name} className="flex items-center gap-3 text-xs">
                  <code className="bg-slate-50 px-1.5 py-0.5 rounded text-indigo-600 font-mono">{p.name}</code>
                  <span className="text-slate-400">{p.type}</span>
                  <span className="text-slate-500">{p.desc}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
