from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from app.agents.tools import mock_web_search
import operator

print("🔵 Initializing ChatOpenAI client...", flush=True)
# CRITICAL FIX: Use 'base_url' and 'api_key' for modern langchain-openai
llm = ChatOpenAI(
    model="qwen-27b",
    api_key="EMPTY", 
    base_url="http://192.168.29.96:8001/v1", # Forces local connection
    temperature=0,
    timeout=30, # Force a timeout so it doesn't hang forever
    max_retries=0
)

tools = [mock_web_search]
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

def agent_node(state: AgentState):
    print(f"🟢 Agent Node called. Messages in state: {len(state['messages'])}", flush=True)
    try:
        response = llm_with_tools.invoke(state["messages"])
        print(f"🟢 LLM responded. Tool calls detected: {len(response.tool_calls)}", flush=True)
        return {"messages": [response]}
    except Exception as e:
        print(f"🔴 LLM ERROR: {e}", flush=True)
        raise e

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        print("🟡 Routing to Tools node.", flush=True)
        return "tools"
    print("🏁 Routing to END.", flush=True)
    return END

def build_research_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END}
    )
    workflow.add_edge("tools", "agent")
    return workflow.compile()

research_agent = build_research_agent()
print("🚀 Research Agent Graph compiled successfully.", flush=True)
