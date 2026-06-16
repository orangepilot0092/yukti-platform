from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.agents.researcher import research_agent

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentRequest(BaseModel):
    query: str

@router.post("/research")
def run_research_agent(request: AgentRequest):
    print(f"📥 Received agent request: {request.query}", flush=True)
    try:
        initial_state = {
            "messages": [HumanMessage(content=request.query)]
        }
        print("⚙️ Invoking LangGraph...", flush=True)
        final_state = research_agent.invoke(initial_state)
        print("✅ LangGraph finished execution.", flush=True)
        
        final_message = final_state["messages"][-1].content
        
        return {
            "query": request.query,
            "response": final_message,
            "steps_taken": len(final_state["messages"]) - 1
        }
    except Exception as e:
        print(f"❌ Agent Error: {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))
