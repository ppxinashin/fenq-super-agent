"""
FastAPI应用主入口
整合所有API路由和中间件
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from src.config import settings
from src.utils.logger import get_logger

# 导入所有路由
from src.api.controller.user_controller import router as user_router
from src.api.controller.user_manage_controller import router as user_manage_router
from src.api.controller.agent_controller import router as agent_router
from src.api.controller.agent_manage_controller import router as agent_manage_router
from src.api.controller.session_controller import router as session_router
from src.api.controller.file_management_controller import router as file_management_router
from src.api.controller.memory_controller import router as memory_router

logger = get_logger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="SuAgent Server API",
    description="SuAgent智能体服务器的RESTful API接口",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加自定义中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加请求处理时间头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# 注册所有路由
app.include_router(user_router)
app.include_router(user_manage_router)
app.include_router(agent_router)
app.include_router(agent_manage_router)
app.include_router(session_router)
app.include_router(file_management_router)
app.include_router(memory_router)


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "SuAgent Server API",
        "version": "1.0.0",
        "docs_url": "/docs" if settings.debug else "Documentation disabled in production"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"全局异常捕获: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None
        }
    )


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("SuAgent Server API 启动中...")

    # 这里可以添加启动时需要执行的逻辑
    # 例如：检查数据库连接、初始化缓存等

    logger.info("SuAgent Server API 启动完成")


# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("SuAgent Server API 关闭中...")

    # 这里可以添加关闭时需要执行的逻辑
    # 例如：关闭数据库连接、清理资源等

    logger.info("SuAgent Server API 关闭完成")