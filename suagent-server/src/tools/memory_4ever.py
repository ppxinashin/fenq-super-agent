from dataclasses import dataclass
from typing import Optional
from langgraph.store.postgres import AsyncPostgresStore
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from src.memory import PGLongMemory
from src.utils import get_logger
from src.context import BaseContext

logger = get_logger(__name__)

store = PGLongMemory.get_store()

async def get_astore() -> AsyncPostgresStore:
    return await PGLongMemory.get_astore()

class Memory(TypedDict):
    name: str
    introduce: Optional[str]
    summary: str
    
class Memory4EverInput(BaseModel):
    memory: Memory = Field(description="记忆内容")
    
@tool(args_schema=Memory4EverInput)
def memory_4ever(memory: Memory, runtime: ToolRuntime[BaseContext]) -> str:
    """
    本工具用于对话总结，当用户提到总结时候，总结出用户的姓名、介绍(没有可以不填)、以及我们都讨论了哪些东西。
    """
    user_id = runtime.context.user_id
    store.put(('memories', ), user_id, memory)
    return "本次对话所有内容已经总结好了"

@tool(args_schema=Memory4EverInput)
async def amemory_4ever(memory: Memory, runtime: ToolRuntime[BaseContext]) -> str:
    """
    本工具用于对话总结，当用户提到总结时候，总结出用户的姓名、介绍(没有可以不填)、以及我们都讨论了哪些东西。
    """
    store = await get_astore()
    user_id = runtime.context.user_id
    await store.aput(('memories', ), user_id, memory)
    return "本次对话所有内容已经总结好了"

def create_memory_4ever_tool():
    return memory_4ever

async def create_amemory_4ever_tool():
    return amemory_4ever