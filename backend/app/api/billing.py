import json
import asyncio
import os
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from app.core.database import get_async_db
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.models.usage import UsageLog
import redis.asyncio as aioredis

router = APIRouter(prefix="/billing", tags=["billing"])
redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"), encoding="utf-8", decode_responses=True, max_connections=100)

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

@router.get("/usage")
async def get_usage(tenant: Tenant = Depends(get_current_tenant), db = Depends(get_async_db)):
    cache_key = f"billing:usage:{tenant.id}"
    
    async def compute():
        stmt = select(UsageLog.action, func.count(UsageLog.id)).where(UsageLog.tenant_id == tenant.id).group_by(UsageLog.action)
        result = await db.execute(stmt)
        usage = {row.action: row.count for row in result.all()}
        leads_generated = usage.get("lead_generated", 0)
        estimated_bill = leads_generated * 100 
        return {
            "tenant": tenant.name, "plan": tenant.plan_type,
            "usage_breakdown": usage, "estimated_bill_inr": estimated_bill
        }
        
    return await get_cached_or_compute(cache_key, compute)
