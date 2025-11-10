from typing import Optional
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.workflow.rag import (
    generate_answer,
    generate_query_or_respond_factory,
    grade_documents,
    rewrite_question,
    retrieve_node,
)

def rag_workflow(agent_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    创建 RAG workflow 实例
    
    Args:
        agent_id: 智能体ID，如果为 None 则从运行时配置获取
        user_id: 用户ID，如果为 None 则从运行时配置获取
        
    Returns:
        编译后的 workflow
    """
    # 使用默认值，如果没有提供
    _agent_id = agent_id or "default"
    _user_id = user_id or "default"
    
    workflow = StateGraph(MessagesState)

    # 定义我们将循环使用的节点，使用工厂函数创建绑定了参数的节点
    workflow.add_node(generate_query_or_respond_factory(_agent_id, _user_id))
    workflow.add_node("retrieve", retrieve_node(_agent_id, _user_id))
    workflow.add_node(rewrite_question)
    workflow.add_node(generate_answer)

    workflow.add_edge(START, "generate_query_or_respond")

    # 决定是否检索
    workflow.add_conditional_edges(
        "generate_query_or_respond",
        # 评估 LLM 决策（调用 `retriever_tool` 工具或响应用户）
        tools_condition,
        {
            # 将条件输出转换为图中的节点
            "tools": "retrieve",
            END: END,
        },
    )

    # 调用 `action` 节点后的边
    workflow.add_conditional_edges(
        "retrieve",
        # 评估代理决策
        grade_documents,
    )
    workflow.add_edge("rewrite_question", "generate_query_or_respond")
    workflow.add_edge("generate_answer", END)

    # 编译
    return workflow.compile()