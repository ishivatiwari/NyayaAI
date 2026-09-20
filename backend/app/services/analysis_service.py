"""
Document Analysis Service: orchestrates all agents to produce complete document analysis.
"""
import os
import uuid
import shutil
import asyncio
from pathlib import Path
from typing import Optional
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.document import Document, DocumentStatus
from app.models.analysis import Analysis
from app.services.document_processor import DocumentProcessor
from app.rag.vector_store import get_vector_store
from app.agents.document_agent import DocumentAgent
from app.agents.clause_agent import ClauseAgent
from app.agents.obligation_agent import ObligationAgent
from app.agents.attention_agent import AttentionAgent
from app.agents.action_agent import ActionAgent

logger = structlog.get_logger()


class DocumentAnalysisService:
    """
    Orchestrates the full document analysis pipeline:
    1. Extract text
    2. Chunk + embed + index
    3. Run all agents
    4. Store results
    """

    def __init__(self):
        self.processor = DocumentProcessor()
        self.vector_store = get_vector_store()
        self.document_agent = DocumentAgent()
        self.clause_agent = ClauseAgent()
        self.obligation_agent = ObligationAgent()
        self.attention_agent = AttentionAgent()
        self.action_agent = ActionAgent()

    async def save_upload(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file path."""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate safe filename
        ext = Path(filename).suffix.lower()
        safe_name = f"{uuid.uuid4()}{ext}"
        file_path = upload_dir / safe_name

        with open(file_path, "wb") as f:
            f.write(file_content)

        return str(file_path)

    async def process_document(self, document_id: str, db: AsyncSession) -> None:
        """
        Full async document processing pipeline.
        Updates document status at each step.
        """
        try:
            # Fetch document
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            doc = result.scalar_one_or_none()
            if not doc:
                logger.error("Document not found", document_id=document_id)
                return

            logger.info("Starting document processing", document_id=document_id, filename=doc.original_filename)

            # Step 1: Extract text
            await self._update_status(doc, DocumentStatus.EXTRACTING, db)
            extraction = self.processor.extract_text(doc.file_path, doc.original_filename)
            full_text = extraction["full_text"]
            pages = extraction["pages"]
            sections = extraction["sections"]

            # Update page count
            doc.page_count = extraction["page_count"]
            doc.detected_sections = sections[:20]
            await db.commit()

            # Step 2: Analyze with AI agents (parallel where possible)
            await self._update_status(doc, DocumentStatus.ANALYZING, db)

            # Run document classification + summary
            doc_result = await self.document_agent.classify_and_summarize(
                full_text, doc.original_filename, document_id
            )

            doc.document_type = doc_result.get("document_type", "Unknown")
            await db.commit()

            # Run clause, obligation, date extraction in parallel
            clauses_task = self.clause_agent.extract_clauses(
                full_text, document_id, doc.document_type
            )
            obligations_task = self.obligation_agent.extract_obligations(
                full_text, document_id, doc_result.get("parties", []), doc.document_type
            )
            dates_task = self.obligation_agent.extract_important_dates(
                full_text, document_id
            )
            attention_task = self.attention_agent.analyze_attention_areas(
                full_text, document_id, doc.document_type, []
            )

            clauses, obligations, dates, attention_areas = await asyncio.gather(
                clauses_task, obligations_task, dates_task, attention_task
            )

            # Generate action plan
            action_plan = await self.action_agent.generate_action_plan(
                doc.document_type, attention_areas, clauses
            )

            # Step 3: Index chunks in vector store
            await self._update_status(doc, DocumentStatus.INDEXING, db)
            chunks = self.processor.chunk_document(document_id, pages, sections)
            await self.vector_store.add_chunks(chunks)

            # Step 4: Store analysis results
            analysis = Analysis(
                id=str(uuid.uuid4()),
                document_id=document_id,
                summary=doc_result.get("summary", ""),
                key_takeaways=doc_result.get("key_takeaways", []),
                document_overview={
                    "document_type": doc_result.get("document_type", "Unknown"),
                    "parties": doc_result.get("parties", []),
                    "effective_date": doc_result.get("effective_date"),
                    "expiration_date": doc_result.get("expiration_date"),
                    "governing_law": doc_result.get("governing_law"),
                    "key_areas": doc_result.get("key_areas", []),
                    "page_count": extraction["page_count"],
                },
                clauses=clauses,
                obligations=obligations,
                important_dates=dates,
                attention_areas=attention_areas,
                action_plan=action_plan,
            )
            db.add(analysis)

            # Mark ready
            await self._update_status(doc, DocumentStatus.READY, db)
            await db.commit()

            logger.info(
                "Document processing complete",
                document_id=document_id,
                clauses=len(clauses),
                obligations=len(obligations),
                dates=len(dates),
                attention=len(attention_areas),
            )

        except Exception as e:
            logger.error("Document processing failed", document_id=document_id, error=str(e))
            try:
                result = await db.execute(
                    select(Document).where(Document.id == document_id)
                )
                doc = result.scalar_one_or_none()
                if doc:
                    doc.status = DocumentStatus.FAILED
                    doc.error_message = str(e)[:500]
                    await db.commit()
            except Exception:
                pass

    async def _update_status(
        self, doc: Document, status: DocumentStatus, db: AsyncSession
    ) -> None:
        doc.status = status
        await db.commit()
        logger.info("Document status updated", document_id=doc.id, status=status)

    async def delete_document_files(self, file_path: str, document_id: str) -> None:
        """Securely delete document files and vector store entries."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info("File deleted", path=file_path)
        except Exception as e:
            logger.error("File deletion failed", error=str(e))

        await self.vector_store.delete_document(document_id)
