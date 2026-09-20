'use client';

import React, { useState } from 'react';
import { Search, Filter, AlertOctagon, HelpCircle, ChevronDown, ChevronUp, FileCode } from 'lucide-react';
import { RiskBadge } from './RiskBadge';

interface Clause {
  title: string;
  content: string;
  section?: string;
  page?: number;
  simplified_explanation: string;
  risk_level: string;
  risk_explanation?: string;
  missing_elements?: string[];
  suggested_questions?: string[];
}

interface Props {
  clauses: Clause[];
}

export const ClausesView: React.FC<Props> = ({ clauses }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  const filtered = clauses.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.simplified_explanation.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRisk =
      riskFilter === 'all' || (c.risk_level || '').toLowerCase() === riskFilter;

    return matchesSearch && matchesRisk;
  });

  return (
    <div className="space-y-4">
      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search clauses, terms, or plain text..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical Risk</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
        </div>
      </div>

      {/* Clauses Count */}
      <div className="text-xs text-slate-400 font-medium">
        Showing {filtered.length} of {clauses.length} extracted clauses
      </div>

      {/* Clause Cards */}
      <div className="space-y-3">
        {filtered.map((clause, idx) => {
          const isExpanded = expandedIndex === idx;

          return (
            <div
              key={idx}
              className={`bg-slate-900/80 border rounded-2xl overflow-hidden transition-all duration-200 ${
                clause.risk_level === 'critical' || clause.risk_level === 'high'
                  ? 'border-red-900/40 hover:border-red-700/60'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              {/* Header */}
              <button
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                className="w-full text-left p-4 flex items-center justify-between gap-4 bg-slate-900/40 hover:bg-slate-800/40 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-slate-800/80 text-slate-300">
                    <FileCode className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-100">{clause.title}</h4>
                    {clause.section && (
                      <span className="text-xs text-slate-400">{clause.section}</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <RiskBadge level={clause.risk_level} />
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </button>

              {/* Content Body */}
              {isExpanded && (
                <div className="p-5 border-t border-slate-800/80 space-y-4 bg-slate-950/40">
                  {/* Simplified Explanation */}
                  <div>
                    <h5 className="text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-1.5">
                      Plain Language Explanation
                    </h5>
                    <p className="text-sm text-slate-200 leading-relaxed bg-indigo-950/20 border border-indigo-900/30 p-3.5 rounded-xl">
                      {clause.simplified_explanation}
                    </p>
                  </div>

                  {/* Legal Text */}
                  <div>
                    <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                      Original Legal Text Snippet
                    </h5>
                    <div className="text-xs text-slate-300 bg-slate-900 border border-slate-800 p-3.5 rounded-xl font-mono whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                      {clause.content}
                    </div>
                  </div>

                  {/* Risk & Analysis */}
                  {clause.risk_explanation && (
                    <div>
                      <h5 className="text-xs font-semibold uppercase tracking-wider text-amber-400 mb-1.5 flex items-center gap-1.5">
                        <AlertOctagon className="w-3.5 h-3.5" /> Risk Analysis
                      </h5>
                      <p className="text-xs text-amber-200/90 bg-amber-950/30 border border-amber-800/40 p-3 rounded-xl">
                        {clause.risk_explanation}
                      </p>
                    </div>
                  )}

                  {/* Missing Elements Warning */}
                  {clause.missing_elements && clause.missing_elements.length > 0 && (
                    <div>
                      <h5 className="text-xs font-semibold uppercase tracking-wider text-rose-400 mb-1.5">
                        Missing Standard Protections
                      </h5>
                      <ul className="list-disc list-inside text-xs text-rose-300/90 space-y-1 bg-rose-950/20 border border-rose-900/30 p-3 rounded-xl">
                        {clause.missing_elements.map((missing, i) => (
                          <li key={i}>{missing}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Suggested Questions */}
                  {clause.suggested_questions && clause.suggested_questions.length > 0 && (
                    <div>
                      <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                        <HelpCircle className="w-3.5 h-3.5 text-indigo-400" /> Questions to Ask the Other Party
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {clause.suggested_questions.map((q, i) => (
                          <span
                            key={i}
                            className="text-xs bg-slate-800 text-slate-300 border border-slate-700/60 px-2.5 py-1 rounded-lg"
                          >
                            "{q}"
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
