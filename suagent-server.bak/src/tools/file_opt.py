"""
文件操作工具 - 用于读取和写入文件
"""
import os

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from src.consts import FileConsts

class FileReadInput(BaseModel):
    """文件读取相关参数"""
    file_name: str = Field(description="文件名")
    
class FileWriteInput(BaseModel):
    """文件写入相关参数"""
    file_name: str = Field(description="文件名")
    content: str = Field(description="文件内容，需要写入的内容")

@tool(args_schema=FileReadInput)
def read_file(file_name: str):
    """
    读取文件
    """
    with open(os.path.join(FileConsts.FILE_DIR, file_name), "r") as f:
        return f.read()
    
@tool(args_schema=FileWriteInput)
def write_file(file_name: str, content: str): 
    """
    写入文件
    """
    with open(os.path.join(FileConsts.FILE_DIR, file_name), "w") as f:
        f.write(content)
    return f"文件 {file_name} 写入成功, 内容如下：\n\"{content}\""

def create_read_file_tool():
    """
    创建读取文件工具
    """
    return read_file

def create_write_file_tool():
    """
    创建写入文件工具
    """
    return write_file
