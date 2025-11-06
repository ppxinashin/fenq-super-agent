from langchain_text_splitters.markdown import MarkdownTextSplitter
from src.rag.chunker import Chunker
from src.utils import get_logger


class MarkdownChunker(Chunker):
    """Markdown文档分块器"""
    _logger = get_logger(__name__)
    
    def _parse(self, data: bytes) -> str:
        """解析Markdown文档"""
        try:
            # 将字节数据解码为字符串
            markdown_text = data.decode('utf-8')
            
            # 使用markdown库将Markdown转换为纯文本
            # 注意：markdown库主要用于转换为HTML，这里我们直接返回原始文本
            # 因为Markdown本身就是可读文本，适合RAG使用
            return markdown_text.strip()
            
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                markdown_text = data.decode('gbk')
                return markdown_text.strip()
            except Exception as e:
                self._logger.error(f"Markdown文本解码失败: {e}")
                return ""
        except Exception as e:
            self._logger.error(f"Markdown解析失败: {e}")
            return ""
    
    def supports(self, content_type: str) -> bool:
        """检查是否支持Markdown"""
        supported_types = [
            'text/markdown',
            'text/x-markdown',
            'markdown',
            'md',
        ]
        return content_type.lower() in [t.lower() for t in supported_types]
    
    def chunk(self, data: bytes) -> list[str]:
        """将Markdown文档内容分块"""
        splitter = MarkdownTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        return splitter.split_text(self._parse(data))


