from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper

wrapper = DuckDuckGoSearchAPIWrapper(region="cn-zh", time="d")
search = DuckDuckGoSearchResults(api_wrapper=wrapper, output_format="list")

def create_web_search_tool():
    """
    创建网页搜索工具
    """
    return search