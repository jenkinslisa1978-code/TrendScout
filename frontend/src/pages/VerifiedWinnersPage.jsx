import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Trophy, ThumbsUp, Crown, Clock, Loader2, Send,
  CheckCircle, Star, Tag, DollarSign, TrendingUp,
  MessageCircle, Filter, Image as ImageIcon,
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

const REVENUE_RANGES = ['$1K-5K', '$5K-10K', '$10K-50K', '$50K-100K', '$100K+'];
const TIMEFRAMES = ['1 week', '2 weeks', '1 month', '3 months', '6 months+'];

export default function VerifiedWinnersPage() {
  const [winners, setWinners] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState('upvotes');
  const [category, setCategory] = useState('all');
  const [showSubmit, setShowSubmit] = useState(false);
  const [stats, setStats] = useState({ verified: 0, pending: 0 });

  useEffect(() => { fetchWinners(); }, [sort, category]);

  const fetchWinners = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ sort, status: 'verified' });
      if (category !== 'all') params.set('category', category);
      const res = await api.get(`/api/winners/?${params}`);
      if (res.ok) {
        setWinners(res.data.winners || []);
        setCategories(res.data.categories || []);
        setStats({ verified: res.data.total_verified || 0, pending: res.data.total_pending || 0 });
      }
    } catch {}
    setLoading(false);
  };

  const handleUpvote = async (winnerId) => {
    try {
      const res = await api.post(`/api/winners/${winnerId}/upvote`);
      if (res.ok) {
        setWinners(prev => prev.map(w =>
          w.id === winnerId ? { ...w, upvotes: res.data.upvotes } : w
        ));
      }
    } catch { toast.error('Login required to upvote'); }
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6 space-y-6" data-testid="verified-winners-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Verified Winners</h1>
            <p className="text-sm text-slate-500 mt-1">Community-proven winning products with real revenue data. Submit your own wins anonymously.</p>
          </div>
          <Button onClick={() => setShowSubmit(true)} className="bg-emerald-600 hover:bg-emerald-700 self-start" data-testid="submit-winner-btn">
            <Trophy className="h-4 w-4 mr-1.5" /> Submit a Winner
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <Card className="border-0 shadow-md">
            <CardContent className="py-4 flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-emerald-50 flex items-center justify-center">
                <CheckCircle className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-lg font-bold text-slate-900">{stats.verified}</p>
                <p className="text-[10px] text-slate-400 uppercase">Verified Winners</p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-md">
            <CardContent className="py-4 flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-amber-50 flex items-center justify-center">
                <Clock className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-lg font-bold text-slate-900">{stats.pending}</p>
                <p className="text-[10px] text-slate-400 uppercase">Pending Review</p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-md hidden sm:block">
            <CardContent className="py-4 flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-indigo-50 flex items-center justify-center">
                <ThumbsUp className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-lg font-bold text-slate-900">{winners.reduce((s, w) => s + (w.upvotes || 0), 0)}</p>
                <p className="text-[10px] text-slate-400 uppercase">Total Upvotes</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={sort}
            onChange={e => setSort(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-600 bg-white"
            data-testid="winners-sort"
          >
            <option value="upvotes">Most Upvoted</option>
            <option value="recent">Most Recent</option>
            <option value="revenue">Highest Revenue</option>
          </select>
          <select
            value={category}
            onChange={e => setCategory(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-600 bg-white"
            data-testid="winners-category"
          >
            <option value="all">All Categories</option>
            {categories.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {/* Winners List */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          </div>
        ) : winners.length === 0 ? (
          <Card className="border-0 shadow-lg">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <Trophy className="h-12 w-12 text-slate-300 mb-4" />
              <p className="text-sm text-slate-500">No verified winners yet. Be the first to submit proof of a winning product!</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3" data-testid="winners-list">
            {winners.map((w, idx) => (
              <WinnerCard key={w.id} winner={w} rank={idx + 1} onUpvote={() => handleUpvote(w.id)} />
            ))}
          </div>
        )}
      </div>

      {showSubmit && (
        <SubmitWinnerModal onClose={() => setShowSubmit(false)} onSubmitted={() => { setShowSubmit(false); fetchWinners(); }} />
      )}
    </DashboardLayout>
  );
}

function WinnerCard({ winner, rank, onUpvote }) {
  const w = winner;
  const badge = w.badge;
  return (
    <Card className="border-0 shadow-md hover:shadow-lg transition-shadow" data-testid="winner-card">
      <CardContent className="py-4">
        <div className="flex items-start gap-4">
          {/* Rank */}
          <div className={`h-10 w-10 rounded-xl flex items-center justify-center text-sm font-black ${
            rank === 1 ? 'bg-amber-100 text-amber-700' : rank === 2 ? 'bg-slate-100 text-slate-600' : rank === 3 ? 'bg-orange-100 text-orange-700' : 'bg-slate-50 text-slate-400'
          }`}>
            {rank <= 3 ? <Crown className="h-5 w-5" /> : `#${rank}`}
          </div>

          {/* Image */}
          {w.product_image ? (
            <img src={w.product_image} alt="" className="h-16 w-16 rounded-lg object-cover"  loading="lazy" />
          ) : (
            <div className="h-16 w-16 rounded-lg bg-slate-100 flex items-center justify-center">
              <ImageIcon className="h-6 w-6 text-slate-300" />
            </div>
          )}

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <p className="text-sm font-bold text-slate-900 truncate">{w.product_name}</p>
              {w.status === 'verified' && (
                <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px]">
                  <CheckCircle className="h-3 w-3 mr-0.5" /> Verified
                </Badge>
              )}
              {badge && (
                <Badge className="text-[10px] border" style={{ backgroundColor: badge.color + '15', color: badge.color, borderColor: badge.color + '40' }} data-testid="winner-badge">
                  <Star className="h-3 w-3 mr-0.5" /> {badge.label}
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-2 mt-1.5">
              <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px]">
                <DollarSign className="h-3 w-3 mr-0.5" /> {w.revenue_range}
              </Badge>
              <Badge className="bg-blue-50 text-blue-700 border-blue-200 text-[10px]">
                <Clock className="h-3 w-3 mr-0.5" /> {w.timeframe}
              </Badge>
              {w.category && (
                <Badge className="bg-slate-50 text-slate-600 border-slate-200 text-[10px]">
                  <Tag className="h-3 w-3 mr-0.5" /> {w.category}
                </Badge>
              )}
              {w.ad_platform && (
                <Badge className="bg-purple-50 text-purple-600 border-purple-200 text-[10px]">{w.ad_platform}</Badge>
              )}
            </div>
            {w.tips && <p className="text-xs text-slate-500 mt-2 line-clamp-2">{w.tips}</p>}
          </div>

          {/* Upvote */}
          <button onClick={onUpvote} className="flex flex-col items-center gap-1 px-3 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors" data-testid={`upvote-${w.id}`}>
            <ThumbsUp className="h-4 w-4 text-slate-400" />
            <span className="text-xs font-bold text-slate-700">{w.upvotes || 0}</span>
          </button>
        </div>
      </CardContent>
    </Card>
  );
}

function SubmitWinnerModal({ onClose, onSubmitted }) {
  const [productId, setProductId] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [revenue, setRevenue] = useState('$1K-5K');
  const [timeframe, setTimeframe] = useState('1 month');
  const [proof, setProof] = useState('');
  const [niche, setNiche] = useState('');
  const [adPlatform, setAdPlatform] = useState('');
  const [tips, setTips] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [searching, setSearching] = useState(false);

  const searchProducts = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.get(`/api/products/search?q=${encodeURIComponent(searchQuery)}&limit=5`);
      if (res.ok) setSearchResults(res.data.products || res.data.data || []);
    } catch {}
    setSearching(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const pid = selectedProduct?.id || productId;
    if (!pid || !proof.trim()) return;
    setSubmitting(true);
    try {
      const res = await api.post('/api/winners/submit', {
        product_id: pid,
        revenue_range: revenue,
        timeframe,
        proof_description: proof,
        store_niche: niche || undefined,
        ad_platform: adPlatform || undefined,
        tips: tips || undefined,
      });
      if (res.ok) {
        toast.success('Winner submitted! It will appear after admin review.');
        onSubmitted();
      } else {
        toast.error(res.data?.detail || 'Failed to submit');
      }
    } catch { toast.error('Submission failed'); }
    setSubmitting(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose} data-testid="submit-winner-modal">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 max-h-[85vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="p-6 space-y-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Submit a Verified Winner</h2>
            <p className="text-xs text-slate-500 mt-1">Your identity stays anonymous. Only the product data and revenue range are shown.</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Product search */}
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Find Product</label>
              <div className="flex gap-2">
                <Input
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder="Search by name..."
                  data-testid="product-search-input"
                />
                <Button type="button" variant="outline" onClick={searchProducts} disabled={searching} data-testid="search-product-btn">
                  {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
                </Button>
              </div>
              {searchResults.length > 0 && (
                <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                  {searchResults.map(p => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => { setSelectedProduct(p); setSearchResults([]); }}
                      className={`w-full text-left px-3 py-2 rounded-lg border text-xs hover:bg-slate-50 ${selectedProduct?.id === p.id ? 'border-indigo-300 bg-indigo-50' : 'border-slate-200'}`}
                    >
                      {p.product_name || p.name}
                    </button>
                  ))}
                </div>
              )}
              {selectedProduct && (
                <div className="mt-2 flex items-center gap-2 px-3 py-2 bg-indigo-50 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-indigo-600" />
                  <span className="text-xs font-medium text-indigo-700">{selectedProduct.product_name || selectedProduct.name}</span>
                </div>
              )}
              {!selectedProduct && (
                <div className="mt-2">
                  <label className="text-[10px] text-slate-400">Or enter Product ID directly</label>
                  <Input value={productId} onChange={e => setProductId(e.target.value)} placeholder="Product ID" className="mt-1" data-testid="product-id-input" />
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Revenue Earned</label>
                <select value={revenue} onChange={e => setRevenue(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" data-testid="revenue-select">
                  {REVENUE_RANGES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Timeframe</label>
                <select value={timeframe} onChange={e => setTimeframe(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm" data-testid="timeframe-select">
                  {TIMEFRAMES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Proof / Description *</label>
              <Textarea value={proof} onChange={e => setProof(e.target.value)} placeholder="Describe your results (e.g., 'Generated $8K in first 2 weeks via TikTok ads targeting 18-24 demo')" rows={3} data-testid="proof-textarea" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Store Niche</label>
                <Input value={niche} onChange={e => setNiche(e.target.value)} placeholder="e.g., pet accessories" />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Ad Platform</label>
                <select value={adPlatform} onChange={e => setAdPlatform(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm">
                  <option value="">Select...</option>
                  <option value="TikTok">TikTok</option>
                  <option value="Meta">Meta / Facebook</option>
                  <option value="Google">Google Ads</option>
                  <option value="Pinterest">Pinterest</option>
                  <option value="Organic">Organic / SEO</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Tips for Others (optional)</label>
              <Textarea value={tips} onChange={e => setTips(e.target.value)} placeholder="Any advice for dropshippers considering this product?" rows={2} />
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="button" variant="outline" onClick={onClose} className="flex-1">Cancel</Button>
              <Button type="submit" disabled={submitting || (!selectedProduct && !productId) || !proof.trim()} className="flex-1 bg-emerald-600 hover:bg-emerald-700" data-testid="submit-winner-form-btn">
                {submitting ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Send className="h-4 w-4 mr-2" />}
                Submit Winner
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
