"""
智能体相关常量
"""


class AgentConsts:
    """智能体常量集合"""

    # 智能体英文名（agent_id）规则
    AGENT_ID_MAX_LENGTH = 20
    AGENT_ID_MIN_LENGTH = 2
    AGENT_ID_PATTERN = r"^[A-Za-z0-9_]{" + str(AGENT_ID_MIN_LENGTH) + "," + str(AGENT_ID_MAX_LENGTH) + "}$"
    AGENT_ID_RULE_DESC = f"仅支持大小写字母、数字以及下划线，长度需在{AGENT_ID_MIN_LENGTH}-{AGENT_ID_MAX_LENGTH}字符之间"
    AGENT_ID_FORBIDDEN_NAMES = ["memory"]  # 禁止使用的智能体名称

    # 智能体中文名（agent_name）规则
    AGENT_NAME_MAX_LENGTH = 100
    AGENT_NAME_MIN_LENGTH = 1

    # 智能体介绍规则
    AGENT_DESCRIPTION_MAX_LENGTH = 500

    # 系统提示词规则
    AGENT_SYSTEM_PROMPT_MAX_LENGTH = 10000

    # 默认值
    DEFAULT_AGENT_NAME = "新智能体"
    DEFAULT_AGENT_DESCRIPTION = "这是一个智能体"
    DEFAULT_SYSTEM_PROMPT = "你是一个有用的AI助手。"

    # 工具列表（可用的工具集合）
    AVAILABLE_TOOLS = [
        "web_scraper", # 网页抓取,
        "calculator", # 计算器,
        "rag", # RAG检索,
        "long_memroy", # 长期记忆,
        "read_file", # 读文件,
        "write_file", # 写文件,
        "execute_command", # 执行命令,
        "web_search", # 网页搜索,
        "downloader", # 文件下载,
        "now_time", # 当前时间,
    ]

    # MCP状态
    MCP_STATUS_ENABLED = "enabled"
    MCP_STATUS_DISABLED = "disabled"

    # 创建者类型
    CREATOR_ADMIN = "admin"
    CREATOR_USER = "user"
