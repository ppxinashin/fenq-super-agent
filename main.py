"""
主入口文件 - 启动 FastAPI 服务
"""

import uvicorn

from src.api import create_app
from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


def main():
    """启动服务"""
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    logger.info(f"API 地址: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"API 文档: http://{settings.api_host}:{settings.api_port}/docs")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()

