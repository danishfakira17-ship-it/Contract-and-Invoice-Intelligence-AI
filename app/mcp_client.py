import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["-m", "mcp_server.server"],
)

async def list_tools() -> list[str]:
    async with stdio_client(PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [t.name for t in tools.tools]

async def call_tool(name: str, args: dict) -> dict:
    async with stdio_client(PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, args)
            text = result.content[0].text
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"result": text}