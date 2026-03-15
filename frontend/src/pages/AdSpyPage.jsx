import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Search, Filter, Eye, Heart, MessageCircle, Share2,
  TrendingUp, Play, Image as ImageIcon, Loader2,
  ChevronDown, ExternalLink,
} from 'lucide-react';
import api from '@/lib/api';

const PLATFORMS = [
  { id: 'all', label: 'All Platforms' },
  { id: 'tiktok', label: 'TikTok' },
  { id: 'meta', label: 'Meta / Facebook' },
  { id: 'pinterest', label: 'Pinterest' },
];

const SORT_OPTIONS = [
  { value: 'engagement', label: 'Highest Engagement' },
  { value: 'recent', label: 'Most Recent' },
  { value: 'spend', label: 'Highest Spend' },
];

export default function AdSpyPage() {
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [platform, setPlatform] = useState('all');
  const [sortBy, setSortBy] = useState('engagement');
  const [searched, setSearched] = useState(false);

  const fetchAds = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (query) params.set('q', query);
      if (platform !== 'all') params.set('platform', platform);
      params.set('sort', sortBy);
      params.set('limit', '24');

      const res = await api.get(`/api/ads/discover?${params}`);
      if (res.ok) {
        setAds(res.data.ads || res.data.results || res.data || []);
      }
    } catch {}
    setLoading(false);
    setSearched(true);
  }, [query, platform, sortBy]);

  useEffect(() => { fetchAds(); }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchAds();
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6 space-y-6" data-testid="ad-spy-page">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Ad Intelligence</h1>
            <p className="text-sm text-slate-500 mt-1">Spy on competitor ads across TikTok, Meta & Pinterest. Find winning creatives and hooks.</p>
          </div>
          <Badge className="bg-indigo-100 text-indigo-700 border-indigo-200 text-xs self-start">
            {ads.length} ads found
          </Badge>
        </div>

        {/* Search & Filters */}
        <Card className="border-0 shadow-lg" data-testid="ad-spy-filters">
          <CardContent className="py-4">
            <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="Search ads by product, niche, or keyword..."
                  className="pl-10"
                  data-testid="ad-search-input"
                />
              </div>
              <div className="flex gap-2">
                {PLATFORMS.map(p => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setPlatform(p.id)}
                    className={`px-3 py-2 rounded-lg text-xs font-medium border transition-all ${
                      platform === p.id
                        ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                        : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                    }`}
                    data-testid={`platform-${p.id}`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
                className="px-3 py-2 rounded-lg border border-slate-200 text-xs text-slate-600 bg-white"
                data-testid="ad-sort-select"
              >
                {SORT_OPTIONS.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
              <Button type="submit" className="bg-indigo-600 hover:bg-indigo-700" data-testid="ad-search-btn">
                <Filter className="h-4 w-4 mr-1" /> Search
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Ad Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          </div>
        ) : ads.length === 0 ? (
          <Card className="border-0 shadow-lg">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <Search className="h-12 w-12 text-slate-300 mb-4" />
              <p className="text-sm text-slate-500">{searched ? 'No ads found. Try different keywords or filters.' : 'Search for ads to get started.'}</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="ad-grid">
            {ads.map((ad, idx) => (
              <AdCard key={ad.id || idx} ad={ad} />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

function AdCard({ ad }) {
  const platformBadge = {
    tiktok: { bg: 'bg-pink-100', color: 'text-pink-700' },
    meta: { bg: 'bg-blue-100', color: 'text-blue-700' },
    facebook: { bg: 'bg-blue-100', color: 'text-blue-700' },
    pinterest: { bg: 'bg-red-100', color: 'text-red-700' },
  };
  const pb = platformBadge[ad.platform?.toLowerCase()] || { bg: 'bg-slate-100', color: 'text-slate-700' };

  return (
    <Card className="border-0 shadow-md hover:shadow-lg transition-shadow overflow-hidden" data-testid="ad-card">
      <div className="aspect-video bg-slate-100 relative overflow-hidden">
        {ad.thumbnail_url || ad.image_url ? (
          <img src={ad.thumbnail_url || ad.image_url} alt="" className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <ImageIcon className="h-8 w-8 text-slate-300" />
          </div>
        )}
        <Badge className={`absolute top-2 left-2 text-[10px] ${pb.bg} ${pb.color} border-0`}>
          {ad.platform || 'Unknown'}
        </Badge>
        {ad.ad_type === 'video' && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <Play className="h-8 w-8 text-white/80" />
          </div>
        )}
      </div>
      <CardContent className="p-3 space-y-2">
        <p className="text-sm font-semibold text-slate-900 line-clamp-2">{ad.headline || ad.title || ad.product_name || 'Ad Creative'}</p>
        {ad.body_text && <p className="text-xs text-slate-500 line-clamp-2">{ad.body_text}</p>}
        <div className="flex items-center gap-3 text-xs text-slate-400">
          {ad.likes != null && <span className="flex items-center gap-1"><Heart className="h-3 w-3" /> {formatNum(ad.likes)}</span>}
          {ad.comments != null && <span className="flex items-center gap-1"><MessageCircle className="h-3 w-3" /> {formatNum(ad.comments)}</span>}
          {ad.shares != null && <span className="flex items-center gap-1"><Share2 className="h-3 w-3" /> {formatNum(ad.shares)}</span>}
          {ad.views != null && <span className="flex items-center gap-1"><Eye className="h-3 w-3" /> {formatNum(ad.views)}</span>}
        </div>
        {ad.advertiser_name && (
          <p className="text-[10px] text-slate-400 truncate">by {ad.advertiser_name}</p>
        )}
        {ad.url && (
          <a href={ad.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:underline">
            View original <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </CardContent>
    </Card>
  );
}

function formatNum(n) {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n?.toString() || '0';
}
