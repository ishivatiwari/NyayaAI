"""
Attention Agent: identify clauses requiring closer review.
Uses a careful, non-alarmist approach with three levels.
"""
import uuid
from typing import Dict, Any, List
import structlog

from app.agents.llm_provider import get_llm_provider, extract_json_from_response

logger = structlog.get_logger()


class AttentionAgent:
    """
    Responsible for:
    - Identifying clauses that merit closer review
    - Categorizing by attention level (not "risk level")
    - Generating suggested questions for each
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def analyze_attention_areas(
        self,
        document_text: str,
        document_id: str,
        document_type: str,
        clauses: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Identify clauses/areas requiring attention."""

        excerpt = document_text[:8000]

        prompt = f"""Analyze this {document_type} and identify clauses or provisions that a user should review carefully.

DOCUMENT CONTENT:
---BEGIN DOCUMENT---
{excerpt}
---END DOCUMENT---

IMPORTANT INSTRUCTIONS:
1. Only identify clauses that ACTUALLY APPEAR in this document.
2. Do NOT label anything as "illegal", "unfair", "invalid", or "unenforceable" — you don't have enough legal and jurisdictional context.
3. Use ONLY these three attention levels:
   - "high": Clause contains substantial obligations, restrictions, financial exposure, broad rights, automatic provisions, or terms the user should clearly understand before agreeing.
   - "medium": Clause contains meaningful obligations or limitations that deserve review.
   - "informational": Clause is primarily descriptive or administrative.
4. Frame concerns as questions or observations, NOT legal conclusions.
5. Generate a helpful question the user could ask a lawyer about this clause.

Respond with JSON:
{{
  "attention_areas": [
    {{
      "title": "Automatic Renewal",
      "clause_type": "Renewal",
      "description": "The agreement appears to renew automatically unless notice is provided within a specified period.",
      "reason": "Missing the notice window may extend the agreement beyond your intended term.",
      "affected_party": "Both parties",
      "attention_level": "high",
      "uncertainty": "The exact notice window should be confirmed with the full document.",
      "suggested_question": "What happens if I miss the notice period for renewal?",
      "page": 12,
      "section": "Section 9 - Renewal"
    }}
  ]
}}

Identify 4-8 notable areas. Focus on what a non-lawyer would most benefit from understanding."""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.1)
            result = extract_json_from_response(response)

            areas_raw = result.get("attention_areas", [])
            areas = []

            for a in areas_raw:
                area = {
                    "id": str(uuid.uuid4()),
                    "title": a.get("title", "Provision"),
                    "clause_type": a.get("clause_type", "General"),
                    "description": a.get("description", ""),
                    "reason": a.get("reason", ""),
                    "affected_party": a.get("affected_party", "Both parties"),
                    "attention_level": a.get("attention_level", "informational"),
                    "uncertainty": a.get("uncertainty", ""),
                    "suggested_question": a.get("suggested_question", ""),
                    "page": a.get("page", 1),
                    "section": a.get("section", ""),
                    "source": {
                        "document_id": document_id,
                        "document_name": "",
                        "page": a.get("page", 1),
                        "section": a.get("section", ""),
                        "text": a.get("description", ""),
                    },
                }
                areas.append(area)

            return areas

        except Exception as e:
            logger.error("Attention agent failed", error=str(e))
            return []
