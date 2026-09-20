'use client';

import React from 'react';
import { FileText, Users, Calendar, Gavel, CheckCircle, ShieldAlert } from 'lucide-react';
import { AnalysisData } from '../lib/api';

interface Props {
  filename: string;
  documentType?: string;
  analysis?: AnalysisData;
}

export const DocumentOverviewCard: React.FC<Props> = ({ filename, documentType, analysis }) => {
  const overview = analysis?.overview || {};

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-start gap-3">
          <div className="p-3 bg-indigo-950/80 border border-indigo-700/50 rounded-xl text-indigo-400">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100">{filename}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-900/50 text-indigo-300 border border-indigo-700/40">
                {overview.document_type || documentType || 'Legal Document'}
              </span>
              {overview.governing_law && (
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <Gavel className="w-3.5 h-3.5 text-slate-500" /> {overview.governing_law}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      {overview.summary && (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Plain Language Summary</h3>
          <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
            {overview.summary}
          </p>
        </div>
      )}

      {/* Key Metadata Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {overview.parties && overview.parties.length > 0 && (
          <div className="p-3.5 bg-slate-950/40 rounded-xl border border-slate-800/80">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400 mb-1">
              <Users className="w-4 h-4 text-indigo-400" /> Parties Involved
            </div>
            <p className="text-sm font-medium text-slate-200">{overview.parties.join(', ')}</p>
          </div>
        )}

        {overview.effective_date && (
          <div className="p-3.5 bg-slate-950/40 rounded-xl border border-slate-800/80">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400 mb-1">
              <Calendar className="w-4 h-4 text-emerald-400" /> Effective Date
            </div>
            <p className="text-sm font-medium text-slate-200">{overview.effective_date}</p>
          </div>
        )}

        {overview.expiration_date && (
          <div className="p-3.5 bg-slate-950/40 rounded-xl border border-slate-800/80">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400 mb-1">
              <Calendar className="w-4 h-4 text-amber-400" /> Expiration / Term
            </div>
            <p className="text-sm font-medium text-slate-200">{overview.expiration_date}</p>
          </div>
        )}
      </div>

      {/* Key Takeaways */}
      {analysis?.key_takeaways && analysis.key_takeaways.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-indigo-400" /> Key Takeaways for You
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {analysis.key_takeaways.map((item, idx) => (
              <div key={idx} className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-950/30 border border-slate-800 text-xs text-slate-300">
                <span className="w-5 h-5 rounded-full bg-indigo-950 border border-indigo-700/50 text-indigo-300 font-bold flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
