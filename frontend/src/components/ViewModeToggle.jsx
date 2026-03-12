import React from 'react';
import { useViewMode } from '@/contexts/ViewModeContext';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Eye, BarChart3 } from 'lucide-react';

export default function ViewModeToggle() {
  const { isBeginner, toggleMode } = useViewMode();

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={toggleMode}
            className="relative flex items-center gap-1.5 bg-slate-100 rounded-full p-0.5 text-xs font-medium border border-slate-200 hover:border-slate-300 transition-colors"
            data-testid="view-mode-toggle"
          >
            <span className={`flex items-center gap-1 px-2.5 py-1 rounded-full transition-all ${
              isBeginner ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500'
            }`}>
              <Eye className="h-3 w-3" />
              Simple
            </span>
            <span className={`flex items-center gap-1 px-2.5 py-1 rounded-full transition-all ${
              !isBeginner ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500'
            }`}>
              <BarChart3 className="h-3 w-3" />
              Advanced
            </span>
          </button>
        </TooltipTrigger>
        <TooltipContent>
          <p className="text-xs">{isBeginner ? 'Simple mode: essential info only' : 'Advanced mode: full analytics'}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
