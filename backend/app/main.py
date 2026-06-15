from fastapi import FastAPI
from app.api import users

app = FastAPI(title="Yukti Platform API", version="0.1.0")

# Include the users router
app.include_router(users.router)

@app.get("/")
def read_root():
    return {
        "message": "Yukti AI Platform is live",
        "node": "PC-Node",
        "status": "operational"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
