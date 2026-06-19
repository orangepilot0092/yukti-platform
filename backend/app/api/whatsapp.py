import asyncio
import httpx
import logging
import time
import traceback
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.agents.lead_qualifier import build_lead_qualifier
from app.models.lead import Lead
from app.models.builder_project import BuilderProject
from app.models.tenant import Tenant
from app.models.usage import UsageLog
from app.services.financials import sync_to_external_crm
from app.services.recommendations import get_recommendations
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

WHAPI_BASE_URL = "https://gate.whapi.cloud"
WHAPI_TOKEN = "8HRmlkoCyjHkhoJ39a6DmlLXqstT44mW"
DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@db:5432/yukti_db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

_cached_qualifier = None
def get_qualifier():
    global _cached_qualifier
    if _cached_qualifier is None:
        _cached_qualifier = build_lead_qualifier()
    return _cached_qualifier

def _task_exception_callback(task: asyncio.Task):
    if not task.cancelled() and task.exception():
        exc = task.exception()
        print(f"❌ BACKGROUND TASK CRASHED: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exception(type(exc), exc, exc.__traceback__)

async def process_and_reply(user_phone: str, message_text: str, from_name: str, tenant_id: int):
    print(f"🟢 BG TASK STARTED for {user_phone} (Tenant {tenant_id})", flush=True)
    try:
        qualifier = get_qualifier()
        initial_state = {
            "messages": [HumanMessage(content=message_text)],
            "phone": user_phone, "name": from_name,
            "intent": None, "score": None, "stage": None, "property_type": None,
            "budget_min": None, "budget_max": None, "preferred_location": None, "timeline": None,
            "monthly_income": None, "existing_emi": None, "max_loan_eligibility": None,
            "steps_taken": 0, "start_time": time.time(), "error": None
        }

        final_state = await qualifier.ainvoke(initial_state)

        async with async_session() as session:
            lead = Lead(
                phone=user_phone, name=from_name,
                intent=final_state.get("intent"), score=final_state.get("score"), stage=final_state.get("stage"),
                property_type=final_state.get("property_type"), budget_min=final_state.get("budget_min"),
                budget_max=final_state.get("budget_max"), preferred_location=final_state.get("preferred_location"),
                timeline=final_state.get("timeline"), monthly_income=final_state.get("monthly_income"),
                existing_emi=final_state.get("existing_emi"), max_loan_eligibility=final_state.get("max_loan_eligibility"),
                tenant_id=tenant_id,
                last_message=message_text,
                conversation_summary=f"Intent: {final_state.get('intent')}, Score: {final_state.get('score')}"
            )
            session.add(lead)
            
            # SPRINT 21: Accurate Usage Metering for the specific Tenant
            session.add(UsageLog(tenant_id=tenant_id, action="lead_generated"))
                
            await session.commit()
            print(f"💾 Lead persisted: ID={lead.id}, Tenant={tenant_id}, Eligibility=₹{lead.max_loan_eligibility:,.0f}", flush=True)

            sync_result = await sync_to_external_crm(lead, webhook_url="https://webhook.site/your-unique-id")
            lead.crm_sync_status = sync_result.get("status")
            await session.commit()

        if final_state.get("error"):
            ai_response = f"⚠️ {final_state['error']}"
        else:
            ai_response = final_state["messages"][-1].content
            eligibility = final_state.get("max_loan_eligibility")
            if eligibility and eligibility > 0:
                async with async_session() as session:
                    recs = await get_recommendations(session, eligibility)
                    if recs:
                        rec_text = "\n\n🏢 *Recommended Projects within your Eligibility:*\n"
                        for r in recs:
                            rec_text += f"• *{r['project']}* ({r['zone']}, {r['line']} Line)\n"
                        ai_response += rec_text

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{WHAPI_BASE_URL}/messages/text",
                headers={"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"},
                json={"to": user_phone, "body": ai_response}
            )
            if resp.status_code == 200:
                print(f"✅ Sent to {user_phone}", flush=True)

    except Exception as e:
        print(f"❌ BG TASK EXCEPTION: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()

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
        
        # --- SPRINT 21: DYNAMIC TENANT ROUTING & SECURITY ---
        # Extract the broker's virtual number from the webhook payload
        broker_phone = msg.get("to") or msg.get("recipient")
        
        async with async_session() as db:
            tenant = None
            if broker_phone:
                result = await db.execute(select(Tenant).where(Tenant.whatsapp_number == broker_phone))
                tenant = result.scalar_one_or_none()
                
            if not tenant:
                # SECURITY GATE: Reject unregistered numbers instantly to prevent AI credit burn
                print(f"⚠️ REJECTED: No tenant found for broker phone {broker_phone}", flush=True)
                return JSONResponse(status_code=403, content={"status": "forbidden", "error": "Unregistered broker number"})

            if not user_phone or not message_text:
                return JSONResponse(status_code=200, content={"status": "ignored"})

            # Pass the validated tenant_id to the background task
            task = asyncio.create_task(process_and_reply(user_phone, message_text, from_name, tenant.id))
            task.add_done_callback(_task_exception_callback)

            return JSONResponse(status_code=200, content={"status": "processing", "tenant": tenant.name})

    except Exception as e:
        print(f"❌ Webhook error: {e}", flush=True)
        return JSONResponse(status_code=200, content={"status": "error"})
