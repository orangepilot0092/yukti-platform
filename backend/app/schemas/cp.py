from pydantic import BaseModel
from typing import Optional

class CPReferralCreate(BaseModel):
    lead_phone: str
    lead_name: Optional[str] = None
    cp_name: str
    cp_phone: str
    commission_pct: Optional[float] = None
    notes: Optional[str] = None
