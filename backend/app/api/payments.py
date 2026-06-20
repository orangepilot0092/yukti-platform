import razorpay
import os
import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_async_db
from app.models.dsa_agent import DSAAgent
from app.models.tenant import Tenant

router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize Razorpay Client (Use test keys for dev, env vars for prod)
razorpay_client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID", "rzp_test_dummy_key"),
        os.getenv("RAZORPAY_KEY_SECRET", "dummy_secret")
    )
)

class CreateOrderRequest(BaseModel):
    amount_inr: int  # e.g., 5000 for ₹5000
    purpose: str     # "dsa_wallet" or "saas_subscription"
    entity_id: int   # DSA ID or Tenant ID

class VerifyPaymentRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str
    purpose: str
    entity_id: int
    amount_inr: int

@router.post("/create-order")
async def create_order(req: CreateOrderRequest):
    """Creates a Razorpay order and returns the order_id to the frontend."""
    try:
        order_data = {
            "amount": req.amount_inr * 100, # Razorpay expects amount in paise
            "currency": "INR",
            "receipt": f"{req.purpose}_{req.entity_id}",
            "payment_capture": 1 # Auto-capture payment
        }
        order = razorpay_client.order.create(order_data)
        return {
            "order_id": order["id"], 
            "amount": order["amount"], 
            "currency": order["currency"],
            "key_id": os.getenv("RAZORPAY_KEY_ID", "rzp_test_dummy_key")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Razorpay order creation failed: {str(e)}")

@router.post("/verify")
async def verify_payment(
    req: VerifyPaymentRequest, 
    db: AsyncSession = Depends(get_async_db)
):
    """
    MOAT: Cryptographic Payment Verification.
    Verifies the Razorpay signature before fulfilling the order (adding wallet balance or upgrading plan).
    """
    secret = os.getenv("RAZORPAY_KEY_SECRET", "dummy_secret")
    
    # 1. Verify HMAC-SHA256 Signature
    generated_signature = hmac.new(
        secret.encode(),
        f"{req.order_id}|{req.payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    if generated_signature != req.signature:
        raise HTTPException(status_code=400, detail="Invalid payment signature. Fraud detected.")
        
    # 2. Fulfill the Order (Atomic DB Update)
    if req.purpose == "dsa_wallet":
        result = await db.execute(select(DSAAgent).where(DSAAgent.id == req.entity_id))
        dsa = result.scalar_one_or_none()
        if dsa:
            dsa.wallet_balance += req.amount_inr # Add top-up to wallet
            await db.commit()
            return {"status": "success", "message": "Wallet topped up", "new_balance": dsa.wallet_balance}
            
    elif req.purpose == "saas_subscription":
        result = await db.execute(select(Tenant).where(Tenant.id == req.entity_id))
        tenant = result.scalar_one_or_none()
        if tenant:
            tenant.plan_type = "enterprise" # Upgrade plan
            # TODO: Add logic to set subscription expiry date
            await db.commit()
            return {"status": "success", "message": "Enterprise subscription activated"}
            
    raise HTTPException(status_code=404, detail="Entity not found for fulfillment")
