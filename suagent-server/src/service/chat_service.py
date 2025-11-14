import json
from datetime import datetime, timedelta
from typing import List, Optional

from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage
from src.agents import MyAgent
from src.mcp_client import MyMCPClient
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware, get_session_middleware
from .agent_manage_service import agent_manage_service
from src.model.crud_session import CRUDSession
from src.model.session import Session
from src.model.crud_session_log import CRUDSessionLog
from src.model.session_log import SessionLog
from src.tools import create_tool
from src.model.database import get_db
from src.utils import get_logger
from src.utils.snowflake_id import Snowflake
from src.response.chat_response import (
    ChatTitleResponse,
    CreateSessionResponse,
    SessionInfoResponse,
    ChatMessageResponse,
    ChatHistoryResponse
)

logger = get_logger(__name__)

class ChatService:
    """聊天服务"""

    def __init__(self):
        self.curd_session = CRUDSession(Session)
        self.curd_session_log = CRUDSessionLog(SessionLog)
        self.id_generator = Snowflake(worker_id=1, datacenter_id=1)

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
        
        # 异步踩坑 - 使用 astream() 时必须使用异步 checkpointer
        if agent_item.mcp_status:
            mcp = MyMCPClient(mcp_servers=json.loads(agent_item.mcp_config))
            tools = await mcp.get_tools()
            
        else:
            for tool in agent_item.tools:
                tools.append(create_tool(tool))
            
        return MyAgent(
            checkpointer = await RedisShortMemory.get_acheckpointer(),
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
            if isinstance(event[0], AIMessageChunk):
                data = json.dumps({"text": event[0].content}, ensure_ascii=False)
            elif isinstance(event[0], ToolMessage):
                data = json.dumps({"text": f'> 已调用工具：{event[0].name}\n\n'}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        
        yield "data: [DONE]\n\n"

    def create_session(self, agent_id: str, user_id: str) -> CreateSessionResponse:
        """
        创建会话

        Args:
            agent_id: 智能体ID
            user_id: 用户ID

        Returns:
            创建会话响应
        """
        db = next(get_db())
        try:
            # 生成会话ID
            session_id = self.id_generator.generate_id()

            # 创建会话
            session = self.curd_session.create_session(
                db=db,
                agent_id=agent_id,
                session_id=session_id,
                title="",
                created_by=user_id
            )

            db.commit()

            return CreateSessionResponse(
                session_id=session.session_id,
                agent_id=session.agent_id,
                title=session.title or "",
                created_at=session.created_at
            )
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def update_session_title(self, session_id: int, title: str, user_id: str) -> bool:
        """
        更新会话标题

        Args:
            session_id: 会话ID
            title: 新标题
            user_id: 用户ID

        Returns:
            是否更新成功
        """
        db = next(get_db())
        try:
            # 验证会话是否属于当前用户
            session = self.curd_session.get_by_session_id(db, session_id)
            if not session:
                raise ValueError(f"会话 {session_id} 不存在")

            if session.created_by != user_id:
                raise ValueError("无权限修改此会话")

            # 更新标题
            updated_session = self.curd_session.update_title(
                db=db,
                session_id=session_id,
                title=title,
                updated_by=user_id
            )

            if updated_session:
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"更新会话标题失败: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def delete_session(self, session_id: int, user_id: str) -> bool:
        """
        删除会话（逻辑删除）

        Args:
            session_id: 会话ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        db = next(get_db())
        try:
            # 验证会话是否属于当前用户
            session = self.curd_session.get_by_session_id(db, session_id)
            if not session:
                raise ValueError(f"会话 {session_id} 不存在")

            if session.created_by != user_id:
                raise ValueError("无权限删除此会话")

            # 软删除会话
            success = self.curd_session.delete_by_session_id(
                db=db,
                session_id=session_id,
                deleted_by=user_id
            )

            if success:
                db.commit()
            return success
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def get_session_list(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        agent_id: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> dict:
        """
        获取会话列表

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            agent_id: 智能体ID（可选）
            keyword: 关键词（可选）

        Returns:
            会话列表分页数据
        """
        db = next(get_db())
        try:
            # 计算跳过记录数
            skip = (page - 1) * page_size

            # 查询会话列表
            if keyword:
                # 按标题搜索
                sessions = self.curd_session.search_by_title(
                    db=db,
                    keyword=keyword,
                    agent_id=agent_id,
                    limit=page_size
                )
                # 过滤用户的会话
                sessions = [s for s in sessions if s.created_by == user_id]
                total = len(sessions)
            elif agent_id:
                # 按智能体ID查询
                sessions = self.curd_session.get_by_agent_and_user(
                    db=db,
                    agent_id=agent_id,
                    created_by=user_id,
                    skip=skip,
                    limit=page_size
                )
                total = self.curd_session.count_by_agent_and_user(db, agent_id, user_id)
            else:
                # 获取用户所有会话（这里需要在基础CRUD中添加方法）
                query = db.query(Session).filter(
                    Session.created_by == user_id,
                    Session.is_deleted == False
                ).order_by(Session.created_at.desc()).offset(skip).limit(page_size)
                sessions = query.all()
                total = db.query(Session).filter(
                    Session.created_by == user_id,
                    Session.is_deleted == False
                ).count()

            # 构建响应数据
            session_infos = []
            for session in sessions:
                # 获取智能体名称
                agent_item = agent_manage_service.get_agent_by_id(session.agent_id)
                agent_name = agent_item.name if agent_item else session.agent_id

                # 获取消息数量和最后消息时间
                message_count = self.curd_session_log.count_by_session_id(db, session.session_id)
                latest_logs = self.curd_session_log.get_latest_by_session_id(db, session.session_id, 1)
                last_message_time = latest_logs[0].created_at if latest_logs else None

                session_infos.append(SessionInfoResponse(
                    session_id=session.session_id,
                    agent_id=session.agent_id,
                    agent_name=agent_name,
                    title=session.title or "",
                    created_at=session.created_at,
                    last_message_time=last_message_time,
                    message_count=message_count
                ))

            return {
                "items": session_infos,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
            }
        except Exception as e:
            logger.error(f"获取会话列表失败: {e}")
            raise
        finally:
            db.close()

    def get_chat_history(self, session_id: int, user_id: str) -> ChatHistoryResponse:
        """
        获取聊天记录

        Args:
            session_id: 会话ID
            user_id: 用户ID

        Returns:
            聊天记录响应
        """
        db = next(get_db())
        try:
            # 验证会话是否属于当前用户
            session = self.curd_session.get_by_session_id(db, session_id)
            if not session:
                raise ValueError(f"会话 {session_id} 不存在")

            if session.created_by != user_id:
                raise ValueError("无权限查看此会话记录")

            # 查询前一天内的聊天记录
            cutoff_time = datetime.now() - timedelta(days=1)
            logs = db.query(SessionLog).filter(
                SessionLog.session_id == session_id,
                SessionLog.is_deleted == False,
                SessionLog.created_at >= cutoff_time
            ).order_by(SessionLog.created_at).limit(20).all()

            # 按轮次分组（人机交互算一轮）
            messages = []
            current_round = []
            round_count = 0

            for log in logs:
                current_round.append(ChatMessageResponse(
                    role=log.role,
                    content=log.content,
                    created_at=log.created_at
                ))

                # 如果是助手回复且当前轮次不为空，表示一轮结束
                if log.role == "assistant" and current_round:
                    messages.extend(current_round)
                    current_round = []
                    round_count += 1

                    # 限制5轮对话
                    if round_count >= 5:
                        break

            # 添加最后一轮（如果没有完整结束）
            if current_round and round_count < 5:
                messages.extend(current_round)

            return ChatHistoryResponse(
                session_id=session_id,
                messages=messages,
                total_count=len(messages)
            )
        except Exception as e:
            logger.error(f"获取聊天记录失败: {e}")
            raise
        finally:
            db.close()
        
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
    
        