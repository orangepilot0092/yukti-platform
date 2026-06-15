from fastapi import FastAPI

app = FastAPI(title="Yukti Platform API", version="0.1.0")

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
