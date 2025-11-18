import json
from datetime import datetime, timedelta
from typing import List, Optional

from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage, AIMessage
from langchain_core.exceptions import LangChainException
from openai import BadRequestError as OpenAIBadRequestError
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

    async def _chat_agent(self, session_id: int, agent_id: str, user_id: str, long_memory: bool = False) -> MyAgent:
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
        
        for tool in agent_item.tools:
            if tool == "long_memroy":
                continue
            tools.append(create_tool(tool))
            
        if long_memory:
            tools.append(create_tool("long_memroy"))
            
        return MyAgent(
            checkpointer = await RedisShortMemory.get_acheckpointer(),
            middlewares=[get_my_logger_middleware(), get_session_middleware()],
            tools=tools,
            system_prompt=agent_item.system_prompt,
            chat_id=session_id,
            agent_id=agent_id,
            user_id=user_id
        )
    
    async def _clean_checkpointer_thread(self, checkpointer, thread_id: str):
        """
        清理checkpointer中的线程历史
        
        Args:
            checkpointer: checkpointer实例
            thread_id: 线程ID
        """
        config = {"configurable": {"thread_id": thread_id}}
        try:
            await checkpointer.adelete(config)
            logger.info(f"已清理checkpointer中的线程，thread_id={thread_id}")
        except Exception as e:
            logger.error(f"清理checkpointer线程失败: {e}", exc_info=True)
    
    async def _fix_incomplete_messages(self, checkpointer, thread_id: str):
        """
        修复checkpointer中不完整的消息历史
        
        如果发现带有tool_calls的AIMessage但没有对应的ToolMessage响应，
        则删除整个线程的历史记录，以避免API调用错误
        
        Args:
            checkpointer: checkpointer实例
            thread_id: 线程ID
        """
        config = {"configurable": {"thread_id": thread_id}}
        try:
            # 获取当前的消息历史
            state = await checkpointer.aget(config)
            
            if not state:
                return
            
            # 检查state的格式，可能是dict或Checkpoint对象
            messages = None
            if isinstance(state, dict):
                messages = state.get("messages") or state.get("channel_values", {}).get("messages")
            elif hasattr(state, "channel_values"):
                messages = state.channel_values.get("messages")
            elif hasattr(state, "messages"):
                messages = state.messages
            
            if not messages:
                return
            
            has_incomplete_tool_calls = False
            
            # 检查是否有不完整的tool_calls
            # 遍历所有消息，检查每个带有tool_calls的AIMessage是否有对应的ToolMessage
            for i, msg in enumerate(messages):
                if isinstance(msg, AIMessage):
                    tool_calls = getattr(msg, 'tool_calls', None)
                    if tool_calls:
                        # 获取所有tool_call的ID
                        tool_call_ids = {tc.get("id") for tc in tool_calls if tc.get("id")}
                        if not tool_call_ids:
                            continue
                        
                        found_tool_messages = set()
                        
                        # 向后查找对应的ToolMessage
                        for j in range(i + 1, len(messages)):
                            next_msg = messages[j]
                            
                            # 如果遇到下一个AIMessage或HumanMessage，停止查找
                            # 因为这意味着当前轮次的tool_calls应该已经处理完了
                            if isinstance(next_msg, (AIMessage, HumanMessage)):
                                break
                            
                            # 检查是否是ToolMessage
                            if isinstance(next_msg, ToolMessage):
                                tool_msg_id = getattr(next_msg, 'tool_call_id', None)
                                if tool_msg_id and tool_msg_id in tool_call_ids:
                                    found_tool_messages.add(tool_msg_id)
                        
                        # 如果有未响应的tool_calls，说明不完整
                        missing_tool_call_ids = tool_call_ids - found_tool_messages
                        if missing_tool_call_ids:
                            has_incomplete_tool_calls = True
                            is_last = (i == len(messages) - 1)
                            logger.warning(
                                f"发现不完整的tool_calls（{'最后一条' if is_last else '中间'}消息），"
                                f"thread_id={thread_id}, "
                                f"消息索引={i}, "
                                f"未响应的tool_call_ids={missing_tool_call_ids}, "
                                f"总tool_calls数={len(tool_call_ids)}, "
                                f"已响应数={len(found_tool_messages)}"
                            )
                            break  # 发现一个不完整的就足够了，直接清理
            
            # 如果发现不完整的tool_calls，清理整个线程
            if has_incomplete_tool_calls:
                logger.info(f"清理不完整的消息历史，thread_id={thread_id}")
                await self._clean_checkpointer_thread(checkpointer, thread_id)
                
        except Exception as e:
            logger.error(f"修复checkpointer消息失败: {e}", exc_info=True)
            # 如果修复失败，尝试清理整个线程（作为最后手段）
            await self._clean_checkpointer_thread(checkpointer, thread_id)
    
    async def chat(self, session_id: int, agent_id: str, user_id: str, message: str, long_memory: bool = False):
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
        agent = await self._chat_agent(session_id, agent_id, user_id, long_memory)
        
        # 在调用agent之前，修复checkpointer中可能的不完整消息
        checkpointer = await RedisShortMemory.get_acheckpointer()
        thread_id = f'{agent_id}_{session_id}'
        await self._fix_incomplete_messages(checkpointer, thread_id)
        
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # 在每次尝试前，先修复可能的不完整消息
                await self._fix_incomplete_messages(checkpointer, thread_id)
                
                async for event in agent.astream({"messages": [HumanMessage(content=message)]}):
                    data = None
                    if isinstance(event, (list, tuple)) and len(event) > 0:
                        msg = event[0]
                        if isinstance(msg, AIMessageChunk):
                            data = json.dumps({"text": msg.content}, ensure_ascii=False)
                        elif isinstance(msg, ToolMessage):
                            tool_name = getattr(msg, 'name', '未知工具')
                            data = json.dumps({"text": f'> 已调用工具：{tool_name}\n\n'}, ensure_ascii=False)
                    
                    if data:
                        yield f"data: {data}\n\n"
                
                yield "data: [DONE]\n\n"
                break  # 成功执行，退出重试循环
                
            except (OpenAIBadRequestError, LangChainException, Exception) as e:
                error_message = str(e)
                error_type = type(e).__name__
                
                # 检查是否是tool_calls相关的错误（更宽泛的匹配）
                is_tool_calls_error = (
                    "tool_calls" in error_message.lower() or
                    "tool_call" in error_message.lower() or
                    "tool message" in error_message.lower() or
                    "must be followed by tool" in error_message.lower()
                )
                
                if is_tool_calls_error:
                    retry_count += 1
                    logger.warning(
                        f"检测到tool_calls相关错误 ({error_type})，清理线程并重试 (第{retry_count}次): "
                        f"thread_id={thread_id}, error={error_message[:500]}"
                    )
                    
                    # 强制清理线程，确保没有残留的不完整消息
                    await self._clean_checkpointer_thread(checkpointer, thread_id)
                    
                    # 再次修复（虽然已经清理，但确保状态一致）
                    await self._fix_incomplete_messages(checkpointer, thread_id)
                    
                    if retry_count <= max_retries:
                        # 重新创建agent以确保使用清理后的checkpointer
                        agent = await self._chat_agent(session_id, agent_id, user_id, long_memory)
                    else:
                        logger.error(f"重试{max_retries}次后仍然失败 ({error_type}): {error_message[:500]}")
                        yield f"data: {json.dumps({'text': '<p style=\"color: red;\">**对话失败，请重试**</p>'}, ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"
                        break
                else:
                    # 其他类型的错误，直接抛出
                    logger.error(f"聊天过程中发生未预期的错误 ({error_type}): {error_message}", exc_info=True)
                    raise

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
            logger.info(f"查询参数: keyword='{keyword}', agent_id='{agent_id}', user_id='{user_id}'")

            if keyword and keyword.strip():
                # 按标题搜索
                logger.info("执行按标题搜索分支")
                sessions = self.curd_session.search_by_title(
                    db=db,
                    keyword=keyword,
                    agent_id=agent_id,
                    limit=page_size
                )
                # 过滤用户的会话
                sessions = [s for s in sessions if s.created_by == user_id]
                total = len(sessions)
            elif agent_id and agent_id.strip():
                # 按智能体ID查询
                logger.info("执行按智能体ID查询分支")
                sessions = self.curd_session.get_by_agent_and_user(
                    db=db,
                    agent_id=agent_id,
                    created_by=user_id,
                    skip=skip,
                    limit=page_size
                )
                total = self.curd_session.count_by_agent_and_user(db, agent_id, user_id)
            else:
                # 获取用户所有会话
                logger.info("执行获取用户所有会话分支")
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
                agent_name = agent_item.agent_name

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
        
    async def generate_title(self, session_id: int, user_id: str):
        """
        生成标题
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            
        Returns:
            标题流
        """
        db = next(get_db())
        session = self.curd_session.get_by_session_id(db, session_id=session_id)
        if session.title:
            data = json.dumps({"text": session.title}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        else:
            session_logs = self.curd_session_log.get_by_session_id(db, session_id, limit=2)
            if not len(session_logs):
                raise ValueError(f"Session Log {session_id} not found")
        
            system_prompt = "你是一个标题助手，我要给你一段话，请你根据这段话生成一个标题，不超过20字"
            content = f"请总结以下内容：\n\n{'\n\n'.join([f'{session.role}: {session.content}' for session in session_logs])}"
            agent = MyAgent(
                checkpointer=await RedisShortMemory.get_acheckpointer(),
                middlewares=[get_my_logger_middleware()],
                system_prompt=system_prompt,
            )
            
            title = ""
            
            async for event in agent.astream({"messages": [HumanMessage(content=content)]}):
                data = None
                if isinstance(event, (list, tuple)) and len(event) > 0:
                    msg = event[0]
                    if isinstance(msg, AIMessageChunk):
                        data = json.dumps({"text": msg.content}, ensure_ascii=False)
                        title += msg.content
                    elif isinstance(msg, ToolMessage):
                        tool_name = getattr(msg, 'name', '未知工具')
                        data = json.dumps({"text": f'> 已调用工具：{tool_name}\n\n'}, ensure_ascii=False)
                
                if data:
                    yield f"data: {data}\n\n"
            
            self.update_session_title(session_id=session_id, title=title, user_id=user_id)
        yield "data: [DONE]\n\n"
            
        
    

chat_service = ChatService()
    
        