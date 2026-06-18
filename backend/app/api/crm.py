from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.lead import Lead
from app.models.cp_referral import CPReferral, ReferralStatus
from app.schemas.lead import LeadOut
from app.schemas.cp import CPReferralCreate

# Async DB setup embedded here to avoid colliding with existing app.db package
DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@db:5432/yukti_db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter(prefix="/crm", tags=["crm"])

@router.get("/leads", response_model=list[LeadOut])
async def get_leads(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_async_db)):
    """Broker View: List all leads with scoring and Tier 2 signals."""
    result = await db.execute(select(Lead).offset(skip).limit(limit).order_by(Lead.created_at.desc()))
    return result.scalars().all()

@router.post("/cp/referrals")
async def submit_cp_referral(referral: CPReferralCreate, db: AsyncSession = Depends(get_async_db)):
    """CP Portal: Submit a new lead referral."""
    # Create Lead first
    lead = Lead(
        phone=referral.lead_phone,
        name=referral.lead_name,
        stage="new",
        intent="cp_referral"
    )
    db.add(lead)
    await db.flush()  # Flush to get lead.id without committing yet
    
    # Create CP Referral linked to Lead
    cp_ref = CPReferral(
        lead_id=lead.id,
        cp_name=referral.cp_name,
        cp_phone=referral.cp_phone,
        commission_pct=referral.commission_pct,
        status=ReferralStatus.SUBMITTED,
        notes=referral.notes
    )
    db.add(cp_ref)
    await db.commit()
    
    return {"status": "success", "lead_id": lead.id, "message": "Referral submitted"}
