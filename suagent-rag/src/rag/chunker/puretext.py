from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.rag.chunker import Chunker
from src.utils import get_logger


class PureTextChunker(Chunker):
    """纯文本文档分块器"""
    _logger = get_logger(__name__)
    
    def _parse(self, data: bytes) -> str:
        """解析纯文本文档"""
        try:
            # 将字节数据解码为字符串
            text = data.decode('utf-8')
            return text.strip()
            
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                text = data.decode('gbk')
                return text.strip()
            except Exception as e:
                self._logger.error(f"纯文本文本解码失败: {e}")
                return ""
        except Exception as e:
            self._logger.error(f"纯文本解析失败: {e}")
            return ""
    
    def supports(self, content_type: str) -> bool:
        """检查是否支持纯文本"""
        supported_types = [
            'text/plain',
            'text/txt',
            'txt',
        ]
        return content_type.lower() in [t.lower() for t in supported_types]
    
    def chunk(self, data: bytes) -> list[str]:
        """将纯文本文档内容分块"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", "；", ";", "，", ",", " ", ""]
        )
        return splitter.split_text(self._parse(data))


