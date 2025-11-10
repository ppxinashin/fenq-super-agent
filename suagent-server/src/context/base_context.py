"""
基础上下文
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class BaseContext:
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    agent_id: Optional[str] = None