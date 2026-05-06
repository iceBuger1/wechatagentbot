from utils.mcp import create_mcp_stdio_client


async def get_stdio_mysql_tools():
    params = {
        "command": "python",
        "args": [
            r"C:\Users\19553\Desktop\code1\Agent\mcp_tools\mysql_tools.py",
        ]
    }

    client, tools = await create_mcp_stdio_client("mysql_tools", params)

    return tools