"""
获取当前时间工具
"""

from datetime import datetime
from langchain_core.tools import tool

@tool
def get_current_time() -> str:
    """
    获取当前时间
    
    返回格式化的当前时间字符串，格式为: YYYY-MM-dd HH:mm:ss
    
    Returns:
        格式化的当前时间字符串，例如 "2025-11-07 14:30:45"
    """
    try:
        # 获取当前时间
        now = datetime.now()
        
        # 格式化为指定格式
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_time
    
    except Exception as e:
        return f"获取时间失败: {str(e)}"


def create_now_time_tool():
    """创建获取当前时间工具"""
    return get_current_time

