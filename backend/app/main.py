from fastapi import FastAPI
from app.api import users, auth, rag
from app.vector_db.client import ensure_collection_exists

app = FastAPI(title="Yukti Platform API", version="0.2.0")

@app.on_event("startup")
def startup_event():
    ensure_collection_exists()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rag.router)

@app.get("/")
def read_root():
    return {
        "message": "Yukti AI Platform is live",
        "node": "PC-Node",
        "status": "operational",
        "phase": "RAG (Phase 2)"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
