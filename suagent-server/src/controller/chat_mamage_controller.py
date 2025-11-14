"""
聊天管理控制器
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Dict, Any

from fastapi.responses import StreamingResponse
from src.api_middlewares.role_middleware import require_roles, require_admin
from src.api_middlewares.jwt_middleware import get_current_user_from_token
from src.response.auth_response import UserInfo
from src.service.chat_service import chat_service
from src.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["聊天管理"])

@router.get("/chat")
async def chat(agent_id: str, session_id: int, message: str, current_user: UserInfo = Depends(get_current_user_from_token)):
    """
    根据所在智能体、会话ID、用户ID、消息，开始聊天
    """
    
    return StreamingResponse(
        chat_service.chat(session_id, agent_id, message, current_user.username),
        media_type="text/event-stream",
    )