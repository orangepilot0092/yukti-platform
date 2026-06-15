from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.vector_db.embeddings import embed_and_store, model
from app.vector_db.client import client, COLLECTION_NAME
from app.llm.client import generate_rag_response

router = APIRouter(prefix="/rag", tags=["rag"])

class IngestRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None

class ChatRequest(BaseModel):
    query: str
    limit: int = 2 # Retrieve top 2 chunks for context

@router.post("/ingest")
def ingest_document(request: IngestRequest):
    try:
        point_id = embed_and_store(request.text, request.metadata)
        return {"status": "success", "point_id": point_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
def chat_with_yukti(request: ChatRequest):
    try:
        # 1. RETRIEVAL: Find relevant vectors
        query_vector = model.encode(request.query).tolist()
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=request.limit
        )
        
        if not search_result:
            return {"answer": "I couldn't find any relevant information in my knowledge base.", "sources": []}

        # 2. AUGMENTATION: Combine chunks into a single context string
        context = "\n\n".join([hit.payload.get("text", "") for hit in search_result])
        sources = [hit.payload.get("metadata", {}) for hit in search_result]

        # 3. GENERATION: Send to Qwen 27B on the AI Node
        answer = generate_rag_response(request.query, context)

        return {
            "query": request.query,
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
