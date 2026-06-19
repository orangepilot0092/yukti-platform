from fastapi import FastAPI
from app.api import users, auth, rag, agents, agents_streaming, whatsapp, whatsapp
from app.vector_db.client import ensure_collection_exists
from app.mcp.manager import mcp_manager

app = FastAPI(title="Yukti Platform API", version="0.5.0")

@app.on_event("startup")
async def startup_event():
    ensure_collection_exists()
    # Start the MCP Forever Task
    await mcp_manager.start()

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanly cancel the forever task and kill the subprocess
    await mcp_manager.stop()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rag.router)
app.include_router(agents.router)
app.include_router(agents_streaming.router) # NEW: SSE Streaming Router
app.include_router(whatsapp.router)
app.include_router(whatsapp.router)

@app.get("/")
def read_root():
    return {
        "message": "Yukti AI Platform is live",
        "node": "PC-Node",
        "status": "operational",
        "phase": "Production Agentic AI with Guardrails & Streaming (Phase 3)"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

from app.api.crm import router as crm_router
app.include_router(crm_router)

from app.api.analytics import router as analytics_router
app.include_router(analytics_router)

from app.api.nurture import router as nurture_router
app.include_router(nurture_router)
