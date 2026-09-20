'use client';

import React from 'react';
import { Calendar, AlertCircle, RefreshCw } from 'lucide-react';

interface ImportantDate {
  date: string;
  event: string;
  consequence: string;
  is_recurring?: boolean;
}

interface Props {
  dates: ImportantDate[];
}

export const TimelineView: React.FC<Props> = ({ dates }) => {
  if (!dates || dates.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 bg-slate-900/60 rounded-2xl border border-slate-800">
        No specific critical dates detected in this document.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
        <Calendar className="w-4 h-4 text-indigo-400" /> Contractual Timeline & Deadlines ({dates.length})
      </h3>

      <div className="relative border-l-2 border-slate-800 ml-4 space-y-6 pl-6">
        {dates.map((d, idx) => (
          <div key={idx} className="relative group">
            {/* Timeline dot */}
            <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-slate-950 border-2 border-indigo-500 group-hover:scale-125 transition-transform" />

            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-sm space-y-2">
              <div className="flex items-center justify-between gap-3">
                <span className="text-xs font-bold text-indigo-400 bg-indigo-950 px-2.5 py-1 rounded-lg border border-indigo-800/40">
                  {d.date}
                </span>
                {d.is_recurring && (
                  <span className="text-[10px] text-amber-300 bg-amber-950 px-2 py-0.5 rounded border border-amber-800/40 flex items-center gap-1 font-medium">
                    <RefreshCw className="w-3 h-3 animate-spin-slow" /> Recurring
                  </span>
                )}
              </div>

              <h4 className="text-sm font-semibold text-slate-100">{d.event}</h4>

              {d.consequence && (
                <p className="text-xs text-slate-300 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/60 flex items-start gap-2">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                  <span>{d.consequence}</span>
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
