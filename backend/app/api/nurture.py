from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.models.lead import Lead
from app.services.follow_up import generate_follow_up_draft

# Embedded Async DB setup
DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@db:5432/yukti_db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter(prefix="/nurture", tags=["nurture"])

@router.post("/generate-draft/{lead_id}")
async def generate_draft(lead_id: int, db: AsyncSession = Depends(get_async_db)):
    """Trigger AI draft generation for a specific lead and save to DB."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        return {"error": "Lead not found"}
        
    # Call the LLM Service
    draft = await generate_follow_up_draft(lead)
    
    # Update Lead State Machine
    lead.follow_up_draft = draft
    lead.follow_up_status = "pending"  # Ready for Broker approval
    await db.commit()
    
    return {"lead_id": lead.id, "draft": draft, "status": "pending"}

@router.get("/scan")
async def scan_stale_leads(db: AsyncSession = Depends(get_async_db)):
    """Cron Job: Finds leads needing follow-up, generates drafts, sets to pending."""
    result = await db.execute(select(Lead).where(Lead.follow_up_status == "none"))
    leads = result.scalars().all()
    
    processed = []
    for lead in leads:
        draft = await generate_follow_up_draft(lead)
        lead.follow_up_draft = draft
        lead.follow_up_status = "pending"
        processed.append({"lead_id": lead.id, "draft": draft})
        
    await db.commit()
    return {"scanned": len(leads), "drafts_generated": processed}

@router.post("/approve/{lead_id}")
async def approve_and_send(lead_id: int, db: AsyncSession = Depends(get_async_db)):
    """HITL Workflow: Broker approves draft, system sends via WhatsApp."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead or lead.follow_up_status != "pending":
        return {"error": "Lead not found or not pending approval"}
        
    # In production, this calls your Whapi.cloud API service
    print(f"🚀 SENDING TO WHAPI: To={lead.phone}, Message={lead.follow_up_draft}")
    
    lead.follow_up_status = "sent"
    lead.last_contacted_at = func.now()
    await db.commit()
    
    return {"status": "sent", "lead_id": lead.id, "message_sent": lead.follow_up_draft}
