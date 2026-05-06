from utils.mcp import create_mcp_stdio_client


async def get_generate_pic_tools():
    params = {
        "command": "python",
        "args": [
            r"C:\Users\19553\Desktop\code1\Agent\mcp_tools\generate_pic_tools.py",
        ]
    }

    client, tools = await create_mcp_stdio_client("generate_pic_tools", params)

    return tools