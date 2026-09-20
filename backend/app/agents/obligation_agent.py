"""
Obligation Agent: extract party obligations, deadlines, and conditions.
"""
import uuid
from typing import Dict, Any, List
import structlog

from app.agents.llm_provider import get_llm_provider, extract_json_from_response

logger = structlog.get_logger()


class ObligationAgent:
    """
    Responsible for:
    - Extracting obligations per party
    - Identifying deadlines and conditions
    - Linking each obligation to its source
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def extract_obligations(
        self,
        document_text: str,
        document_id: str,
        parties: List[str],
        document_type: str,
    ) -> List[Dict[str, Any]]:
        """Extract obligations for each party."""

        excerpt = document_text[:8000]
        parties_str = ", ".join(parties) if parties else "the parties"

        prompt = f"""Analyze this {document_type} and extract the obligations of each party.

PARTIES: {parties_str}

DOCUMENT CONTENT:
---BEGIN DOCUMENT---
{excerpt}
---END DOCUMENT---

IMPORTANT: Only extract obligations that ACTUALLY APPEAR in this document.
Do NOT invent obligations. If a deadline is not specified, say "Not specified in document."

An obligation is something a party MUST DO or MUST NOT DO under this agreement.

For each obligation found, provide:
- party: the party who has the obligation (use actual party names or roles from the document)
- description: clear description of the obligation
- deadline: the timeframe or deadline (or "Not specified in document")
- condition: any condition that triggers this obligation (optional)
- page: approximate page number
- section: section name/number

Respond with JSON:
{{
  "obligations": [
    {{
      "party": "Employee",
      "description": "Maintain confidentiality of company information",
      "deadline": "During and after employment",
      "condition": "Applies to all proprietary information",
      "page": 8,
      "section": "Section 6 - Confidentiality"
    }},
    {{
      "party": "Employer",
      "description": "Pay agreed monthly salary",
      "deadline": "Monthly",
      "condition": null,
      "page": 4,
      "section": "Section 3 - Compensation"
    }}
  ]
}}

Extract all significant obligations. Focus on what each party MUST do or not do."""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.1)
            result = extract_json_from_response(response)

            obligations_raw = result.get("obligations", [])
            
            # Group by party
            by_party: Dict[str, List] = {}
            for o in obligations_raw:
                party = o.get("party", "Unknown")
                if party not in by_party:
                    by_party[party] = []
                
                obligation = {
                    "id": str(uuid.uuid4()),
                    "party": party,
                    "description": o.get("description", ""),
                    "deadline": o.get("deadline", "Not specified in document"),
                    "condition": o.get("condition"),
                    "page": o.get("page", 1),
                    "section": o.get("section", ""),
                    "source": {
                        "document_id": document_id,
                        "document_name": "",
                        "page": o.get("page", 1),
                        "section": o.get("section", ""),
                        "text": o.get("description", ""),
                    },
                }
                by_party[party].append(obligation)

            # Convert to list of {party, obligations}
            result_list = [
                {"party": party, "obligations": obs}
                for party, obs in by_party.items()
            ]

            return result_list

        except Exception as e:
            logger.error("Obligation agent failed", error=str(e))
            return []

    async def extract_important_dates(
        self, document_text: str, document_id: str
    ) -> List[Dict[str, Any]]:
        """Extract important dates and deadlines."""

        excerpt = document_text[:6000]

        prompt = f"""Extract all important dates and deadlines from this legal document.

DOCUMENT CONTENT:
---BEGIN DOCUMENT---
{excerpt}
---END DOCUMENT---

IMPORTANT: Only extract dates that ACTUALLY APPEAR in the document.
If a date is not specified, say "Not specified in document" — do NOT invent dates.

Types to look for:
- Effective/start dates
- Expiration/end dates
- Notice periods (e.g., "30 days written notice")
- Payment deadlines
- Renewal dates/windows
- Response deadlines
- Review periods
- Termination windows

Respond with JSON:
{{
  "dates": [
    {{
      "label": "Agreement Start Date",
      "date_text": "1 January 2026",
      "context": "The agreement commences on 1 January 2026",
      "page": 1,
      "section": "Section 1 - Term"
    }},
    {{
      "label": "Notice Period for Termination",
      "date_text": "30 days",
      "context": "Either party must provide 30 days written notice before termination",
      "page": 10,
      "section": "Section 8 - Termination"
    }}
  ]
}}"""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.1)
            result = extract_json_from_response(response)

            dates_raw = result.get("dates", [])
            dates = []

            for d in dates_raw:
                date_item = {
                    "id": str(uuid.uuid4()),
                    "label": d.get("label", "Important Date"),
                    "date_text": d.get("date_text", ""),
                    "date_value": None,
                    "context": d.get("context", ""),
                    "page": d.get("page", 1),
                    "section": d.get("section", ""),
                    "source": {
                        "document_id": document_id,
                        "document_name": "",
                        "page": d.get("page", 1),
                        "section": d.get("section", ""),
                        "text": d.get("context", ""),
                    },
                }
                dates.append(date_item)

            return dates

        except Exception as e:
            logger.error("Date extraction failed", error=str(e))
            return []
