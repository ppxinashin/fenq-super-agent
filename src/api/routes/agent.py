"""
Agent 相关路由
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from src.agents import create_graph_agent
from src.tools import (
    create_web_search_tool,
    create_web_scraper_tool,
    create_calculator_tool,
)
from src.memory import get_redis_memory
from src.utils import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ===== 请求/响应模型 =====

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息", min_length=1)
    session_id: Optional[str] = Field(default="default", description="会话 ID")
    use_memory: bool = Field(default=False, description="是否使用记忆功能")
    enable_tools: bool = Field(default=True, description="是否启用工具")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    reply: str = Field(..., description="Agent 回复")
    session_id: str = Field(..., description="会话 ID")


class StreamChatRequest(BaseModel):
    """流式聊天请求模型"""
    message: str = Field(..., description="用户消息", min_length=1)
    session_id: Optional[str] = Field(default="default", description="会话 ID")
    enable_tools: bool = Field(default=True, description="是否启用工具")


# ===== 路由端点 =====

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    与 Agent 对话（标准模式）
    
    Args:
        request: 聊天请求
    
    Returns:
        Agent 的回复
    """
    try:
        logger.info(f"收到聊天请求，会话 ID: {request.session_id}")
        
        # 创建工具列表
        tools = []
        if request.enable_tools:
            tools = [
                create_web_search_tool(),
                create_web_scraper_tool(),
                create_calculator_tool(),
            ]
        
        # 创建 Agent
        agent = create_graph_agent(tools=tools)
        
        # 处理记忆
        if request.use_memory:
            memory = get_redis_memory(request.session_id)
            
            # 获取历史消息
            history_messages = memory.messages
            
            # 构建完整的消息上下文
            from langchain_core.messages import HumanMessage
            full_message = f"历史对话:\n"
            for msg in history_messages[-10:]:  # 只保留最近 10 条
                full_message += f"{msg.type}: {msg.content}\n"
            full_message += f"\n当前问题: {request.message}"
            
            # 调用 Agent
            reply = await agent.ainvoke(full_message)
            
            # 保存到记忆
            memory.add_message(HumanMessage(content=request.message))
            from langchain_core.messages import AIMessage
            memory.add_message(AIMessage(content=reply))
        else:
            # 直接调用 Agent
            reply = await agent.ainvoke(request.message)
        
        logger.info(f"聊天请求处理完成，会话 ID: {request.session_id}")
        
        return ChatResponse(
            reply=reply,
            session_id=request.session_id,
        )
    
    except Exception as e:
        logger.error(f"聊天请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: StreamChatRequest):
    """
    与 Agent 对话（流式模式）
    
    Args:
        request: 流式聊天请求
    
    Returns:
        Server-Sent Events 流
    """
    try:
        logger.info(f"收到流式聊天请求，会话 ID: {request.session_id}")
        
        # 创建工具列表
        tools = []
        if request.enable_tools:
            tools = [
                create_web_search_tool(),
                create_web_scraper_tool(),
                create_calculator_tool(),
            ]
        
        # 创建 Agent
        agent = create_graph_agent(tools=tools)
        
        async def generate():
            """生成流式响应"""
            try:
                for output in agent.stream(request.message):
                    messages = output.get("messages", [])
                    for msg in messages:
                        if hasattr(msg, "content") and msg.content:
                            # 发送 SSE 格式数据
                            data = json.dumps(
                                {"content": msg.content, "type": msg.type},
                                ensure_ascii=False,
                            )
                            yield f"data: {data}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"流式生成失败: {str(e)}")
                error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
        )
    
    except Exception as e:
        logger.error(f"流式聊天请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@router.delete("/memory/{session_id}")
async def clear_memory(session_id: str):
    """
    清除指定会话的记忆
    
    Args:
        session_id: 会话 ID
    
    Returns:
        操作结果
    """
    try:
        logger.info(f"清除会话记忆，会话 ID: {session_id}")
        
        memory = get_redis_memory(session_id)
        memory.clear()
        
        return {
            "status": "success",
            "message": f"已清除会话 {session_id} 的记忆",
        }
    
    except Exception as e:
        logger.error(f"清除记忆失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清除记忆时出错: {str(e)}")

