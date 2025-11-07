"""
下载工具
"""
import os
import requests
from typing import Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from src.consts import FileConsts

class DownloaderInput(BaseModel):
    url: str = Field(description='下载链接')
    fileName: Optional[str] = Field(description='文件名', default=None)
    
@tool(args_schema=DownloaderInput)
def downloader(url: str, fileName: Optional[str] = None) -> str:
    """
    下载文件
    """
    if fileName is None:
        fileName = url.split('/')[-1]
    with open(os.path.join(FileConsts.FILE_DIR, fileName), 'wb') as f:
        f.write(requests.get(url).content)
    return f'文件 {fileName} 下载成功'

def create_downloader_tool():
    """
    创建下载工具
    """
    return downloader