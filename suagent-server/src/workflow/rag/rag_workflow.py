from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from src.workflow.rag import (
    generate_answer,
    generate_query_or_respond,
    grade_documents,
    rewrite_question,
    retrieve_node,
)

workflow = StateGraph(MessagesState)

# 定义我们将循环使用的节点
workflow.add_node(generate_query_or_respond)
workflow.add_node("retrieve", retrieve_node())
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
def rag_workflow():
    return workflow.compile()