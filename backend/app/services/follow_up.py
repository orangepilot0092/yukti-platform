import httpx
import logging
from app.models.lead import Lead

logger = logging.getLogger(__name__)

# Ensure 'ai-node' resolves to your MSI Edge Expert's IP. 
# If it doesn't, replace 'ai-node' with the actual IP (e.g., '192.168.1.50')
VLLM_API_URL = "http://ai-node:8000/v1/chat/completions"
MODEL_NAME = "qwen-27b"  # Matches the --served-model-name from your vLLM startup

async def generate_follow_up_draft(lead: Lead) -> str:
    """Generates a contextual WhatsApp follow-up draft using local vLLM."""
    
    # Fallbacks for missing data
    name = lead.name or "there"
    intent = lead.intent or "explore properties"
    location = lead.preferred_location or "Mumbai"
    budget = f"₹{lead.budget_max:,.0f}" if lead.budget_max else "your budget"
    
    prompt = f"""You are an expert real estate broker in Mumbai. 
Draft a short, professional, and friendly WhatsApp follow-up message for a client.
Client Name: {name}
Intent: {intent}
Preferred Location: {location}
Budget: {budget}

Rules:
- Keep it under 30 words.
- Do not use quotes or markdown.
- End with a simple question to prompt a reply.
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful real estate assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(VLLM_API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            draft = data["choices"][0]["message"]["content"].strip()
            return draft
    except Exception as e:
        logger.error(f"vLLM draft generation failed: {e}. Using fallback template.")
        # Graceful Degradation: Return a high-converting static template if AI is down
        return f"Hi {name}, I found some excellent {intent} options in {location} around {budget}. Are you free for a quick 2-min call today?"
