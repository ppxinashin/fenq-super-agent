import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.consts import FileConsts
from src.utils import get_logger

class MyMCPClient(MultiServerMCPClient):
    """MCP客户端"""
    _logger = get_logger(__name__)
    
    def __init__(self, mcp_servers_file: str = FileConsts.MCP_SERVERS):
        """初始化MCP客户端"""
        self._logger.info(f"MCP服务器配置文件: {mcp_servers_file}")
        with open(mcp_servers_file, "r") as f:
            mcp_servers = json.load(f)
        self._logger.info(f"MCP服务器配置: {mcp_servers}")
        # 转换配置格式：将 'type' 字段映射为 'transport' 字段
        connections = {}
        for server_name, config in mcp_servers["mcpServers"].items():
            server_config = config.copy()
            # 如果存在 'type' 字段，将其重命名为 'transport'
            if 'type' in server_config and 'transport' not in server_config:
                server_config['transport'] = server_config.pop('type')
            connections[server_name] = server_config
        
        self._logger.info(f"转换后的MCP服务器配置: {connections}")
        super().__init__(connections=connections)
        