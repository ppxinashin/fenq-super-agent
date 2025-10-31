"""
健康检查路由
"""

from fastapi import APIRouter
from datetime import datetime

from src.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/ping")
async def ping():
    """简单的 ping 端点"""
    return {"message": "pong"}

