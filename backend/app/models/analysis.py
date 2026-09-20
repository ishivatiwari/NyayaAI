"""SQLAlchemy models for document analysis results."""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, unique=True)
    
    # Overview
    summary = Column(Text, nullable=True)
    key_takeaways = Column(JSON, default=list)     # List[str]
    document_overview = Column(JSON, default=dict)  # parties, dates, etc.
    
    # Clauses
    clauses = Column(JSON, default=list)            # List[ClauseResult]
    
    # Obligations
    obligations = Column(JSON, default=dict)        # {party: List[Obligation]}
    
    # Dates / Timeline
    important_dates = Column(JSON, default=list)    # List[ImportantDate]
    
    # Attention areas
    attention_areas = Column(JSON, default=list)    # List[AttentionArea]
    
    # Action plan
    action_plan = Column(JSON, default=list)        # List[str]
    
    # Lawyer prep
    lawyer_prep = Column(JSON, default=dict)        # {summary, questions, concerns}
    
    # Checklist
    checklist = Column(JSON, default=list)          # List[ChecklistItem]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    document = relationship("Document", back_populates="analysis")
