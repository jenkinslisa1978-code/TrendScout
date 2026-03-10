import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Trophy, 
  TrendingUp, 
  Flame,
  Calendar,
  ArrowRight,
  Rocket,
  Share2,
  Sparkles,
  Lock,
  PieChart
} from 'lucide-react';
import { formatNumber, getEarlyTrendInfo, getMarketOpportunityInfo } from '@/lib/utils';
import { API_URL } from '@/lib/config';

export default function WeeklyWinnersPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeeklyWinners = async () => {
      try {
        const response = await fetch(`${API_URL}/api/viral/public/weekly-winners?limit=10`);
        if (response.ok) {
          const result = await response.json();
          setData(result);
        }
      } catch (err) {
        console.error('Error fetching weekly winners:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWeeklyWinners();
  }, []);

  const handleShare = () => {
    const shareUrl = window.location.href;
    const shareText = `🏆 This Week's Winning Products on ViralScout\n\nTop trending products with the highest market scores.\n\nCheck it out 👇`;
    
    if (navigator.share) {
      navigator.share({
        title: "Weekly Winning Products - ViralScout",
        text: shareText,
        url: shareUrl
      });
    } else {
      window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`, '_blank');
    }
  };

  const winners = data?.products || [];
  const branding = data?.branding || { name: 'ViralScout', tagline: 'Find winning products before they go viral' };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="font-manrope font-bold text-xl text-slate-900">{branding.name}</span>
          </Link>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={handleShare} data-testid="share-weekly-winners">
              <Share2 className="mr-2 h-4 w-4" />
              Share Report
            </Button>
            <Link to="/signup">
              <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="weekly-winners-signup-cta">
                <Rocket className="mr-2 h-4 w-4" />
                Join Free
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 text-white">
        <div className="max-w-5xl mx-auto px-6 py-16 text-center">
          <Badge className="bg-white/20 text-white border-white/30 mb-4">
            <Calendar className="h-3 w-3 mr-1" />
            Week of {data?.week_of || 'This Week'}
          </Badge>
          <h1 className="font-manrope text-4xl md:text-5xl font-bold mb-4">
            Weekly Winning Products
          </h1>
          <p className="text-indigo-100 text-lg max-w-2xl mx-auto">
            {branding.tagline}. Top trending products this week, ranked by our Market Score algorithm.
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-5xl mx-auto px-6 -mt-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Products Ranked', value: winners.length, icon: Trophy, color: 'bg-amber-50' },
            { label: 'Market Score Avg', value: winners.length > 0 ? Math.round(winners.reduce((a, p) => a + (p.market_score || 0), 0) / winners.length) : 0, icon: PieChart, color: 'bg-indigo-50' },
            { label: 'Trend Score Avg', value: winners.length > 0 ? Math.round(winners.reduce((a, p) => a + (p.trend_score || 0), 0) / winners.length) : 0, icon: TrendingUp, color: 'bg-emerald-50' },
            { label: 'Exploding Trends', value: winners.filter(p => p.early_trend_label === 'exploding' || p.early_trend_label === 'rising').length, icon: Flame, color: 'bg-red-50' },
          ].map((stat) => (
            <Card key={stat.label} className={`${stat.color} border-0 shadow-lg`}>
              <CardContent className="p-4 text-center">
                <stat.icon className="h-6 w-6 mx-auto mb-2 text-slate-600" />
                <p className="font-mono text-2xl font-bold text-slate-900">{stat.value}</p>
                <p className="text-xs text-slate-500">{stat.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Winners List */}
      <main className="max-w-5xl mx-auto px-6 py-12">
        <Card className="border-0 shadow-lg overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-amber-50 to-orange-50 border-b border-slate-100">
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-6 w-6 text-amber-500" />
              This Week's Top Winners
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-12 text-center">
                <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
              </div>
            ) : winners.length === 0 ? (
              <div className="p-12 text-center text-slate-500">
                <Trophy className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                <p>No winners data available this week.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {winners.map((product) => {
                  const earlyTrendInfo = getEarlyTrendInfo(product.early_trend_label);
                  const marketInfo = getMarketOpportunityInfo(product.market_label);
                  
                  return (
                    <div 
                      key={product.id}
                      className="flex items-center gap-4 p-5 hover:bg-slate-50 transition-colors"
                      data-testid={`weekly-winner-${product.id}`}
                    >
                      {/* Rank */}
                      <div className={`flex h-12 w-12 items-center justify-center rounded-xl font-bold text-lg shrink-0 ${
                        product.rank === 1 ? 'bg-gradient-to-br from-amber-400 to-amber-600 text-white' :
                        product.rank === 2 ? 'bg-gradient-to-br from-slate-300 to-slate-400 text-white' :
                        product.rank === 3 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white' :
                        'bg-slate-100 text-slate-600'
                      }`}>
                        #{product.rank}
                      </div>
                      
                      {/* Product Image */}
                      {product.image_url && (
                        <img 
                          src={product.image_url} 
                          alt={product.product_name}
                          className="w-12 h-12 rounded-lg object-cover shrink-0"
                        />
                      )}
                      
                      {/* Product Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-slate-900 truncate">{product.product_name}</h3>
                          <Badge className={`${marketInfo.color} border text-xs shrink-0`}>
                            {marketInfo.shortText}
                          </Badge>
                          {product.early_trend_label && product.early_trend_label !== 'stable' && (
                            <Badge className={`${earlyTrendInfo.color} border text-xs shrink-0`}>
                              {earlyTrendInfo.text}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-sm text-slate-500">
                          <span>{product.category}</span>
                          <span className="text-slate-300">•</span>
                          <span className="text-emerald-600 font-medium flex items-center gap-1">
                            <Lock className="h-3 w-3" />
                            {product.margin_range} margin
                          </span>
                          <span className="text-slate-300">•</span>
                          <span>{product.trend_stage}</span>
                        </div>
                      </div>
                      
                      {/* Scores */}
                      <div className="flex items-center gap-4 shrink-0">
                        <div className="text-center hidden sm:block">
                          <p className="font-mono text-xl font-bold text-indigo-600">{product.market_score}</p>
                          <p className="text-xs text-slate-400">Market</p>
                        </div>
                        <div className="text-center hidden sm:block">
                          <p className="font-mono text-xl font-bold text-emerald-600">{product.trend_score}</p>
                          <p className="text-xs text-slate-400">Trend</p>
                        </div>
                        <Link to={`/discover/product/${product.id}`}>
                          <Button variant="outline" size="sm" data-testid={`view-winner-${product.id}`}>
                            View
                            <ArrowRight className="ml-1 h-4 w-4" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* CTA */}
        <div className="mt-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-center text-white">
          <h2 className="font-manrope text-2xl font-bold mb-2">
            Want Full Insights & Build Stores?
          </h2>
          <p className="text-indigo-100 mb-6">
            {data?.signup_cta || 'Sign up to unlock full insights and build your store'}
          </p>
          <Link to="/signup">
            <Button size="lg" className="bg-white text-indigo-600 hover:bg-indigo-50 font-semibold" data-testid="weekly-winners-bottom-cta">
              <Rocket className="mr-2 h-5 w-5" />
              Start Building Free
            </Button>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="max-w-5xl mx-auto px-6 py-8 text-center text-sm text-slate-500">
          <p className="mb-2">
            <strong className="text-slate-700">{branding.name}</strong> - {branding.tagline}
          </p>
          <p>
            Updated weekly • Powered by AI-driven trend detection
          </p>
        </div>
      </footer>
    </div>
  );
}
