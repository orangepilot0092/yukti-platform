from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select, func, case
from app.core.database import get_async_db
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.models.deal import Deal
from app.models.lead import Lead
from app.models.builder_project import BuilderProject

router = APIRouter(prefix="/builder", tags=["builder_enterprise"])

class CPPerformance(BaseModel):
    cp_name: str
    total_deals: int
    total_volume: float

@router.get("/analytics/cp-leaderboard", response_model=list[CPPerformance])
async def get_cp_leaderboard(tenant: Tenant = Depends(get_current_tenant), db = Depends(get_async_db)):
    stmt = (
        select(
            Deal.cp_name,
            func.count(Deal.id).label("total_deals"),
            func.sum(Deal.deal_value).label("total_volume")
        )
        .where(Deal.tenant_id == tenant.id, Deal.cp_name.isnot(None))
        .group_by(Deal.cp_name)
        .order_by(func.sum(Deal.deal_value).desc())
    )
    result = await db.execute(stmt)
    return [CPPerformance(cp_name=r.cp_name, total_deals=r.total_deals, total_volume=float(r.total_volume or 0)) for r in result.all()]
