import os
import time
import uuid
import asyncio
import aiohttp
import requests
import zipfile
import tempfile
from io import BytesIO
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.rag.chunker import Chunker
from src.utils import get_logger
from src.config import settings

class OCRChunker(Chunker):
    """OCR文档分块器，使用MinerU API处理需要OCR的文档"""
    _logger = get_logger(__name__)
    
    def __init__(self):
        """初始化OCR分块器"""
        # 从环境变量获取MinerU API Token
        self.api_token = settings.mineru_api_token
        if not self.api_token:
            self._logger.warning("未配置MINERU_API_TOKEN环境变量，OCR功能可能无法使用")
        
        self.api_base_url = "https://mineru.net/api/v4"
        self.timeout = 3000  # 超时时间
        self.retry_interval = 20  # 尝试次数
    
    def _parse(self, data: bytes) -> str:
        """
        使用MinerU API解析需要OCR的文档
        
        Args:
            data: 文档二进制数据
            
        Returns:
            str: 解析出的文本内容
        """
        try:
            if not self.api_token:
                self._logger.error("未配置MINERU_API_TOKEN，无法使用OCR功能")
                return ""
            
            # 1. 创建解析任务
            task_id = self._create_task(data)
            if not task_id:
                return ""
            
            # 2. 异步轮询查询任务状态（使用asyncio运行异步函数）
            result_url = asyncio.run(self._wait_for_task(task_id))
            
            if not result_url:
                return ""
            
            # 3. 下载并解析结果
            text_content = self._download_and_parse_result(result_url)
            return text_content
            
        except Exception as e:
            self._logger.error(f"OCR解析失败: {e}")
            return ""
    
    def _create_task(self, data: bytes) -> str:
        """
        创建MinerU解析任务
        
        Args:
            data: 文档二进制数据
            
        Returns:
            str: 任务ID
        """
        url = data.decode('utf-8')
        self._logger.info(f"文件链接: {url}")
        try:
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
            
            url = f"{self.api_base_url}/extract/task"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
            
            payload = {
                "url": url,
                "is_ocr": True,  # 启用OCR功能
                "enable_formula": True,  # 启用公式识别
                "enable_table": True,  # 启用表格识别
                "model_version": "pipeline"  # 使用pipeline模型
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self._logger.info(f"创建任务响应: {result}")
                if result.get("code") == 0:
                    task_id = result.get("data", {}).get("task_id", "")
                    self._logger.info(f"成功创建解析任务: {task_id}")
                    return task_id
                else:
                    self._logger.error(f"创建任务失败: {result.get('msg', '未知错误')}")
                    return ""
            else:
                self._logger.error(f"API请求失败: HTTP {response.status_code}")
                return ""
            
        except Exception as e:
            self._logger.error(f"创建解析任务失败: {e}")
            return ""
      
    async def _wait_for_task(self, task_id: str) -> str:
        """
        异步等待任务完成并获取结果URL
        
        Args:
            task_id: 任务ID
            
        Returns:
            str: 结果压缩包URL，如果超时或失败返回空字符串
        """
        try:
            url = f"{self.api_base_url}/extract/task/{task_id}"
            headers = {
                "Authorization": f"Bearer {self.api_token}"
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                while True:
                    # 检查是否超时
                    elapsed = time.time() - start_time
                    if elapsed >= self.timeout:
                        self._logger.warning(f"等待zip链接超时（{self.timeout}秒），放弃下载")
                        return ""
                    
                    try:
                        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                result = await response.json()
                                self._logger.info(f"任务响应: {result}")
                                if result.get("code") == 0:
                                    data = result.get("data", {})
                                    state = data.get("state", "")
                                    
                                    if state == "done":
                                        # 任务完成，获取zip链接
                                        zip_url = data.get("full_zip_url", "")
                                        if zip_url:
                                            self._logger.info(f"任务完成，获取到zip链接: {zip_url}")
                                            return zip_url
                                        else:
                                            self._logger.error("任务完成但未获取到zip链接")
                                            return ""
                                    elif state == "failed":
                                        # 任务失败
                                        err_msg = data.get("err_msg", "未知错误")
                                        self._logger.error(f"任务执行失败: {err_msg}")
                                        return ""
                                    elif state == "waiting-file":
                                        # 等待文件上传完成
                                        self._logger.info(f"等待文件上传完成... 已等待{elapsed:.1f}秒")
                                    elif state == "pending":
                                        # 等待任务开始
                                        self._logger.info(f"任务排队中... 已等待{elapsed:.1f}秒")
                                    elif state == "running":
                                        # 任务进行中，继续等待
                                        progress = data.get("extract_progress", {})
                                        if isinstance(progress, dict):
                                            extracted = progress.get("extracted_pages", 0)
                                            total = progress.get("total_pages", 0)
                                            self._logger.info(f"任务进行中... ({extracted}/{total}) 已等待{elapsed:.1f}秒")
                                        else:
                                            self._logger.info(f"任务进行中... 已等待{elapsed:.1f}秒")
                                    else:
                                        self._logger.info(f"任务状态: {state}")
                                else:
                                    self._logger.error(f"查询任务失败: {result.get('msg', '未知错误')}")
                                    return ""
                            else:
                                self._logger.error(f"API请求失败: HTTP {response.status}")
                    
                    except asyncio.TimeoutError:
                        self._logger.warning(f"单次请求超时，继续重试...")
                    except Exception as e:
                        self._logger.error(f"请求异常: {e}")
                    
                    # 等待一段时间后重试
                    await asyncio.sleep(self.retry_interval)
            
        except Exception as e:
            self._logger.error(f"等待任务完成失败: {e}")
            return ""
    
    def _download_and_parse_result(self, zip_url: str) -> str:
        """
        下载并解析结果压缩包
        
        Args:
            zip_url: 结果压缩包URL
            
        Returns:
            str: 提取的文本内容
        """
        try:
            # 下载zip文件
            response = requests.get(zip_url, timeout=60)
            if response.status_code != 200:
                self._logger.error(f"下载结果失败: HTTP {response.status_code}")
                return ""
            
            # 解压zip文件
            with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
                # 查找markdown文件（MinerU默认输出格式）
                md_files = [f for f in zip_file.namelist() if f.endswith('.md')]
                
                if not md_files:
                    self._logger.error("结果中未找到markdown文件")
                    return ""
                
                # 读取第一个markdown文件
                with zip_file.open(md_files[0]) as md_file:
                    text_content = md_file.read().decode('utf-8')
                    self._logger.info(f"成功提取文本内容，长度: {len(text_content)}")
                    return text_content
                    
        except Exception as e:
            self._logger.error(f"下载和解析结果失败: {e}")
            return ""
    
    def supports(self, content_type: str) -> bool:
        """
        检查是否支持指定的内容类型
        支持需要OCR的文档格式
        
        Args:
            content_type: 内容类型
            
        Returns:
            bool: 是否支持
        """
        supported_types = [
            'application/pdf',
            'application/msword',  # .doc
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/vnd.ms-powerpoint',  # .ppt
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # .pptx
            'image/png',
            'image/jpeg',
            'image/jpg',
            # 简化的类型标识
            'pdf', 'doc', 'docx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg'
        ]
        return content_type.lower() in [t.lower() for t in supported_types]
    
    def chunk(self, data: bytes) -> list[str]:
        """
        将OCR文档内容分块
        
        Args:
            data: 文档二进制数据
            
        Returns:
            list[str]: 分块后的文档内容
        """
        text_content = self._parse(data)
        if not text_content:
            return []
        
        # 使用RecursiveCharacterTextSplitter进行分块
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        chunks = splitter.split_text(text_content)
        
        self._logger.info(f"文档分块完成，共{len(chunks)}块")
        return chunks
    