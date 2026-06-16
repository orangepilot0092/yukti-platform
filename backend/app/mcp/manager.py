import sys
import os
import asyncio
import traceback
from contextlib import AsyncExitStack
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class SearchInput(BaseModel):
    query: str = Field(description="The search query to look up in the enterprise knowledge base.")

class MCPManager:
    def __init__(self):
        self.tools = []
        self.session = None
        self._task = None
        self._ready = asyncio.Event()
        self._error = None

    async def start(self):
        print("🔵 Starting MCP Forever Task...", flush=True)
        self._task = asyncio.create_task(self._run_forever())
        try:
            # Wait up to 15 seconds for the MCP handshake to complete
            await asyncio.wait_for(self._ready.wait(), timeout=15.0)
            if self._error:
                print(f"❌ MCP Startup failed with error: {self._error}", flush=True)
            else:
                print("✅ MCP Manager is ready and tools are discovered!", flush=True)
        except asyncio.TimeoutError:
            print("❌ MCP Handshake TIMED OUT after 15 seconds. The subprocess is hanging or crashed.", flush=True)
            self._error = "Timeout"

    async def _run_forever(self):
        try:
            print("🔵 Entering MCP ExitStack...", flush=True)
            async with AsyncExitStack() as stack:
                server_params = StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "app.mcp.server"],
                    env=dict(os.environ)
                )
                print(f"🔵 Spawning subprocess: {sys.executable} -m app.mcp.server", flush=True)
                
                stdio_transport = await stack.enter_async_context(stdio_client(server_params))
                read, write = stdio_transport
                print("🔵 Subprocess spawned successfully. Entering ClientSession...", flush=True)
                
                self.session = await stack.enter_async_context(ClientSession(read, write))
                print("🔵 ClientSession entered. Sending initialize handshake...", flush=True)
                await self.session.initialize()
                print("🔵 Handshake accepted. Listing tools...", flush=True)
                
                tools_result = await self.session.list_tools()
                for tool in tools_result.tools:
                    langchain_tool = StructuredTool(
                        name=tool.name,
                        description=tool.description or "",
                        coroutine=self._create_tool_caller(tool.name),
                        args_schema=SearchInput
                    )
                    self.tools.append(langchain_tool)
                
                print(f"✅ MCP Tools discovered: {[t.name for t in self.tools]}", flush=True)
                self._ready.set() # Unblock FastAPI startup
                
                # Keep task alive forever
                while True:
                    await asyncio.sleep(3600)
                    
        except Exception as e:
            print(f"❌ MCP FOREVER TASK CRASHED: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            self._error = e
            self._ready.set() # Unblock FastAPI startup even if we crashed

    def _create_tool_caller(self, tool_name: str):
        async def call_tool(query: str):
            if not self.session:
                return "Error: MCP session not initialized."
            result = await self.session.call_tool(tool_name, {"query": query})
            return "\n".join([item.text for item in result.content if hasattr(item, 'text')])
        return call_tool

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

mcp_manager = MCPManager()
