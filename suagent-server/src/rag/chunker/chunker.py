from abc import ABC, abstractmethod

class Chunker(ABC):
    """文档分块器抽象基类"""
    
    @abstractmethod
    def _parse(self, data: bytes) -> str:
        """
        解析文档内容
        
        Args:
            data (bytes): 文档二进制数据
            
        Returns:
            str: 解析出的文本内容
        """
        pass
    
    @abstractmethod
    def supports(self, content_type: str) -> bool:
        """
        检查是否支持指定的内容类型
        
        Args:
            content_type (str): 内容类型
            
        Returns:
            bool: 是否支持
        """
        pass
    
    @abstractmethod
    def chunk(self, data: bytes) -> list[str]:
        """
        将文档内容分块
        
        Returns:
            list[str]: 分块后的文档内容
        """
        pass

