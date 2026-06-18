from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime

class LeadOut(BaseModel):
    id: int
    phone: str
    name: Optional[str] = None
    intent: Optional[str] = None
    score: Optional[float] = None
    stage: Optional[str] = None
    preferred_location: Optional[str] = None
    budget_max: Optional[float] = None
    loan_prequal_signal: Optional[str] = None
    created_at: datetime

    @field_validator('intent', 'stage', mode='before')
    @classmethod
    def extract_enum_value(cls, v: Any) -> Optional[str]:
        """Safely extract string value from SQLAlchemy Native Enums."""
        if hasattr(v, 'value'):
            return v.value
        return v

    class Config:
        from_attributes = True
