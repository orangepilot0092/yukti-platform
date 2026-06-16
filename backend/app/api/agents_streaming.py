import time
import json
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.researcher import build_research_agent
from app.mcp.manager import mcp_manager

router = APIRouter(prefix="/agents", tags=["agents-streaming"])

class AgentRequest(BaseModel):
    query: str

async def generate_stream(request: AgentRequest):
    """Yields SSE events as the agent executes."""
    try:
        tools = mcp_manager.tools
        if not tools:
            yield f"data: {json.dumps({'event': 'error', 'data': 'MCP Tools not initialized'})}\n\n"
            return
            
        agent = build_research_agent(tools)
        
        initial_state = {
            "messages": [
                SystemMessage(content="You are the Yukti Enterprise Research Agent."),
                HumanMessage(content=request.query)
            ],
            "steps_taken": 0,
            "start_time": time.time(),
            "error": None
        }
        
        # Stream: Start
        yield f"data: {json.dumps({'event': 'start', 'data': '🤔 Analyzing query...'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Execute agent (simplified streaming - in production, hook into LangGraph callbacks)
        final_state = await agent.ainvoke(initial_state)
        
        if final_state.get("error"):
            yield f"data: {json.dumps({'event': 'error', 'data': final_state['error']})}\n\n"
            yield f"data: {json.dumps({'event': 'end'})}\n\n"
            return
        
        # Stream: Final answer
        final_message = final_state["messages"][-1].content
        yield f"data: {json.dumps({'event': 'answer', 'data': final_message})}\n\n"
        yield f"data: {json.dumps({'event': 'end', 'data': {'steps': final_state.get('steps_taken', 0)}})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'event': 'error', 'data': str(e)})}\n\n"
        yield f"data: {json.dumps({'event': 'end'})}\n\n"

@router.post("/research/stream")
async def stream_research_agent(request: AgentRequest):
    return StreamingResponse(
        generate_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable Nginx buffering if used
        }
    )
