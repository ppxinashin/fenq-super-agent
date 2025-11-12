"""
智能体相关常量
"""


class AgentConsts:
    """智能体常量集合"""
    
    # 仅允许大小写字母、数字、下划线，长度2-20
    AGENT_ID_PATTERN = r"^[A-Za-z0-9_]{2,20}$"
    AGENT_ID_RULE_DESC = "仅支持大小写字母、数字以及下划线，长度需在2-20字符之间"
