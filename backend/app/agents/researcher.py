from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
import operator

print("🔵 Initializing ChatOpenAI client for MCP Agentic RAG...", flush=True)
llm = ChatOpenAI(
    model="qwen-27b",
    api_key="EMPTY", 
    base_url="http://192.168.29.96:8001/v1",
    temperature=0,
    timeout=60,
    max_retries=0
)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

def build_research_agent(tools):
    print(f"🔵 Binding {len(tools)} dynamic MCP tools to LLM...", flush=True)
    llm_with_tools = llm.bind_tools(tools)

    async def agent_node(state: AgentState):
        # CRITICAL FIX: Use ainvoke to prevent blocking the FastAPI event loop
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: AgentState):
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
