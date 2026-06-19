from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select
from app.core.database import get_async_db
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.models.deal import Deal
from app.models.builder_project import BuilderProject
from app.models.cp_commission import CPCommission

router = APIRouter(prefix="/deals", tags=["deals"])

class DealCreate(BaseModel):
    lead_id: int
    project_id: int
    broker_name: str
    cp_name: Optional[str] = None
    deal_value: float

class DealStatusUpdate(BaseModel):
    status: str
    platform_fee: Optional[float] = 0.0
    commission_pct: Optional[float] = None

@router.post("/")
async def create_deal(deal: DealCreate, tenant: Tenant = Depends(get_current_tenant), db = Depends(get_async_db)):
    new_deal = Deal(**deal.model_dump(), tenant_id=tenant.id)
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)
    return {"status": "success", "deal_id": new_deal.id, "tenant": tenant.name}

@router.patch("/{deal_id}/status")
async def update_deal_status(deal_id: int, update: DealStatusUpdate, tenant: Tenant = Depends(get_current_tenant), db = Depends(get_async_db)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id, Deal.tenant_id == tenant.id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found in your workspace")
        
    deal.status = update.status
    if update.platform_fee: deal.platform_fee = update.platform_fee
    await db.commit()
    
    if update.status in ["registration", "disbursed"] and deal.cp_name and update.commission_pct:
        comm_amount = deal.deal_value * (update.commission_pct / 100.0)
        existing_comm = await db.execute(select(CPCommission).where(CPCommission.deal_id == deal_id))
        if not existing_comm.scalar_one_or_none():
            db.add(CPCommission(deal_id=deal_id, cp_name=deal.cp_name, commission_pct=update.commission_pct, commission_amount=comm_amount))
            await db.commit()
            
    return {"deal_id": deal.id, "new_status": deal.status}
