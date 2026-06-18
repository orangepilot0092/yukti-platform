import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.user import Base


class ReferralStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    QUALIFIED = "qualified"
    SITE_VISIT_SCHEDULED = "site_visit_scheduled"
    BOOKED = "booked"
    REJECTED = "rejected"
    COMMISSION_PAID = "commission_paid"


class CPReferral(Base):
    __tablename__ = "cp_referrals"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, unique=True)
    cp_name = Column(String(100), nullable=False)
    cp_phone = Column(String(20), nullable=False, index=True)
    commission_pct = Column(Float, nullable=True)
    status = Column(String(50), default=ReferralStatus.SUBMITTED)
    notes = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lead = relationship("Lead", back_populates="cp_referral")

    def __repr__(self):
        return f"<CPReferral(id={self.id}, cp={self.cp_name}, status={self.status})>"
