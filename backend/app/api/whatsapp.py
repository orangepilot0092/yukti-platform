import logging
import os
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.tenant import Tenant
from app.workers.ai_tasks import process_whatsapp_lead
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@pgbouncer:6432/yukti_db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    try:
        body = await request.json()
        messages = body.get("messages", [])
        if not messages:
            return JSONResponse(status_code=200, content={"status": "ignored"})

        msg = messages[0]
        if msg.get("from_me") or msg.get("type") != "text":
            return JSONResponse(status_code=200, content={"status": "ignored"})

        user_phone = msg.get("from")
        message_text = msg.get("text", {}).get("body", "")
        from_name = msg.get("from_name", "User")
        broker_phone = msg.get("to") or msg.get("recipient")

        if not broker_phone:
            return JSONResponse(status_code=400, content={"error": "Missing broker phone"})

        # Check Redis Cache for Tenant ID first (bypasses Postgres)
        cache_key = f"tenant_map:{broker_phone}"
        tenant_id = await redis_client.get(cache_key)

        if not tenant_id:
            async with async_session() as db:
                result = await db.execute(select(Tenant).where(Tenant.whatsapp_number == broker_phone))
                tenant = result.scalar_one_or_none()
                if not tenant:
                    return JSONResponse(status_code=403, content={"status": "forbidden"})
                tenant_id = tenant.id
                await redis_client.setex(cache_key, 86400, str(tenant_id))

        if not user_phone or not message_text:
            return JSONResponse(status_code=200, content={"status": "ignored"})

        process_whatsapp_lead.delay(user_phone, message_text, from_name, int(tenant_id))
        return JSONResponse(status_code=200, content={"status": "queued", "tenant_id": tenant_id})

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return JSONResponse(status_code=200, content={"status": "error"})
