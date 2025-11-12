from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String
from sqlalchemy.orm import declarative_base
from src.utils import Snowflake

DeclarativeBase = declarative_base()

# 创建全局雪花ID生成器
_snowflake_generator = Snowflake(worker_id=1, datacenter_id=1)

def generate_id():
    """生成雪花ID"""
    return _snowflake_generator.generate_id()

class Base(DeclarativeBase):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, default=generate_id)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(100), default="admin")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = Column(String(100), default="admin")
    is_deleted = Column(Boolean, default=False)