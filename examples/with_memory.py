"""
带记忆的对话示例 - 展示如何使用 Redis 记忆功能
"""

import asyncio
from src.agents import create_graph_agent
from src.tools import create_calculator_tool
from src.memory import get_redis_memory
from src.utils import get_logger
from langchain_core.messages import HumanMessage, AIMessage

logger = get_logger(__name__)


async def main():
    """带记忆的对话示例"""
    
    # 创建 Agent
    agent = create_graph_agent(tools=[create_calculator_tool()])
    
    # 创建记忆
    session_id = "example_session_001"
    memory = get_redis_memory(session_id)
    
    # 清除之前的记忆（可选）
    memory.clear()
    
    print("=" * 60)
    print("Fenq Super Agent - 带记忆的对话示例")
    print(f"会话 ID: {session_id}")
    print("=" * 60)
    print()
    
    # 多轮对话
    conversations = [
        "我叫张三，今年 25 岁",
        "我喜欢编程和人工智能",
        "你还记得我的名字吗？",
        "我今年多少岁了？",
        "我的爱好是什么？",
    ]
    
    for user_message in conversations:
        print(f"👤 用户: {user_message}")
        
        # 获取历史记忆
        history = memory.messages
        
        # 构建上下文
        if history:
            context = "历史对话:\n"
            for msg in history[-6:]:  # 最近 6 条消息
                role = "用户" if msg.type == "human" else "助手"
                context += f"{role}: {msg.content}\n"
            context += f"\n当前问题: {user_message}"
        else:
            context = user_message
        
        # 调用 Agent
        response = await agent.ainvoke(context)
        
        print(f"🤖 Agent: {response}")
        print()
        
        # 保存到记忆
        memory.add_message(HumanMessage(content=user_message))
        memory.add_message(AIMessage(content=response))
        
        print("-" * 60)
        print()
    
    print("\n✅ 对话完成！记忆已保存到 Redis。")
    print(f"📝 总共保存了 {len(memory.messages)} 条消息。")


if __name__ == "__main__":
    asyncio.run(main())

