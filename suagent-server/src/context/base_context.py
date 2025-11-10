"""
基础上下文
"""

from dataclasses import dataclass

@dataclass
class BaseContext:
    user_id: str
    chat_id: str