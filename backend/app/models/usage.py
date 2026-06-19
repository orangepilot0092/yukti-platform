from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.user import Base

class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    action = Column(String(50), nullable=False) # 'lead_generated', 'deal_created'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
