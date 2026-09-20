"""Compare API: compare two legal documents."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.services.document_processor import DocumentProcessor
from app.agents.comparison_agent import ComparisonAgent

logger = structlog.get_logger()
router = APIRouter()

processor = DocumentProcessor()
comparison_agent = ComparisonAgent()


class CompareRequest(BaseModel):
    doc_a_id: str
    doc_b_id: str


@router.post("")
async def compare_documents(
    request: CompareRequest,
    db: AsyncSession = Depends(get_db),
):
    """Compare two legal documents and return structured differences."""

    # Fetch both documents
    result_a = await db.execute(select(Document).where(Document.id == request.doc_a_id))
    doc_a = result_a.scalar_one_or_none()

    result_b = await db.execute(select(Document).where(Document.id == request.doc_b_id))
    doc_b = result_b.scalar_one_or_none()

    if not doc_a:
        raise HTTPException(status_code=404, detail=f"Document A not found: {request.doc_a_id}")
    if not doc_b:
        raise HTTPException(status_code=404, detail=f"Document B not found: {request.doc_b_id}")

    # Check status
    for doc, label in [(doc_a, "A"), (doc_b, "B")]:
        if doc.status == DocumentStatus.FAILED:
            raise HTTPException(status_code=400, detail=f"Document {label} failed processing.")

    # Extract text from both
    try:
        extraction_a = processor.extract_text(doc_a.file_path, doc_a.original_filename)
        extraction_b = processor.extract_text(doc_b.file_path, doc_b.original_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    # Compare
    result = await comparison_agent.compare_documents(
        doc_a_text=extraction_a["full_text"],
        doc_b_text=extraction_b["full_text"],
        doc_a_id=doc_a.id,
        doc_b_id=doc_b.id,
        doc_a_name=doc_a.original_filename,
        doc_b_name=doc_b.original_filename,
    )

    return result
