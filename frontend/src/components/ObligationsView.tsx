'use client';

import React from 'react';
import { UserCheck, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

interface Obligation {
  who: string;
  must_do: string;
  by_when?: string;
  consequence_if_missed?: string;
  is_conditional?: boolean;
  condition?: string;
}

interface Props {
  obligations: Obligation[];
}

export const ObligationsView: React.FC<Props> = ({ obligations }) => {
  if (!obligations || obligations.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 bg-slate-900/60 rounded-2xl border border-slate-800">
        No specific obligations extracted for this document.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <UserCheck className="w-4 h-4 text-indigo-400" /> Key Obligations & Duties Matrix ({obligations.length})
        </h3>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {obligations.map((ob, idx) => (
          <div
            key={idx}
            className="bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 rounded-2xl p-4 shadow-sm space-y-3 transition-all"
          >
            {/* Top row: Who & Condition */}
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-lg bg-indigo-950 text-indigo-300 font-bold text-xs border border-indigo-700/50">
                  {ob.who}
                </span>
                {ob.is_conditional && (
                  <span className="text-xs px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/40 font-medium">
                    Conditional
                  </span>
                )}
              </div>

              {ob.by_when && (
                <span className="text-xs text-slate-400 flex items-center gap-1 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                  <Clock className="w-3.5 h-3.5 text-indigo-400" /> Deadline: {ob.by_when}
                </span>
              )}
            </div>

            {/* Action / Must Do */}
            <div>
              <p className="text-sm font-medium text-slate-100 leading-relaxed">{ob.must_do}</p>
              {ob.condition && (
                <p className="text-xs text-amber-300/80 mt-1 italic">
                  Condition: {ob.condition}
                </p>
              )}
            </div>

            {/* Consequence */}
            {ob.consequence_if_missed && (
              <div className="p-2.5 bg-red-950/20 border border-red-900/30 rounded-xl text-xs text-red-300 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Consequence if missed:</strong> {ob.consequence_if_missed}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
