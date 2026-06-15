import os
import uuid
import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from app.vector_db.embeddings import embed_and_store, model
from app.vector_db.client import client, COLLECTION_NAME
from app.llm.client import generate_rag_response, stream_rag_response
from app.document_processor import process_and_ingest_pdf
from app.vector_db.manager import list_documents, delete_document

router = APIRouter(prefix="/rag", tags=["rag"])

class ChatRequest(BaseModel):
    query: str
    limit: int = 2

# --- DOCUMENT MANAGEMENT ---
@router.get("/documents")
def get_documents():
    return {"documents": list_documents()}

@router.delete("/documents/{filename}")
def remove_document(filename: str):
    try:
        delete_document(filename)
        return {"status": "success", "message": f"Deleted all chunks for {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- INGESTION ---
@router.post("/ingest-file")
async def ingest_file_endpoint(
    file: UploadFile = File(...),
    source: str = Form("unknown"),
    author: str = Form("unknown")
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently.")
    
    temp_file_path = f"/tmp/{uuid.uuid4()}.pdf"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        metadata = {"source": source, "author": author, "filename": file.filename}
        point_ids = process_and_ingest_pdf(temp_file_path, metadata=metadata)
        os.remove(temp_file_path)
        
        return {
            "status": "success",
            "message": f"Successfully processed and ingested {len(point_ids)} chunks from {file.filename}",
            "point_ids": point_ids
        }
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

# --- STANDARD RAG CHAT ---
@router.post("/chat")
def chat_with_yukti(request: ChatRequest):
    try:
        query_vector = model.encode(request.query).tolist()
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=request.limit
        )
        
        if not search_result:
            return {"answer": "I couldn't find any relevant information.", "sources": []}

        context = "\n\n".join([hit.payload.get("text", "") for hit in search_result])
        sources = [hit.payload.get("metadata", {}) for hit in search_result]
        answer = generate_rag_response(request.query, context)

        return {"query": request.query, "answer": answer, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- STREAMING RAG CHAT (PRODUCTION GRADE) ---
@router.post("/chat-stream")
async def chat_stream_with_yukti(request: ChatRequest):
    try:
        # 1. Run blocking sync operations in a background thread to protect the async event loop
        query_vector = await asyncio.to_thread(model.encode, request.query)
        query_vector = query_vector.tolist()
        
        search_result = await asyncio.to_thread(
            client.search,
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=request.limit
        )
        
        if not search_result:
            async def empty_generator():
                yield "I couldn't find any relevant information in my knowledge base."
            return StreamingResponse(empty_generator(), media_type="text/plain")

        # 2. Prepare context
        context = "\n\n".join([hit.payload.get("text", "") for hit in search_result])
        
        # 3. Return the streaming response
        return StreamingResponse(
            stream_rag_response(request.query, context),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
