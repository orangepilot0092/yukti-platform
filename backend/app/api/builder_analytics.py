import json
import asyncio
import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func, case
from app.core.database import get_async_db
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.models.deal import Deal
from app.models.lead import Lead
from app.core.redis_client import redis_client

router = APIRouter(prefix="/builder", tags=["builder_enterprise"])

_cache_locks = {}

async def get_cached_or_compute(cache_key: str, compute_func, ttl: int = 60):
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    if cache_key not in _cache_locks:
        _cache_locks[cache_key] = asyncio.Lock()

    async with _cache_locks[cache_key]:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        result = await compute_func()
        await redis_client.setex(cache_key, ttl, json.dumps(result))
        return result

class CPPerformance(BaseModel):
    cp_name: str
    total_deals: int
    total_volume: float

@router.get("/analytics/cp-leaderboard", response_model=list[CPPerformance])
async def get_cp_leaderboard(tenant: Tenant = Depends(get_current_tenant), db = Depends(get_async_db)):
    cache_key = f"analytics:cp_leaderboard:{tenant.id}"

    async def compute():
        stmt = (
            select(Deal.cp_name, func.count(Deal.id).label("total_deals"), func.sum(Deal.deal_value).label("total_volume"))
            .where(Deal.tenant_id == tenant.id, Deal.cp_name.isnot(None))
            .group_by(Deal.cp_name).order_by(func.sum(Deal.deal_value).desc())
        )
        result = await db.execute(stmt)
        return [CPPerformance(cp_name=r.cp_name, total_deals=r.total_deals, total_volume=float(r.total_volume or 0)).model_dump() for r in result.all()]

    return await get_cached_or_compute(cache_key, compute)

@router.get("/analytics/transit-heatmap")
async def get_transit_heatmap(tenant: Tenant = Depends(get_current_tenant), db = Depends(get_async_db)):
    cache_key = f"analytics:transit_heatmap:{tenant.id}"

    async def compute():
        transit_line_expr = case(
            (Lead.preferred_location.in_(["Bandra", "Andheri", "Worli", "Prabhadevi", "Kandivali", "Goregaon", "Malad"]), "Western"),
            (Lead.preferred_location.in_(["Powai", "Vikhroli", "Mulund", "Thane", "Dadar", "Parel", "Bkc"]), "Central"),
            (Lead.preferred_location.in_(["Kharghar", "Ghansoli", "Panvel", "Ulwe", "Vashi", "Nerul", "Navi Mumbai"]), "Harbour"),
            else_="Other"
        ).label("transit_line")

        stmt = (
            select(
                transit_line_expr, func.count(Lead.id).label("total_demand_leads"), func.count(Deal.id).label("converted_deals"),
                func.coalesce(func.sum(Deal.deal_value), 0).label("total_converted_volume"), func.coalesce(func.avg(Lead.max_loan_eligibility), 0).label("avg_buyer_eligibility")
            )
            .outerjoin(Deal, Lead.id == Deal.lead_id).where(Lead.tenant_id == tenant.id)
            .group_by(transit_line_expr).order_by(func.count(Lead.id).desc())
        )
        result = await db.execute(stmt)
        return [
            {"transit_line": r.transit_line, "total_demand_leads": r.total_demand_leads, "converted_deals": r.converted_deals,
             "total_converted_volume": float(r.total_converted_volume), "avg_buyer_eligibility": round(float(r.avg_buyer_eligibility), 2)}
            for r in result.all()
        ]

    return await get_cached_or_compute(cache_key, compute)
