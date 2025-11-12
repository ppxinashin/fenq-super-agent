#!/home/ubuntu/miniconda3/envs/suagent-server/bin/python
"""
环境检查脚本 - 确认在正确的conda环境中运行
"""

import os
import sys
import subprocess

def check_environment():
    """检查当前环境"""
    print("🔍 环境检查报告")
    print("=" * 50)

    # Python环境检查
    print(f"🐍 Python路径: {sys.executable}")
    print(f"🐍 Python版本: {sys.version}")

    # 检查是否在正确的conda环境
    conda_prefix = os.path.dirname(os.path.dirname(sys.executable))
    conda_env = os.path.basename(conda_prefix)
    print(f"📦 Conda环境: {conda_env}")
    print(f"📦 Conda环境路径: {conda_prefix}")

    if conda_env == "suagent-server":
        print("✅ 在正确的conda环境中")
    else:
        print("❌ 不在suagent-server conda环境中")
        return False

    # 检查工作目录
    work_dir = os.getcwd()
    print(f"📁 工作目录: {work_dir}")
    expected_dir = "/home/ubuntu/fenq-super-agent/suagent-server"
    if work_dir == expected_dir:
        print("✅ 在正确的工作目录中")
    else:
        print(f"❌ 不在正确的工作目录中，应该是在: {expected_dir}")
        return False

    # 检查Python路径
    src_path = os.path.join(work_dir, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"🔧 已添加src路径到Python路径")

    # 测试关键包导入
    print("\n📦 检查关键包:")

    packages_to_check = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("jose", "Python-JOSE"),
        ("loguru", "Loguru"),
        ("aiohttp", "aiohttp")
    ]

    for package, name in packages_to_check:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - 未安装")
            return False

    # 测试认证模块导入
    print("\n🔐 检查认证模块:")
    try:
        from src.api_middlewares import get_current_user_from_token
        from src.service import auth_service, token_service
        from src.controller.auth_controller import router
        from src.model.database import get_db
        print("✅ 所有认证模块导入成功")
    except ImportError as e:
        print(f"❌ 认证模块导入失败: {e}")
        return False

    print("\n🎉 环境检查完成 - 所有检查通过!")
    return True

def show_usage_info():
    """显示使用信息"""
    print("\n📚 使用信息:")
    print("=" * 30)
    print("🚀 启动服务器:")
    print("   python start_server.py")
    print()
    print("🧪 运行测试:")
    print("   python test_auth.py")
    print()
    print("📖 访问API文档:")
    print("   http://localhost:8000/docs")
    print()
    print("🏥 健康检查:")
    print("   http://localhost:8000/health")

if __name__ == "__main__":
    success = check_environment()

    if success:
        show_usage_info()
        sys.exit(0)
    else:
        print("\n❌ 环境检查失败，请修复上述问题")
        sys.exit(1)