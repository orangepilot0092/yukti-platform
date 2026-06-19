from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.user import Base

class CPCommission(Base):
    __tablename__ = "cp_commissions"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    cp_name = Column(String(100), nullable=False)
    commission_pct = Column(Float, nullable=False)
    commission_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")  # pending, paid
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
