import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Sparkles, Rocket, TrendingUp, Star, Package, Loader2,
  ArrowRight, Flame, Zap, DollarSign,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const TREND_BADGE = {
  Exploding: 'bg-red-100 text-red-700 border-red-200',
  Emerging: 'bg-orange-100 text-orange-700 border-orange-200',
  Rising: 'bg-amber-100 text-amber-700 border-amber-200',
  Stable: 'bg-blue-100 text-blue-700 border-blue-200',
  Declining: 'bg-slate-100 text-slate-500 border-slate-200',
};

export default function DailyOpportunitiesPanel() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiGet('/api/dashboard/daily-opportunities');
        if (res.ok) setData(await res.json());
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <Card className="border-0 shadow-lg">
        <CardContent className="flex items-center justify-center py-10">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-400" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const top = data.top_opportunity;

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="daily-opportunities">
      <CardHeader className="bg-gradient-to-r from-amber-500 to-orange-500 text-white py-4 pb-3">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Flame className="h-5 w-5" />
          Daily Opportunities
          <Badge className="bg-white/20 text-white border-white/30 text-[10px] ml-auto">
            {data.emerging_products?.length || 0} emerging
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {/* Top Opportunity of the Day */}
        {top && (
          <div className="p-5 bg-gradient-to-r from-amber-50/60 to-orange-50/40 border-b" data-testid="top-opportunity">
            <p className="text-xs font-semibold text-amber-700 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Star className="h-3 w-3" /> Top Opportunity Today
            </p>
            <div className="flex items-start gap-3">
              {top.image_url ? (
                <img src={top.image_url} alt="" className="w-14 h-14 rounded-lg object-cover bg-slate-100 flex-shrink-0" />
              ) : (
                <div className="w-14 h-14 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0">
                  <Package className="h-6 w-6 text-amber-400" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p
                  className="font-semibold text-slate-900 text-sm truncate cursor-pointer hover:text-indigo-600 transition-colors"
                  onClick={() => navigate(`/product/${top.id}`)}
                >
                  {top.product_name}
                </p>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <Badge className={`text-[10px] border ${TREND_BADGE[top.trend_stage] || TREND_BADGE.Stable}`}>
                    {top.trend_stage}
                  </Badge>
                  <span className="text-xs font-mono font-bold text-indigo-600">{top.launch_score}</span>
                  <span className="text-xs text-emerald-600 font-medium flex items-center gap-0.5">
                    <DollarSign className="h-3 w-3" />£{top.estimated_profit > 0 ? top.estimated_profit.toFixed(0) : '—'}
                  </span>
                </div>
              </div>
              <Button
                size="sm"
                className="bg-amber-600 hover:bg-amber-700 flex-shrink-0"
                onClick={() => navigate(`/launch/${top.id}`)}
                data-testid="top-opp-launch-btn"
              >
                <Rocket className="h-3.5 w-3.5 mr-1" />
                Launch
              </Button>
            </div>
          </div>
        )}

        {/* Tabs for categories */}
        <div className="p-4">
          <Tabs defaultValue="emerging">
            <TabsList className="w-full bg-slate-50 text-xs">
              <TabsTrigger value="emerging" className="text-xs flex-1">
                <Zap className="h-3 w-3 mr-1" /> Emerging
              </TabsTrigger>
              <TabsTrigger value="strong" className="text-xs flex-1">
                <Rocket className="h-3 w-3 mr-1" /> Strong Launch
              </TabsTrigger>
              <TabsTrigger value="spikes" className="text-xs flex-1">
                <TrendingUp className="h-3 w-3 mr-1" /> Trend Spikes
              </TabsTrigger>
            </TabsList>

            <TabsContent value="emerging">
              <ProductMiniList products={data.emerging_products} navigate={navigate} />
            </TabsContent>
            <TabsContent value="strong">
              <ProductMiniList products={data.strong_launches} navigate={navigate} />
            </TabsContent>
            <TabsContent value="spikes">
              <ProductMiniList products={data.trend_spikes} navigate={navigate} />
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  );
}

function ProductMiniList({ products, navigate }) {
  if (!products?.length) {
    return <p className="text-center text-sm text-slate-400 py-4">No products in this category</p>;
  }

  return (
    <div className="space-y-2 mt-2">
      {products.slice(0, 5).map((p) => (
        <div
          key={p.id}
          className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer"
          onClick={() => navigate(`/product/${p.id}`)}
          data-testid={`daily-opp-${p.id}`}
        >
          {p.image_url ? (
            <img src={p.image_url} alt="" className="w-9 h-9 rounded-md object-cover bg-slate-100 flex-shrink-0" />
          ) : (
            <div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center flex-shrink-0">
              <Package className="h-4 w-4 text-slate-400" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">{p.product_name}</p>
            <div className="flex items-center gap-2">
              <Badge className={`text-[10px] border ${TREND_BADGE[p.trend_stage] || TREND_BADGE.Stable}`}>
                {p.trend_stage}
              </Badge>
              <span className="text-xs text-slate-500">{p.category}</span>
            </div>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="font-mono text-sm font-bold text-indigo-600">{p.launch_score}</p>
            <p className="text-[10px] text-slate-400">score</p>
          </div>
        </div>
      ))}
    </div>
  );
}
