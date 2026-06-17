import asyncio
import httpx
import logging
import traceback
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.agents.researcher import build_research_agent
from app.mcp.manager import mcp_manager
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

WHAPI_BASE_URL = "https://gate.whapi.cloud"
WHAPI_TOKEN = "8HRmlkoCyjHkhoJ39a6DmlLXqstT44mW"

# CACHE: Build agent once when module loads, not per request
_cached_agent = None

def get_agent():
    global _cached_agent
    if _cached_agent is None and mcp_manager.tools:
        print("🔵 Caching compiled WhatsApp agent...", flush=True)
        _cached_agent = build_research_agent(mcp_manager.tools)
    return _cached_agent

def _task_exception_callback(task: asyncio.Task):
    if not task.cancelled() and task.exception():
        exc = task.exception()
        print(f"❌ BACKGROUND TASK CRASHED: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exception(type(exc), exc, exc.__traceback__)

async def process_and_reply(user_phone: str, message_text: str, from_name: str):
    print(f"🟢 BG TASK STARTED for {user_phone}", flush=True)
    start = time.time()
    try:
        logger.info(f"💬 [{from_name}] Processing: {message_text}")
        print(f"💬 [{from_name}] Processing: {message_text}", flush=True)
        
        agent = get_agent()
        if not agent:
            raise Exception("Agent not ready - MCP tools not initialized")
        
        initial_state = {
            "messages": [
                SystemMessage(content="You are the VYUHLEADS AI Assistant for Mumbai real estate brokers. Be concise, professional, and helpful."),
                HumanMessage(content=message_text)
            ],
            "steps_taken": 0,
            "start_time": time.time(),
            "error": None
        }
        
        print("🟢 INVOKING AGENT...", flush=True)
        final_state = await agent.ainvoke(initial_state)
        elapsed = time.time() - start
        print(f"🟢 AGENT COMPLETED in {elapsed:.1f}s", flush=True)
        
        if final_state.get("error"):
            ai_response = f"⚠️ {final_state['error']}"
        else:
            ai_response = final_state["messages"][-1].content
            
        print(f"🤖 Response: {ai_response[:80]}...", flush=True)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{WHAPI_BASE_URL}/messages/text",
                headers={"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"},
                json={"to": user_phone, "body": ai_response}
            )
            if resp.status_code == 200:
                print(f"✅ Sent to {user_phone}", flush=True)
            else:
                print(f"❌ Send failed: {resp.text}", flush=True)
                
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
        
        if not user_phone or not message_text:
            return JSONResponse(status_code=200, content={"status": "ignored"})
        
        task = asyncio.create_task(process_and_reply(user_phone, message_text, from_name))
        task.add_done_callback(_task_exception_callback)
        
        return JSONResponse(status_code=200, content={"status": "processing"})
        
    except Exception as e:
        print(f"❌ Webhook error: {e}", flush=True)
        return JSONResponse(status_code=200, content={"status": "error"})
