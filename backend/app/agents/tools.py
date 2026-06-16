from langchain_core.tools import tool

@tool
def mock_web_search(query: str) -> str:
    """
    Searches for internal knowledge about the Yukti Platform and VYUHLEADS.ORG.
    Use this tool when the user asks about Advait Sanap's projects, architecture, or business goals.
    """
    query_lower = query.lower()
    if "yukti" in query_lower or "platform" in query_lower:
        return "Yukti is an Enterprise AI Operating System built by Advait Sanap. It features a distributed 2-node architecture, RAG, Agentic workflows, and local LLM inference via vLLM on an MSI Edge Expert."
    elif "vyuhleads" in query_lower or "real estate" in query_lower:
        return "VYUHLEADS.ORG is an AI-first lead intelligence platform targeting Real Estate and Banking in Mumbai, featuring AI scoring, WhatsApp automation, and CRM pipeline tracking."
    else:
        return f"No specific internal knowledge found for '{query}'. Please rely on general knowledge."
