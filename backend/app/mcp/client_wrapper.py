import sys
import os
from typing import List, Optional
from contextlib import AsyncExitStack
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class SearchInput(BaseModel):
    query: str = Field(description="The search query to look up in the enterprise knowledge base.")

class MCPToolWrapper:
    def __init__(self, command: str, args: List[str]):
        self.command = command
        self.args = args
        self._exit_stack: Optional[AsyncExitStack] = None
        self._session: Optional[ClientSession] = None
        self._tools: List[BaseTool] = []
    
    async def __aenter__(self):
        self._exit_stack = AsyncExitStack()
        await self._exit_stack.__aenter__()
        
        server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=dict(os.environ) # FIX: Must be a strict dict, not os._Environ
        )
        
        stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        
        self._session = await self._exit_stack.enter_async_context(ClientSession(read, write))
        await self._session.initialize()
        
        tools_result = await self._session.list_tools()
        for tool in tools_result.tools:
            langchain_tool = StructuredTool(
                name=tool.name,
                description=tool.description or "",
                coroutine=self._call_mcp_tool(tool.name),
                args_schema=SearchInput
            )
            self._tools.append(langchain_tool)
            
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._exit_stack:
            await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)
            
    def _call_mcp_tool(self, tool_name: str):
        async def call_tool(query: str):
            result = await self._session.call_tool(tool_name, {"query": query})
            return "\n".join([item.text for item in result.content if hasattr(item, 'text')])
        return call_tool
    
    @property
    def tools(self) -> List[BaseTool]:
        return self._tools
