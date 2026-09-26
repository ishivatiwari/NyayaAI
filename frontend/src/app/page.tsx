'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import { FileUpload } from '../components/FileUpload';
import { DocumentOverviewCard } from '../components/DocumentOverviewCard';
import { ClausesView } from '../components/ClausesView';
import { ObligationsView } from '../components/ObligationsView';
import { TimelineView } from '../components/TimelineView';
import { QAChatView } from '../components/QAChatView';
import { DocumentCompareView } from '../components/DocumentCompareView';
import { LawyerPrepView } from '../components/LawyerPrepView';
import { api, DocumentSummary, DocumentDetail } from '../lib/api';
import {
  FileText,
  FileCode,
  UserCheck,
  Calendar,
  MessageSquare,
  Plus,
  Loader2,
  Trash2,
  AlertCircle,
  Sparkles,
} from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState('documents');
  const [subTab, setSubTab] = useState<'overview' | 'clauses' | 'obligations' | 'timeline' | 'chat'>('overview');

  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<DocumentDetail | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const fetchDocuments = useCallback(async (autoSelectId?: string) => {
    try {
      const res = await api.listDocuments();
      setDocuments(res.documents);

      if (autoSelectId) {
        setSelectedDocId((current) => current ?? autoSelectId);
      } else if (res.documents.length > 0) {
        setSelectedDocId((current) => current ?? res.documents[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  }, []);

  useEffect(() => {
    // This initial mount fetch is intentionally async and does not need to be
    // converted to a sync setter pattern for the app's data flow.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void fetchDocuments();
  }, [fetchDocuments]);

  // Fetch detail for selected document & poll while processing
  useEffect(() => {
    if (!selectedDocId) return;

    let isSubscribed = true;
    let pollTimer: ReturnType<typeof setTimeout> | undefined;

    const fetchDetail = async () => {
      try {
        const detail = await api.getDocument(selectedDocId);
        if (!isSubscribed) return;

        setSelectedDoc(detail);

        // Poll if document is still processing
        if (detail.status === 'uploading' || detail.status === 'extracting' || detail.status === 'analyzing') {
          pollTimer = setTimeout(() => {
            fetchDetail();
            fetchDocuments();
          }, 2500);
        } else {
          fetchDocuments();
        }
      } catch (err) {
        console.error('Failed to fetch document detail:', err);
      }
    };

    fetchDetail();

    return () => {
      isSubscribed = false;
      if (pollTimer) clearTimeout(pollTimer);
    };
  }, [selectedDocId, fetchDocuments]);

  const handleDelete = async (docId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await api.deleteDocument(docId);
      if (selectedDocId === docId) {
        setSelectedDocId(null);
        setSelectedDoc(null);
      }
      await fetchDocuments();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error deleting document';
      alert(`Delete failed: ${message}`);
    }
  };

  const handleDocumentKeyDown = (event: React.KeyboardEvent<HTMLDivElement>, docId: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      setSelectedDocId(docId);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-indigo-600 focus:px-4 focus:py-2 focus:text-white"
      >
        Skip to main content
      </a>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Top Disclaimer Banner */}
        <DisclaimerBanner />

        {/* TAB 1: DOCUMENTS DASHBOARD */}
        {activeTab === 'documents' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Sidebar / Document List (4 cols) */}
            <div className="lg:col-span-4 space-y-4">
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-xl space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Your Legal Documents ({documents.length})
                  </h3>
                  <button
                    type="button"
                    aria-expanded={showUploadModal}
                    aria-label={showUploadModal ? 'Hide upload panel' : 'Show upload panel'}
                    onClick={() => setShowUploadModal(!showUploadModal)}
                    className="px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1 transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5" aria-hidden="true" /> Upload New
                  </button>
                </div>

                {/* File Upload Box */}
                {showUploadModal || documents.length === 0 ? (
                  <div className="pt-2">
                    <FileUpload
                      onUploadSuccess={(docId) => {
                        setShowUploadModal(false);
                        fetchDocuments(docId);
                      }}
                    />
                  </div>
                ) : null}

                {/* Documents List */}
                <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                  {documents.map((doc) => {
                    const isSelected = doc.id === selectedDocId;
                    const isProcessing =
                      doc.status === 'uploading' || doc.status === 'extracting' || doc.status === 'analyzing';

                    return (
                      <div
                        key={doc.id}
                        role="button"
                        tabIndex={0}
                        aria-pressed={isSelected}
                        aria-label={`Select document ${doc.filename}`}
                        onClick={() => setSelectedDocId(doc.id)}
                        onKeyDown={(event) => handleDocumentKeyDown(event, doc.id)}
                        className={`w-full p-3.5 rounded-xl border text-left cursor-pointer transition-all flex items-center justify-between gap-3 ${
                          isSelected
                            ? 'bg-gradient-to-r from-indigo-950/80 to-slate-900 border-indigo-500/60 shadow-md shadow-indigo-500/10'
                            : 'bg-slate-950/50 border-slate-800/80 hover:bg-slate-800/40 hover:border-slate-700'
                        }`}
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <div className={`p-2 rounded-lg shrink-0 ${isSelected ? 'bg-indigo-900/60 text-indigo-300' : 'bg-slate-800 text-slate-400'}`}>
                            {isProcessing ? (
                              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                            ) : (
                              <FileText className="w-4 h-4" />
                            )}
                          </div>
                          <div className="min-w-0">
                            <p className="text-xs font-semibold text-slate-100 truncate">{doc.filename}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className="text-[10px] text-slate-400">{doc.document_type || 'Legal Doc'}</span>
                              <span
                                className={`text-[9px] uppercase font-bold px-1.5 py-0.2 rounded border ${
                                  doc.status === 'ready'
                                    ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                                    : doc.status === 'failed'
                                    ? 'bg-rose-950 text-rose-300 border-rose-800'
                                    : 'bg-amber-950 text-amber-300 border-amber-800 animate-pulse'
                                }`}
                              >
                                {doc.status}
                              </span>
                            </div>
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={(e) => handleDelete(doc.id, e)}
                          aria-label={`Delete ${doc.filename}`}
                          title="Delete document"
                          className="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-800 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
                        >
                          <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Document Analysis Workspace (8 cols) */}
            <div className="lg:col-span-8 space-y-4">
              {selectedDoc ? (
                <>
                  {/* Status processing banner */}
                  {(selectedDoc.status === 'extracting' || selectedDoc.status === 'analyzing' || selectedDoc.status === 'uploading') && (
                    <div className="bg-indigo-950/40 border border-indigo-700/50 p-4 rounded-2xl flex items-center gap-3 text-indigo-200">
                      <Loader2 className="w-5 h-5 text-indigo-400 animate-spin shrink-0" />
                      <div>
                        <p className="text-sm font-semibold">AI Multi-Agent Pipeline Running</p>
                        <p className="text-xs text-indigo-300/80">
                          Extracting clauses, detecting obligations, evaluating risk levels, and indexing chunks into ChromaDB vector store...
                        </p>
                      </div>
                    </div>
                  )}

                  {selectedDoc.status === 'failed' && (
                    <div className="bg-rose-950/40 border border-rose-700/50 p-4 rounded-2xl flex items-center gap-3 text-rose-200">
                      <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
                      <div>
                        <p className="text-sm font-semibold">Document Analysis Failed</p>
                        <p className="text-xs text-rose-300/80">{selectedDoc.error_message || 'An error occurred during multi-agent analysis.'}</p>
                      </div>
                    </div>
                  )}

                  {/* Sub-tab Navigation */}
                  <div
                    role="tablist"
                    aria-label="Document analysis sections"
                    className="flex items-center gap-1 bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800 overflow-x-auto"
                  >
                    {[
                      { id: 'overview', label: 'Overview & Summary', icon: FileText },
                      { id: 'clauses', label: `Clauses (${selectedDoc.analysis?.clauses?.length || 0})`, icon: FileCode },
                      { id: 'obligations', label: `Obligations (${selectedDoc.analysis?.obligations?.length || 0})`, icon: UserCheck },
                      { id: 'timeline', label: `Timeline (${selectedDoc.analysis?.important_dates?.length || 0})`, icon: Calendar },
                      { id: 'chat', label: 'Ask RAG AI', icon: MessageSquare },
                    ].map((st) => {
                      const Icon = st.icon;
                      const isActive = subTab === st.id;
                      return (
                        <button
                          key={st.id}
                          type="button"
                          role="tab"
                          id={`tab-${st.id}`}
                          aria-controls={`panel-${st.id}`}
                          aria-selected={isActive}
                          tabIndex={isActive ? 0 : -1}
                          aria-label={st.label}
                          onClick={() => setSubTab(st.id as 'overview' | 'clauses' | 'obligations' | 'timeline' | 'chat')}
                          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                            isActive
                              ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md shadow-indigo-600/20'
                              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                          }`}
                        >
                          <Icon className="w-4 h-4" aria-hidden="true" />
                          <span>{st.label}</span>
                        </button>
                      );
                    })}
                  </div>

                  {/* Sub-tab Content */}
                  <div
                    role="tabpanel"
                    id={`panel-${subTab}`}
                    aria-labelledby={`tab-${subTab}`}
                    tabIndex={0}
                    className="focus:outline-none"
                  >
                    {subTab === 'overview' && (
                      <DocumentOverviewCard
                        filename={selectedDoc.filename}
                        documentType={selectedDoc.document_type}
                        analysis={selectedDoc.analysis}
                      />
                    )}

                    {subTab === 'clauses' && (
                      <ClausesView clauses={selectedDoc.analysis?.clauses || []} />
                    )}

                    {subTab === 'obligations' && (
                      <ObligationsView obligations={selectedDoc.analysis?.obligations || []} />
                    )}

                    {subTab === 'timeline' && (
                      <TimelineView dates={selectedDoc.analysis?.important_dates || []} />
                    )}

                    {subTab === 'chat' && (
                      <QAChatView documentId={selectedDoc.id} documentStatus={selectedDoc.status} />
                    )}
                  </div>
                </>
              ) : (
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 space-y-4">
                  <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-slate-700 mx-auto flex items-center justify-center">
                    <Sparkles className="w-8 h-8 text-indigo-400" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-200">No Document Selected</h3>
                    <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                      Upload a legal document on the left or select an existing document to view plain-language analysis and RAG Q&A.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: COMPARE AGREEMENTS */}
        {activeTab === 'compare' && <DocumentCompareView />}

        {/* TAB 3: LAWYER PREP */}
        {activeTab === 'lawyer-prep' && <LawyerPrepView />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-4 text-center text-xs text-slate-500">
        <p>NyayaAI Legal Intelligence Platform — Built for legal transparency, privacy, and user empowerment.</p>
        <p className="text-[10px] text-slate-600 mt-1">Not professional legal advice. All document data stored locally/in session.</p>
      </footer>
    </div>
  );
}
