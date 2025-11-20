"""
时间格式化工具类
"""

from datetime import datetime
from typing import Optional
from pydantic import GetCoreSchema, GetJsonSchemaHandler
from pydantic_core import core_schema
import json


class FormattedDateTime:
    """
    自定义时间格式化类，用于统一API响应中的时间格式
    """

    @classmethod
    def format_datetime(cls, dt: Optional[datetime]) -> Optional[str]:
        """
        将datetime格式化为 yyyy-MM-dd HH:mm:ss 格式

        Args:
            dt: datetime对象，None时返回None

        Returns:
            格式化后的时间字符串或None
        """
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")


# 自定义Pydantic字段类型
class FormattedDateTimeField:
    """
    用于Pydantic模型的自定义时间字段类型
    自动将datetime转换为 yyyy-MM-dd HH:mm:ss 格式的字符串
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type,
        handler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._format_datetime,
            handler(source_type),
        )

    @classmethod
    def _format_datetime(cls, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


# 便捷函数
def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    便捷的时间格式化函数

    Args:
        dt: datetime对象，None时返回None

    Returns:
        格式化后的时间字符串或None
    """
    return FormattedDateTime.format_datetime(dt)