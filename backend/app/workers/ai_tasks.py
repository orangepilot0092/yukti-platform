import time
import traceback
import httpx
import logging
from app.core.celery_app import celery_app
from app.agents.lead_qualifier import build_lead_qualifier
from app.services.financials import sync_to_external_crm
from app.services.recommendations import get_recommendations
from app.models.lead import Lead
from app.models.usage import UsageLog
from app.models.tenant import Tenant
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import asyncio

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@db:5432/yukti_db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

WHAPI_BASE_URL = "https://gate.whapi.cloud"
WHAPI_TOKEN = "8HRmlkoCyjHkhoJ39a6DmlLXqstT44mW"

_cached_qualifier = None
def get_qualifier():
    global _cached_qualifier
    if _cached_qualifier is None:
        _cached_qualifier = build_lead_qualifier()
    return _cached_qualifier

@celery_app.task(name="process_whatsapp_lead", bind=True, max_retries=3)
def process_whatsapp_lead(self, user_phone: str, message_text: str, from_name: str, tenant_id: int):
    """
    Celery Worker Task: Executes heavy LangGraph AI inference off the main API event loop.
    """
    print(f"🟢 CELERY WORKER STARTED for {user_phone} (Tenant {tenant_id})", flush=True)
    
    # Celery tasks are synchronous by default, so we run the async code in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(_async_ai_logic(user_phone, message_text, from_name, tenant_id))
    except Exception as e:
        print(f"❌ CELERY TASK EXCEPTION: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        # Exponential backoff retry if the LLM node is temporarily down
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
    finally:
        loop.close()

async def _async_ai_logic(user_phone: str, message_text: str, from_name: str, tenant_id: int):
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
        session.add(UsageLog(tenant_id=tenant_id, action="lead_generated"))
        await session.commit()
        print(f"💾 Lead persisted: ID={lead.id}, Tenant={tenant_id}", flush=True)

    # Generate AI Response
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

    # Send back via Whapi
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{WHAPI_BASE_URL}/messages/text",
            headers={"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"},
            json={"to": user_phone, "body": ai_response}
        )
        if resp.status_code == 200:
            print(f"✅ Sent to {user_phone}", flush=True)

from datetime import datetime, timedelta
from celery.schedules import crontab

# Schedule the task to run every 60 minutes
celery_app.conf.beat_schedule = {
    'scan-stale-leads-every-hour': {
        'task': 'nurture_stale_leads',
        'schedule': crontab(minute=0), # Runs at the top of every hour
    },
}

@celery_app.task(name="nurture_stale_leads")
def nurture_stale_leads():
    """
    Celery Beat Task: Scans for qualified leads with no activity in 48 hours
    and triggers an automated WhatsApp follow-up.
    """
    print("⏰ CELERY BEAT: Starting stale lead scan...", flush=True)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_async_nurture_logic())
    except Exception as e:
        print(f"❌ NURTURE TASK ERROR: {e}", flush=True)
    finally:
        loop.close()

async def _async_nurture_logic():
    from sqlalchemy import select, and_
    from app.models.lead import Lead
    
    cutoff_time = datetime.utcnow() - timedelta(hours=48)
    
    async with async_session() as db:
        # Find leads that are qualified but haven't been updated in 48 hours
        stmt = select(Lead).where(
            and_(
                Lead.stage == "qualified",
                Lead.updated_at < cutoff_time,
                Lead.nurture_sent == False # Assuming we add a boolean flag later, or just rely on updated_at
            )
        ).limit(50) # Process in batches to avoid rate limits
        
        result = await db.execute(stmt)
        stale_leads = result.scalars().all()
        
        print(f"⏰ Found {len(stale_leads)} stale leads to nurture.", flush=True)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for lead in stale_leads:
                # Contextual Follow-up Message
                msg = f"Hi {lead.name}, just checking in on your property search in {lead.preferred_location or 'Mumbai'}. Are you still looking for a home loan around ₹{lead.max_loan_eligibility:,.0f}? Reply 'YES' to connect with our top partner."
                
                resp = await client.post(
                    f"{WHAPI_BASE_URL}/messages/text",
                    headers={"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"},
                    json={"to": lead.phone, "body": msg}
                )
                
                if resp.status_code == 200:
                    print(f"✅ Nurture sent to {lead.phone}", flush=True)
                    lead.updated_at = datetime.utcnow() # Reset the 48h timer
                    await db.commit()
