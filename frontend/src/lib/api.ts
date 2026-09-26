/**
 * NyayaAI API Client
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Session management (persisted in localStorage)
const getSessionId = (): string => {
  if (typeof window === 'undefined') return '';
  let id = localStorage.getItem('nyaya_session_id');
  if (!id) {
    id = 'sess_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('nyaya_session_id', id);
  }
  return id;
};

const getHeaders = (isJson = true) => {
  const headers: Record<string, string> = {
    'X-Session-ID': getSessionId(),
  };
  if (isJson) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
};

export interface DocumentSummary {
  id: string;
  filename: string;
  document_type?: string;
  status: string;
  page_count?: number;
  language?: string;
  file_size?: number;
  created_at?: string;
  has_analysis?: boolean;
}

export interface AnalysisData {
  overview?: {
    document_type?: string;
    governing_law?: string;
    parties?: string[];
    effective_date?: string;
    expiration_date?: string;
    summary?: string;
    primary_purpose?: string;
  };
  summary?: string;
  key_takeaways?: string[];
  clauses?: Array<{
    title: string;
    content: string;
    section?: string;
    page?: number;
    simplified_explanation: string;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    risk_explanation?: string;
    missing_elements?: string[];
    suggested_questions?: string[];
  }>;
  obligations?: Array<{
    who: string;
    must_do: string;
    by_when?: string;
    consequence_if_missed?: string;
    is_conditional?: boolean;
    condition?: string;
  }>;
  important_dates?: Array<{
    date: string;
    event: string;
    consequence: string;
    is_recurring?: boolean;
  }>;
  attention_areas?: Array<{
    title: string;
    description: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    clause_reference?: string;
    why_it_matters: string;
    user_action_recommended: string;
  }>;
  action_plan?: Array<{
    step: number;
    action: string;
    deadline?: string;
    importance: 'high' | 'medium' | 'low';
  }>;
}

export interface DocumentDetail extends DocumentSummary {
  detected_sections?: string[];
  error_message?: string;
  analysis?: AnalysisData;
}

export interface QAResponse {
  question: string;
  answer: string;
  sources: Array<{
    document_id: string;
    document_name: string;
    text: string;
    page?: number;
    section?: string;
    relevance_score?: number;
  }>;
  suggested_followups: string[];
  confidence: number;
  high_risk_flag?: boolean;
  disclaimer: string;
  conversation_id?: string;
}

export interface ComparisonResult {
  doc_a: { id: string; name: string };
  doc_b: { id: string; name: string };
  overall_summary: string;
  key_differences: Array<{
    category: string;
    doc_a_version: string;
    doc_b_version: string;
    change_type: 'added' | 'removed' | 'modified' | 'identical';
    impact_level: 'high' | 'medium' | 'low';
    explanation: string;
  }>;
  risk_comparison: {
    doc_a_risk: string;
    doc_b_risk: string;
    safer_option?: string;
    reasoning: string;
  };
  recommendation: string;
}

const normalizeComparisonResult = (raw: any): ComparisonResult => {
  const keyDifferences = Array.isArray(raw?.differences)
    ? raw.differences.map((diff: any) => ({
        category: diff?.category || 'General',
        doc_a_version: diff?.doc_a_text || 'No text provided',
        doc_b_version: diff?.doc_b_text || 'No text provided',
        change_type: (diff?.difference_type || 'modified') as ComparisonResult['key_differences'][number]['change_type'],
        impact_level: (diff?.impact_level || 'medium') as ComparisonResult['key_differences'][number]['impact_level'],
        explanation: diff?.description || diff?.potential_implication || 'No impact description provided.',
      }))
    : [];

  const overallSummary = Array.isArray(raw?.executive_summary)
    ? raw.executive_summary.join(' ')
    : (raw?.overall_summary || 'No comparison summary available.');

  return {
    doc_a: {
      id: raw?.doc_a_id || '',
      name: raw?.doc_a_name || 'Document A',
    },
    doc_b: {
      id: raw?.doc_b_id || '',
      name: raw?.doc_b_name || 'Document B',
    },
    overall_summary: overallSummary,
    key_differences: keyDifferences,
    risk_comparison: {
      doc_a_risk: raw?.risk_comparison?.doc_a_risk || 'Unknown',
      doc_b_risk: raw?.risk_comparison?.doc_b_risk || 'Unknown',
      safer_option: raw?.risk_comparison?.safer_option,
      reasoning: raw?.risk_comparison?.reasoning || raw?.recommendation || 'No risk comparison available.',
    },
    recommendation: raw?.recommendation || raw?.risk_comparison?.safer_option || 'Review both documents carefully before signing.',
  };
};

export interface LawyerPrepPackage {
  document_summary: string;
  key_concerns_for_lawyer: string[];
  questions_to_ask_lawyer: string[];
  high_risk_clauses_summary: Array<{
    clause_title: string;
    issue: string;
    recommended_negotiation_point: string;
  }>;
  missing_protections: string[];
  suggested_agenda: string[];
  user_notes?: string;
}

export const api = {
  // Upload document
  async uploadDocument(file: File): Promise<{ id: string; filename: string; status: string; message: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers: getHeaders(false),
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  // List documents
  async listDocuments(): Promise<{ documents: DocumentSummary[]; total: number }> {
    const res = await fetch(`${API_BASE}/documents`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  // Get document detail
  async getDocument(id: string): Promise<DocumentDetail> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch document detail');
    return res.json();
  },

  // Ask document Q&A
  async askDocument(documentId: string, question: string, conversationId?: string): Promise<QAResponse> {
    const res = await fetch(`${API_BASE}/documents/${documentId}/ask`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ question, conversation_id: conversationId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to answer question' }));
      throw new Error(err.detail || 'Failed to answer question');
    }
    return res.json();
  },

  // Get suggested questions
  async getSuggestedQuestions(documentId: string): Promise<{ document_id: string; questions: string[] }> {
    const res = await fetch(`${API_BASE}/documents/${documentId}/suggested-questions`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch suggested questions');
    return res.json();
  },

  // Compare 2 documents
  async compareDocuments(docAId: string, docBId: string): Promise<ComparisonResult> {
    const res = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ doc_a_id: docAId, doc_b_id: docBId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Comparison failed' }));
      throw new Error(err.detail || 'Comparison failed');
    }
    const raw = await res.json();
    return normalizeComparisonResult(raw);
  },

  // Generate Lawyer Prep Package
  async generateLawyerPrep(documentId: string, concerns?: string): Promise<LawyerPrepPackage> {
    const res = await fetch(`${API_BASE}/lawyer-prep`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ document_id: documentId, concerns }),
    });
    if (!res.ok) throw new Error('Failed to generate lawyer prep package');
    return res.json();
  },

async generateChecklist(documentId: string): Promise<{ checklist?: Array<{ item: string; why_important?: string }> }> {
    const res = await fetch(`${API_BASE}/lawyer-prep/checklist`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ document_id: documentId }),
    });
    if (!res.ok) throw new Error('Failed to generate checklist');
    return res.json();
  },

  // Delete document
  async deleteDocument(documentId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${documentId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete document');
  },
};
