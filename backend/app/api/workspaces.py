"""Workspaces API for multi-document Q&A."""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.agents.qa_agent import QAAgent
from app.schemas.schemas import AskRequest

router = APIRouter()
qa_agent = QAAgent()


class WorkspaceAskRequest(BaseModel):
    question: str
    document_ids: List[str]
    conversation_id: Optional[str] = None


@router.post("/ask")
async def ask_workspace(
    request: WorkspaceAskRequest,
    db: AsyncSession = Depends(get_db),
    x_session_id: Optional[str] = Header(None),
):
    """Ask a question across multiple documents."""
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="At least one document ID required")

    # Fetch document names
    document_names = {}
    for doc_id in request.document_ids:
        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()
        if doc:
            document_names[doc_id] = doc.original_filename

    answer = await qa_agent.answer(
        question=request.question,
        document_ids=request.document_ids,
        document_names=document_names,
    )

    return answer
