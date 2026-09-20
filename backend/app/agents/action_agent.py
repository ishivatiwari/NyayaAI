"""
Action Agent: generate checklists, lawyer prep, and action plans.
"""
import uuid
from typing import Dict, Any, List, Optional
import structlog

from app.agents.llm_provider import get_llm_provider, extract_json_from_response

logger = structlog.get_logger()


class ActionAgent:
    """
    Responsible for:
    - Generating action checklists
    - Lawyer preparation questions
    - Next-step action plans
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def generate_lawyer_prep(
        self,
        document_text: str,
        document_id: str,
        document_type: str,
        document_name: str,
        analysis: Optional[Dict] = None,
        user_concerns: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a comprehensive lawyer preparation package."""

        excerpt = document_text[:7000]
        concerns_str = f"\nUser's specific concerns: {user_concerns}" if user_concerns else ""

        prompt = f"""Create a lawyer preparation package for a user who is reviewing their {document_type}.

DOCUMENT NAME: {document_name}

DOCUMENT CONTENT:
---BEGIN DOCUMENT---
{excerpt}
---END DOCUMENT---
{concerns_str}

IMPORTANT:
1. Only reference what is ACTUALLY in the document.
2. Generate questions that are genuinely helpful for a conversation with a lawyer.
3. Frame everything as informational — not as legal advice.
4. Do not make legal conclusions.

Generate:
1. A case/document summary (2-3 sentences)
2. Key dates mentioned
3. Key obligations for each party
4. Areas of concern worth discussing
5. Unclear provisions that need clarification
6. 8-15 specific questions to ask a lawyer

Respond with JSON:
{{
  "case_summary": "...",
  "parties": ["Party A", "Party B"],
  "key_dates": ["Agreement starts January 1, 2026", "Notice required 30 days before termination"],
  "key_obligations": [
    "Employee must maintain confidentiality (Page 8)",
    "Employer must pay monthly (Page 4)"
  ],
  "key_concerns": [
    "Automatic renewal provision (Page 12)",
    "Broad IP assignment clause (Page 9)"
  ],
  "unclear_provisions": [
    "The scope of 'proprietary information' is not precisely defined"
  ],
  "questions": [
    {{
      "question": "Does the termination clause apply equally to both parties?",
      "context": "The termination section describes the conditions for ending this agreement.",
      "priority": "high",
      "source_page": 10,
      "source_section": "Section 8 - Termination"
    }},
    {{
      "question": "How broad is the confidentiality obligation, and does it extend beyond my role?",
      "context": "The confidentiality section creates ongoing obligations.",
      "priority": "high",
      "source_page": 8,
      "source_section": "Section 6 - Confidentiality"
    }}
  ],
  "attention_areas_summary": [
    "Automatic renewal provision",
    "Non-compete restrictions",
    "IP ownership scope"
  ]
}}"""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.15)
            result = extract_json_from_response(response)

            if not result:
                return self._default_lawyer_prep(document_id, document_name, document_type)

            # Process questions
            questions_raw = result.get("questions", [])
            questions = []
            for q in questions_raw:
                if isinstance(q, str):
                    questions.append({
                        "question": q,
                        "context": "",
                        "priority": "medium",
                        "source_page": None,
                        "source_section": None,
                    })
                elif isinstance(q, dict):
                    questions.append({
                        "question": q.get("question", ""),
                        "context": q.get("context", ""),
                        "priority": q.get("priority", "medium"),
                        "source_page": q.get("source_page"),
                        "source_section": q.get("source_section"),
                    })

            return {
                "document_id": document_id,
                "document_name": document_name,
                "case_summary": result.get("case_summary", ""),
                "document_type": document_type,
                "parties": result.get("parties", []),
                "key_dates": result.get("key_dates", []),
                "key_obligations": result.get("key_obligations", []),
                "key_concerns": result.get("key_concerns", []),
                "unclear_provisions": result.get("unclear_provisions", []),
                "questions": questions,
                "attention_areas_summary": result.get("attention_areas_summary", []),
            }

        except Exception as e:
            logger.error("Action agent (lawyer prep) failed", error=str(e))
            return self._default_lawyer_prep(document_id, document_name, document_type)

    async def generate_checklist(
        self,
        document_text: str,
        document_id: str,
        document_type: str,
        clauses: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Generate a 'Before You Sign' checklist."""

        excerpt = document_text[:5000]

        prompt = f"""Generate a practical "Before You Sign" checklist for someone reviewing this {document_type}.

DOCUMENT CONTENT:
---BEGIN DOCUMENT---
{excerpt}
---END DOCUMENT---

Create a checklist with 10-15 items organized by category.
Focus on what the person should verify, confirm, or understand before signing.
Frame items as tasks, not legal advice.

Respond with JSON:
{{
  "title": "Before You Sign: {document_type} Checklist",
  "items": [
    {{
      "category": "Parties & Identity",
      "item": "Confirm all parties are correctly identified",
      "description": "Verify full legal names and addresses of all parties are accurate",
      "source_page": 1,
      "source_section": "Section 1 - Parties"
    }},
    {{
      "category": "Payment Terms",
      "item": "Verify payment amount and schedule",
      "description": "Confirm the stated compensation/payment terms match your understanding",
      "source_page": 4,
      "source_section": "Section 3 - Compensation"
    }}
  ]
}}"""

        try:
            response = await self.llm.generate(prompt, response_format="json", temperature=0.15)
            result = extract_json_from_response(response)

            items_raw = result.get("items", [])
            items = []
            for item in items_raw:
                items.append({
                    "id": str(uuid.uuid4()),
                    "category": item.get("category", "General"),
                    "item": item.get("item", ""),
                    "description": item.get("description", ""),
                    "completed": False,
                    "source_page": item.get("source_page"),
                    "source_section": item.get("source_section"),
                })

            return {
                "document_id": document_id,
                "title": result.get("title", f"Before You Sign: {document_type} Checklist"),
                "items": items,
            }

        except Exception as e:
            logger.error("Checklist generation failed", error=str(e))
            return {
                "document_id": document_id,
                "title": f"Before You Sign: {document_type} Checklist",
                "items": [],
            }

    async def generate_action_plan(
        self, document_type: str, attention_areas: List[Dict], clauses: List[Dict]
    ) -> List[str]:
        """Generate 'What You May Want To Do Next' action items."""
        actions = [
            "Review this document carefully before signing or agreeing to its terms.",
            "Note any clauses marked as High Attention and ask for clarification if needed.",
            "Confirm all important dates mentioned in the document.",
            "Verify that your understanding of the obligations matches the document language.",
            "Consider consulting a qualified legal professional for clauses you are uncertain about.",
        ]

        # Add document-type-specific actions
        type_lower = document_type.lower()
        if "employment" in type_lower:
            actions.extend([
                "Clarify the scope of any IP assignment or work-for-hire provisions.",
                "Confirm whether any non-compete or non-solicitation restrictions apply in your jurisdiction.",
                "Understand the post-termination obligations before signing.",
            ])
        elif "rental" in type_lower or "lease" in type_lower:
            actions.extend([
                "Confirm the lease term and renewal conditions.",
                "Understand the deposit terms and conditions for return.",
                "Review the maintenance and repair obligations.",
            ])
        elif "nda" in type_lower or "non-disclosure" in type_lower:
            actions.extend([
                "Clarify the definition of 'confidential information' and whether it matches your situation.",
                "Note the duration of the confidentiality obligation.",
            ])

        if attention_areas:
            for area in attention_areas[:3]:
                if area.get("attention_level") == "high":
                    actions.append(f"Review the {area.get('title', 'highlighted')} clause carefully.")

        return actions[:10]

    def _default_lawyer_prep(
        self, document_id: str, document_name: str, document_type: str
    ) -> Dict[str, Any]:
        return {
            "document_id": document_id,
            "document_name": document_name,
            "case_summary": f"This is a {document_type} that has been analyzed by NyayaAI.",
            "document_type": document_type,
            "parties": [],
            "key_dates": [],
            "key_obligations": [],
            "key_concerns": [],
            "unclear_provisions": [],
            "questions": [
                {
                    "question": "Please configure your GOOGLE_API_KEY to generate personalized questions.",
                    "context": "AI analysis requires a valid API key.",
                    "priority": "high",
                    "source_page": None,
                    "source_section": None,
                }
            ],
            "attention_areas_summary": [],
        }
