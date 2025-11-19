"""
FastAPI应用主入口
"""

import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage
from starlette.responses import StreamingResponse
from src.config.settings import settings
from src.controller.auth_controller import router as auth_router
from src.controller.user_manage_controller import router as user_manage_router
from src.controller.agent_manage_controller import router as agent_manage_router
from src.controller.chat_controller import router as chat_router
from src.controller.file_manage_controller import router as file_manage_router
from src.api_middlewares.exception_middleware import ExceptionMiddleware
from src.api_middlewares.path_middleware import PathNormalizeMiddleware
from src.middlewares import get_my_logger_middleware
from src.utils.logger import get_logger
from src.tools import all_tools
import uvicorn
from src.agents import MyAgent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool


# 初始化 LLM（OpenAI / Azure / 本地模型都可以）
llm = ChatOpenAI(
    model="qwen3-max",
    temperature=0,
)

# 创建 Agent（create_agent 自动构建一个图）
agent = MyAgent(
    llm=llm,
    middlewares=[get_my_logger_middleware()],
    tools=[]
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动Fenq Super Agent服务器...")

    try:
        # 初始化数据库（如果需要）
        from src.model.init_db import init_database
        init_database()
        logger.info("数据库初始化完成")

        # 测试Redis连接
        from src.service.token_service import token_service
        if token_service.redis_client:
            token_service.redis_client.ping()
            logger.info("Redis连接正常")
        else:
            logger.warning("Redis连接失败，部分功能可能不可用")

        logger.info("服务器启动完成")

    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise

    yield

    # 关闭时执行
    logger.info("正在关闭Fenq Super Agent服务器...")

    try:
        # 清理过期token
        from src.service.token_service import token_service
        cleaned_count = token_service.cleanup_expired_tokens()
        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 个过期token")

        # 关闭Redis连接
        if token_service.redis_client:
            token_service.redis_client.close()
            logger.info("Redis连接已关闭")

        logger.info("服务器关闭完成")

    except Exception as e:
        logger.error(f"服务器关闭时发生异常: {e}")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    description="Fenq Super Agent - AI智能体服务器",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# 添加路径规范化中间件（最先添加，处理双斜杠等路径问题）
app.add_middleware(PathNormalizeMiddleware)

# 添加CORS中间件（需要在异常处理之前，因为FastAPI中间件是反向执行的）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的允许域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # 暴露所有响应头，确保CORS正常工作
)

# 添加异常处理中间件（需要最先添加，以便捕获所有异常）
app.add_middleware(ExceptionMiddleware)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_manage_router, prefix="/api/v1")
app.include_router(agent_manage_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(file_manage_router, prefix="/api/v1")



@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        from src.model.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        db_status = "unhealthy"

    try:
        # 检查Redis连接
        from src.service.token_service import token_service
        if token_service.redis_client:
            token_service.redis_client.ping()
            redis_status = "healthy"
        else:
            redis_status = "disconnected"
    except Exception as e:
        logger.error(f"Redis健康检查失败: {e}")
        redis_status = "unhealthy"

    overall_status = "healthy" if db_status == "healthy" else "unhealthy"

    return {
        "status": overall_status,
        "version": settings.app_version,
        "components": {
            "database": db_status,
            "redis": redis_status
        }
    }

async def agent_stream(prompt: str):
    """
    把 LangGraph 的 stream 包装成 FastAPI 能用的 async generator。
    """

    # astream = 异步流式输出
    async for event in agent.astream({"messages": [HumanMessage(content=prompt)]}):
        logger.info(f"Agent Event: {event}")
        if isinstance(event[0], AIMessageChunk):
            data = json.dumps({"text": event[0].content}, ensure_ascii=False)
        elif isinstance(event[0], ToolMessage):
            data = json.dumps({"text": f'> 已调用{event[0].name}\n\n'}, ensure_ascii=False)
            
        yield f"data: {data}\n\n"
    
    yield "data: [DONE]\n\n"


@app.get("/agent_health")
async def agent_health(m: str = "你好，这里是Fenq Super Agent，目前服务器已经启动，如果能够接收我的消息，请回复“收到”"):
    """
    智能体健康检测
    """
    return StreamingResponse(
        agent_stream(m),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )