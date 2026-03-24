import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Store, Package, TrendingUp, BarChart3, Zap, Shield, Bell,
  ArrowRight, CheckCircle2, Copy, ExternalLink, Loader2,
  Code2, Globe, Lock, ChevronDown, ChevronRight, Users,
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const FEATURES = [
  { icon: TrendingUp, title: '7-Signal Launch Score', desc: 'AI-powered product scoring across 7 key signals to predict launch success.' },
  { icon: BarChart3, title: 'Ad Intelligence', desc: 'Spy on competitor ads across TikTok, Meta, and Pinterest.' },
  { icon: Package, title: '1-Click Import', desc: 'Push winning products directly to your Shopify store as drafts.' },
  { icon: Bell, title: 'Radar Alerts', desc: 'Real-time notifications when products cross your scoring thresholds.' },
  { icon: Shield, title: 'Competitor Analysis', desc: 'Deep-dive into competitor stores — revenue estimates, pricing strategy.' },
  { icon: Zap, title: 'Profitability Simulator', desc: 'Calculate unit economics before you spend a dollar on ads.' },
];

const INSTALL_STEPS = [
  { step: 1, title: 'Go to Connections', desc: 'In your TrendScout dashboard, navigate to Connections in the sidebar.' },
  { step: 2, title: 'Enter Your Store Domain', desc: 'Type your Shopify store domain (e.g. your-store.myshopify.com) into the Shopify card.' },
  { step: 3, title: 'Authorise on Shopify', desc: 'Click "Connect with Shopify" — you\'ll be redirected to Shopify to approve the connection.' },
  { step: 4, title: 'Start Syncing', desc: 'Once connected, go to Shopify Products in the sidebar to sync and manage your store\'s products.' },
];

function FeatureCard({ icon: Icon, title, desc }) {
  return (
    <Card className="border border-slate-200/60 bg-white hover:shadow-md transition-shadow" data-testid={`feature-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <CardContent className="p-5">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-indigo-50 flex-shrink-0">
            <Icon className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 text-sm">{title}</h3>
            <p className="text-slate-500 text-xs mt-1 leading-relaxed">{desc}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function InstallStep({ step, title, desc, isLast }) {
  return (
    <div className="flex gap-4" data-testid={`install-step-${step}`}>
      <div className="flex flex-col items-center">
        <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
          {step}
        </div>
        {!isLast && <div className="w-px flex-1 bg-indigo-200 mt-2" />}
      </div>
      <div className={!isLast ? 'pb-6' : ''}>
        <h4 className="font-semibold text-slate-900 text-sm">{title}</h4>
        <p className="text-slate-500 text-xs mt-1 leading-relaxed">{desc}</p>
      </div>
    </div>
  );
}

function ApiEndpointRow({ method, path, desc }) {
  return (
    <tr className="border-b border-slate-100 last:border-0">
      <td className="py-2.5 pr-3">
        <Badge variant="outline" className={`text-[10px] font-mono ${method === 'POST' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-blue-50 text-blue-700 border-blue-200'}`}>
          {method}
        </Badge>
      </td>
      <td className="py-2.5 pr-3 font-mono text-xs text-slate-700">{path}</td>
      <td className="py-2.5 text-xs text-slate-500">{desc}</td>
    </tr>
  );
}

export default function ShopifyAppPage() {
  const { user } = useAuth();
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showApiDocs, setShowApiDocs] = useState(false);

  useEffect(() => {
    async function fetchStatus() {
      if (!user) { setLoading(false); return; }
      try {
        const res = await api.get('/api/shopify/oauth/status');
        setConnectionStatus(res.data);
      } catch {
        setConnectionStatus(null);
      }
      setLoading(false);
    }
    fetchStatus();
  }, [user]);

  const isConnected = connectionStatus?.connected;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero */}
      <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="flex items-center gap-2 mb-4">
            <Store className="h-5 w-5 text-indigo-400" />
            <Badge className="bg-indigo-500/20 text-indigo-300 border-indigo-500/30 text-xs">Shopify App</Badge>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight" data-testid="shopify-app-title">
            TrendScout for Shopify
          </h1>
          <p className="text-lg text-slate-300 mt-4 max-w-2xl">
            Find winning products, validate before you launch, and push directly to your store.
            The AI-powered decision engine built for dropshippers.
          </p>
          <div className="flex flex-wrap gap-3 mt-8">
            {user ? (
              isConnected ? (
                <Link to="/dashboard">
                  <Button className="bg-white text-slate-900 hover:bg-slate-100 gap-2" data-testid="go-to-dashboard-btn">
                    <BarChart3 className="h-4 w-4" /> Go to Dashboard
                  </Button>
                </Link>
              ) : (
                <Link to="/settings/connections">
                  <Button className="bg-indigo-500 hover:bg-indigo-600 text-white gap-2" data-testid="connect-store-btn">
                    <Store className="h-4 w-4" /> Connect Your Store
                  </Button>
                </Link>
              )
            ) : (
              <Link to="/signup">
                <Button className="bg-indigo-500 hover:bg-indigo-600 text-white gap-2" data-testid="get-started-btn">
                  Get Started Free <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            )}
            <a href="#install-guide">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 gap-2">
                <Code2 className="h-4 w-4" /> Installation Guide
              </Button>
            </a>
          </div>

          {/* Connection Status */}
          {user && !loading && (
            <div className="mt-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/60 text-sm" data-testid="connection-status">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-amber-400'}`} />
              <span className="text-slate-300">
                {isConnected ? `Connected to ${connectionStatus.shop_name || connectionStatus.shop_domain}` : 'Store not connected'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Features */}
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-lg font-bold text-slate-900 mb-6">What You Get</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map(f => <FeatureCard key={f.title} {...f} />)}
        </div>
      </div>

      {/* Installation Guide */}
      <div id="install-guide" className="bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="flex items-center gap-3 mb-8">
            <div className="p-2 rounded-lg bg-indigo-50">
              <Lock className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Installation Guide</h2>
              <p className="text-sm text-slate-500">Connect TrendScout to your Shopify store in 4 steps</p>
            </div>
          </div>
          <div className="max-w-xl">
            {INSTALL_STEPS.map((s, i) => (
              <InstallStep key={s.step} {...s} isLast={i === INSTALL_STEPS.length - 1} />
            ))}
          </div>
          <div className="mt-8 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <h4 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-600" /> Security
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              Your OAuth access tokens are obtained securely via Shopify's consent flow and encrypted at rest using Fernet symmetric encryption. We never store tokens in plaintext. All API communication uses HTTPS.
            </p>
          </div>
        </div>
      </div>

      {/* GDPR & Compliance */}
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 rounded-lg bg-green-50">
            <Globe className="h-5 w-5 text-green-600" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">GDPR & Compliance</h2>
            <p className="text-sm text-slate-500">We take privacy seriously</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { title: 'Customer Data Requests', desc: 'We handle Shopify GDPR data request webhooks. We do not store end-customer PII from your store.' },
            { title: 'Data Erasure', desc: 'Customer and shop data erasure requests are processed automatically. Your data is deleted within 48 hours.' },
            { title: 'Webhook Verification', desc: 'All Shopify webhooks are verified via HMAC-SHA256 signatures to prevent tampering.' },
          ].map(c => (
            <Card key={c.title} className="border-slate-200/60">
              <CardContent className="p-5">
                <CheckCircle2 className="h-5 w-5 text-green-500 mb-2" />
                <h3 className="font-semibold text-slate-900 text-sm">{c.title}</h3>
                <p className="text-slate-500 text-xs mt-1 leading-relaxed">{c.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Embedded App */}
      <div className="bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="flex items-center gap-3 mb-8">
            <div className="p-2 rounded-lg bg-indigo-50">
              <Store className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Embedded App Mode</h2>
              <p className="text-sm text-slate-500">TrendScout runs directly inside your Shopify Admin</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-slate-900 text-sm mb-3">What you get inside Shopify Admin</h3>
              <ul className="space-y-2">
                {[
                  'Top trending products with real-time launch scores',
                  '1-click "Push to Store" — products imported as drafts instantly',
                  'Radar detection alerts for score spikes and trend changes',
                  'Recent export history at a glance',
                  'Direct link to full TrendScout dashboard for deep analysis',
                ].map(item => (
                  <li key={item} className="flex items-start gap-2 text-xs text-slate-600">
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-500 mt-0.5 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <Card className="border-slate-200 bg-slate-50" data-testid="embedded-preview-card">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="h-4 w-4 text-indigo-600" />
                  <span className="text-sm font-bold text-slate-900">TrendScout</span>
                  <Badge className="bg-indigo-50 text-indigo-600 border-indigo-200 text-[10px]">Embedded</Badge>
                </div>
                <div className="space-y-2">
                  {[85, 78, 72].map(score => (
                    <div key={score} className="flex items-center justify-between p-2 bg-white rounded border border-slate-200">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded bg-slate-100" />
                        <div className="h-2 w-20 bg-slate-200 rounded" />
                      </div>
                      <Badge variant="outline" className="text-[10px] font-mono bg-green-50 text-green-700 border-green-200">{score}</Badge>
                    </div>
                  ))}
                </div>
                <p className="text-[10px] text-slate-400 text-center mt-3">Preview — actual data shown in your Shopify Admin</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* API Docs Toggle */}
      <div className="bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <button
            onClick={() => setShowApiDocs(!showApiDocs)}
            className="flex items-center gap-2 text-sm font-semibold text-slate-900 hover:text-indigo-600 transition-colors"
            data-testid="toggle-api-docs"
          >
            {showApiDocs ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            <Code2 className="h-4 w-4" /> Shopify Integration API Endpoints
          </button>
          {showApiDocs && (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left" data-testid="api-docs-table">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="py-2 text-[10px] font-medium text-slate-400 uppercase">Method</th>
                    <th className="py-2 text-[10px] font-medium text-slate-400 uppercase">Endpoint</th>
                    <th className="py-2 text-[10px] font-medium text-slate-400 uppercase">Description</th>
                  </tr>
                </thead>
                <tbody>
                  <ApiEndpointRow method="POST" path="/api/shopify/oauth/init" desc="Start OAuth connection with your store credentials" />
                  <ApiEndpointRow method="GET" path="/api/shopify/oauth/callback" desc="OAuth callback — exchanges code for access token" />
                  <ApiEndpointRow method="GET" path="/api/shopify/oauth/status" desc="Check your Shopify connection status" />
                  <ApiEndpointRow method="POST" path="/api/shopify/push-product" desc="Push a product to your store as a draft" />
                  <ApiEndpointRow method="GET" path="/api/shopify/exports" desc="List your Shopify export history" />
                  <ApiEndpointRow method="POST" path="/api/shopify/app/webhooks/app/uninstalled" desc="App uninstall lifecycle webhook" />
                  <ApiEndpointRow method="POST" path="/api/shopify/app/webhooks/customers/data_request" desc="GDPR: Customer data request" />
                  <ApiEndpointRow method="POST" path="/api/shopify/app/webhooks/customers/redact" desc="GDPR: Customer data erasure" />
                  <ApiEndpointRow method="POST" path="/api/shopify/app/webhooks/shop/redact" desc="GDPR: Shop data erasure" />
                  <ApiEndpointRow method="GET" path="/api/shopify/app/info" desc="App metadata and manifest info" />
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* CTA */}
      <div className="max-w-6xl mx-auto px-6 py-16 text-center">
        <h2 className="text-lg font-bold text-slate-900">Ready to find your next winning product?</h2>
        <p className="text-sm text-slate-500 mt-2 max-w-lg mx-auto">
          Join thousands of dropshippers using TrendScout to discover, validate, and launch profitable products.
        </p>
        <div className="flex justify-center gap-3 mt-6">
          {user ? (
            <Link to="/dashboard">
              <Button className="bg-indigo-600 hover:bg-indigo-700 text-white gap-2" data-testid="cta-dashboard-btn">
                Go to Dashboard <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          ) : (
            <>
              <Link to="/signup">
                <Button className="bg-indigo-600 hover:bg-indigo-700 text-white gap-2" data-testid="cta-signup-btn">
                  Start Free Trial <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link to="/pricing">
                <Button variant="outline" className="gap-2" data-testid="cta-pricing-btn">
                  View Pricing
                </Button>
              </Link>
            </>
          )}
        </div>
        <p className="text-xs text-slate-400 mt-6">
          Questions? <a href="mailto:info@trendscout.click" className="underline hover:text-slate-600">info@trendscout.click</a> &middot; <Link to="/privacy" className="underline hover:text-slate-600">Privacy Policy</Link> &middot; <Link to="/terms" className="underline hover:text-slate-600">Terms of Service</Link>
        </p>
      </div>
    </div>
  );
}
