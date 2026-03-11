import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Search,
  ExternalLink,
  Loader2,
  Radio,
  Eye,
  ThumbsUp,
  ShoppingBag,
  RefreshCw,
  AlertCircle,
  Activity,
} from 'lucide-react';
import { apiGet, apiPost } from '@/lib/api';
import { toast } from 'sonner';

const PLATFORM_CONFIG = {
  tiktok: {
    label: 'TikTok',
    color: 'bg-rose-100 text-rose-700 border-rose-200',
    activeColor: 'bg-rose-500',
    icon: '♪',
  },
  meta: {
    label: 'Meta',
    color: 'bg-blue-100 text-blue-700 border-blue-200',
    activeColor: 'bg-blue-500',
    icon: 'f',
  },
  google_shopping: {
    label: 'Google Shopping',
    color: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    activeColor: 'bg-emerald-500',
    icon: 'G',
  },
};

const ACTIVITY_COLORS = {
  very_high: 'bg-red-100 text-red-700 border-red-200',
  high: 'bg-orange-100 text-orange-700 border-orange-200',
  moderate: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-green-100 text-green-700 border-green-200',
  none: 'bg-slate-100 text-slate-600 border-slate-200',
};

export default function AdDiscoverySection({ productId }) {
  const [discovery, setDiscovery] = useState(null);
  const [loading, setLoading] = useState(false);
  const [discovering, setDiscovering] = useState(false);

  useEffect(() => {
    fetchDiscovery();
  }, [productId]);

  const fetchDiscovery = async () => {
    setLoading(true);
    try {
      const res = await apiGet(`/api/ad-discovery/${productId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.total_ads > 0 || data.summary) {
          setDiscovery(data);
        }
      }
    } catch (err) {
      console.error('Failed to fetch ad discovery:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDiscover = async (forceRefresh = false) => {
    setDiscovering(true);
    try {
      const res = await apiPost(
        `/api/ad-discovery/discover/${productId}?force_refresh=${forceRefresh}`
      );
      if (res.ok) {
        const data = await res.json();
        setDiscovery(data);
        toast.success(`Found ${data.total_ads} ads across ${data.summary?.platforms_active?.length || 0} platforms`);
      } else {
        toast.error('Failed to discover ads');
      }
    } catch (err) {
      console.error('Ad discovery error:', err);
      toast.error('Ad discovery failed');
    } finally {
      setDiscovering(false);
    }
  };

  if (loading) {
    return (
      <Card data-testid="ad-discovery-section">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 animate-spin text-slate-400" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card data-testid="ad-discovery-section">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Radio className="h-5 w-5 text-rose-500" />
            Ad Discovery
          </CardTitle>
          <div className="flex items-center gap-2">
            {discovery?.summary && (
              <Badge
                className={`border ${ACTIVITY_COLORS[discovery.summary.activity_level] || ACTIVITY_COLORS.none}`}
                data-testid="ad-activity-badge"
              >
                <Activity className="h-3 w-3 mr-1" />
                {discovery.summary.activity_label}
              </Badge>
            )}
            <Button
              size="sm"
              variant={discovery ? 'outline' : 'default'}
              onClick={() => handleDiscover(!discovery)}
              disabled={discovering}
              data-testid="discover-ads-btn"
            >
              {discovering ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />
                  Scanning...
                </>
              ) : discovery ? (
                <>
                  <RefreshCw className="h-3.5 w-3.5 mr-1" />
                  Refresh
                </>
              ) : (
                <>
                  <Search className="h-3.5 w-3.5 mr-1" />
                  Discover Ads
                </>
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {!discovery ? (
          <div className="text-center py-6" data-testid="ad-discovery-empty">
            <Radio className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-500 mb-1">No ad intelligence gathered yet</p>
            <p className="text-xs text-slate-400">
              Click "Discover Ads" to scan TikTok, Meta & Google Shopping
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Platform Summary Bar */}
            <div className="flex items-center gap-3" data-testid="platform-summary">
              {Object.entries(discovery.platforms || {}).map(([platform, data]) => {
                const config = PLATFORM_CONFIG[platform];
                if (!config) return null;
                return (
                  <div
                    key={platform}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-medium ${config.color}`}
                  >
                    <span className="font-bold">{config.icon}</span>
                    <span>{config.label}</span>
                    <span className="font-bold">{data.count}</span>
                  </div>
                );
              })}
              <span className="text-xs text-slate-400 ml-auto">
                Total: {discovery.total_ads} ads
              </span>
            </div>

            {/* Platform Tabs */}
            <Tabs defaultValue="all">
              <TabsList className="w-full justify-start bg-slate-50">
                <TabsTrigger value="all" className="text-xs">All Platforms</TabsTrigger>
                <TabsTrigger value="tiktok" className="text-xs">TikTok</TabsTrigger>
                <TabsTrigger value="meta" className="text-xs">Meta</TabsTrigger>
                <TabsTrigger value="google_shopping" className="text-xs">Google</TabsTrigger>
              </TabsList>

              <TabsContent value="all">
                <AdList
                  ads={getAllAds(discovery.platforms)}
                  emptyMessage="No ads discovered across any platform"
                />
              </TabsContent>

              {Object.keys(PLATFORM_CONFIG).map((platform) => (
                <TabsContent key={platform} value={platform}>
                  <AdList
                    ads={discovery.platforms?.[platform]?.ads || []}
                    emptyMessage={`No ${PLATFORM_CONFIG[platform].label} ads found`}
                  />
                </TabsContent>
              ))}
            </Tabs>

            {/* Discovery timestamp */}
            {discovery.discovered_at && (
              <p className="text-xs text-slate-400 text-right">
                Last scanned: {new Date(discovery.discovered_at).toLocaleString()}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function getAllAds(platforms) {
  if (!platforms) return [];
  const all = [];
  Object.values(platforms).forEach((p) => {
    if (p.ads) all.push(...p.ads);
  });
  return all;
}

function AdList({ ads, emptyMessage }) {
  if (!ads || ads.length === 0) {
    return (
      <div className="text-center py-4 text-slate-400 text-sm">
        <AlertCircle className="h-6 w-6 mx-auto mb-1 opacity-50" />
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-80 overflow-y-auto" data-testid="ad-list">
      {ads.map((ad) => (
        <AdCard key={ad.id} ad={ad} />
      ))}
    </div>
  );
}

function AdCard({ ad }) {
  const config = PLATFORM_CONFIG[ad.platform] || PLATFORM_CONFIG.meta;
  const isEstimated = ad.status === 'estimated';

  return (
    <div
      className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors border border-slate-100"
      data-testid={`ad-card-${ad.id}`}
    >
      <div
        className={`w-8 h-8 rounded-lg ${config.activeColor} text-white flex items-center justify-center text-xs font-bold flex-shrink-0`}
      >
        {config.icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-800 truncate">{ad.title}</p>
        <div className="flex items-center gap-2 mt-1 flex-wrap">
          <Badge variant="outline" className={`text-xs ${config.color}`}>
            {config.label}
          </Badge>
          {ad.format && (
            <span className="text-xs text-slate-400">{ad.format}</span>
          )}
          {ad.views && ad.views !== 'N/A' && (
            <span className="text-xs text-slate-500 flex items-center gap-0.5">
              <Eye className="h-3 w-3" /> {ad.views}
            </span>
          )}
          {ad.likes && ad.likes !== 'N/A' && (
            <span className="text-xs text-slate-500 flex items-center gap-0.5">
              <ThumbsUp className="h-3 w-3" /> {ad.likes}
            </span>
          )}
          {ad.price && ad.price !== 'N/A' && (
            <span className="text-xs text-emerald-600 font-medium flex items-center gap-0.5">
              <ShoppingBag className="h-3 w-3" /> {ad.price}
            </span>
          )}
          {isEstimated && (
            <Badge variant="outline" className="text-xs bg-amber-50 text-amber-600 border-amber-200">
              Estimated
            </Badge>
          )}
        </div>
      </div>
      {ad.source_url && (
        <a
          href={ad.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-400 hover:text-indigo-600 transition-colors flex-shrink-0"
          data-testid={`ad-external-link-${ad.id}`}
        >
          <ExternalLink className="h-4 w-4" />
        </a>
      )}
    </div>
  );
}
