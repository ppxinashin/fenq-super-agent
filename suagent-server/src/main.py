"""
FastAPI应用主入口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.settings import settings
from src.controller.auth_controller import router as auth_router
from src.controller.user_manage_controller import router as user_manage_router
from src.api_middlewares.exception_middleware import ExceptionMiddleware
from src.utils.logger import get_logger
import uvicorn

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

# 添加异常处理中间件（需要最先添加，以便捕获所有异常）
app.add_middleware(ExceptionMiddleware)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的允许域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_manage_router, prefix="/api/v1")


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


# 注意：由于已经添加了 ExceptionMiddleware，以下异常处理器不再需要
# ExceptionMiddleware 会统一处理所有异常并返回标准JSON格式

# @app.exception_handler(HTTPException)
# async def http_exception_handler(request, exc):
#     """HTTP异常处理器"""
#     return {
#         "code": exc.status_code,
#         "message": exc.detail,
#         "result": None
#     }
#
#
# @app.exception_handler(Exception)
# async def general_exception_handler(request, exc):
#     """通用异常处理器"""
#     logger.error(f"未处理的异常: {exc}", exc_info=True)
#     return {
#         "code": 500,
#         "message": "服务器内部错误",
#         "result": None
#     }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )