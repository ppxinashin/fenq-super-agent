"""
网页搜索工具 - 使用 DuckDuckGo 搜索
"""

from typing import Optional
from langchain_core.tools import tool
from ddgs import DDGS

from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


@tool
def web_search(query: str, max_results: Optional[int] = None) -> str:
    """
    使用 DuckDuckGo 搜索网页信息
    
    Args:
        query: 搜索查询词
        max_results: 最大返回结果数（默认使用配置值）
    
    Returns:
        格式化的搜索结果字符串
    """
    if not settings.enable_web_search:
        return "网页搜索功能未启用"
    
    max_results = max_results or settings.max_search_results
    
    try:
        logger.info(f"执行网页搜索: {query}")
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return "未找到相关搜索结果"
        
        # 格式化搜索结果
        formatted_results = []
        for idx, result in enumerate(results, 1):
            title = result.get("title", "无标题")
            body = result.get("body", "无描述")
            url = result.get("href", "")
            
            formatted_results.append(
                f"{idx}. **{title}**\n"
                f"   {body}\n"
                f"   来源: {url}\n"
            )
        
        logger.info(f"搜索完成，返回 {len(results)} 条结果")
        return "\n".join(formatted_results)
    
    except Exception as e:
        logger.error(f"网页搜索失败: {str(e)}")
        return f"搜索出错: {str(e)}"


def create_web_search_tool():
    """创建网页搜索工具"""
    return web_search

