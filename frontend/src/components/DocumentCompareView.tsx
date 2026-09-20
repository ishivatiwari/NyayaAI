'use client';

import React, { useState, useEffect } from 'react';
import { GitCompare, ArrowRight, AlertTriangle, ShieldCheck, CheckCircle2, Loader2, Sparkles } from 'lucide-react';
import { api, DocumentSummary, ComparisonResult } from '../lib/api';

export const DocumentCompareView: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [docAId, setDocAId] = useState<string>('');
  const [docBId, setDocBId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listDocuments().then((res) => {
      setDocuments(res.documents);
      if (res.documents.length >= 2) {
        setDocAId(res.documents[0].id);
        setDocBId(res.documents[1].id);
      }
    }).catch(console.error);
  }, []);

  const handleCompare = async () => {
    if (!docAId || !docBId) return;
    if (docAId === docBId) {
      setError('Please select two different documents to compare.');
      return;
    }

    setError(null);
    setLoading(true);
    setResult(null);

    try {
      const res = await api.compareDocuments(docAId, docBId);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Comparison failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-950 border border-indigo-700/50 rounded-xl text-indigo-400">
            <GitCompare className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100">Document & Clause Comparison Engine</h2>
            <p className="text-xs text-slate-400">
              Compare two agreements, track modifications, added/removed clauses, and risk shifts
            </p>
          </div>
        </div>

        {/* Document Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {/* Document A */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
              Document A (Original / Baseline)
            </label>
            <select
              value={docAId}
              onChange={(e) => setDocAId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">Select Baseline Document...</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename} ({d.document_type || 'Doc'})
                </option>
              ))}
            </select>
          </div>

          {/* Document B */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-amber-400">
              Document B (Revised / Counterparty Version)
            </label>
            <select
              value={docBId}
              onChange={(e) => setDocBId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="">Select Revised Document...</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename} ({d.document_type || 'Doc'})
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <p className="text-xs text-rose-400 bg-rose-950/40 p-3 rounded-xl border border-rose-900/50">
            {error}
          </p>
        )}

        <button
          onClick={handleCompare}
          disabled={loading || !docAId || !docBId}
          className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-700 text-white font-semibold text-sm flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-indigo-600/20 disabled:opacity-40 transition-all"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Analyzing Differences & Risk Delta...
            </>
          ) : (
            <>
              <GitCompare className="w-4 h-4" /> Compare Agreements Now
            </>
          )}
        </button>
      </div>

      {/* Comparison Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary & Recommendation */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" /> Comparison Overview
            </h3>
            <p className="text-sm text-slate-200 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800">
              {result.overall_summary}
            </p>

            {/* Safer Option Banner */}
            {result.risk_comparison?.safer_option && (
              <div className="p-4 bg-emerald-950/40 border border-emerald-700/50 rounded-xl text-emerald-200 space-y-1">
                <div className="flex items-center gap-2 font-bold text-sm text-emerald-300">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Safer Option Recommendation: {result.risk_comparison.safer_option}
                </div>
                <p className="text-xs text-emerald-200/90 leading-relaxed">{result.risk_comparison.reasoning}</p>
              </div>
            )}
          </div>

          {/* Key Differences Table/Cards */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
              Clause-by-Clause Differences ({result.key_differences?.length || 0})
            </h3>

            <div className="space-y-3">
              {result.key_differences?.map((diff, idx) => (
                <div key={idx} className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-xs font-bold text-slate-200 uppercase tracking-wider bg-slate-900 px-3 py-1 rounded-lg border border-slate-800">
                      {diff.category}
                    </span>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${
                          diff.change_type === 'added'
                            ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                            : diff.change_type === 'removed'
                            ? 'bg-rose-950 text-rose-300 border-rose-800'
                            : 'bg-amber-950 text-amber-300 border-amber-800'
                        }`}
                      >
                        {diff.change_type}
                      </span>
                      <span
                        className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${
                          diff.impact_level === 'high'
                            ? 'bg-red-950 text-red-300 border-red-800'
                            : 'bg-slate-900 text-slate-400 border-slate-800'
                        }`}
                      >
                        {diff.impact_level} impact
                      </span>
                    </div>
                  </div>

                  {/* Side-by-side comparison */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="p-3 bg-indigo-950/20 border border-indigo-900/40 rounded-xl space-y-1">
                      <span className="font-semibold text-indigo-300">{result.doc_a?.name || 'Document A'}</span>
                      <p className="text-slate-300 font-mono text-[11px] leading-relaxed">{diff.doc_a_version}</p>
                    </div>

                    <div className="p-3 bg-amber-950/20 border border-amber-900/40 rounded-xl space-y-1">
                      <span className="font-semibold text-amber-300">{result.doc_b?.name || 'Document B'}</span>
                      <p className="text-slate-300 font-mono text-[11px] leading-relaxed">{diff.doc_b_version}</p>
                    </div>
                  </div>

                  {/* Impact explanation */}
                  <p className="text-xs text-slate-300 bg-slate-900/80 p-3 rounded-xl border border-slate-800/80">
                    <strong>Practical Impact:</strong> {diff.explanation}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
