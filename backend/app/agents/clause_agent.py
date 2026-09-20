"""
Clause Agent: identify, categorize, and explain legal clauses.
"""
import uuid
from typing import Dict, Any, List
import structlog

from app.agents.llm_provider import get_llm_provider, extract_json_from_response

logger = structlog.get_logger()

CLAUSE_TYPES = [
    "Parties", "Definitions", "Payment", "Compensation", "Fees",
    "Term", "Duration", "Renewal", "Termination", "Notice Period",
    "Confidentiality", "Privacy", "Intellectual Property", "Licensing",
    "Liability", "Limitation of Liability", "Indemnification", "Warranties",
    "Representations", "Dispute Resolution", "Arbitration", "Governing Law",
    "Jurisdiction", "Non-compete", "Non-solicitation", "Exclusivity",
    "Force Majeure", "Data Protection", "Security", "Compliance",
    "Penalties", "Automatic Renewal", "Restrictions", "Deadlines",
    "Obligations", "Assignment", "Severability", "Entire Agreement",
    "Amendment", "Waiver", "Notices", "Counterparts"
]


class ClauseAgent:
    """
    Responsible for:
    - Identifying important clauses
    - Categorizing clause types
    - Plain-language explanation
    - Attention level classification
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def extract_clauses(
        self, document_text: str, document_id: str, document_type: str
    ) -> List[Dict[str, Any]]:
        """Extract and categorize all important clauses."""

        # Use first ~8000 chars for clause extraction
        excerpt = document_text[:8000]

        prompt = f"""Analyze this {document_type} and identify its important clauses.

DOCUMENT CONTENT:
---BEGIN DOCUMENT---
{excerpt}
---END DOCUMENT---

IMPORTANT: Only extract clauses that ACTUALLY APPEAR in the document above.
Do NOT invent clauses, obligations, or language that is not present.

For each important clause found, provide:
- The exact clause type from this list: {', '.join(CLAUSE_TYPES[:20])} (or use closest match)
- A short title
- The original text (verbatim quote from document, max 300 chars)
- A plain-language explanation
- Why it matters to the reader
- Attention level: "high" (substantial obligations/restrictions/financial exposure), "medium" (meaningful but less critical), or "informational"
- Approximate page number if discernible, otherwise 1
- Section name if discernible

Respond with JSON:
{{
  "clauses": [
    {{
      "clause_type": "Termination",
      "title": "Termination Rights",
      "original_text": "Either party may terminate this Agreement upon 30 days written notice...",
      "plain_language": "Either party can end this agreement by giving 30 days notice in writing.",
      "why_it_matters": "This defines how and when the agreement can be ended by either party.",
      "attention_level": "high",
      "page": 10,
      "section": "Section 8 - Termination",
      "suggested_question": "What happens if the notice period is missed?"
    }}
  ]
}}

Extract up to 15 of the most important clauses. Focus on what a non-lawyer would most need to understand."""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.1)
            result = extract_json_from_response(response)

            clauses_raw = result.get("clauses", [])
            clauses = []

            for i, c in enumerate(clauses_raw):
                clause = {
                    "id": str(uuid.uuid4()),
                    "clause_type": c.get("clause_type", "General"),
                    "title": c.get("title", "Clause"),
                    "original_text": c.get("original_text", ""),
                    "plain_language": c.get("plain_language", ""),
                    "why_it_matters": c.get("why_it_matters", ""),
                    "attention_level": c.get("attention_level", "informational"),
                    "page": c.get("page", 1),
                    "section": c.get("section", ""),
                    "suggested_question": c.get("suggested_question", ""),
                    "source": {
                        "document_id": document_id,
                        "document_name": "",
                        "page": c.get("page", 1),
                        "section": c.get("section", ""),
                        "text": c.get("original_text", "")[:200],
                    },
                }
                clauses.append(clause)

            return clauses

        except Exception as e:
            logger.error("Clause agent failed", error=str(e))
            return []
