from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from app.models.user import Base

class LeadUnlock(Base):
    __tablename__ = "lead_unlocks"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    dsa_id = Column(Integer, ForeignKey("dsa_agents.id"), nullable=False)
    unlock_price = Column(Float, nullable=False)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
