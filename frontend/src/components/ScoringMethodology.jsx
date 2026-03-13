import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ChevronDown, ChevronUp, Shield, TrendingUp, PoundSterling, Users,
  Megaphone, Package, Search, Activity, Info, Database, Clock,
} from 'lucide-react';

const SIGNAL_ICONS = {
  'Trend Score': TrendingUp,
  'Margin Score': PoundSterling,
  'Competition Score': Users,
  'Ad Activity Score': Megaphone,
  'Supplier Demand Score': Package,
  'Search Growth Score': Search,
  'Order Velocity Score': Activity,
};

export default function ScoringMethodology() {
  const [data, setData] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const [expandedSignal, setExpandedSignal] = useState(null);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/scoring/methodology`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {});
  }, []);

  if (!data) return null;

  return (
    <Card className="border-slate-200 shadow-sm" data-testid="scoring-methodology">
      <CardHeader
        className="cursor-pointer border-b border-slate-100 pb-4 hover:bg-slate-50/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle className="font-manrope text-lg font-semibold text-slate-900 flex items-center gap-2">
            <Shield className="h-5 w-5 text-indigo-500" />
            How Our Scores Work
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs text-slate-500">Transparent scoring</Badge>
            {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
          </div>
        </div>
        {!expanded && (
          <p className="text-sm text-slate-500 mt-1">{data.overview}</p>
        )}
      </CardHeader>

      {expanded && (
        <CardContent className="p-6 space-y-6">
          {/* Overview */}
          <div>
            <p className="text-sm text-slate-600 leading-relaxed">{data.overview}</p>
            <div className="mt-3 bg-indigo-50 border border-indigo-100 rounded-lg p-3">
              <p className="text-xs font-mono text-indigo-700">{data.formula}</p>
            </div>
          </div>

          {/* 7 Signals */}
          <div>
            <h4 className="text-sm font-semibold text-slate-800 mb-3">The 7 Scoring Signals</h4>
            <div className="space-y-2">
              {data.signals.map((signal) => {
                const Icon = SIGNAL_ICONS[signal.name] || Info;
                const isOpen = expandedSignal === signal.name;
                return (
                  <div
                    key={signal.name}
                    className="border border-slate-200 rounded-lg overflow-hidden"
                  >
                    <button
                      onClick={() => setExpandedSignal(isOpen ? null : signal.name)}
                      className="w-full flex items-center justify-between p-3 hover:bg-slate-50 transition-colors text-left"
                      data-testid={`signal-${signal.name.toLowerCase().replace(/\s/g, '-')}`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="h-4 w-4 text-indigo-500" />
                        <span className="text-sm font-medium text-slate-800">{signal.name}</span>
                        <Badge variant="outline" className="text-[10px]">{signal.weight}</Badge>
                      </div>
                      {isOpen ? <ChevronUp className="h-3.5 w-3.5 text-slate-400" /> : <ChevronDown className="h-3.5 w-3.5 text-slate-400" />}
                    </button>
                    {isOpen && (
                      <div className="px-3 pb-3 pt-0 space-y-2 border-t border-slate-100">
                        <p className="text-xs text-slate-600 mt-2">{signal.description}</p>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div className="bg-emerald-50 rounded p-2">
                            <span className="font-medium text-emerald-700">High score means:</span>
                            <p className="text-emerald-600 mt-0.5">{signal.what_high_means}</p>
                          </div>
                          <div className="bg-amber-50 rounded p-2">
                            <span className="font-medium text-amber-700">Low score means:</span>
                            <p className="text-amber-600 mt-0.5">{signal.what_low_means}</p>
                          </div>
                        </div>
                        <div className="text-[10px] text-slate-400">
                          <span className="font-medium">Data from:</span> {signal.sources.join(' + ')}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Data Sources */}
          <div>
            <h4 className="text-sm font-semibold text-slate-800 mb-3 flex items-center gap-2">
              <Database className="h-4 w-4 text-slate-500" />
              Where Our Data Comes From
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {data.data_sources.map((src) => (
                <div key={src.name} className="bg-slate-50 rounded-lg p-2.5 text-xs">
                  <p className="font-semibold text-slate-800">{src.name}</p>
                  <p className="text-slate-500 mt-0.5">{src.type}</p>
                  <div className="flex items-center gap-1 mt-1 text-slate-400">
                    <Clock className="h-3 w-3" />
                    <span>{src.update_frequency}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Honest Limitations */}
          <div className="bg-amber-50/50 border border-amber-100 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-amber-800 mb-2 flex items-center gap-2">
              <Info className="h-4 w-4" />
              What You Should Know
            </h4>
            <ul className="space-y-1.5">
              {data.honest_limitations.map((limitation, i) => (
                <li key={i} className="text-xs text-amber-700 flex items-start gap-2">
                  <span className="text-amber-400 mt-0.5">-</span>
                  {limitation}
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
