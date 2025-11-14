import json

from langchain_core.messages import HumanMessage
from src.agents import MyAgent
from src.mcp import MyMCPClient
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware, get_session_middleware
from .agent_manage_service import agent_manage_service
from src.model.crud_session import CRUDSession
from src.model.session import Session
from src.model.crud_session_log import CRUDSessionLog
from src.model.session_log import SessionLog
from src.tools import create_tool
from src.model.database import get_db
from src.response.chat_response import ChatTitleResponse

class ChatService:
    """聊天服务"""
    
    def __init__(self):
        self.curd_session = CRUDSession(Session)
        self.curd_session_log = CRUDSessionLog(SessionLog)

    async def _chat_agent(self, session_id: int, agent_id: str, user_id: str) -> MyAgent:
        """
        创建聊天智能体
        
        Args:
            session_id: 会话ID
            agent_id: 智能体ID
            user_id: 用户ID
            
        Returns:
            聊天智能体
        """
        agent_item = agent_manage_service.get_agent_by_id(agent_id)
        
        if not agent_item:
            raise ValueError(f"Agent {agent_id} not found")
        
        tools = []
        
        if agent_item.mcp_status:
            mcp = MyMCPClient(mcp_servers=json.loads(agent_item.mcp_config))
            tools = await mcp.get_tools()
        else:
            for tool in agent_item.tools:
                tools.append(create_tool(tool))
            
        return MyAgent(
            checkpointer=RedisShortMemory.get_checkpointer(),
            middlewares=[get_my_logger_middleware(), get_session_middleware()],
            tools=tools,
            system_prompt=agent_item.system_prompt,
            chat_id=session_id,
            agent_id=agent_id,
            user_id=user_id
        )
    
    async def chat(self, session_id: int, agent_id: str, user_id: str, message: str):
        """
        聊天
        
        Args:
            session_id: 会话ID
            agent_id: 智能体ID
            user_id: 用户ID
            message: 消息
            
        Returns:
            聊天流
        """
        agent = await self._chat_agent(session_id, agent_id, user_id)
        async for event in agent.astream({"messages": [HumanMessage(content=message)]}):
            data = json.dumps({"text": event[0].content}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        
        yield "data: [DONE]\n\n"
        
    def generate_title(self, session_id: int, user_id: str):
        """
        生成标题
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            
        Returns:
            标题
        """
        db = next(get_db())
        session_logs = self.curd_session_log.get_by_session_id(db, session_id)
        if not len(session_logs):
            raise ValueError(f"Session Log {session_id} not found")
        
        contents = '\n\n'.join([f'{session.role}: {session.content}' for session in session_logs])

        system_prompt = f"你是一个标题助手，我要给你一段话，请你根据这段话生成一个标题，不超过20字\n\n这段话是：{contents}\n\n请直接返回标题，不要有其他内容。"
        
        agent = MyAgent(
            checkpointer=RedisShortMemory.get_checkpointer(),
            middlewares=[get_my_logger_middleware()],
            system_prompt=system_prompt,
        )
        
        response = agent.invoke({"messages": [HumanMessage(content=contents)]})
        title = response.get("content", "")[:20]
        
        session = self.curd_session.get_by_session_id(db, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        self.curd_session.update(db, db_obj=session, obj_in={"title": title}, updated_by=user_id)
        
        return ChatTitleResponse(title=title)
    

chat_service = ChatService()
    
        