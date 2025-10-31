"""
FastAPI 应用 - 主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.routes import agent_router, health_router
from src.utils import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="基于 LangChain 和 LangGraph 的智能 AI Agent 系统",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制来源
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(health_router, prefix="/api", tags=["健康检查"])
    app.include_router(agent_router, prefix="/api/agent", tags=["Agent"])
    
    logger.info(f"{settings.app_name} v{settings.app_version} 启动完成")
    
    return app

