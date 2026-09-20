"""
Comparison Agent: compare two legal documents, identify differences.
"""
import uuid
from typing import Dict, Any, List, Optional
import structlog

from app.agents.llm_provider import get_llm_provider, extract_json_from_response

logger = structlog.get_logger()


class ComparisonAgent:
    """
    Responsible for:
    - Comparing two documents clause by clause
    - Identifying added, removed, and modified clauses
    - Distinguishing cosmetic from potentially substantive changes
    - Detecting inconsistencies
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def compare_documents(
        self,
        doc_a_text: str,
        doc_b_text: str,
        doc_a_id: str,
        doc_b_id: str,
        doc_a_name: str,
        doc_b_name: str,
    ) -> Dict[str, Any]:
        """Compare two documents and return structured differences."""

        # Use reasonable excerpts
        excerpt_a = doc_a_text[:5000]
        excerpt_b = doc_b_text[:5000]

        prompt = f"""Compare these two legal documents and identify meaningful differences.

DOCUMENT A: {doc_a_name}
---BEGIN DOCUMENT A---
{excerpt_a}
---END DOCUMENT A---

DOCUMENT B: {doc_b_name}
---BEGIN DOCUMENT B---
{excerpt_b}
---END DOCUMENT B---

IMPORTANT INSTRUCTIONS:
1. Only identify differences that ACTUALLY EXIST between the two documents.
2. Do NOT invent differences.
3. Classify each difference as:
   - "added": clause/provision appears in Document B but not Document A
   - "removed": clause/provision appears in Document A but not Document B
   - "modified": clause exists in both but with changed content
   - "cosmetic": wording changed but meaning appears unchanged
   - "substantive": meaning, obligation, amount, duration, right, or restriction appears to have changed
4. Do NOT say a change is "better" or "worse" — just describe what changed.
5. Do NOT characterize changes as beneficial or harmful without context.

Respond with JSON:
{{
  "executive_summary": [
    "Payment terms changed from X to Y.",
    "Notice period increased from 30 to 60 days.",
    "New arbitration clause added in Document B."
  ],
  "differences": [
    {{
      "category": "Notice Period",
      "doc_a_text": "Either party may terminate with 30 days written notice.",
      "doc_b_text": "Either party may terminate with 60 days written notice.",
      "difference_type": "substantive",
      "description": "The stated notice period increased from 30 days to 60 days.",
      "potential_implication": "The longer notice period extends the time required before termination can take effect.",
      "doc_a_page": 10,
      "doc_b_page": 11,
      "doc_a_section": "Section 8 - Termination",
      "doc_b_section": "Section 8 - Termination"
    }}
  ],
  "added_clauses": ["Arbitration clause"],
  "removed_clauses": [],
  "modified_clauses": ["Notice period", "Payment terms"],
  "inconsistencies": [
    {{
      "description": "Two documents specify different notice periods: 30 days (Doc A) vs 60 days (Doc B).",
      "doc_a_reference": "Page 10, Section 8",
      "doc_b_reference": "Page 11, Section 8"
    }}
  ]
}}

Identify all meaningful differences. Be precise and factual."""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.1)
            result = extract_json_from_response(response)

            if not result:
                return self._empty_comparison(doc_a_id, doc_b_id, doc_a_name, doc_b_name)

            # Process differences
            diffs = []
            for d in result.get("differences", []):
                diff = {
                    "id": str(uuid.uuid4()),
                    "category": d.get("category", "General"),
                    "doc_a_text": d.get("doc_a_text"),
                    "doc_b_text": d.get("doc_b_text"),
                    "difference_type": d.get("difference_type", "modified"),
                    "description": d.get("description", ""),
                    "potential_implication": d.get("potential_implication", ""),
                    "doc_a_page": d.get("doc_a_page"),
                    "doc_b_page": d.get("doc_b_page"),
                    "doc_a_section": d.get("doc_a_section"),
                    "doc_b_section": d.get("doc_b_section"),
                }
                diffs.append(diff)

            return {
                "doc_a_id": doc_a_id,
                "doc_b_id": doc_b_id,
                "doc_a_name": doc_a_name,
                "doc_b_name": doc_b_name,
                "executive_summary": result.get("executive_summary", []),
                "total_differences": len(diffs),
                "differences": diffs,
                "added_clauses": result.get("added_clauses", []),
                "removed_clauses": result.get("removed_clauses", []),
                "modified_clauses": result.get("modified_clauses", []),
                "inconsistencies": result.get("inconsistencies", []),
            }

        except Exception as e:
            logger.error("Comparison agent failed", error=str(e))
            return self._empty_comparison(doc_a_id, doc_b_id, doc_a_name, doc_b_name)

    def _empty_comparison(
        self, doc_a_id: str, doc_b_id: str, doc_a_name: str, doc_b_name: str
    ) -> Dict[str, Any]:
        return {
            "doc_a_id": doc_a_id,
            "doc_b_id": doc_b_id,
            "doc_a_name": doc_a_name,
            "doc_b_name": doc_b_name,
            "executive_summary": ["Comparison could not be completed. Please try again."],
            "total_differences": 0,
            "differences": [],
            "added_clauses": [],
            "removed_clauses": [],
            "modified_clauses": [],
            "inconsistencies": [],
        }
