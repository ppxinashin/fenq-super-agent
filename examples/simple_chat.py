"""
简单对话示例 - 基础的 Agent 对话
"""

import asyncio
from src.agents import create_graph_agent
from src.tools import (
    create_web_search_tool,
    create_calculator_tool,
)
from src.utils import get_logger

logger = get_logger(__name__)


async def main():
    """简单对话示例"""
    
    # 创建工具
    tools = [
        create_web_search_tool(),
        create_calculator_tool(),
    ]
    
    # 创建 Agent
    agent = create_graph_agent(tools=tools)
    
    print("=" * 60)
    print("Fenq Super Agent - 简单对话示例")
    print("=" * 60)
    print()
    
    # 示例对话
    questions = [
        "你好，请介绍一下你自己",
        "计算一下 123 * 456 等于多少",
        "搜索一下 2024 年最新的 AI 技术趋势",
    ]
    
    for question in questions:
        print(f"👤 用户: {question}")
        print()
        
        # 调用 Agent
        response = await agent.ainvoke(question)
        
        print(f"🤖 Agent: {response}")
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    asyncio.run(main())

