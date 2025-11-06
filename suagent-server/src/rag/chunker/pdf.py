from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.rag.chunker import Chunker
from pypdf import PdfReader
from io import BytesIO
from src.utils import get_logger

class PDFChunker(Chunker):
    """PDF文档分块器"""
    _logger = get_logger(__name__)
    
    def _parse(self, data: bytes) -> str:
        """解析PDF文档"""
        try:
            reader = PdfReader(BytesIO(data))
            text_content = ""
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
            
            return text_content.strip()
            
        except Exception as e:
            self._logger.error(f"PDF解析失败: {e}")
            return ""
    
    def supports(self, content_type: str) -> bool:
        """检查是否支持PDF"""
        return content_type.lower() in ['application/pdf', 'pdf']
    
    def chunk(self, data: bytes) -> list[str]:
        """将PDF文档内容分块"""
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return splitter.split_text(self._parse(data))

