from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import select, func
from app.core.database import get_async_db
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.models.lead import Lead
from app.models.dsa_agent import DSAAgent
from app.models.lead_unlock import LeadUnlock

router = APIRouter(prefix="/dsa", tags=["dsa_marketplace"])

class MaskedLeadProfile(BaseModel):
    lead_id: int
    intent: Optional[str]
    preferred_location: Optional[str]
    budget_max: Optional[float]
    monthly_income: Optional[float]
    existing_emi: Optional[float]
    max_loan_eligibility: Optional[float]
    masked_phone: str = Field(..., description="Phone number masked for privacy")
    score: Optional[float]
    # MOAT: Pre-Underwritten Financial Metrics
    dti_ratio: Optional[float] = Field(None, description="Debt-to-Income Ratio (%)")
    eligibility_confidence: Optional[str] = Field(None, description="AI Confidence Level: High/Medium/Low")

class UnlockLeadRequest(BaseModel):
    lead_id: int
    max_bid: float  # DSA's maximum bid to unlock contact

@router.get("/leads/available", response_model=List[MaskedLeadProfile])
async def get_available_leads(
    dsa_phone: str,
    min_eligibility: Optional[float] = None,
    location: Optional[str] = None,
    db = Depends(get_async_db)
):
    """
    DSA Marketplace: Query pre-qualified leads with PII masked.
    Leads are only shown if they haven't been unlocked by this DSA already.
    Includes MOAT metrics: DTI Ratio and Eligibility Confidence.
    """
    # Fetch DSA agent
    result = await db.execute(select(DSAAgent).where(DSAAgent.phone == dsa_phone))
    dsa = result.scalar_one_or_none()
    if not dsa or not dsa.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive DSA agent")

    # Build query for available leads
    stmt = select(Lead).where(
        Lead.max_loan_eligibility.isnot(None),
        Lead.max_loan_eligibility > 0,
        # Exclude leads already unlocked by this DSA
        ~select(LeadUnlock.id)
            .where(LeadUnlock.lead_id == Lead.id, LeadUnlock.dsa_id == dsa.id)
            .exists()
    )

    if min_eligibility:
        stmt = stmt.where(Lead.max_loan_eligibility >= min_eligibility)
    if location:
        stmt = stmt.where(Lead.preferred_location.ilike(f"%{location}%"))

    result = await db.execute(stmt)
    leads = result.scalars().all()

    # Return masked profiles with computed MOAT metrics
    profiles = []
    for lead in leads:
        # Compute Debt-to-Income Ratio (MOAT)
        dti = 0.0
        if lead.monthly_income and lead.monthly_income > 0 and lead.existing_emi:
            dti = round((lead.existing_emi / lead.monthly_income * 100), 2)
            
        # Compute AI Confidence Level (MOAT)
        if lead.score and lead.score >= 80 and lead.monthly_income:
            confidence = "High"
        elif lead.score and lead.score >= 50:
            confidence = "Medium"
        else:
            confidence = "Low"

        profiles.append(MaskedLeadProfile(
            lead_id=lead.id,
            intent=lead.intent,
            preferred_location=lead.preferred_location,
            budget_max=lead.budget_max,
            monthly_income=lead.monthly_income,
            existing_emi=lead.existing_emi,
            max_loan_eligibility=lead.max_loan_eligibility,
            masked_phone=f"{lead.phone[:2]}XXXXXX{lead.phone[-4:]}" if lead.phone else "XXXX",
            score=lead.score,
            dti_ratio=dti,
            eligibility_confidence=confidence
        ))
        
    return profiles

@router.post("/leads/{lead_id}/unlock")
async def unlock_lead(
    lead_id: int,
    request: UnlockLeadRequest,
    dsa_phone: str,
    db = Depends(get_async_db)
):
    """
    Blind Auction: DSA bids to unlock a lead's contact details.
    Deducts from wallet, logs the transaction, returns unmasked contact.
    """
    # Fetch DSA
    result = await db.execute(select(DSAAgent).where(DSAAgent.phone == dsa_phone))
    dsa = result.scalar_one_or_none()
    if not dsa or not dsa.is_active:
        raise HTTPException(status_code=401, detail="Invalid DSA agent")

    # Fetch Lead
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Check if already unlocked by this DSA
    existing = await db.execute(select(LeadUnlock).where(
        LeadUnlock.lead_id == lead_id, LeadUnlock.dsa_id == dsa.id))
    if existing.scalar_one_or_none():
        return {
            "status": "already_unlocked",
            "contact": {
                "phone": lead.phone,
                "name": lead.name
            }
        }

    # Check wallet balance
    if dsa.wallet_balance < request.max_bid:
        raise HTTPException(status_code=402, detail="Insufficient wallet balance")

    # Deduct from wallet and log unlock
    dsa.wallet_balance -= request.max_bid
    unlock = LeadUnlock(
        lead_id=lead_id,
        dsa_id=dsa.id,
        unlock_price=request.max_bid
    )
    db.add(unlock)
    await db.commit()
    
    # Compute DTI for the unlocked summary
    unlocked_dti = round((lead.existing_emi / lead.monthly_income * 100), 2) if lead.monthly_income and lead.monthly_income > 0 and lead.existing_emi else 0.0

    return {
        "status": "unlocked",
        "amount_charged": request.max_bid,
        "remaining_wallet": dsa.wallet_balance,
        "contact": {
            "phone": lead.phone,
            "name": lead.name,
            "financial_summary": f"Eligibility: ₹{lead.max_loan_eligibility:,.0f}, Income: ₹{lead.monthly_income:,.0f}/mo, DTI: {unlocked_dti}%"
        }
    }
