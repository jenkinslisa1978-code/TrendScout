import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Search, Filter, Eye, Heart, MessageCircle, Share2,
  TrendingUp, Play, Image as ImageIcon, Loader2,
  ExternalLink, Bookmark, BookmarkCheck, X, Target,
  BarChart3, ChevronDown, ArrowUpRight,
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';
import { useSubscription } from '@/hooks/useSubscription';
import { LockedContent } from '@/components/common/UpgradePrompts';

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
  const [category, setCategory] = useState('all');
  const [categories, setCategories] = useState([]);
  const [searched, setSearched] = useState(false);
  const [savedIds, setSavedIds] = useState(new Set());
  const [selectedAd, setSelectedAd] = useState(null);
  const { isFree, isStarter } = useSubscription();
  const FREE_AD_LIMIT = 2;

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
        let results = res.data.ads || [];
        if (category !== 'all') {
          results = results.filter(a => a.advertiser_name === category);
        }
        setAds(results);
        if (res.data.categories) setCategories(res.data.categories);
      }
    } catch {}
    setLoading(false);
    setSearched(true);
  }, [query, platform, sortBy, category]);

  useEffect(() => { fetchAds(); }, []);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/api/ads/saved');
        if (res.ok) {
          setSavedIds(new Set((res.data.saved_ads || []).map(s => s.ad_id)));
        }
      } catch {}
    })();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchAds();
  };

  const toggleSave = async (ad) => {
    const isSaved = savedIds.has(ad.id);
    if (isSaved) {
      try {
        await api.delete(`/api/ads/saved/${ad.id}`);
        setSavedIds(prev => { const n = new Set(prev); n.delete(ad.id); return n; });
        toast.success('Ad removed from saved');
      } catch { toast.error('Failed to remove'); }
    } else {
      try {
        await api.post('/api/ads/save', { ad_id: ad.id, ad_data: ad });
        setSavedIds(prev => new Set(prev).add(ad.id));
        toast.success('Ad saved');
      } catch { toast.error('Failed to save'); }
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6 space-y-6" data-testid="ad-spy-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Ad Intelligence</h1>
            <p className="text-sm text-slate-500 mt-1">Spy on competitor ads across TikTok, Meta & Pinterest. Find winning creatives and hooks.</p>
          </div>
          <Badge className="bg-indigo-100 text-indigo-700 border-indigo-200 text-xs self-start" data-testid="ads-count-badge">
            {ads.length} ads found
          </Badge>
        </div>

        {/* Search & Filters */}
        <Card className="border-0 shadow-lg" data-testid="ad-spy-filters">
          <CardContent className="py-4 space-y-3">
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
            {/* Platform & Category filters */}
            <div className="flex flex-wrap items-center gap-2">
              {PLATFORMS.map(p => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => { setPlatform(p.id); setTimeout(fetchAds, 50); }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    platform === p.id
                      ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                      : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}
                  data-testid={`platform-${p.id}`}
                >
                  {p.label}
                </button>
              ))}
              <span className="w-px h-5 bg-slate-200 mx-1" />
              <select
                value={category}
                onChange={e => { setCategory(e.target.value); setTimeout(fetchAds, 50); }}
                className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-600 bg-white"
                data-testid="ad-category-filter"
              >
                <option value="all">All Categories</option>
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
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
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="ad-grid">
              {ads.slice(0, isFree ? FREE_AD_LIMIT : ads.length).map((ad, idx) => (
                <AdCard
                  key={ad.id || idx}
                  ad={ad}
                  isSaved={savedIds.has(ad.id)}
                  onSave={() => toggleSave(ad)}
                  onDetail={() => setSelectedAd(ad)}
                />
              ))}
            </div>
            {isFree && ads.length > FREE_AD_LIMIT && (
              <LockedContent feature="Full Ad Intelligence" requiredPlan="Starter" blurIntensity="heavy">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {ads.slice(FREE_AD_LIMIT, FREE_AD_LIMIT + 6).map((ad, idx) => (
                    <AdCard
                      key={ad.id || idx}
                      ad={ad}
                      isSaved={false}
                      onSave={() => {}}
                      onDetail={() => {}}
                    />
                  ))}
                </div>
              </LockedContent>
            )}
          </>
        )}
      </div>

      {/* Detail Modal */}
      {selectedAd && (
        <AdDetailModal ad={selectedAd} onClose={() => setSelectedAd(null)} isSaved={savedIds.has(selectedAd.id)} onSave={() => toggleSave(selectedAd)} />
      )}
    </DashboardLayout>
  );
}

function AdCard({ ad, isSaved, onSave, onDetail }) {
  const platformBadge = {
    tiktok: 'bg-pink-100 text-pink-700',
    meta: 'bg-blue-100 text-blue-700',
    facebook: 'bg-blue-100 text-blue-700',
    pinterest: 'bg-red-100 text-red-700',
  };
  const pb = platformBadge[ad.platform?.toLowerCase()] || 'bg-slate-100 text-slate-700';

  return (
    <Card className="border-0 shadow-md hover:shadow-lg transition-shadow overflow-hidden group cursor-pointer" data-testid="ad-card" onClick={onDetail}>
      <div className="aspect-video bg-slate-100 relative overflow-hidden">
        {ad.thumbnail_url || ad.image_url ? (
          <img src={ad.thumbnail_url || ad.image_url} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <ImageIcon className="h-8 w-8 text-slate-300" />
          </div>
        )}
        <Badge className={`absolute top-2 left-2 text-[10px] ${pb} border-0`}>
          {ad.platform || 'Unknown'}
        </Badge>
        {ad.ad_type === 'video' && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <Play className="h-8 w-8 text-white/80" />
          </div>
        )}
        <button
          onClick={(e) => { e.stopPropagation(); onSave(); }}
          className="absolute top-2 right-2 h-7 w-7 rounded-full bg-white/90 shadow flex items-center justify-center hover:bg-white transition-colors"
          data-testid={`save-ad-${ad.id}`}
        >
          {isSaved ? <BookmarkCheck className="h-3.5 w-3.5 text-indigo-600" /> : <Bookmark className="h-3.5 w-3.5 text-slate-400" />}
        </button>
      </div>
      <CardContent className="p-3 space-y-2">
        <p className="text-sm font-semibold text-slate-900 line-clamp-2">{ad.headline || ad.product_name || 'Ad Creative'}</p>
        {ad.body_text && <p className="text-xs text-slate-500 line-clamp-2">{ad.body_text}</p>}
        <div className="flex items-center gap-3 text-xs text-slate-400">
          {ad.likes != null && <span className="flex items-center gap-1"><Heart className="h-3 w-3" /> {formatNum(ad.likes)}</span>}
          {ad.comments != null && <span className="flex items-center gap-1"><MessageCircle className="h-3 w-3" /> {formatNum(ad.comments)}</span>}
          {ad.shares != null && <span className="flex items-center gap-1"><Share2 className="h-3 w-3" /> {formatNum(ad.shares)}</span>}
          {ad.views != null && <span className="flex items-center gap-1"><Eye className="h-3 w-3" /> {formatNum(ad.views)}</span>}
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-slate-400 truncate">{ad.advertiser_name}</span>
          {ad.launch_score > 0 && (
            <Badge className="text-[10px] bg-indigo-50 text-indigo-600 border-indigo-200">
              Score: {ad.launch_score}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function AdDetailModal({ ad, onClose, isSaved, onSave }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose} data-testid="ad-detail-modal">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[85vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        {/* Image */}
        <div className="relative aspect-video bg-slate-100">
          {ad.image_url ? (
            <img src={ad.image_url} alt="" className="w-full h-full object-cover rounded-t-2xl" />
          ) : (
            <div className="w-full h-full flex items-center justify-center"><ImageIcon className="h-12 w-12 text-slate-300" /></div>
          )}
          <button onClick={onClose} className="absolute top-3 right-3 h-8 w-8 rounded-full bg-black/40 text-white flex items-center justify-center hover:bg-black/60" data-testid="close-ad-modal">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="p-6 space-y-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-slate-900">{ad.headline || ad.product_name}</h2>
              {ad.body_text && <p className="text-sm text-slate-500 mt-1">{ad.body_text}</p>}
            </div>
            <button onClick={onSave} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium hover:bg-slate-50" data-testid="modal-save-btn">
              {isSaved ? <><BookmarkCheck className="h-3.5 w-3.5 text-indigo-600" /> Saved</> : <><Bookmark className="h-3.5 w-3.5" /> Save</>}
            </button>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-4 gap-3">
            <MetricBox icon={Heart} label="Likes" value={formatNum(ad.likes)} />
            <MetricBox icon={MessageCircle} label="Comments" value={formatNum(ad.comments)} />
            <MetricBox icon={Share2} label="Shares" value={formatNum(ad.shares)} />
            <MetricBox icon={Eye} label="Views" value={formatNum(ad.views)} />
          </div>

          {/* Extra Intel */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-50 rounded-lg p-3">
              <p className="text-[10px] text-slate-400 uppercase">Platform</p>
              <p className="text-sm font-semibold text-slate-800 capitalize mt-0.5">{ad.platform}</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-3">
              <p className="text-[10px] text-slate-400 uppercase">Launch Score</p>
              <p className="text-sm font-semibold text-slate-800 mt-0.5">{ad.launch_score || '—'}/100</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-3">
              <p className="text-[10px] text-slate-400 uppercase">Est. Monthly Spend</p>
              <p className="text-sm font-semibold text-slate-800 mt-0.5">${ad.estimated_spend ? formatNum(ad.estimated_spend) : '—'}</p>
            </div>
            <div className="bg-slate-50 rounded-lg p-3">
              <p className="text-[10px] text-slate-400 uppercase">Trend Stage</p>
              <p className="text-sm font-semibold text-slate-800 capitalize mt-0.5">{ad.trend_stage || '—'}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2 border-t border-slate-100">
            <Button asChild variant="outline" size="sm" className="flex-1 text-xs">
              <a href={ad.url} target={ad.url?.startsWith('/') ? '_self' : '_blank'} rel="noreferrer" data-testid="view-product-btn">
                <ArrowUpRight className="h-3.5 w-3.5 mr-1.5" /> View Product
              </a>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricBox({ icon: Icon, label, value }) {
  return (
    <div className="bg-slate-50 rounded-lg p-3 text-center">
      <Icon className="h-4 w-4 text-slate-400 mx-auto mb-1" />
      <p className="text-sm font-bold text-slate-800">{value}</p>
      <p className="text-[10px] text-slate-400">{label}</p>
    </div>
  );
}

function formatNum(n) {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n?.toString() || '0';
}
