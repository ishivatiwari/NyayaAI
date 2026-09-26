"""
Document Analysis Service: orchestrates all agents to produce complete document analysis.
"""
import os
import re
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

    def _build_offline_analysis(self, full_text: str, filename: str, document_id: str) -> dict:
        """Create a fast local fallback analysis when no LLM API key is configured."""
        text = (full_text or "").strip()
        lower_text = text.lower()

        document_type = "Unknown"
        if any(term in lower_text for term in ["employment agreement", "employee", "employer", "termination"]):
            document_type = "Employment Agreement"
        elif any(term in lower_text for term in ["lease", "tenant", "landlord", "rental"]):
            document_type = "Rental / Lease Agreement"
        elif any(term in lower_text for term in ["non-disclosure", "confidential information", "nda"]):
            document_type = "Non-Disclosure Agreement"
        elif any(term in lower_text for term in ["vendor", "supplier", "services provided"]):
            document_type = "Vendor Agreement"
        elif any(term in lower_text for term in ["terms of service", "acceptable use", "privacy policy"]):
            document_type = "Terms of Service"

        parties = []
        for pattern in [
            r"between\s+(.+?)\s+and\s+(.+?)(?:\n|\.)",
            r"by\s+(.+?)\s+and\s+(.+?)(?:\n|\.)",
        ]:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                parties.extend([p.strip() for p in match.groups() if p and p.strip()][:2])
        if not parties:
            if "employee" in lower_text and "company" in lower_text:
                parties = ["Employee", "Company"]
            elif "tenant" in lower_text and "landlord" in lower_text:
                parties = ["Tenant", "Landlord"]

        effective_match = re.search(
            r"(?:effective|as of|commencing on)\s+(?:date\s+)?([A-Z][a-z]+\s+\d{1,2},\s+\d{4}|\d{1,2}/\d{1,2}/\d{2,4})",
            text,
            re.IGNORECASE,
        )
        effective_date = effective_match.group(1).strip() if effective_match else None

        key_areas = []
        if "confidential" in lower_text:
            key_areas.append("Confidentiality")
        if "termination" in lower_text:
            key_areas.append("Termination")
        if "notice" in lower_text:
            key_areas.append("Notice requirements")
        if "payment" in lower_text:
            key_areas.append("Payment terms")
        if "governing law" in lower_text:
            key_areas.append("Governing law")
        if not key_areas:
            key_areas = ["Core commercial terms", "Compliance obligations", "Operational requirements"]

        key_takeaways = []
        key_takeaways.append(f"This is a {document_type.lower()} document based on the available text.")
        if parties:
            key_takeaways.append(f"The document references the parties: {', '.join(parties[:2])}.")
        if effective_date:
            key_takeaways.append(f"The document references an effective date of {effective_date}.")
        key_takeaways.append("Key business, notice, or confidentiality obligations are present in the text.")
        key_takeaways.append("For production-grade legal analysis, configure a real LLM provider in the environment settings.")

        summary = (
            f"This document appears to be a {document_type.lower()} containing the core commercial, operational, "
            "and compliance terms between the identified parties. The text describes the agreement’s purpose, "
            "key obligations, and any timing or notice requirements documented in the file."
        )

        return {
            "document_type": document_type,
            "confidence": "medium",
            "parties": parties,
            "effective_date": effective_date,
            "expiration_date": None,
            "governing_law": None,
            "key_areas": key_areas[:5],
            "summary": summary,
            "key_takeaways": key_takeaways[:5],
            "document_id": document_id,
            "filename": filename,
        }

    async def save_upload(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file path."""
        upload_dir = Path(settings.UPLOAD_DIR).resolve()
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_name = self.processor.sanitize_filename(filename) or f"document-{uuid.uuid4()}.txt"
        candidate = upload_dir / safe_name
        if candidate.exists() or not candidate.resolve().is_relative_to(upload_dir):
            suffix = Path(safe_name).suffix.lower() or ".txt"
            stem = Path(safe_name).stem or "document"
            safe_name = f"{stem}-{uuid.uuid4()}{suffix}"
            candidate = upload_dir / safe_name

        # Fail closed if the resolved path escapes the upload directory.
        resolved = candidate.resolve()
        if not resolved.is_relative_to(upload_dir):
            raise ValueError("Invalid upload path")

        with open(resolved, "wb") as f:
            f.write(file_content)

        logger.info("Uploaded file saved securely", filename=safe_name, size=len(file_content))
        return str(resolved)

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

            has_external_llm = bool(settings.GOOGLE_API_KEY or settings.OPENAI_API_KEY)
            if not has_external_llm or settings.DEMO_MODE:
                logger.info(
                    "Using offline fallback analysis for document",
                    document_id=document_id,
                    has_google_key=bool(settings.GOOGLE_API_KEY),
                    has_openai_key=bool(settings.OPENAI_API_KEY),
                    demo_mode=settings.DEMO_MODE,
                )
                doc_result = self._build_offline_analysis(full_text, doc.original_filename, document_id)
                clauses = [
                    {
                        "title": "Core commercial terms",
                        "content": full_text[:1000],
                        "section": "Document Overview",
                        "page": 1,
                        "simplified_explanation": "The document sets out the parties, rights, responsibilities, and key commercial terms described in the text.",
                        "risk_level": "medium",
                        "risk_explanation": "Review the exact wording for any confidential, termination, or payment obligations.",
                        "missing_elements": [],
                        "suggested_questions": [
                            "What are the key obligations in this agreement?",
                            "What are the notice and termination requirements?",
                        ],
                    }
                ]
                obligations = [
                    {
                        "who": ", ".join(doc_result.get("parties", [])[:2]) or "Document parties",
                        "must_do": "Review and comply with the core duties and responsibilities described in the document.",
                        "by_when": doc_result.get("effective_date"),
                        "consequence_if_missed": "Missed obligations may trigger contractual or operational risk depending on the exact wording.",
                        "is_conditional": False,
                        "condition": None,
                    }
                ]
                dates = []
                if doc_result.get("effective_date"):
                    dates.append({
                        "date": doc_result["effective_date"],
                        "event": "Agreement effective date",
                        "consequence": "This date may mark the beginning of the parties' obligations.",
                        "is_recurring": False,
                    })
                attention_areas = [
                    {
                        "title": "Operational and legal review",
                        "description": "The document should be reviewed for dates, obligations, and specific wording before relying on it.",
                        "severity": "medium",
                        "clause_reference": "Document Overview",
                        "why_it_matters": "Reviewing key terms early reduces the risk of missing obligations or notice deadlines.",
                        "user_action_recommended": "Read the agreement carefully and confirm the key dates and duties with a qualified professional if needed.",
                    }
                ]
                action_plan = [
                    {"step": 1, "action": "Review the core terms and obligations in the agreement.", "deadline": None, "importance": "high"},
                    {"step": 2, "action": "Confirm any notice, termination, and payment obligations in the document.", "deadline": None, "importance": "high"},
                    {"step": 3, "action": "Use the document text as the source for final legal review and negotiation decisions.", "deadline": None, "importance": "medium"},
                ]
            else:
                # Run document classification + summary
                doc_result = await self.document_agent.classify_and_summarize(
                    full_text, doc.original_filename, document_id
                )

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

            doc.document_type = doc_result.get("document_type", "Unknown")
            await db.commit()

            # Step 3: Index chunks in vector store
            await self._update_status(doc, DocumentStatus.INDEXING, db)
            chunks = self.processor.chunk_document(document_id, pages, sections)
            try:
                await self.vector_store.add_chunks(chunks)
            except Exception as e:
                logger.warning(
                    "Vector indexing failed; continuing with document ready state",
                    document_id=document_id,
                    error=str(e),
                )

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
            resolved_path = Path(file_path).resolve()
            upload_dir = Path(settings.UPLOAD_DIR).resolve()
            if resolved_path.is_relative_to(upload_dir) and resolved_path.exists():
                resolved_path.unlink()
                logger.info("File deleted", path=str(resolved_path))
        except Exception as e:
            logger.error("File deletion failed", error=str(e))

        await self.vector_store.delete_document(document_id)
