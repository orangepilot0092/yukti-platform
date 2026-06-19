from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from app.core.database import get_async_db
from app.core.auth import get_current_tenant
from app.models.tenant import Tenant
from app.models.usage import UsageLog

router = APIRouter(prefix="/billing", tags=["billing"])

@router.get("/usage")
async def get_usage(tenant: Tenant = Depends(get_current_tenant), db = Depends(get_async_db)):
    """SaaS Billing: Aggregates usage logs and calculates estimated invoice."""
    stmt = select(UsageLog.action, func.count(UsageLog.id)).where(UsageLog.tenant_id == tenant.id).group_by(UsageLog.action)
    result = await db.execute(stmt)
    usage = {row.action: row.count for row in result.all()}
    
    # Usage-Based Pricing Model: ₹100 per AI-qualified lead generated
    leads_generated = usage.get("lead_generated", 0)
    estimated_bill = leads_generated * 100 
    
    return {
        "tenant": tenant.name,
        "plan": tenant.plan_type,
        "usage_breakdown": usage,
        "estimated_bill_inr": estimated_bill
    }
