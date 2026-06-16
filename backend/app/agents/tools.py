from langchain_core.tools import tool
from app.vector_db.embeddings import model
from app.vector_db.client import client, COLLECTION_NAME

@tool
def search_enterprise_knowledge(query: str) -> str:
    """
    Searches the internal Yukti enterprise knowledge base for documents,
    PDFs, technical manuals, and company data. 
    Use this tool to find specific information about company projects, 
    architecture, or uploaded documents before answering the user.
    """
    try:
        # 1. Embed the agent's query
        query_vector = model.encode(query).tolist()
        
        # 2. Search Qdrant on the AI Node
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=3 # Retrieve top 3 most relevant chunks
        )
        
        if not search_result:
            return "No relevant documents found in the enterprise knowledge base."
        
        # 3. Format the context for the LLM to read
        context = []
        for hit in search_result:
            filename = hit.payload.get("filename", "unknown_document")
            text = hit.payload.get("text", "")
            context.append(f"[Source: {filename}]\n{text}")
            
        return "\n\n---\n\n".join(context)
        
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"
