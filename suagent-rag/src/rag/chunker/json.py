import json
from langchain_text_splitters import RecursiveJsonSplitter
from src.rag.chunker import Chunker
from src.utils import get_logger

class JSONChunker(Chunker):
    """JSON文档分块器"""
    _logger = get_logger(__name__)
    
    def _parse(self, data: bytes) -> str:
        """解析JSON文档"""
        try:
            # 将字节数据解码为字符串
            json_text = data.decode('utf-8')
            
            # JSON 本身可以直接读
            return json_text.strip()
            
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                json_text = data.decode('gbk')
                return json_text.strip()
            except Exception as e:
                self._logger.error(f"JSON文本解码失败: {e}")
                return ""
        except json.JSONDecodeError as e:
            self._logger.error(f"JSON解析失败: {e}")
            return ""
        except Exception as e:
            self._logger.error(f"JSON处理失败: {e}")
            return ""
    
    def supports(self, content_type: str) -> bool:
        """检查是否支持JSON"""
        supported_types = [
            'application/json',
            'text/json',
            'json',
        ]
        return content_type.lower() in [t.lower() for t in supported_types]
    
    def chunk(self, data: bytes) -> list[str]:
        """将JSON文档内容分块"""
        splitter = RecursiveJsonSplitter(min_chunk_size=500, max_chunk_size=1000)
        return splitter.split_text(json.loads(self._parse(data)))


