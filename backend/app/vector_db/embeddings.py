from sentence_transformers import SentenceTransformer
from app.vector_db.client import client, COLLECTION_NAME
import uuid

# Load the model globally. 
# Because we pre-downloaded it in the Dockerfile, this is now instant.
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_and_store(text: str, metadata: dict = None):
    # 1. Generate the 384-dimensional vector
    vector = model.encode(text).tolist()
    
    # 2. Prepare the payload
    point_id = str(uuid.uuid4())
    payload = metadata or {}
    payload["text"] = text # Store original text so we can retrieve it later
    
    # 3. Upsert to Qdrant
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            {
                "id": point_id,
                "vector": vector,
                "payload": payload
            }
        ]
    )
    return point_id
