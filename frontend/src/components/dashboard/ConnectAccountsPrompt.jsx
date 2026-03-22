import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Link2, ShoppingBag, Megaphone, Truck, ChevronRight,
  Check, Store, ShoppingCart, Globe, ArrowRight, X,
} from 'lucide-react';
import api from '@/lib/api';

const CATEGORIES = [
  {
    id: 'store',
    label: 'Stores',
    icon: ShoppingBag,
    color: 'text-emerald-600 bg-emerald-50 border-emerald-200',
    desc: 'Shopify, WooCommerce, Etsy, Amazon',
  },
  {
    id: 'social',
    label: 'Social',
    icon: Globe,
    color: 'text-violet-600 bg-violet-50 border-violet-200',
    desc: 'TikTok Shop, Instagram',
  },
  {
    id: 'ads',
    label: 'Ad Accounts',
    icon: Megaphone,
    color: 'text-blue-600 bg-blue-50 border-blue-200',
    desc: 'Facebook Ads, Google Ads, TikTok Ads',
  },
  {
    id: 'supplier',
    label: 'Suppliers',
    icon: Truck,
    color: 'text-amber-600 bg-amber-50 border-amber-200',
    desc: 'AliExpress, CJ Dropshipping, Zendrop',
  },
];

export default function ConnectAccountsPrompt() {
  const navigate = useNavigate();
  const [connections, setConnections] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const hidden = localStorage.getItem('trendscout_connections_dismissed');
    if (hidden) setDismissed(true);

    api.get('/api/connections/').then(({ data }) => {
      if (data?.stores || data?.ads) {
        const storeCount = Object.values(data.stores || {}).filter(s => s.status === 'active').length;
        const adCount = Object.values(data.ads || {}).filter(a => a.status === 'active').length;
        setConnections({ stores: storeCount, ads: adCount, total: storeCount + adCount });
      } else {
        setConnections({ stores: 0, ads: 0, total: 0 });
      }
    }).catch(() => setConnections({ stores: 0, ads: 0, total: 0 }));
  }, []);

  if (dismissed || connections === null) return null;

  const isFullyConnected = connections.total >= 3;

  if (isFullyConnected) return null;

  return (
    <Card className="border-indigo-200 bg-gradient-to-r from-indigo-50/80 via-white to-violet-50/80 shadow-sm overflow-hidden" data-testid="connect-accounts-prompt">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-100">
              <Link2 className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-base">Connect Your Accounts</h3>
              <p className="text-sm text-slate-500 mt-0.5">
                Link your stores, social media, and ad accounts to unlock automated product publishing, ad creation, and real-time sync.
              </p>

              <div className="flex flex-wrap gap-2 mt-3">
                {CATEGORIES.map(cat => {
                  const Icon = cat.icon;
                  return (
                    <button
                      key={cat.id}
                      onClick={() => navigate('/settings/connections')}
                      className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium transition-all hover:shadow-sm ${cat.color}`}
                      data-testid={`connect-category-${cat.id}`}
                    >
                      <Icon className="h-3.5 w-3.5" />
                      <span>{cat.label}</span>
                      <span className="text-[10px] opacity-60">{cat.desc}</span>
                    </button>
                  );
                })}
              </div>

              <div className="flex items-center gap-3 mt-3">
                <Button
                  size="sm"
                  onClick={() => navigate('/settings/connections')}
                  className="bg-indigo-600 hover:bg-indigo-700 text-xs"
                  data-testid="connect-accounts-btn"
                >
                  <Link2 className="h-3.5 w-3.5 mr-1.5" />
                  Set Up Connections
                  <ArrowRight className="h-3.5 w-3.5 ml-1.5" />
                </Button>
                {connections.total > 0 && (
                  <span className="text-xs text-emerald-600 flex items-center gap-1">
                    <Check className="h-3 w-3" />
                    {connections.total} connected
                  </span>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={() => {
              setDismissed(true);
              localStorage.setItem('trendscout_connections_dismissed', 'true');
            }}
            className="text-slate-400 hover:text-slate-600 p-1 shrink-0"
            data-testid="dismiss-connect-prompt"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </CardContent>
    </Card>
  );
}
