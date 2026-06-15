import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Point to the AI Node's IP address
QDRANT_URL = os.getenv("QDRANT_URL", "http://192.168.29.96:6333")
COLLECTION_NAME = "yukti_documents"

# Initialize the client
client = QdrantClient(url=QDRANT_URL)

def ensure_collection_exists(vector_size: int = 384):
    """
    Checks if the collection exists. If not, creates it.
    384 is the default vector size for 'all-MiniLM-L6-v2' embedding model.
    """
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"✅ Created Qdrant collection: {COLLECTION_NAME}")
    else:
        print(f"✅ Qdrant collection already exists: {COLLECTION_NAME}")

# Test the connection on module import
try:
    client.get_collections()
    print("✅ Successfully connected to Qdrant on AI Node!")
except Exception as e:
    print(f"❌ Failed to connect to Qdrant: {e}")
