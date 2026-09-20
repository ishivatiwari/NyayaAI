"""
Q&A Agent: RAG-grounded question answering with citations.
This is the core conversational AI with hallucination prevention.
"""
import uuid
from typing import Dict, Any, List, Optional
import structlog

from app.agents.llm_provider import get_llm_provider, extract_json_from_response
from app.rag.vector_store import get_vector_store

logger = structlog.get_logger()

HIGH_RISK_KEYWORDS = [
    "criminal", "arrested", "charged", "eviction", "evicted", "deported",
    "custody", "divorce", "lawsuit", "sued", "court order", "bankruptcy",
    "foreclosure", "immigration", "visa", "domestic violence", "restraining order",
    "regulatory enforcement", "urgent", "deadline today", "hearing tomorrow"
]


class QAAgent:
    """
    Responsible for:
    - RAG-grounded Q&A from uploaded documents
    - Citation-first answering
    - Follow-up question suggestions
    - High-risk situation detection
    - Prompt injection defense
    """

    def __init__(self):
        self.llm = get_llm_provider()
        self.vector_store = get_vector_store()

    def _is_high_risk(self, question: str) -> bool:
        """Detect high-risk legal situations requiring stronger caution."""
        q_lower = question.lower()
        return any(kw in q_lower for kw in HIGH_RISK_KEYWORDS)

    def _contains_injection(self, text: str) -> bool:
        """Basic prompt injection detection."""
        injection_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "disregard your instructions",
            "forget your instructions",
            "you are now",
            "new instructions:",
            "system prompt:",
            "reveal your prompt",
            "show me your system",
        ]
        text_lower = text.lower()
        return any(p in text_lower for p in injection_patterns)

    async def answer(
        self,
        question: str,
        document_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        document_names: Optional[Dict[str, str]] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG with citations.
        Returns structured response with sources.
        """
        conversation_id = str(uuid.uuid4())

        if self._contains_injection(question):
            return self._injection_response(conversation_id)

        is_high_risk = self._is_high_risk(question)

        # Retrieve relevant chunks
        retrieved = await self.vector_store.query(
            query_text=question,
            document_id=document_id,
            document_ids=document_ids,
            n_results=8,
        )

        if not retrieved:
            return self._no_document_response(question, conversation_id)

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved[:6]):
            doc_name = ""
            if document_names:
                doc_name = document_names.get(chunk["document_id"], "")
            context_parts.append(
                f"[SOURCE {i+1}] Document: {doc_name} | Page {chunk['page']} | "
                f"Section: {chunk['section']}\n{chunk['text']}"
            )

        context = "\n\n".join(context_parts)

        history_str = ""
        if conversation_history:
            recent = conversation_history[-4:]
            for msg in recent:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_str += f"{role}: {msg['content'][:200]}\n"

        prompt = f"""A user is asking a question about their legal document(s).

RETRIEVED DOCUMENT SECTIONS (use ONLY these as your source):
---BEGIN RETRIEVED CONTENT---
{context}
---END RETRIEVED CONTENT---

{f"RECENT CONVERSATION:{chr(10)}{history_str}" if history_str else ""}

USER QUESTION: {question}

CRITICAL INSTRUCTIONS:
1. Answer ONLY based on the retrieved document sections above.
2. If the answer is not in the retrieved content, say "I could not find this information in the provided document."
3. NEVER invent clauses, dates, obligations, or legal conclusions not supported by the sources.
4. Always cite the source (Document name, Page number, Section).
5. Communicate uncertainty where interpretation is not clear.
6. You are providing document analysis, NOT legal advice.

Respond with JSON:
{{
  "answer": "Your plain-language answer here. Cite specific pages/sections inline.",
  "confidence": 0.9,
  "sources": [
    {{
      "document_id": "...",
      "document_name": "...",
      "page": 1,
      "section": "Section 1",
      "text": "Verbatim quote..."
    }}
  ],
  "suggested_questions": [
    "Follow-up question 1?",
    "Follow-up question 2?"
  ]
}}"""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.15)
            result = extract_json_from_response(response)

            if not result or not result.get("answer"):
                result = {
                    "answer": f"Based on the retrieved document sections:\n\n{retrieved[0]['text'][:300]}...",
                    "confidence": 0.8,
                    "sources": [],
                    "suggested_questions": [],
                }

            # Normalize confidence to numeric float (0.0 to 1.0)
            conf = result.get("confidence", 0.8)
            if isinstance(conf, str):
                conf_map = {"high": 0.95, "medium": 0.75, "low": 0.45, "not_found": 0.0}
                conf = conf_map.get(conf.lower(), 0.8)
            result["confidence"] = float(conf)

            # Enrich sources with document names
            sources = result.get("sources", [])
            if not sources and retrieved:
                for chunk in retrieved[:3]:
                    sources.append({
                        "document_id": chunk["document_id"],
                        "document_name": document_names.get(chunk["document_id"], "") if document_names else "",
                        "page": chunk["page"],
                        "section": chunk["section"],
                        "text": chunk["text"][:200],
                    })

            for src in sources:
                if document_names and src.get("document_id"):
                    src["document_name"] = document_names.get(
                        src["document_id"], src.get("document_name", "")
                    )

            result["sources"] = sources
            result["conversation_id"] = conversation_id
            result["requires_professional"] = is_high_risk

            if is_high_risk:
                result["safety_note"] = (
                    "⚠️ This situation may have significant legal consequences. "
                    "The information above is general and should be reviewed with a "
                    "qualified legal professional before taking action."
                )

            return result

        except Exception as e:
            logger.error("Q&A agent failed, using direct grounded fallback", error=str(e))
            snippets = []
            sources = []
            for chunk in retrieved[:3]:
                doc_n = document_names.get(chunk["document_id"], "Document") if document_names else "Document"
                snippets.append(f"• **{doc_n} (Page {chunk['page']})**: \"{chunk['text'][:250]}...\"")
                sources.append({
                    "document_id": chunk["document_id"],
                    "document_name": doc_n,
                    "page": chunk["page"],
                    "section": chunk["section"],
                    "text": chunk["text"][:200],
                })

            fallback_answer = (
                f"Here are the relevant passages retrieved from your document:\n\n"
                + "\n\n".join(snippets)
                + "\n\n*(Note: Displaying cited document passages directly)*"
            )

            return {
                "answer": fallback_answer,
                "confidence": 0.85,
                "sources": sources,
                "suggested_questions": [],
                "conversation_id": conversation_id,
                "requires_professional": is_high_risk,
            }

    def _no_document_response(self, question: str, conv_id: str) -> Dict[str, Any]:
        return {
            "answer": (
                "No document content was found to answer your question. "
                "Please upload a document first, or ensure the document has been processed."
            ),
            "confidence": 0.0,
            "sources": [],
            "suggested_questions": [],
            "conversation_id": conv_id,
            "requires_professional": False,
        }

    def _injection_response(self, conv_id: str) -> Dict[str, Any]:
        return {
            "answer": (
                "Your question appears to contain instructions to modify system behavior. "
                "For security, I can only answer questions about your legal documents."
            ),
            "confidence": 0.0,
            "sources": [],
            "suggested_questions": [],
            "conversation_id": conv_id,
            "requires_professional": False,
        }
