"""Lawyer Prep API."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.analysis import Analysis
from app.services.document_processor import DocumentProcessor
from app.agents.action_agent import ActionAgent

router = APIRouter()
processor = DocumentProcessor()
action_agent = ActionAgent()


class LawyerPrepRequest(BaseModel):
    document_id: str
    concerns: Optional[str] = None


@router.post("")
async def generate_lawyer_prep(
    request: LawyerPrepRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a lawyer preparation package for a document."""
    result = await db.execute(select(Document).where(Document.id == request.document_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != DocumentStatus.READY:
        raise HTTPException(status_code=400, detail="Document is still processing.")

    extraction = processor.extract_text(doc.file_path, doc.original_filename)
    
    prep = await action_agent.generate_lawyer_prep(
        document_text=extraction["full_text"],
        document_id=doc.id,
        document_type=doc.document_type or "Legal Document",
        document_name=doc.original_filename,
        user_concerns=request.concerns,
    )

    return prep


@router.post("/checklist")
async def generate_checklist(
    request: LawyerPrepRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a 'Before You Sign' checklist."""
    result = await db.execute(select(Document).where(Document.id == request.document_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    extraction = processor.extract_text(doc.file_path, doc.original_filename)

    checklist = await action_agent.generate_checklist(
        document_text=extraction["full_text"],
        document_id=doc.id,
        document_type=doc.document_type or "Legal Document",
    )

    return checklist
