from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.deal import Deal
from app.models.builder_project import BuilderProject  # Ensures metadata registration
from app.models.cp_commission import CPCommission

DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@db:5432/yukti_db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter(prefix="/deals", tags=["deals"])

class DealCreate(BaseModel):
    lead_id: int
    project_id: int
    broker_name: str
    cp_name: Optional[str] = None
    deal_value: float

class DealStatusUpdate(BaseModel):
    status: str  # token_paid, agreement, registration, disbursed
    platform_fee: Optional[float] = 0.0
    commission_pct: Optional[float] = None  # The % agreed with the CP

@router.post("/")
async def create_deal(deal: DealCreate, db: AsyncSession = Depends(get_async_db)):
    """Initiate a new real estate transaction (Token Paid)."""
    new_deal = Deal(**deal.model_dump())
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)
    return {"status": "success", "deal_id": new_deal.id, "message": "Deal initiated (Token Paid)"}

@router.patch("/{deal_id}/status")
async def update_deal_status(deal_id: int, update: DealStatusUpdate, db: AsyncSession = Depends(get_async_db)):
    """Transition deal lifecycle and trigger billing/CP payouts on registration."""
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    deal.status = update.status
    if update.platform_fee:
        deal.platform_fee = update.platform_fee
        
    await db.commit()
    
    # AUTOMATED BILLING & CP COMMISSION TRIGGER
    if update.status in ["registration", "disbursed"]:
        print(f"🚀 BILLING TRIGGER: Invoice generated for Deal {deal_id}! Platform Fee: ₹{deal.platform_fee}")
        
        # Calculate CP Commission if a CP was involved
        if deal.cp_name and update.commission_pct:
            comm_amount = deal.deal_value * (update.commission_pct / 100.0)
            
            # Idempotency check: prevent duplicate payouts
            existing_comm = await db.execute(select(CPCommission).where(CPCommission.deal_id == deal_id))
            if not existing_comm.scalar_one_or_none():
                commission = CPCommission(
                    deal_id=deal_id,
                    cp_name=deal.cp_name,
                    commission_pct=update.commission_pct,
                    commission_amount=comm_amount,
                    status="pending"
                )
                db.add(commission)
                await db.commit()
                print(f"💰 CP COMMISSION TRIGGER: {deal.cp_name} earned ₹{comm_amount:,.0f} ({update.commission_pct}%)")
        
    return {"deal_id": deal.id, "new_status": deal.status, "platform_fee": deal.platform_fee}

@router.get("/cp/ledger/{cp_name}")
async def get_cp_ledger(cp_name: str, db: AsyncSession = Depends(get_async_db)):
    """CP Dashboard: View all earned commissions transparently."""
    result = await db.execute(select(CPCommission).where(CPCommission.cp_name == cp_name))
    commissions = result.scalars().all()
    
    total_earned = sum(c.commission_amount for c in commissions)
    
    return {
        "cp_name": cp_name,
        "total_earned": total_earned,
        "transactions": [
            {
                "deal_id": c.deal_id,
                "amount": c.commission_amount,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            } for c in commissions
        ]
    }
