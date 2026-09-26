'use client';

import React, { useState, useEffect } from 'react';
import { UserCheck, Download, CheckSquare, AlertTriangle, FileText, Loader2, Sparkles } from 'lucide-react';
import { api, DocumentSummary, LawyerPrepPackage } from '../lib/api';

export const LawyerPrepView: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string>('');
  const [concerns, setConcerns] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [prepPackage, setPrepPackage] = useState<LawyerPrepPackage | null>(null);
  const [checklist, setChecklist] = useState<{ checklist?: Array<{ item: string; why_important?: string }> } | null>(null);

  useEffect(() => {
    api.listDocuments().then((res) => {
      setDocuments(res.documents);
      if (res.documents.length > 0) {
        setSelectedDocId(res.documents[0].id);
      }
    }).catch(console.error);
  }, []);

  const handleGenerate = async () => {
    if (!selectedDocId) return;

    setLoading(true);
    setPrepPackage(null);
    setChecklist(null);

    try {
      const [prepRes, checklistRes] = await Promise.all([
        api.generateLawyerPrep(selectedDocId, concerns),
        api.generateChecklist(selectedDocId),
      ]);
      setPrepPackage(prepRes);
      setChecklist(checklistRes);
    } catch (err: unknown) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportText = () => {
    if (!prepPackage) return;
    const text = `
==================================================
NYAYAAI LEGAL CONSULTATION PREPARATION PACKAGE
==================================================
Document: ${documents.find((d) => d.id === selectedDocId)?.filename || 'Legal Document'}
Generated On: ${new Date().toLocaleDateString()}

1. EXECUTIVE SUMMARY FOR LAWYER
${prepPackage.document_summary}

2. KEY CONCERNS TO HIGHLIGHT
${prepPackage.key_concerns_for_lawyer?.map((c, i) => `[ ] ${i + 1}. ${c}`).join('\n')}

3. HIGH RISK CLAUSES & NEGOTIATION POINTS
${prepPackage.high_risk_clauses_summary
  ?.map(
    (h) => `• Clause: ${h.clause_title}\n  Issue: ${h.issue}\n  Negotiation Point: ${h.recommended_negotiation_point}\n`
  )
  .join('\n')}

4. MISSING PROTECTIONS TO DISCUSS
${prepPackage.missing_protections?.map((m) => `• ${m}`).join('\n')}

5. QUESTIONS TO ASK YOUR LAWYER
${prepPackage.questions_to_ask_lawyer?.map((q, i) => `${i + 1}. ${q}`).join('\n')}

==================================================
DISCLAIMER: Prepared by NyayaAI for client preparation.
This package is an AI-generated organization aid, not legal advice.
==================================================
    `;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Lawyer_Prep_Package_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-950 border border-indigo-700/50 rounded-xl text-indigo-400">
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100">Lawyer Prep & Export Engine</h2>
            <p className="text-xs text-slate-400">
              Generate structured consultation briefs, “Before You Sign” checklists, and custom negotiation points
            </p>
          </div>
        </div>

        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Select Document
            </label>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">Select a document...</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename} ({d.document_type || 'Legal Doc'})
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Your Specific Concerns or Goals (Optional)
            </label>
            <textarea
              placeholder="e.g. I want to make sure I can resign with 30 days notice, or check if the non-compete is enforceable..."
              value={concerns}
              onChange={(e) => setConcerns(e.target.value)}
              rows={2}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !selectedDocId}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-semibold text-sm flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-indigo-600/20 disabled:opacity-40 transition-all"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Structuring Consultation Package...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" /> Generate Lawyer Prep Brief & Checklist
              </>
            )}
          </button>
        </div>
      </div>

      {/* Output Package */}
      {prepPackage && (
        <div className="space-y-6">
          {/* Download Button */}
          <div className="flex justify-end">
            <button
              onClick={handleExportText}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 border border-slate-700 transition-colors"
            >
              <Download className="w-4 h-4 text-indigo-400" /> Export Brief (.txt)
            </button>
          </div>

          {/* Consultation Agenda & Brief */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-400" /> Lawyer Consultation Brief
            </h3>

            {/* Document Summary */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Executive Overview for Attorney
              </h4>
              <p className="text-sm text-slate-300 bg-slate-950 p-4 rounded-xl border border-slate-800 leading-relaxed">
                {prepPackage.document_summary}
              </p>
            </div>

            {/* High Risk Clauses */}
            {prepPackage.high_risk_clauses_summary && prepPackage.high_risk_clauses_summary.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-amber-400 mb-2 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" /> Priority Clauses to Review
                </h4>
                <div className="space-y-3">
                  {prepPackage.high_risk_clauses_summary.map((h, idx) => (
                    <div key={idx} className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2 text-xs">
                      <div className="font-bold text-slate-200 text-sm">{h.clause_title}</div>
                      <p className="text-amber-300/90">
                        <strong>Identified Issue:</strong> {h.issue}
                      </p>
                      <p className="text-indigo-300 bg-indigo-950/30 p-2.5 rounded-lg border border-indigo-900/40">
                        <strong>Suggested Negotiation Counter:</strong> {h.recommended_negotiation_point}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Questions to Ask Lawyer */}
            {prepPackage.questions_to_ask_lawyer && prepPackage.questions_to_ask_lawyer.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-2">
                  Recommended Questions to Ask Your Attorney
                </h4>
                <ul className="space-y-2">
                  {prepPackage.questions_to_ask_lawyer.map((q, idx) => (
                    <li key={idx} className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200">
                      <span className="w-5 h-5 rounded-full bg-indigo-950 text-indigo-300 font-bold flex items-center justify-center text-[10px] shrink-0">
                        {idx + 1}
                      </span>
                      <span>{q}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Checklist */}
          {checklist && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <CheckSquare className="w-5 h-5 text-emerald-400" /> “Before You Sign” Final Checklist
              </h3>

              <div className="space-y-2">
                {checklist.checklist?.map((item, idx: number) => (
                  <label key={idx} className="flex items-start gap-3 p-3 bg-slate-950 border border-slate-800 rounded-xl cursor-pointer hover:bg-slate-800/40 transition-colors">
                    <input type="checkbox" className="mt-1 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-700" />
                    <div>
                      <span className="text-xs font-semibold text-slate-200 block">{item.item}</span>
                      {item.why_important && (
                        <span className="text-[11px] text-slate-400 mt-0.5 block">{item.why_important}</span>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
