import httpx
import logging
from app.models.lead import Lead

logger = logging.getLogger(__name__)

def calculate_loan_eligibility(monthly_income: float, existing_emi: float = 0.0) -> float:
    """
    Deterministic Mumbai Real Estate Loan Eligibility Calculator.
    Rule of thumb: Max EMI = 50% of Net Monthly Income.
    Interest Rate: ~8.5% (Current Indian Home Loan avg).
    Tenure: 20 Years (240 months).
    """
    if not monthly_income:
        return 0.0
        
    max_emi_capacity = (monthly_income * 0.50) - existing_emi
    if max_emi_capacity <= 0:
        return 0.0
        
    # PMT formula reverse: PV = EMI * [ (1 - (1+r)^-n) / r ]
    r = 0.085 / 12  # Monthly interest rate
    n = 240         # 20 years
    
    pv_factor = (1 - (1 + r)**-n) / r
    max_loan = max_emi_capacity * pv_factor
    
    return round(max_loan, 2)

async def sync_to_external_crm(lead: Lead, webhook_url: str = "https://webhook.site/your-unique-id") -> dict:
    """
    Headless Overlay: Pushes the enriched lead to the Broker's existing CRM.
    In production, webhook_url is fetched from broker_integrations table.
    """
    payload = {
        "source": "VYUHLEADS_AI",
        "name": lead.name,
        "phone": lead.phone,
        "intent": lead.intent,
        "budget_max": lead.budget_max,
        "preferred_location": lead.preferred_location,
        "financials": {
            "monthly_income": lead.monthly_income,
            "existing_emi": lead.existing_emi,
            "max_loan_eligibility": lead.max_loan_eligibility
        },
        "ai_score": lead.score
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Simulating Zoho/Realbooks Webhook
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
            # Assume CRM returns an ID
            return {"status": "synced", "external_id": "EXT-12345"}
    except Exception as e:
        logger.error(f"CRM Sync failed for lead {lead.id}: {e}")
        return {"status": "failed", "error": str(e)}
