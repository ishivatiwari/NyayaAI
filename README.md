# ⚖️ NyayaAI

### **Understand. Compare. Navigate.**

> **An AI-powered legal document intelligence platform that makes complex legal information easier to understand, analyze, compare, and navigate.**

NyayaAI is a **GenAI-powered Legal Assistance & Document Intelligence platform** designed to help individuals and organizations understand complex legal documents without requiring them to be experts in legal terminology.

It combines **Generative AI, Retrieval-Augmented Generation (RAG), document intelligence, multi-agent workflows, citation-grounded answers, clause analysis, obligation extraction, contract comparison, and lawyer-preparation tools** into a single platform.

> ⚠️ **Important:** NyayaAI provides legal information and document assistance. It does **not** provide professional legal advice and is not a replacement for a qualified legal professional.

---

## 🚀 Why NyayaAI?

Legal documents can be difficult to navigate because they are often:

* 📄 Long and complex
* ⚖️ Filled with legal terminology
* 🔍 Difficult to search
* 🧩 Hard to interpret in context
* 🔄 Difficult to compare across versions
* ⏰ Full of obligations and deadlines
* ❓ Difficult for non-lawyers to know what questions to ask

NyayaAI aims to bridge this information gap.

Instead of simply asking an AI:

> *"Explain this PDF."*

NyayaAI creates a structured understanding of the document:

```text
Legal Document
      ↓
Document Understanding
      ↓
Clause Detection
      ↓
Obligation Extraction
      ↓
Important Dates
      ↓
Attention Areas
      ↓
Grounded Q&A
      ↓
Document Comparison
      ↓
Actionable Checklist
      ↓
Questions for a Legal Professional
```

---

# ✨ Key Features

## 📄 1. Intelligent Document Analysis

Upload a legal document and NyayaAI automatically analyzes it.

Supported document types can include:

* Employment Agreements
* NDAs
* Rental Agreements
* Vendor Contracts
* Service Agreements
* Privacy Policies
* Terms & Conditions
* Freelance Agreements
* Licensing Agreements
* Other legal documents

The system identifies:

* Document type
* Parties
* Sections
* Clauses
* Obligations
* Dates
* Restrictions
* Important terms
* Areas requiring attention

---

## 🧠 2. Plain-Language Legal Explanations

Legal terminology can be intimidating.

NyayaAI converts complex clauses into understandable language while preserving the original clause.

### Example

**Original Clause**

> "The Employee shall indemnify and hold harmless..."

### NyayaAI

**Simple Explanation**

> This provision may require the employee to cover certain losses or claims arising from specified situations.

The original text remains available so users can verify the explanation.

---

# 🔍 3. Ask Your Document

Users can ask questions using natural language.

### Example

**User**

> What happens if I resign?

**NyayaAI**

> The agreement states that either party may terminate the employment relationship by providing 60 days' written notice, subject to the qualifications described in the termination section.

**Source:** Employment Agreement — Section 9

The system uses **RAG** to retrieve relevant sections before generating the answer.

---

# 📚 4. Citation-Grounded Answers

One of NyayaAI's core principles is:

> **Every important answer should be traceable back to evidence.**

Instead of producing unsupported AI-generated answers, NyayaAI provides:

* Document
* Page
* Section
* Relevant text
* Source reference

Example:

```text
Answer
──────
The agreement requires 60 days' written notice.

Source
──────
Employment Agreement
Page 4
Section 9 — Termination
```

If the information cannot be found:

> **"I could not find this information in the provided document."**

NyayaAI should never fabricate citations or document content.

---

# 📋 5. Obligation Extraction

NyayaAI identifies obligations and maps them to the relevant party.

### Example

| Party    | Obligation               | Timing                    | Source     |
| -------- | ------------------------ | ------------------------- | ---------- |
| Employee | Maintain confidentiality | During & after employment | Section 5  |
| Employee | Return company property  | Upon termination          | Section 10 |
| Employer | Pay salary               | Payroll schedule          | Section 3  |

This transforms a long contract into an actionable view.

---

# ⏰ 6. Important Dates & Deadlines

NyayaAI automatically identifies:

* Effective dates
* Expiration dates
* Notice periods
* Renewal periods
* Payment deadlines
* Termination windows
* Other specified dates

Example:

```text
01 Jan 2026
Agreement Begins
       │
       ▼
Annual Review
       │
       ▼
30-Day Notice Window
       │
       ▼
Agreement Continues / Terminates
```

The system must never invent dates that are not present in the source document.

---

# ⚠️ 7. Areas Requiring Attention

NyayaAI highlights clauses that may deserve closer review.

Instead of saying:

> ❌ "This clause is illegal."

NyayaAI uses evidence-based language such as:

> ⚠️ **Attention Area**
>
> The agreement contains a 12-month post-termination non-solicitation provision.
>
> **Why it may matter:** This provision creates a restriction following termination.
>
> **Source:** Section 11
>
> **Question to consider:** What is the scope and applicability of this restriction under the relevant law?

This helps users understand the document without pretending to make a legal determination.

---

# 🔄 8. Contract Comparison

Upload two versions of a document and identify changes.

### Example

**Original**

> Notice period: 30 days

**Revised**

> Notice period: 60 days

NyayaAI produces:

```text
WHAT CHANGED?

Notice Period

OLD
30 days

NEW
60 days

Difference
The stated notice period increased from
30 days to 60 days.

Source
Document A — Section 8
Document B — Section 9
```

The system can identify:

* Added clauses
* Removed clauses
* Modified clauses
* Changed dates
* Changed amounts
* Changed obligations
* Changed restrictions
* Potential inconsistencies

---

# 🔀 9. Multi-Document Intelligence

NyayaAI can organize documents into a workspace.

Example:

```text
Employment Review
│
├── Offer Letter
├── Employment Agreement
├── Company Policy
└── Revised Agreement
```

Users can ask questions across documents.

### Example

> Does the revised agreement change anything mentioned in the offer letter?

NyayaAI retrieves evidence from the relevant documents and explains the differences.

---

# 🧩 10. Potential Inconsistency Detection

NyayaAI can identify potential conflicts between documents.

Example:

```text
Document A
Notice Period → 30 Days

Document B
Notice Period → 60 Days
```

NyayaAI:

> ⚠️ **Potential Inconsistency**
>
> The two documents appear to specify different notice periods.
>
> This may require clarification.

The system does not automatically determine which document legally controls.

---

# 👨‍⚖️ 11. Prepare for a Lawyer

One of NyayaAI's key features.

Instead of attempting to replace legal professionals, NyayaAI helps users **prepare for a more productive conversation with one**.

It generates:

### Document Summary

* Parties
* Purpose
* Key dates
* Main obligations

### Areas to Review

* Termination
* Confidentiality
* IP
* Restrictions
* Dispute resolution

### Questions for a Lawyer

For example:

> 1. What are the consequences of the stated termination period?
>
> 2. How broadly does the confidentiality obligation apply?
>
> 3. What intellectual property is covered by this provision?
>
> 4. What restrictions continue after termination?
>
> 5. Which jurisdiction governs potential disputes?

---

# ✅ 12. Smart Checklist

Generate a document-specific checklist.

### Before Signing

```text
☐ Verify parties
☐ Confirm compensation/payment terms
☐ Review duration
☐ Review termination requirements
☐ Check renewal provisions
☐ Understand confidentiality obligations
☐ Review intellectual-property provisions
☐ Review restrictions
☐ Check dispute-resolution provisions
☐ Confirm governing jurisdiction
☐ Identify questions for a legal professional
```

The checklist is dynamically generated from the document.

---

# 🤖 AI Agent Architecture

NyayaAI uses an orchestrated AI architecture.

```text
                         ┌──────────────────┐
                         │      USER        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Web Interface  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   API Gateway    │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │     AI Orchestrator       │
                    └─────────────┬─────────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
      │  Document   │      │    Q&A      │      │ Comparison  │
      │    Agent    │      │    Agent    │      │    Agent    │
      └─────────────┘      └─────────────┘      └─────────────┘
             │                    │                    │
             ▼                    ▼                    ▼
      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
      │   Clause    │      │    RAG      │      │ Difference  │
      │   Agent     │      │   Engine    │      │  Analysis   │
      └─────────────┘      └─────────────┘      └─────────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Safety & Grounding│
                         │    Guardrails     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Cited AI Response│
                         └──────────────────┘
```

---

# 🧠 RAG Pipeline

NyayaAI uses Retrieval-Augmented Generation to ground responses in document evidence.

```text
                 Legal Document
                       │
                       ▼
                Text Extraction
                       │
                       ▼
                    OCR
                 (if needed)
                       │
                       ▼
              Document Structure
                       │
                       ▼
                   Chunking
                       │
                       ▼
                Metadata Layer
                       │
                       ▼
                  Embeddings
                       │
                       ▼
                Vector Store
                       │
                       ▼
             Semantic Retrieval
                       │
                       ▼
                  Reranking
                       │
                       ▼
                     LLM
                       │
                       ▼
              Citation Generation
                       │
                       ▼
                Grounded Answer
```

---

# 🏗️ Technology Stack

## Frontend

* React
* TypeScript
* Vite / Next.js
* Tailwind CSS

## Backend

* Python
* FastAPI
* Pydantic

## AI / GenAI

* Large Language Model
* Retrieval-Augmented Generation
* Embeddings
* Agent orchestration
* Structured model outputs

## Data

* PostgreSQL / relational database
* Vector database
* Object storage

## Document Processing

* PDF parsing
* DOCX extraction
* OCR
* Text chunking
* Metadata extraction

## Infrastructure

* Docker
* REST APIs
* Cloud deployment

> The AI/LLM layer is designed to be provider-agnostic where practical.

---

# 🔐 Security & Privacy

Legal documents can contain highly sensitive information.

NyayaAI is designed with privacy and security in mind.

### Security principles

* 🔒 Secure API communication
* 🔑 Secrets stored through environment variables
* 🚫 API keys never exposed to the frontend
* 🛡️ File validation
* 📦 Controlled document storage
* 🔐 User/document isolation
* 🧹 Secure deletion workflow
* 📝 Minimal sensitive-data logging
* 🧪 Prompt-injection protection

Uploaded documents are treated as **untrusted data** and cannot override system instructions.

---

# 🛡️ AI Safety & Legal Guardrails

NyayaAI is intentionally designed as a **legal information assistant**, not an autonomous legal decision-maker.

The system must:

* Avoid claiming to be a lawyer
* Avoid guaranteeing legal outcomes
* Avoid fabricating laws or cases
* Avoid fabricated citations
* Communicate uncertainty
* Ask for jurisdiction when necessary
* Separate document facts from general legal information
* Escalate high-stakes situations to qualified professionals
* Encourage professional legal review when appropriate

### Core principle

> **Don't make legal decisions for people. Make legal information easier for people to understand.**

---

# 🧪 Example Demo

### Step 1 — Upload

Upload an employment agreement.

### Step 2 — Analyze

NyayaAI generates:

```text
Document Type
Employment Agreement

Clauses
24

Obligations
12

Important Dates
5

Attention Areas
6
```

### Step 3 — Ask

> What happens if I resign?

### Step 4 — Evidence

NyayaAI retrieves the relevant termination clause.

### Step 5 — Explore

> Which obligations continue after termination?

### Step 6 — Compare

Upload a revised contract.

### Step 7 — Difference

```text
Notice Period

30 Days → 60 Days
```

### Step 8 — Prepare

Click:

> **Prepare for Lawyer**

NyayaAI generates a document summary and relevant questions to discuss with a legal professional.

---

# 📁 Project Structure

```text
NyayaAI/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── types/
│   │
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── rag/
│   │   ├── services/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── security/
│   │   └── utils/
│   │
│   └── requirements.txt
│
├── sample_documents/
│
├── tests/
│
├── docker/
│
├── .env.example
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

# ⚙️ Getting Started

## Prerequisites

Make sure you have:

* Python 3.11+
* Node.js 20+
* npm
* Docker
* Git

---

## 1. Clone the repository

```bash
git clone https://github.com/<your-username>/NyayaAI.git
cd NyayaAI
```

---

## 2. Configure environment variables

Create a `.env` file based on:

```bash
cp .env.example .env
```

Configure the required:

```env
LLM_PROVIDER=
LLM_MODEL=
API_KEY=

DATABASE_URL=
VECTOR_DB_URL=
STORAGE_URL=
```

Never commit your `.env` file.

---

# 🐳 Run with Docker

```bash
docker compose up --build
```

After startup:

```text
Frontend → http://localhost:3000
Backend  → http://localhost:8000
API Docs → http://localhost:8000/docs
```

Adjust ports according to the implementation.

---

# 🧪 Testing

Run backend tests:

```bash
pytest
```

Run frontend tests:

```bash
npm test
```

The test suite should cover:

* Document ingestion
* Text extraction
* Chunking
* Retrieval
* Citation generation
* Clause detection
* Obligation extraction
* Document comparison
* Safety guardrails
* Prompt injection resistance

---

# 🗺️ Roadmap

## Phase 1 — MVP

* [x] Product architecture
* [ ] Document upload
* [ ] Text extraction
* [ ] Document summarization
* [ ] RAG Q&A
* [ ] Citation generation

## Phase 2 — Document Intelligence

* [ ] Clause extraction
* [ ] Obligation mapping
* [ ] Important-date extraction
* [ ] Attention areas
* [ ] Document classification

## Phase 3 — Advanced Intelligence

* [ ] Contract comparison
* [ ] Version diff
* [ ] Cross-document analysis
* [ ] Inconsistency detection
* [ ] Lawyer preparation
* [ ] Smart checklists

## Phase 4 — Advanced Capabilities

* [ ] OCR
* [ ] PII detection/redaction
* [ ] Multilingual support
* [ ] Voice interaction
* [ ] Authoritative legal-source retrieval
* [ ] Advanced document visualization

---

# 💡 Future Vision

NyayaAI can evolve into a broader **Legal Information Intelligence Platform** supporting:

```text
                 NYAYAAI
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
  Documents      Research     Preparation
       │            │            │
       ▼            ▼            ▼
   Contracts      Laws        Checklists
   Policies      Cases       Questions
   Agreements    Rules       Summaries
       │            │            │
       └────────────┼────────────┘
                    ▼
            Better Legal Access
```

The long-term goal is not to replace legal professionals.

It is to help people become **better informed, better prepared, and better able to navigate legal information.**

---

# 🌟 What Makes NyayaAI Different?

NyayaAI goes beyond a traditional legal chatbot.

| Traditional Approach     | NyayaAI                                      |
| ------------------------ | -------------------------------------------- |
| Chat with a PDF          | Document intelligence                        |
| Generic answers          | Citation-grounded answers                    |
| Summaries                | Structured insights                          |
| Keyword search           | Semantic retrieval                           |
| One document             | Multi-document workspaces                    |
| Basic Q&A                | Clause + obligation intelligence             |
| Manual comparison        | AI-assisted contract comparison              |
| AI gives answers         | AI shows evidence                            |
| Legal advice positioning | Legal information + professional preparation |

### The core differentiator:

> **From Legal Document → Understanding → Evidence → Action Preparation**

---

# ⚖️ Disclaimer

NyayaAI is an AI-powered legal information and document-analysis prototype.

It does not provide legal advice, establish an attorney-client relationship, guarantee legal outcomes, or replace a qualified lawyer or other appropriate legal professional.

Users should independently verify important information and seek professional legal advice for matters involving significant legal, financial, personal, or regulatory consequences.

---

# 🤝 Contributing

Contributions are welcome.

```bash
# Fork the repository

# Create a feature branch
git checkout -b feature/your-feature

# Commit changes
git commit -m "Add your feature"

# Push branch
git push origin feature/your-feature

# Open a Pull Request
```

Please ensure that contributions:

* Do not introduce security vulnerabilities
* Do not expose API keys or sensitive data
* Maintain AI safety principles
* Include appropriate tests
* Follow the existing project structure

---

# 📜 License

This project is intended for educational, research, and prototype purposes.

Add the appropriate open-source license to this repository based on your intended usage.

---

# 👨‍💻 Built With

**NyayaAI**

### *Understand. Compare. Navigate.*

Built with ❤️ using **Generative AI, RAG, Agentic AI, and Document Intelligence**.

---

> **Legal complexity shouldn't become an information barrier.**
>
> **NyayaAI helps turn complex legal information into understandable, evidence-grounded insights — while keeping humans and qualified legal professionals in the loop.**
