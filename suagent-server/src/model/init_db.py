"""
数据库初始化脚本
用于创建所有数据表
"""

from sqlalchemy import inspect
from src.model.base import Base
from src.model.database import engine
from src.model import User, Agent, SessionLog  # 导入所有模型以确保注册到Base.metadata
from src.utils.logger import get_logger

logger = get_logger(__name__)


def init_database():
    """
    初始化数据库
    创建所有未存在的表
    """
    try:
        # 获取数据库检查器
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # 获取所有需要创建的表
        tables_to_create = [table for table in Base.metadata.tables.keys() 
                           if table not in existing_tables]
        
        if tables_to_create:
            logger.info(f"开始创建数据表: {', '.join(tables_to_create)}")
            # 创建所有表
            Base.metadata.create_all(bind=engine)
            logger.info("数据表创建完成")
        else:
            logger.info("所有数据表已存在，无需创建")
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def drop_all_tables():
    """
    删除所有数据表（谨慎使用！）
    """
    try:
        logger.warning("开始删除所有数据表...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("所有数据表已删除")
    except Exception as e:
        logger.error(f"删除数据表失败: {e}")
        raise


if __name__ == "__main__":
    # 初始化数据库
    init_database()

