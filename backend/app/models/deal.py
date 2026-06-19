from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.user import Base

class Deal(Base):
    __tablename__ = "deals"
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("builder_projects.id"), nullable=False)
    broker_name = Column(String(100), nullable=False)
    cp_name = Column(String(100), nullable=True)  # Optional: If a CP brought the lead
    deal_value = Column(Float, nullable=False)     # Total property value
    platform_fee = Column(Float, default=0.0)     # VYUHLEADS Success Fee
    status = Column(String(50), default="token_paid") 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
