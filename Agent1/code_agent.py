import asyncio
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from tools.mysql_tools import get_stdio_mysql_tools
from tools.amaptools import get_amap_tools
from tools.mcdtools import get_mcd_tools
from tools.generate_pic_tools import get_generate_pic_tools
from tools.wechatbot import get_wechatbot_tools

from tools.file_saver import FileSaver

llm = ChatOpenAI(model = 'qwen3_4b_instruct',  base_url="http://localhost:18000/v1", api_key ='None')

def format_debug_output(step_name: str, content: str, is_tool_call = False) -> None:
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


async def run_agent():
    #memory = FileSaver()

    memory = MemorySaver()

    mysql_tools = await get_stdio_mysql_tools()
    wife_tools = await get_generate_pic_tools()
    amap_tools = await get_amap_tools()
    mcd_tools = await get_mcd_tools()


    tools =  mysql_tools + wife_tools + mcd_tools + amap_tools
    # tools = file_tools + terminal_tools + rag_self_tools + browser_tools
    # tools = file_tools + browser_tools

    prompt = PromptTemplate.from_template(template="""# 角色
你是一名优秀的工程师，你的名字叫做{name}""")
    
    agent = create_react_agent(
        model = llm,
        tools=tools,
        checkpointer=memory,
        debug=False,
        prompt=SystemMessage(content=prompt.format(name="Bot")),
    )

    config = RunnableConfig(configurable={"thread_id": 5}, recursion_limit=100)

    while True:
        user_input = input("用户: ")

        if user_input.lower() == "exit":
            break

        print("\n🤖 助手正在思考...")
        print("=" * 60)
#         user_prompt = \
# f"""# 要求
# 执行任务之前先使用 query_rag 工具查询知识库，根据知识库中的知识执行任务
#
# # 用户问题
# {user_input}"""
        user_prompt = user_input

        iteration_count = 0
        start_time = time.time()
        last_tool_time = start_time


        async for chunk in agent.astream(input={"messages": user_prompt}, config=config):
            iteration_count += 1

            print(f"\n📊 第 {iteration_count} 步执行：")
            print("-" * 30)

            items = chunk.items()

            for node_name, node_output in items:
                if "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg, AIMessage):
                            if msg.content:
                                format_debug_output("AI思考", msg.content)
                            else:
                                for tool in msg.tool_calls:
                                    format_debug_output("工具调用", f"{tool['name']}: {tool['args']}")

                        elif isinstance(msg, ToolMessage):
                            tool_name = getattr(msg, "name", "unknown")
                            tool_content = msg.content

                            current_time = time.time()
                            tool_duration = current_time - last_tool_time
                            last_tool_time = current_time

                            tool_result = f"""🔧 工具：{tool_name}
📤 结果：
{tool_content}
✅ 状态：执行完成，可以开始下一个任务
️⏱️ 执行时间：{tool_duration:.2f}秒"""

                            format_debug_output("工具执行结果", tool_result, is_tool_call=True)

                        else:
                            format_debug_output("未实现", f"暂未实现的打印内容: {chunk}")

        print()


asyncio.run(run_agent())