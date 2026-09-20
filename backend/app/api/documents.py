"""
Documents API: upload, manage, analyze, and query legal documents.
"""
import uuid
import asyncio
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import structlog

from app.database import get_db, AsyncSessionLocal
from app.models.document import Document, DocumentStatus
from app.models.analysis import Analysis
from app.models.conversation import Conversation
from app.services.document_processor import DocumentProcessor
from app.services.analysis_service import DocumentAnalysisService
from app.agents.qa_agent import QAAgent
from app.config import settings
from app.schemas.schemas import AskRequest, DocumentResponse

logger = structlog.get_logger()
router = APIRouter()

processor = DocumentProcessor()
analysis_service = DocumentAnalysisService()
qa_agent = QAAgent()


def get_session_id(x_session_id: Optional[str] = Header(None)) -> str:
    """Extract or generate session ID from header."""
    return x_session_id or str(uuid.uuid4())


async def _run_analysis(document_id: str):
    """Background task wrapper for document analysis using a fresh session."""
    async with AsyncSessionLocal() as db:
        try:
            await analysis_service.process_document(document_id, db)
        except Exception as e:
            logger.error("Background analysis failed", document_id=document_id, error=str(e))
            try:
                result = await db.execute(select(Document).where(Document.id == document_id))
                doc = result.scalar_one_or_none()
                if doc:
                    doc.status = DocumentStatus.FAILED
                    doc.error_message = str(e)
                    await db.commit()
            except Exception as commit_err:
                logger.error("Failed to set document status to FAILED", error=str(commit_err))


# ─── Upload ───────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    session_id: str = Depends(get_session_id),
):
    """Upload a legal document for processing and analysis."""

    # Validate file
    content = await file.read()
    valid, error = processor.validate_file(file.filename or "file.txt", len(content))
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    # Save file
    try:
        file_path = await analysis_service.save_upload(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # Create document record
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        session_id=session_id,
        filename=Path(file_path).name,
        original_filename=file.filename or "document",
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        status=DocumentStatus.UPLOADING,
    )
    db.add(doc)
    await db.commit()

    # Trigger async analysis with document_id (fresh session created inside _run_analysis)
    background_tasks.add_task(_run_analysis, doc_id)

    return {
        "id": doc_id,
        "filename": file.filename,
        "status": DocumentStatus.EXTRACTING,
        "message": "Document received. Analysis starting...",
    }


# ─── List Documents ───────────────────────────────────────────────────────────

@router.get("")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    session_id: str = Depends(get_session_id),
):
    """List all documents for this session."""
    result = await db.execute(
        select(Document)
        .where(Document.session_id == session_id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    doc_list = []
    for doc in docs:
        analysis_result = await db.execute(
            select(Analysis).where(Analysis.document_id == doc.id)
        )
        has_analysis = analysis_result.scalar_one_or_none() is not None

        doc_list.append({
            "id": doc.id,
            "filename": doc.original_filename,
            "document_type": doc.document_type,
            "status": doc.status,
            "page_count": doc.page_count,
            "language": doc.language,
            "file_size": doc.file_size,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "has_analysis": has_analysis,
        })

    return {"documents": doc_list, "total": len(doc_list)}


# ─── Get Document ─────────────────────────────────────────────────────────────

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get document details and analysis."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    analysis_result = await db.execute(
        select(Analysis).where(Analysis.document_id == document_id)
    )
    analysis = analysis_result.scalar_one_or_none()

    response = {
        "id": doc.id,
        "filename": doc.original_filename,
        "document_type": doc.document_type,
        "status": doc.status,
        "page_count": doc.page_count,
        "language": doc.language,
        "file_size": doc.file_size,
        "detected_sections": doc.detected_sections or [],
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "error_message": doc.error_message,
        "has_analysis": analysis is not None,
    }

    if analysis:
        response["analysis"] = {
            "overview": analysis.document_overview,
            "summary": analysis.summary,
            "key_takeaways": analysis.key_takeaways,
            "clauses": analysis.clauses,
            "obligations": analysis.obligations,
            "important_dates": analysis.important_dates,
            "attention_areas": analysis.attention_areas,
            "action_plan": analysis.action_plan,
        }

    return response


# ─── Get Clauses ──────────────────────────────────────────────────────────────

@router.get("/{document_id}/clauses")
async def get_clauses(document_id: str, db: AsyncSession = Depends(get_db)):
    """Get extracted clauses for a document."""
    analysis_result = await db.execute(
        select(Analysis).where(Analysis.document_id == document_id)
    )
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return {"document_id": document_id, "clauses": analysis.clauses or []}


# ─── Get Obligations ──────────────────────────────────────────────────────────

@router.get("/{document_id}/obligations")
async def get_obligations(document_id: str, db: AsyncSession = Depends(get_db)):
    """Get extracted obligations for a document."""
    analysis_result = await db.execute(
        select(Analysis).where(Analysis.document_id == document_id)
    )
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return {"document_id": document_id, "obligations": analysis.obligations or []}


# ─── Get Timeline ─────────────────────────────────────────────────────────────

@router.get("/{document_id}/timeline")
async def get_timeline(document_id: str, db: AsyncSession = Depends(get_db)):
    """Get important dates / timeline for a document."""
    analysis_result = await db.execute(
        select(Analysis).where(Analysis.document_id == document_id)
    )
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return {"document_id": document_id, "dates": analysis.important_dates or []}


# ─── Ask Document ─────────────────────────────────────────────────────────────

@router.post("/{document_id}/ask")
async def ask_document(
    document_id: str,
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
    session_id: str = Depends(get_session_id),
):
    """Ask a question about a specific document using RAG."""

    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != DocumentStatus.READY:
        raise HTTPException(
            status_code=400,
            detail=f"Document is not ready (status: {doc.status}). Please wait for processing to complete."
        )

    conversation_history = []
    if request.conversation_id:
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conv = conv_result.scalar_one_or_none()
        if conv:
            conversation_history = conv.messages or []

    answer = await qa_agent.answer(
        question=request.question,
        document_id=document_id,
        document_names={document_id: doc.original_filename},
        conversation_history=conversation_history,
    )

    new_messages = conversation_history + [
        {"role": "user", "content": request.question},
        {
            "role": "assistant",
            "content": answer["answer"],
            "sources": answer.get("sources", []),
        },
    ]

    conv_id = request.conversation_id
    if conv_id:
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == conv_id)
        )
        conv = conv_result.scalar_one_or_none()
        if conv:
            conv.messages = new_messages
    else:
        conv_id = str(uuid.uuid4())
        conv = Conversation(
            id=conv_id,
            document_id=document_id,
            session_id=session_id,
            messages=new_messages,
        )
        db.add(conv)

    await db.commit()
    answer["conversation_id"] = conv_id

    return answer


# ─── Delete Document ──────────────────────────────────────────────────────────

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Securely delete a document and all associated data."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete physical files and Chroma vector store embeddings
    try:
        await analysis_service.delete_document_files(doc.file_path, document_id)
    except Exception as e:
        logger.warning("Error deleting document files/vectors", error=str(e))

    # Delete child ORM records explicitly (analyses and conversations)
    await db.execute(delete(Analysis).where(Analysis.document_id == document_id))
    await db.execute(delete(Conversation).where(Conversation.document_id == document_id))

    # Delete document record
    await db.delete(doc)
    await db.commit()

    return {"message": "Document deleted successfully", "id": document_id}


# ─── Suggested Questions ──────────────────────────────────────────────────────

@router.get("/{document_id}/suggested-questions")
async def get_suggested_questions(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get suggested questions based on document type."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_type = (doc.document_type or "").lower()

    base_questions = [
        "What are my main obligations?",
        "When does this agreement expire?",
        "What are the payment terms?",
        "What happens if there is a dispute?",
        "Which jurisdiction applies?",
        "What should I clarify before signing?",
    ]

    if "employment" in doc_type:
        specific = [
            "What happens if I resign?",
            "Which obligations continue after termination?",
            "How much notice is required for termination?",
            "Are there automatic renewal provisions?",
            "What restrictions apply after I leave?",
            "Does the IP clause cover work done outside working hours?",
        ]
    elif "rental" in doc_type or "lease" in doc_type:
        specific = [
            "What are the lease renewal conditions?",
            "What are the deposit return conditions?",
            "Who is responsible for repairs?",
            "What are the termination requirements?",
            "What are the restrictions on the property?",
        ]
    elif "nda" in doc_type or "non-disclosure" in doc_type:
        specific = [
            "What information is considered confidential?",
            "How long does the confidentiality obligation last?",
            "Are there any exceptions to confidentiality?",
            "What happens if confidentiality is breached?",
        ]
    else:
        specific = [
            "What are the termination conditions?",
            "Are there any automatic renewal provisions?",
            "What are the notice requirements?",
        ]

    return {
        "document_id": document_id,
        "questions": specific[:5] + base_questions[:4],
    }
