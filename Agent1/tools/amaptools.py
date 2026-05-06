import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_amap_tools():

    client = MultiServerMCPClient(
        {       
            "mcpServers": {
                    "transport": "streamable_http",
                    "url": "https://mcp.amap.com/mcp?key=yourkeys"             
            }       
        }
    )

    tools = await client.get_tools()
    return tools

