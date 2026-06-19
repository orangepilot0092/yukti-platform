from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tenant import Tenant, APIKey
from app.core.database import get_async_db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_tenant(
    x_api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_async_db)
) -> Tenant:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
        
    result = await db.execute(select(APIKey).where(APIKey.api_key == x_api_key, APIKey.is_active == True))
    api_key_obj = result.scalar_one_or_none()
    
    if not api_key_obj:
        raise HTTPException(status_code=401, detail="Invalid or inactive API Key")
        
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == api_key_obj.tenant_id))
    tenant = tenant_result.scalar_one()
    
    return tenant
