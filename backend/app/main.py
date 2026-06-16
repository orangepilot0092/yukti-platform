from fastapi import FastAPI
from app.api import users, auth, rag, agents
from app.vector_db.client import ensure_collection_exists
from app.mcp.manager import mcp_manager

app = FastAPI(title="Yukti Platform API", version="0.4.0")

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

@app.get("/")
def read_root():
    return {
        "message": "Yukti AI Platform is live",
        "node": "PC-Node",
        "status": "operational",
        "phase": "Agentic AI with MCP (Phase 3)"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
