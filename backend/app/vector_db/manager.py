from app.vector_db.client import client, COLLECTION_NAME
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

def list_documents():
    """
    Retrieves a list of unique documents currently stored in Qdrant.
    Groups the vector chunks by their 'filename' metadata.
    """
    # Scroll through the collection (limit 1000 for this demo)
    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
        with_vectors=False # We don't need the raw vectors for listing
    )
    
    docs = {}
    for point in results:
        filename = point.payload.get("filename")
        if filename:
            if filename not in docs:
                docs[filename] = {
                    "filename": filename,
                    "source": point.payload.get("source", "unknown"),
                    "author": point.payload.get("author", "unknown"),
                    "chunks": 0
                }
            docs[filename]["chunks"] += 1
            
    return list(docs.values())

def delete_document(filename: str):
    """
    Deletes all vector chunks associated with a specific filename.
    Uses Qdrant's Filter API to target the payload metadata.
    """
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(key="filename", match=MatchValue(value=filename))
            ]
        )
    )
