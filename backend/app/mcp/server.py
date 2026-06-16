import os

# CRITICAL FIX: Silence HuggingFace and SentenceTransformers progress bars 
# using environment variables. NEVER reassign sys.stdout in MCP stdio servers.
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Yukti-Knowledge-Server")

@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """
    Searches the internal Yukti enterprise knowledge base for documents,
    PDFs, technical manuals, and company data.
    """
    # LAZY LOADING: Prevents the MCP server from blocking the handshake 
    # while PyTorch and Qdrant initialize.
    from app.vector_db.embeddings import model
    from app.vector_db.client import client, COLLECTION_NAME
    
    try:
        query_vector = model.encode(query).tolist()
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=3
        )
        if not search_result:
            return "No relevant documents found in the enterprise knowledge base."
        
        context = []
        for hit in search_result:
            filename = hit.payload.get("filename", "unknown_document")
            text = hit.payload.get("text", "")
            context.append(f"[Source: {filename}]\n{text}")
            
        return "\n\n---\n\n".join(context)
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
