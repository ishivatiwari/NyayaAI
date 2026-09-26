"""
Document processor: extract text, detect structure, chunk, prepare for embedding.
Supports PDF, DOCX, and TXT files.
"""
import os
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import structlog

from app.config import settings

logger = structlog.get_logger()


class DocumentChunk:
    """A chunk of document text with metadata."""

    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        text: str,
        page: int,
        section: str,
        section_index: int,
        chunk_index: int,
        metadata: Dict[str, Any] = None,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.text = text
        self.page = page
        self.section = section
        self.section_index = section_index
        self.chunk_index = chunk_index
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "page": self.page,
            "section": self.section,
            "section_index": self.section_index,
            "chunk_index": self.chunk_index,
            **self.metadata,
        }


class DocumentProcessor:
    """
    Processes uploaded documents:
    - Validates file type and size
    - Extracts text with page numbers
    - Detects section headings
    - Splits into chunks
    - Preserves metadata
    """

    HEADING_PATTERNS = [
        r"^(ARTICLE|SECTION|CLAUSE|SCHEDULE|EXHIBIT|APPENDIX)\s+[\dIVXLC]+",
        r"^\d+\.\s+[A-Z][A-Za-z\s]+$",
        r"^\d+\.\d+\s+[A-Z][A-Za-z\s]+$",
        r"^[A-Z][A-Z\s]{3,}$",   # ALL CAPS headings
    ]

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        """Return a safe filename that cannot escape the upload directory."""
        name = Path((filename or "document.txt").strip()).name
        name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
        name = name.strip("._ ") or "document.txt"
        ext = Path(name).suffix.lower()
        if ext and ext.lstrip(".") not in settings.ALLOWED_EXTENSIONS:
            name = f"{Path(name).stem or 'document'}{ext or '.txt'}"
        return name

    def validate_file(self, filename: str, file_size: int, mime_type: Optional[str] = None) -> Tuple[bool, str]:
        """Validate file type, MIME type, and size."""
        safe_filename = self.sanitize_filename(filename)
        ext = Path(safe_filename).suffix.lower().lstrip(".")
        if ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type: .{ext}. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"

        allowed_mimetypes = {
            "pdf": {"application/pdf"},
            "docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
            "txt": {"text/plain", "application/octet-stream"},
        }
        if mime_type and ext in allowed_mimetypes and mime_type.lower() not in allowed_mimetypes[ext]:
            return False, f"MIME type mismatch for .{ext}. Received: {mime_type}"

        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size <= 0:
            return False, "Uploaded file is empty."
        if file_size > max_bytes:
            return False, f"File too large: {file_size // 1024 // 1024}MB. Maximum: {settings.MAX_FILE_SIZE_MB}MB"
        return True, ""

    def _sanitize_text(self, text: str) -> str:
        """Strip control characters and log suspicious prompt-injection patterns."""
        cleaned = text.replace("\x00", "").replace("\r", "\n")
        lowered = cleaned.lower()
        if any(pattern in lowered for pattern in [
            "ignore previous instructions",
            "ignore all previous",
            "system prompt",
            "reveal your prompt",
            "disregard your instructions",
        ]):
            logger.warning("Suspicious document text detected", marker="possible_prompt_injection")
        return cleaned.strip()

    def extract_text(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Extract text from document.
        Returns: {pages: [{page_num, text}], sections: [...], full_text: str, page_count: int}
        """
        ext = Path(filename).suffix.lower()
        try:
            if ext == ".pdf":
                return self._extract_pdf(file_path)
            elif ext == ".docx":
                return self._extract_docx(file_path)
            elif ext == ".txt":
                return self._extract_txt(file_path)
            else:
                raise ValueError(f"Unsupported format: {ext}")
        except Exception as e:
            logger.error("Text extraction failed", error=str(e), file=filename)
            raise

    def _extract_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF using PyMuPDF."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

        pages = []
        doc = fitz.open(file_path)
        full_text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = self._sanitize_text(page.get_text("text"))
            pages.append({"page_num": page_num + 1, "text": text})
            full_text += f"\n\n--- PAGE {page_num + 1} ---\n\n{text}"

        doc.close()
        full_text = self._sanitize_text(full_text)
        sections = self._detect_sections(full_text)

        return {
            "pages": pages,
            "sections": sections,
            "full_text": full_text,
            "page_count": len(pages),
        }

    def _extract_docx(self, file_path: str) -> Dict[str, Any]:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx not installed. Run: pip install python-docx")

        doc = Document(file_path)
        pages = []
        full_text = ""
        current_page = 1
        current_text = ""
        sections_found = []

        for para in doc.paragraphs:
            text = self._sanitize_text(para.text.strip())
            if not text:
                continue

            # Detect headings
            if para.style.name.startswith("Heading") or self._is_heading(text):
                sections_found.append(text)

            current_text += text + "\n"
            full_text += text + "\n"

        # Simulate pages (DOCX doesn't have easy page breaks)
        words = full_text.split()
        words_per_page = 400
        for i in range(0, len(words), words_per_page):
            page_text = " ".join(words[i : i + words_per_page])
            pages.append({"page_num": current_page, "text": page_text})
            current_page += 1

        sections = self._detect_sections(full_text)
        return {
            "pages": pages,
            "sections": sections,
            "full_text": full_text,
            "page_count": len(pages),
        }

    def _extract_txt(self, file_path: str) -> Dict[str, Any]:
        """Extract text from plain TXT file."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            full_text = self._sanitize_text(f.read())

        lines = full_text.split("\n")
        words_per_page = 400
        words = full_text.split()
        pages = []
        current_page = 1
        for i in range(0, len(words), words_per_page):
            page_text = " ".join(words[i : i + words_per_page])
            pages.append({"page_num": current_page, "text": page_text})
            current_page += 1

        if not pages:
            pages = [{"page_num": 1, "text": full_text}]

        sections = self._detect_sections(full_text)
        return {
            "pages": pages,
            "sections": sections,
            "full_text": full_text,
            "page_count": len(pages),
        }

    def _is_heading(self, text: str) -> bool:
        """Check if a line looks like a section heading."""
        if len(text) > 120:
            return False
        for pattern in self.HEADING_PATTERNS:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                return True
        return False

    def _detect_sections(self, full_text: str) -> List[str]:
        """Detect section headings in document text."""
        sections = []
        for line in full_text.split("\n"):
            line = line.strip()
            if line and self._is_heading(line):
                sections.append(line)
        return sections[:50]  # Cap at 50 sections

    def chunk_document(
        self, document_id: str, pages: List[Dict], sections: List[str]
    ) -> List[DocumentChunk]:
        """
        Split document into overlapping chunks with metadata.
        Uses semantic boundaries (paragraphs, sections) where possible.
        """
        chunks = []
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        chunk_index = 0

        # Build a flat list of (page_num, paragraph) tuples
        paragraphs = []
        for page_data in pages:
            page_num = page_data["page_num"]
            text = page_data.get("text", "")
            # Split by double newline (paragraphs)
            for para in re.split(r"\n\s*\n", text):
                para = para.strip()
                if len(para) > 30:  # Skip very short fragments
                    paragraphs.append((page_num, para))

        # Group paragraphs into chunks of ~chunk_size words with overlap
        current_text = ""
        current_page = 1
        current_section = "Document"
        buffer = []

        for i, (page_num, para) in enumerate(paragraphs):
            # Detect section change
            if self._is_heading(para):
                current_section = para[:100]

            buffer.append((page_num, para))
            current_text += " " + para

            # Check if chunk is full
            if len(current_text.split()) >= chunk_size:
                chunk_text = current_text.strip()
                chunk = DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    text=chunk_text,
                    page=buffer[0][0] if buffer else 1,
                    section=current_section,
                    section_index=len(chunks),
                    chunk_index=chunk_index,
                )
                chunks.append(chunk)
                chunk_index += 1

                # Keep overlap: last N words
                overlap_words = current_text.split()[-overlap:]
                current_text = " ".join(overlap_words)
                # Keep last few paragraphs for overlap
                buffer = buffer[max(0, len(buffer) - 2) :]

        # Add remaining text as final chunk
        if current_text.strip() and len(current_text.strip().split()) > 10:
            chunk = DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                text=current_text.strip(),
                page=buffer[0][0] if buffer else 1,
                section=current_section,
                section_index=len(chunks),
                chunk_index=chunk_index,
            )
            chunks.append(chunk)

        logger.info(
            "Document chunked",
            document_id=document_id,
            total_chunks=len(chunks),
            pages=len(pages),
        )
        return chunks
