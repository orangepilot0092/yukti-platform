import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.models.user import Base


class LeadIntent(str, enum.Enum):
    BUY = "buy"
    RENT = "rent"
    SITE_VISIT = "site_visit"
    PRICING_INQUIRY = "pricing_inquiry"
    SPAM = "spam"
    OTHER = "other"


class LeadStage(str, enum.Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    INTERESTED = "interested"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    
    # AI Classification Fields
    intent = Column(SQLEnum(LeadIntent), nullable=True)
    score = Column(Float, nullable=True)  # 0-100
    stage = Column(SQLEnum(LeadStage), default=LeadStage.NEW)
    
    # Extracted Structured Data
    property_type = Column(String(50), nullable=True)  # e.g., "2BHK", "Villa"
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    preferred_location = Column(String(200), nullable=True)
    timeline = Column(String(100), nullable=True)  # e.g., "immediate", "3 months"
    
    # Conversation Context
    last_message = Column(Text, nullable=True)
    conversation_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Lead(id={self.id}, phone={self.phone}, score={self.score})>"
