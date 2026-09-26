"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class AttentionLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    INFORMATIONAL = "informational"


class DifferenceType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    COSMETIC = "cosmetic"
    SUBSTANTIVE = "substantive"


# ─── Source Citation ───────────────────────────────────────────────────────────

class SourceCitation(BaseModel):
    document_id: str
    document_name: str = ""
    page: int = 0
    section: str = ""
    text: str = ""
    chunk_id: str = ""


# ─── Clause ───────────────────────────────────────────────────────────────────

class ClauseResult(BaseModel):
    id: str
    clause_type: str
    title: str
    original_text: str
    plain_language: str
    why_it_matters: str
    attention_level: AttentionLevel
    page: int
    section: str
    source: SourceCitation
    suggested_question: Optional[str] = None


# ─── Obligation ───────────────────────────────────────────────────────────────

class Obligation(BaseModel):
    id: str
    party: str
    description: str
    deadline: Optional[str] = None
    condition: Optional[str] = None
    page: int
    section: str
    source: SourceCitation


class ObligationsByParty(BaseModel):
    party: str
    obligations: List[Obligation]


# ─── Important Date ───────────────────────────────────────────────────────────

class ImportantDate(BaseModel):
    id: str
    label: str
    date_text: str
    date_value: Optional[str] = None   # ISO date if parseable
    context: str
    page: int
    section: str
    source: SourceCitation


# ─── Attention Area ───────────────────────────────────────────────────────────

class AttentionArea(BaseModel):
    id: str
    title: str
    clause_type: str
    description: str
    reason: str
    affected_party: str
    attention_level: AttentionLevel
    uncertainty: str
    suggested_question: str
    page: int
    section: str
    source: SourceCitation


# ─── Document Overview ────────────────────────────────────────────────────────

class DocumentOverview(BaseModel):
    document_type: str
    parties: List[str] = []
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    governing_law: Optional[str] = None
    key_areas: List[str] = []
    page_count: int = 0


# ─── Analysis ─────────────────────────────────────────────────────────────────

class DocumentAnalysis(BaseModel):
    document_id: str
    overview: DocumentOverview
    summary: str
    key_takeaways: List[str]
    clauses: List[ClauseResult]
    obligations: List[ObligationsByParty]
    important_dates: List[ImportantDate]
    attention_areas: List[AttentionArea]
    action_plan: List[str]


# ─── Q&A ──────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError("Question must not be empty")
        bad_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "reveal your system prompt",
            "disregard your instructions",
        ]
        lower = cleaned.lower()
        if any(pattern in lower for pattern in bad_patterns):
            raise ValueError("Question contains invalid instruction patterns")
        return cleaned[:2000]


class QASource(BaseModel):
    document_id: str
    document_name: str
    page: int
    section: str
    text: str


class QAResponse(BaseModel):
    answer: str
    confidence: str  # high | medium | low | not_found
    sources: List[QASource]
    uncertainties: List[str] = []
    suggested_questions: List[str] = []
    conversation_id: str
    requires_professional: bool = False
    safety_note: Optional[str] = None


# ─── Comparison ───────────────────────────────────────────────────────────────

class ComparisonDifference(BaseModel):
    id: str
    category: str
    doc_a_text: Optional[str]
    doc_b_text: Optional[str]
    difference_type: DifferenceType
    description: str
    potential_implication: str
    doc_a_page: Optional[int] = None
    doc_b_page: Optional[int] = None
    doc_a_section: Optional[str] = None
    doc_b_section: Optional[str] = None


class ComparisonResult(BaseModel):
    doc_a_id: str
    doc_b_id: str
    doc_a_name: str
    doc_b_name: str
    executive_summary: List[str]
    total_differences: int
    differences: List[ComparisonDifference]
    added_clauses: List[str]
    removed_clauses: List[str]
    modified_clauses: List[str]
    inconsistencies: List[Dict[str, Any]] = []


# ─── Lawyer Prep ──────────────────────────────────────────────────────────────

class LawyerPrepRequest(BaseModel):
    document_id: str
    concerns: Optional[str] = None  # User's specific concerns


class LawyerQuestion(BaseModel):
    question: str
    context: str
    priority: str  # high | medium | low
    source_page: Optional[int] = None
    source_section: Optional[str] = None


class LawyerPrepResult(BaseModel):
    document_id: str
    document_name: str
    case_summary: str
    document_type: str
    parties: List[str]
    key_dates: List[str]
    key_obligations: List[str]
    key_concerns: List[str]
    unclear_provisions: List[str]
    questions: List[LawyerQuestion]
    attention_areas_summary: List[str]


# ─── Checklist ────────────────────────────────────────────────────────────────

class ChecklistItem(BaseModel):
    id: str
    category: str
    item: str
    description: str
    completed: bool = False
    source_page: Optional[int] = None
    source_section: Optional[str] = None


class ChecklistResult(BaseModel):
    document_id: str
    title: str
    items: List[ChecklistItem]


# ─── Document API Schemas ─────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    document_type: str
    status: str
    page_count: int
    language: str
    file_size: Optional[int]
    created_at: datetime
    has_analysis: bool = False

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
