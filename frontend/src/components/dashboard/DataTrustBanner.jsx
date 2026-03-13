import React, { useState } from 'react';
import { Shield, ChevronDown, ChevronUp, Database, Activity, TrendingUp, Package } from 'lucide-react';

export default function DataTrustBanner() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-slate-900 rounded-xl overflow-hidden" data-testid="data-trust-banner">
      <button
        className="w-full flex items-center justify-between px-5 py-3 hover:bg-slate-800/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <Shield className="h-4 w-4 text-emerald-400" />
          <span className="text-sm font-medium text-slate-200">Your data is sourced from real platforms</span>
          <span className="text-xs text-slate-500">Amazon, Google Trends, TikTok, AliExpress, Meta Ad Library</span>
        </div>
        {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
      </button>

      {expanded && (
        <div className="px-5 pb-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { icon: TrendingUp, label: 'Trend Data', desc: 'Google Trends + TikTok views, updated daily', color: 'text-blue-400' },
            { icon: Package, label: 'Supplier Pricing', desc: 'AliExpress + CJ Dropshipping, real-time', color: 'text-emerald-400' },
            { icon: Activity, label: 'Ad Intelligence', desc: 'Meta Ad Library, active ads tracked daily', color: 'text-purple-400' },
            { icon: Database, label: 'Market Data', desc: 'Amazon reviews, BSR, pricing signals', color: 'text-amber-400' },
          ].map(({ icon: Icon, label, desc, color }) => (
            <div key={label} className="bg-slate-800/50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Icon className={`h-3.5 w-3.5 ${color}`} />
                <span className="text-xs font-medium text-slate-300">{label}</span>
              </div>
              <p className="text-[11px] text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
