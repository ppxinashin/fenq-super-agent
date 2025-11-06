from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.rag.chunker import Chunker
from markitdown import MarkItDown
from io import BytesIO
from src.utils import get_logger


class OfficeChunker(Chunker):
    """Office文档分块器，使用markitdown"""
    _logger = get_logger(__name__)
    
    def __init__(self):
        """初始化markitdown实例"""
        self.markitdown = MarkItDown(enable_plugins=False)
    
    def _parse(self, data: bytes) -> str:
        """解析Office文档"""
        try:
            # 使用BytesIO创建文件类对象
            file_stream = BytesIO(data)
            
            # 使用markitdown的convert_stream方法解析
            result = self.markitdown.convert_stream(file_stream)
            
            if result and hasattr(result, 'text_content'):
                return result.text_content.strip()
            else:
                self._logger.error("markitdown解析结果为空或格式异常")
                return ""
                
        except Exception as e:
            self._logger.error(f"Office文档解析失败: {e}")
            return ""
    
    def supports(self, content_type: str) -> bool:
        """检查是否支持Office文档格式"""
        supported_types = [
            # Word文档
            'application/msword',  # .doc
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            
            # Excel文档
            'application/vnd.ms-excel',  # .xls
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
            
            # PowerPoint文档
            'application/vnd.ms-powerpoint',  # .ppt
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # .pptx
            
            # PDF (markitdown也支持PDF)
            'application/pdf',
        ]
        
        return content_type.lower() in [t.lower() for t in supported_types]
    
    def chunk(self, data: bytes) -> list[str]:
        """将Office文档内容分块"""
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return splitter.split_text(self._parse(data))


