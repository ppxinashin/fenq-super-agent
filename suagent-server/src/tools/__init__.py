"""
工具集模块 - 为 Agent 提供各种能力
"""

from .web_scraper import create_web_scraper_tool
from .calculator import create_calculator_tool
from .rag import create_rag_tool, create_long_memroy_tool
from .file_opt import create_read_file_tool, create_write_file_tool
from .terminal_opt import create_execute_command_tool
from .web_search import create_web_search_tool
from .downloader import create_downloader_tool
from .now_time import create_now_time_tool
from src.consts import AgentConsts

TOOL_MAP = {
    "web_scraper": create_web_scraper_tool(),
    "calculator": create_calculator_tool(),
    "rag": create_rag_tool(),
    "long_memroy": create_long_memroy_tool(),
    "read_file": create_read_file_tool(),
    "write_file": create_write_file_tool(),
    "execute_command": create_execute_command_tool(),
    "web_search": create_web_search_tool(),
    "downloader": create_downloader_tool(),
    "now_time": create_now_time_tool(),
}

def create_tool(tool_name: str):
    if tool_name not in AgentConsts.AVAILABLE_TOOLS:
        raise ValueError(f"Tool {tool_name} not found")
    return TOOL_MAP[tool_name]

def all_tools():
    return [
        create_web_scraper_tool(),
        create_calculator_tool(),
        create_rag_tool(),
        create_long_memroy_tool(),
        create_read_file_tool(),
        create_write_file_tool(),
        create_execute_command_tool(),
        create_web_search_tool(),
        create_downloader_tool(),
        create_now_time_tool(),
    ]

__all__ = [
    "create_web_scraper_tool",
    "create_calculator_tool",
    "create_rag_tool",
    "create_long_memroy_tool",
    "create_read_file_tool",
    "create_write_file_tool",
    "create_execute_command_tool",
    "create_web_search_tool",
    "create_downloader_tool",
    "create_now_time_tool",
    "all_tools",
]

