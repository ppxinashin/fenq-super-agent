from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from src.config import settings

wrapper = DuckDuckGoSearchAPIWrapper(region="cn-zh", max_results=settings.max_search_results)
search_on = DuckDuckGoSearchResults(api_wrapper=wrapper, output_format="list")

@tool
def search_off(query: str) -> str:
    """
    使用搜索工具
    """
    return "搜索工具已关闭"

def create_web_search_tool():
    """
    创建网页搜索工具
    """
    if not settings.enable_web_search:
        return search_off
    
    return search_on