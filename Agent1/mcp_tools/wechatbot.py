from typing import List

from mcp.server.fastmcp import FastMCP

from pyweixin.WeChatAuto import (
    Messages,
    Files,
    AutoReply,
    Navigator,
    Monitor
)

mcp = FastMCP()


# =========================================================
# Send Message
# =========================================================

def sendmessage2friend(friend: str, message: List):

    try:

        Messages.send_messages_to_friend(friend, message)

        return f"message sent to {friend}"

    except Exception as e:

        msg = f"send message to friend error: {str(e)}"

        return msg


# =========================================================
# Send Files
# =========================================================

def sendfile2friend(friend: str, files: List):

    try:

        Files.send_files_to_friend(friend, files)

        return f"files sent to {friend}"

    except Exception as e:

        msg = f"send files to friend error: {str(e)}"

        return msg

# =========================================================
# Tool
# =========================================================

@mcp.tool(
    name="wechat_send_message",
    description="Send message to WeChat friend"
)
def wechat_send_message(
    friend: str,
    message: List[str]
):

    return sendmessage2friend(
        friend=friend,
        message=message
    )


# =========================================================
# Tool
# =========================================================

@mcp.tool(
    name="wechat_send_file",
    description="Send files to WeChat friend"
)
def wechat_send_file(
    friend: str,
    files: List[str]
):

    return sendfile2friend(
        friend=friend,
        files=files
    )


if __name__ == "__main__":

    mcp.run(transport="stdio")