"""
Document Agent: classify, summarize, and structure documents.
"""
import json
import uuid
from typing import Dict, Any, List
import structlog

from app.agents.llm_provider import get_llm_provider, extract_json_from_response

logger = structlog.get_logger()


class DocumentAgent:
    """
    Responsible for:
    - Document classification
    - Summary generation
    - Key takeaways
    - Document overview (parties, dates, governing law)
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def classify_and_summarize(
        self, document_text: str, filename: str, document_id: str
    ) -> Dict[str, Any]:
        """
        Classify document type and generate a plain-language summary.
        Returns structured JSON.
        """
        # Truncate for safety (use first ~6000 chars for classification)
        excerpt = document_text[:6000]

        prompt = f"""Analyze the following legal document excerpt and provide a structured analysis.

DOCUMENT FILENAME: {filename}

DOCUMENT CONTENT (excerpt):
---BEGIN DOCUMENT---
{excerpt}
---END DOCUMENT---

IMPORTANT: Base your analysis ONLY on the document content above. Do not invent information.

Respond with a JSON object with the following structure:
{{
  "document_type": "One of: Employment Agreement, Rental / Lease Agreement, Non-Disclosure Agreement, Vendor Agreement, Service Agreement, Privacy Policy, Terms of Service, Loan Agreement, Freelance Agreement, Partnership Agreement, Purchase Agreement, Licensing Agreement, Insurance Document, Government / Legal Notice, Unknown",
  "confidence": "high | medium | low",
  "parties": ["Party 1 name/role", "Party 2 name/role"],
  "effective_date": "date as found in document, or null",
  "expiration_date": "date as found in document, or null", 
  "governing_law": "jurisdiction as stated in document, or null",
  "key_areas": ["area1", "area2"],
  "summary": "A 2-3 sentence plain-language summary of what this document is and its purpose.",
  "key_takeaways": [
    "Plain language point 1",
    "Plain language point 2",
    "Plain language point 3",
    "Plain language point 4",
    "Plain language point 5"
  ]
}}

For key_takeaways:
- Write 5-8 points
- Use plain English, not legal jargon
- Be factual — only state what the document says
- Do not make legal conclusions
- Do not invent information not in the document"""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.1)
            result = extract_json_from_response(response)

            # Validate and set defaults
            if not result:
                result = self._default_result(filename)

            result.setdefault("document_type", "Unknown")
            result.setdefault("confidence", "low")
            result.setdefault("parties", [])
            result.setdefault("effective_date", None)
            result.setdefault("expiration_date", None)
            result.setdefault("governing_law", None)
            result.setdefault("key_areas", [])
            result.setdefault("summary", "Document analysis in progress.")
            result.setdefault("key_takeaways", [])

            return result

        except Exception as e:
            logger.error("Document agent failed", error=str(e))
            return self._default_result(filename)

    def _default_result(self, filename: str) -> Dict[str, Any]:
        return {
            "document_type": "Unknown",
            "confidence": "low",
            "parties": [],
            "effective_date": None,
            "expiration_date": None,
            "governing_law": None,
            "key_areas": [],
            "summary": f"Document '{filename}' has been received and processed.",
            "key_takeaways": [
                "The document has been processed.",
                "Add your API key for full AI analysis.",
            ],
        }
