from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.user import Base

class VendorReferral(Base):
    __tablename__ = "vendor_referrals"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    vendor_type = Column(String(50), nullable=False)  # 'interior', 'movers', 'vastu'
    vendor_name = Column(String(100), nullable=False)
    referral_fee_pct = Column(Float, default=10.0)  # 10% affiliate fee
    deal_value = Column(Float, nullable=False)
    status = Column(String(50), default="referred")  # referred, converted, paid
    created_at = Column(DateTime(timezone=True), server_default=func.now())
