"""SQLAlchemy models for documents."""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.database import Base


class DocumentStatus(str, enum.Enum):
    UPLOADING = "uploading"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    INDEXING = "indexing"
    READY = "ready"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    EMPLOYMENT_AGREEMENT = "Employment Agreement"
    RENTAL_AGREEMENT = "Rental / Lease Agreement"
    NDA = "Non-Disclosure Agreement"
    VENDOR_AGREEMENT = "Vendor Agreement"
    SERVICE_AGREEMENT = "Service Agreement"
    PRIVACY_POLICY = "Privacy Policy"
    TERMS_OF_SERVICE = "Terms of Service"
    LOAN_AGREEMENT = "Loan Agreement"
    FREELANCE_AGREEMENT = "Freelance Agreement"
    PARTNERSHIP_AGREEMENT = "Partnership Agreement"
    PURCHASE_AGREEMENT = "Purchase Agreement"
    LICENSING_AGREEMENT = "Licensing Agreement"
    INSURANCE_DOCUMENT = "Insurance Document"
    GOVERNMENT_NOTICE = "Government / Legal Notice"
    UNKNOWN = "Unknown"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    document_type = Column(String, default=DocumentType.UNKNOWN)
    language = Column(String, default="en")
    page_count = Column(Integer, default=0)
    status = Column(String, default=DocumentStatus.UPLOADING)
    error_message = Column(Text, nullable=True)
    detected_sections = Column(JSON, default=list)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analysis = relationship("Analysis", back_populates="document", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="document", cascade="all, delete-orphan")
