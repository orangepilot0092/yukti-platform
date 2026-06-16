import time
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.researcher import build_research_agent
from app.mcp.manager import mcp_manager

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentRequest(BaseModel):
    query: str

@router.post("/research")
async def run_research_agent(request: AgentRequest):
    print(f"📥 Received Production Agentic RAG request: {request.query}", flush=True)
    try:
        tools = mcp_manager.tools
        if not tools:
            raise Exception("MCP Tools not initialized.")
            
        agent = build_research_agent(tools)
        
        # Initialize state with guardrail metadata
        initial_state = {
            "messages": [
                SystemMessage(content="You are the Yukti Enterprise Research Agent. Use the provided MCP tools to search the company knowledge base before answering."),
                HumanMessage(content=request.query)
            ],
            "steps_taken": 0,
            "start_time": time.time(),
            "error": None
        }
        
        final_state = await agent.ainvoke(initial_state)
        
        # Handle guardrail termination
        if final_state.get("error"):
            return {
                "query": request.query,
                "response": f"⚠️ {final_state['error']}",
                "steps_taken": final_state.get("steps_taken", 0),
                "status": "terminated"
            }
        
        final_message = final_state["messages"][-1].content
        
        return {
            "query": request.query,
            "response": final_message,
            "steps_taken": final_state.get("steps_taken", 0),
            "status": "success"
        }
    except Exception as e:
        print(f"❌ Agent Error: {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))
