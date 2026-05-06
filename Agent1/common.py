import asyncio
import time
from typing import List
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from pyweixin import Messages, Files
from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    SystemMessage
)

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig

from langgraph.prebuilt import create_react_agent

from tools.mysql_tools import get_stdio_mysql_tools
from tools.amaptools import get_amap_tools
from tools.mcdtools import get_mcd_tools
from tools.generate_pic_tools import get_generate_pic_tools
from tools.wechatbot import get_wechatbot_tools

from tools.file_saver import FileSaver

from pyweixin.WeChatAuto import (
    AutoReply,
    Navigator
)


# =========================================================
# LLM
# =========================================================

llm = ChatOpenAI(
    model='qwen3_4b_instruct',
    base_url="http://localhost:18000/v1",
    api_key='None'
)

# =========================================================
# Global Agent
# =========================================================

agent = None

# =========================================================
# Debug Output
# =========================================================

def format_debug_output(
    step_name: str,
    content: str,
    is_tool_call=False
):

    if is_tool_call:

        print(f'🔄 【工具调用】 {step_name}')
        print("-" * 40)
        print(content.strip())
        print("-" * 40)

    else:

        print(f"💭 【{step_name}】")
        print("-" * 40)
        print(content.strip())
        print("-" * 40)


# =========================================================
# Create Agent
# =========================================================

async def create_tools():

    print("加载 amap tools...")
    amap_tools = await get_amap_tools()

    print("加载 mcd tools...")
    mcd_tools = await get_mcd_tools()

    print("加载 mysql tools...")
    mysql_tools = await get_stdio_mysql_tools()

    print("加载 generate pic tools...")
    wife_tools = await get_generate_pic_tools()

    #print("加载 wechat tools...")
    #wechat_tools = await get_wechatbot_tools()

    tools = mysql_tools + wife_tools + amap_tools + mcd_tools
    
    return tools

def create_agent(tools):
    memory = FileSaver()
    prompt = PromptTemplate.from_template(
        template="""
# 角色
你是一名优秀的工程师，你的名字叫做{name}
"""
    )
    agent_instance = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        debug=False,
        prompt=SystemMessage(
            content=prompt.format(name="Bot")
        ),
    )

    print("Agent 初始化完成")

    return agent_instance


# =========================================================
# Agent Function
# =========================================================

async def run_agent(prompt_text: str):

    if 'Bot' not in prompt_text:
        return

    global agent

    config = RunnableConfig(
        configurable={"thread_id": 1110},
        recursion_limit=100
    )

    print("\n🤖 助手正在思考...")
    print("=" * 60)

    iteration_count = 0

    start_time = time.time()

    last_tool_time = start_time

    final_response = ""

    async for chunk in agent.astream(
        input={"messages": prompt_text},
        config=config
    ):

        iteration_count += 1

        print(f"\n📊 第 {iteration_count} 步执行：")
        print("-" * 30)

        items = chunk.items()

        for node_name, node_output in items:

            if "messages" in node_output:

                for msg in node_output["messages"]:

                    # =====================================
                    # AI Message
                    # =====================================

                    if isinstance(msg, AIMessage):

                        if msg.content:

                            final_response = msg.content

                            format_debug_output(
                                "AI思考",
                                msg.content
                            )

                        else:

                            for tool in msg.tool_calls:

                                format_debug_output(
                                    "工具调用",
                                    f"{tool['name']}: {tool['args']}"
                                )

                    # =====================================
                    # Tool Message
                    # =====================================

                    elif isinstance(msg, ToolMessage):

                        tool_name = getattr(
                            msg,
                            "name",
                            "unknown"
                        )

                        tool_content = msg.content

                        current_time = time.time()

                        tool_duration = (
                            current_time - last_tool_time
                        )

                        last_tool_time = current_time

                        tool_result = f"""
🔧 工具：{tool_name}

📤 结果：
{tool_content}

✅ 状态：执行完成，可以开始下一个任务

⏱️ 执行时间：{tool_duration:.2f}秒
"""

                        format_debug_output(
                            "工具执行结果",
                            tool_result,
                            is_tool_call=True
                        )

    return final_response


# =========================================================
# Main
# =========================================================

async def main(dialog_window):

    global agent

    tools = await create_tools()

    def sendmessage2friend(friend: str, message: List):
        try:
            Messages.send_messages_to_friend(friend, message)
            return f"message sent to {friend}"
        except Exception as e:
            msg = f"send message to friend error: {str(e)}"
            return msg

    def sendfile2friend(friend: str, files: List):
        try:
            Files.send_files_to_friend(friend, files, close_weixin = False, _main_window = dialog_window)
            return f"files sent to {friend}"
        except Exception as e:
            msg = f"send files to friend error: {str(e)}"
            return msg

    @tool(
        description="Send message to WeChat friend"
    )
    def wechat_send_message(
        friend: str,
        message: List[str]
    ):
        """Send message to WeChat friend"""
        return sendmessage2friend(
            friend=friend,
            message=message
        )

    @tool(
        description="Send files to WeChat friend"
    )
    def wechat_send_file(
        friend: str,
        files: List[str]
    ):
        """Send files to WeChat friend"""
        return sendfile2friend(
            friend=friend,
            files=files
        )
    
    tools.extend([
    wechat_send_message,
    wechat_send_file
    ])

    # 初始化 Agent
    agent = create_agent(tools)
    print("微信监听已启动")

    # 开始监听
    await AutoReply.auto_reply_to_friend(
        dialog_window = dialog_window,
        duration = '60min',
        callback = run_agent
    )

if __name__ == "__main__":

    # 打开聊天窗口
    dialog_window = Navigator.open_seperate_dialog_window(
        friend='waqaear',
    )
    
    asyncio.run(main(dialog_window))