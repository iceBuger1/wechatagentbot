import asyncio
import time

from langchain_openai import ChatOpenAI

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

async def create_agent():

    memory = FileSaver()

    print("加载 amap tools...")
    amap_tools = await get_amap_tools()

    print("加载 mcd tools...")
    mcd_tools = await get_mcd_tools()

    print("加载 mysql tools...")
    mysql_tools = await get_stdio_mysql_tools()

    print("加载 generate pic tools...")
    wife_tools = await get_generate_pic_tools()

    print("加载 wechat tools...")
    wechat_tools = await get_wechatbot_tools()

    tools = (
        mysql_tools
        + wife_tools
        + wechat_tools
        + amap_tools
        + mcd_tools
    )

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
        configurable={"thread_id": 55},
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

async def main():

    global agent

    # 初始化 Agent
    agent = await create_agent()

    # 打开聊天窗口
    dialog_window = Navigator.open_seperate_dialog_window(
        friend='奶龙'
    )

    print("微信监听已启动")

    # 开始监听
    await AutoReply.auto_reply_to_friend(
        dialog_window=dialog_window,
        duration='60min',
        callback=run_agent
    )


# =========================================================
# Start
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())