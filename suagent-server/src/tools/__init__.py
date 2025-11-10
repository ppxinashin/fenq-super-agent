"""
工具集模块 - 为 Agent 提供各种能力
"""

from .web_scraper import create_web_scraper_tool
from .calculator import create_calculator_tool
from .rag import create_rag_tool
from .file_opt import create_read_file_tool, create_write_file_tool
from .terminal_opt import create_execute_command_tool
from .web_search import create_web_search_tool
from .downloader import create_downloader_tool
from .now_time import create_now_time_tool
from .memory_4ever import create_memory_4ever_tool, create_amemory_4ever_tool

def all_tools():
    return [
        create_web_scraper_tool(),
        create_calculator_tool(),
        create_rag_tool(),
        create_read_file_tool(),
        create_write_file_tool(),
        create_execute_command_tool(),
        create_web_search_tool(),
        create_downloader_tool(),
        create_now_time_tool(),
        create_memory_4ever_tool(),
        create_amemory_4ever_tool(),
    ]

__all__ = [
    "create_web_scraper_tool",
    "create_calculator_tool",
    "create_rag_tool",
    "create_read_file_tool",
    "create_write_file_tool",
    "create_execute_command_tool",
    "create_web_search_tool",
    "create_downloader_tool",
    "create_now_time_tool",
    "create_memory_4ever_tool",
    "create_amemory_4ever_tool",
    "all_tools",
]

