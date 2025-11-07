"""
终端操作工具 - 用于执行终端命令
"""

import subprocess
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class TerminalInput(BaseModel):
    """终端操作相关参数"""
    command: str = Field(description="终端命令")

@tool(args_schema=TerminalInput)
def execute_command(command: str):
    """
    执行终端命令
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f"终端命令 {command} 执行成功, 结果如下：\n\"{result.stdout}\""

def create_execute_command_tool():
    """
    创建执行终端命令工具
    """
    return execute_command