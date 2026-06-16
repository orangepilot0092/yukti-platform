from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
import operator
import time

print("🔵 Initializing ChatOpenAI client for Production Agentic RAG...", flush=True)
llm = ChatOpenAI(
    model="qwen-27b",
    api_key="EMPTY", 
    base_url="http://192.168.29.96:8001/v1",
    temperature=0,
    timeout=30,  # Guardrail: Abort slow LLM calls
    max_retries=0
)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    steps_taken: int
    start_time: float
    error: Optional[str]

MAX_STEPS = 5  # Guardrail: Prevent infinite loops

def build_research_agent(tools):
    print(f"🔵 Binding {len(tools)} dynamic MCP tools to LLM...", flush=True)
    llm_with_tools = llm.bind_tools(tools)

    async def agent_node(state: AgentState):
        # Guardrail: Check step limit
        if state.get("steps_taken", 0) >= MAX_STEPS:
            return {"error": f"Agent exceeded maximum steps ({MAX_STEPS}). Terminating to prevent infinite loop."}
        
        # Guardrail: Check timeout
        if time.time() - state.get("start_time", time.time()) > 60:
            return {"error": "Agent execution timed out after 60 seconds."}
        
        try:
            response = await llm_with_tools.ainvoke(state["messages"])
            return {"messages": [response], "steps_taken": 1}
        except Exception as e:
            return {"error": f"LLM call failed: {str(e)}"}

    def should_continue(state: AgentState):
        if state.get("error"):
            return END  # Force termination on error
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
