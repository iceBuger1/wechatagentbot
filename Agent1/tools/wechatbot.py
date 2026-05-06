from utils.mcp import create_mcp_stdio_client


async def get_wechatbot_tools():
    params = {
        "command": "python",
        "args": [
            r"C:\Users\19553\Desktop\code1\Agent\mcp_tools\wechatbot.py",
        ]
    }

    client, tools = await create_mcp_stdio_client("wechatbot_tools", params)

    return tools