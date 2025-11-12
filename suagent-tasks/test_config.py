#!/usr/bin/env python3
"""
Configuration Test Script - 配置系统测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_config():
    """测试基础配置加载"""
    print("=== 测试基础配置加载 ===")

    try:
        from src.config.settings import settings

        print(f"✅ 配置加载成功")
        print(f"   应用名称: {settings.app_name}")
        print(f"   应用版本: {settings.app_version}")
        print(f"   调试模式: {settings.debug}")
        print(f"   日志级别: {settings.log_level}")

        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_database_config():
    """测试数据库配置"""
    print("\n=== 测试数据库配置 ===")

    try:
        from src.config.settings import settings

        print(f"✅ 数据库配置加载成功")
        print(f"   数据库URL: {settings.database_url}")
        print(f"   PostgreSQL主机: {settings.postgres_host}")
        print(f"   PostgreSQL端口: {settings.postgres_port}")
        print(f"   PostgreSQL数据库: {settings.postgres_db}")

        return True
    except Exception as e:
        print(f"❌ 数据库配置加载失败: {e}")
        return False

def test_celery_config():
    """测试 Celery 配置"""
    print("\n=== 测试 Celery 配置 ===")

    try:
        from src.config.settings import settings

        print(f"✅ Celery 配置加载成功")
        print(f"   Broker URL: {settings.celery_broker_url}")
        print(f"   Result Backend: {settings.celery_result_backend}")
        print(f"   时区: {settings.celery_timezone}")
        print(f"   Worker并发数: {settings.celery_worker_concurrency}")

        return True
    except Exception as e:
        print(f"❌ Celery 配置加载失败: {e}")
        return False

def test_minio_config():
    """测试 MinIO 配置"""
    print("\n=== 测试 MinIO 配置 ===")

    try:
        from src.config.settings import settings

        print(f"✅ MinIO 配置加载成功")
        print(f"   端点: {settings.minio_endpoint}")
        print(f"   访问密钥: {'已设置' if settings.minio_access_key else '未设置'}")
        print(f"   秘密密钥: {'已设置' if settings.minio_secret_key else '未设置'}")
        print(f"   SSL安全连接: {settings.minio_secure}")
        print(f"   存储桶: {settings.minio_memory_bucket}")

        return True
    except Exception as e:
        print(f"❌ MinIO 配置加载失败: {e}")
        return False

def test_scheduler_config():
    """测试调度器配置"""
    print("\n=== 测试调度器配置 ===")

    try:
        from src.config.settings import settings

        print(f"✅ 调度器配置加载成功")
        print(f"   最大并发用户数: {settings.max_concurrent_users}")
        print(f"   批处理大小: {settings.batch_size}")
        print(f"   记忆同步重试延迟: {settings.memory_sync_retry_delay}秒")
        print(f"   记忆同步最大重试次数: {settings.memory_sync_max_retries}")
        print(f"   记忆同步启用: {settings.memory_sync_enabled}")
        print(f"   Flower监控启用: {settings.flower_enabled}")

        return True
    except Exception as e:
        print(f"❌ 调度器配置加载失败: {e}")
        return False

def test_celery_integration():
    """测试与 Celery 的集成"""
    print("\n=== 测试与 Celery 的集成 ===")

    try:
        from src.scheduler.config import (
            CELERY_BROKER_URL,
            CELERY_RESULT_BACKEND,
            DATABASE_URL,
            MINIO_ENDPOINT,
            MEMORY_SYNC_ENABLED,
            FLOWER_ENABLED
        )

        print(f"✅ Celery 集成配置加载成功")
        print(f"   Celery Broker URL: {CELERY_BROKER_URL}")
        print(f"   Celery Result Backend: {CELERY_RESULT_BACKEND}")
        print(f"   Database URL: {DATABASE_URL}")
        print(f"   MinIO Endpoint: {MINIO_ENDPOINT}")
        print(f"   Memory Sync Enabled: {MEMORY_SYNC_ENABLED}")
        print(f"   Flower Enabled: {FLOWER_ENABLED}")

        return True
    except Exception as e:
        print(f"❌ Celery 集成配置加载失败: {e}")
        return False

def test_database_integration():
    """测试与数据库的集成"""
    print("\n=== 测试与数据库的集成 ===")

    try:
        from src.model.database import engine, SessionLocal

        print(f"✅ 数据库集成配置加载成功")
        print(f"   数据库引擎: {type(engine).__name__}")
        print(f"   会话工厂: {type(SessionLocal).__name__}")

        return True
    except Exception as e:
        print(f"❌ 数据库集成配置加载失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Fenq Super Agent - 配置系统测试")
    print("=" * 50)

    test_results = []

    # 运行所有测试
    tests = [
        test_basic_config,
        test_database_config,
        test_celery_config,
        test_minio_config,
        test_scheduler_config,
        test_celery_integration,
        test_database_integration
    ]

    for test_func in tests:
        try:
            result = test_func()
            test_results.append(result)
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 执行失败: {e}")
            test_results.append(False)

    # 测试结果汇总
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    passed = sum(test_results)
    total = len(test_results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("🎉 所有测试通过！配置系统工作正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())