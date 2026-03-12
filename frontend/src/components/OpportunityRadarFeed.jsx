import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Loader2, TrendingUp, Megaphone, Truck, Shield, Package, Rocket, Radio, RefreshCcw,
} from 'lucide-react';
import { apiGet } from '@/lib/api';

const EVENT_ICONS = {
  trend_spike: TrendingUp,
  new_ads: Megaphone,
  supplier_demand: Truck,
  competition_drop: Shield,
};

const EVENT_COLORS = {
  trend_spike: 'bg-red-100 text-red-600',
  new_ads: 'bg-violet-100 text-violet-600',
  supplier_demand: 'bg-teal-100 text-teal-600',
  competition_drop: 'bg-emerald-100 text-emerald-600',
};

const EVENT_LABELS = {
  trend_spike: 'Trend Spike',
  new_ads: 'Ad Activity',
  supplier_demand: 'Demand Jump',
  competition_drop: 'Low Competition',
};

export default function OpportunityRadarFeed() {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);
  const intervalRef = useRef(null);

  const fetchEvents = useCallback(async () => {
    try {
      const res = await apiGet('/api/radar/live-events?limit=15');
      if (res.ok) {
        const d = await res.json();
        setEvents(d.events || []);
        setLastRefresh(new Date());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
    intervalRef.current = setInterval(fetchEvents, 30000);
    return () => clearInterval(intervalRef.current);
  }, [fetchEvents]);

  return (
    <Card className="border-0 shadow-lg overflow-hidden" data-testid="opportunity-radar">
      <CardHeader className="bg-gradient-to-r from-slate-900 to-slate-800 text-white py-4 pb-3">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Radio className="h-5 w-5 text-emerald-400 animate-pulse" />
          Opportunity Radar
          <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-400/30 text-[10px] ml-auto">
            LIVE
          </Badge>
        </CardTitle>
        {lastRefresh && (
          <p className="text-[10px] text-slate-400 flex items-center gap-1 mt-1">
            <RefreshCcw className="h-2.5 w-2.5" />
            Refreshes every 30s &middot; Last: {lastRefresh.toLocaleTimeString()}
          </p>
        )}
      </CardHeader>
      <CardContent className="p-0 max-h-[420px] overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-10">
            <Loader2 className="h-6 w-6 animate-spin text-indigo-400" />
          </div>
        ) : events.length === 0 ? (
          <div className="text-center py-10 text-slate-400">
            <Radio className="h-8 w-8 mx-auto mb-2 opacity-40" />
            <p className="text-sm">No signal events detected</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {events.map((evt, i) => {
              const Icon = EVENT_ICONS[evt.type] || TrendingUp;
              const color = EVENT_COLORS[evt.type] || 'bg-slate-100 text-slate-600';
              const label = EVENT_LABELS[evt.type] || evt.type;
              return (
                <div
                  key={`${evt.product_id}-${i}`}
                  className="flex items-center gap-3 p-3.5 hover:bg-slate-50 transition-colors cursor-pointer"
                  onClick={() => navigate(`/product/${evt.product_id}`)}
                  data-testid={`radar-event-${evt.product_id}`}
                >
                  {/* Icon */}
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${color}`}>
                    <Icon className="h-4 w-4" />
                  </div>

                  {/* Image */}
                  {evt.image_url ? (
                    <img src={evt.image_url} alt="" className="w-9 h-9 rounded-md object-cover bg-slate-100 flex-shrink-0" />
                  ) : (
                    <div className="w-9 h-9 rounded-md bg-slate-100 flex items-center justify-center flex-shrink-0">
                      <Package className="h-4 w-4 text-slate-400" />
                    </div>
                  )}

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate">{evt.product_name}</p>
                    <p className="text-xs text-slate-500 truncate">{evt.detail}</p>
                  </div>

                  {/* Score & badge */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Badge className={`text-[10px] border ${color}`}>{label}</Badge>
                    <span className="font-mono text-sm font-bold text-indigo-600">{evt.launch_score}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
