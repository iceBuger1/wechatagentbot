import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_mcd_tools():

    client = MultiServerMCPClient(
        {
            "mcd-mcp": {
                "transport": "streamable_http",

                "url": "https://mcp.mcd.cn/mcp-servers/mcd-mcp",

                "headers": {
                    "Authorization": "Bearer yourapi"
                }
            }     
        }
    )

    tools = await client.get_tools()
    return tools
