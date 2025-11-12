"""
日志配置模块 - 使用 Loguru
"""

import sys
from loguru import logger
from pathlib import Path

from src.config.settings import settings


def setup_logger():
    """配置 Loguru 日志"""
    # 移除默认处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )

    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 添加文件输出（按日期滚动）
    logger.add(
        log_dir / "fenq_agent_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天午夜轮换
        retention="30 days",  # 保留 30 天
        compression="zip",  # 压缩旧日志
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        encoding="utf-8",
    )

    # 添加错误日志单独输出
    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        encoding="utf-8",
    )

    return logger


def get_logger(name: str = None):
    """获取 logger 实例"""
    if name:
        return logger.bind(name=name)
    return logger


# 初始化日志
setup_logger()

