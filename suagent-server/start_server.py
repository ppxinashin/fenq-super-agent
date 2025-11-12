#!/home/ubuntu/miniconda3/envs/suagent-server/bin/python
"""
启动服务器脚本 - 在suagent-server conda环境中运行
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 确认当前环境
print(f"🐍 Python环境: {sys.executable}")
print(f"📦 当前环境: suagent-server conda环境")

if __name__ == "__main__":
    import uvicorn
    from src.config.settings import settings

    print(f"🚀 启动 {settings.app_name} v{settings.app_version}")
    print(f"📍 服务地址: http://{settings.api_host}:{settings.api_port}")
    print(f"📚 API文档: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"🔧 调试模式: {'开启' if settings.debug else '关闭'}")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )