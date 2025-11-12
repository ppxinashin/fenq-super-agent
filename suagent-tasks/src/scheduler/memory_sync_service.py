"""
Memory Sync Service - 记忆同步核心业务服务
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from src.model.base import Base
from src.model.session_log import SessionLog
from src.model.session import Session
from src.model.user_memory_setting import UserMemorySetting
from src.model.init_db import get_db
from src.scheduler.config import MEMORY_SYNC_DATE_RANGE_DAYS, BATCH_SIZE
from src.scheduler.utils.retry_handler import database_retry

logger = logging.getLogger(__name__)

class MemorySyncService:
    """记忆同步服务"""

    def __init__(self):
        self.db_session = None

    def get_db_session(self) -> Session:
        """获取数据库会话"""
        if self.db_session is None:
            self.db_session = next(get_db())
        return self.db_session

    def close_db_session(self):
        """关闭数据库会话"""
        if self.db_session:
            self.db_session.close()
            self.db_session = None

    @database_retry
    def get_long_memory_users(self) -> List[str]:
        """
        获取开启长期记忆功能的用户列表

        Returns:
            用户名列表
        """
        session = self.get_db_session()
        try:
            users = session.query(UserMemorySetting.username)\
                          .filter(UserMemorySetting.enabled == True)\
                          .filter(UserMemorySetting.is_deleted == False)\
                          .all()

            user_list = [user[0] for user in users]
            logger.info(f"Found {len(user_list)} users with long memory enabled")
            return user_list

        except Exception as e:
            logger.error(f"Failed to get long memory users: {e}")
            raise
        finally:
            self.close_db_session()

    @database_retry
    def get_long_memory_users_count(self) -> int:
        """
        获取开启长期记忆功能的用户数量

        Returns:
            用户数量
        """
        session = self.get_db_session()
        try:
            count = session.query(func.count(UserMemorySetting.username))\
                         .filter(UserMemorySetting.enabled == True)\
                         .filter(UserMemorySetting.is_deleted == False)\
                         .scalar()
            return count or 0

        except Exception as e:
            logger.error(f"Failed to get long memory users count: {e}")
            raise
        finally:
            self.close_db_session()

    @database_retry
    def get_user_sessions_by_date_range(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
        offset: int = 0,
        limit: int = BATCH_SIZE
    ) -> List[Dict[str, Any]]:
        """
        获取指定用户在日期范围内的会话列表

        Args:
            username: 用户名
            start_date: 开始日期
            end_date: 结束日期
            offset: 偏移量
            limit: 限制数量

        Returns:
            会话信息列表
        """
        session = self.get_db_session()
        try:
            # 查询用户会话
            sessions_query = session.query(Session)\
                                  .filter(Session.created_at >= start_date)\
                                  .filter(Session.created_at < end_date)\
                                  .filter(Session.is_deleted == False)\
                                  .order_by(desc(Session.created_at))

            # 这里需要根据实际的用户关联逻辑调整
            # 假设 agent_id 包含用户信息，或者需要额外的用户会话关联表
            sessions = sessions_query.offset(offset).limit(limit).all()

            session_list = []
            for sess in sessions:
                session_info = {
                    'session_id': sess.session_id,
                    'agent_id': sess.agent_id,
                    'title': sess.title or '未命名会话',
                    'created_at': sess.created_at,
                    'updated_at': sess.updated_at
                }
                session_list.append(session_info)

            logger.info(f"Found {len(session_list)} sessions for user {username}")
            return session_list

        except Exception as e:
            logger.error(f"Failed to get sessions for user {username}: {e}")
            raise
        finally:
            self.close_db_session()

    @database_retry
    def get_session_logs(self, session_id: int) -> List[Dict[str, Any]]:
        """
        获取指定会话的日志内容

        Args:
            session_id: 会话ID

        Returns:
            会话日志列表
        """
        session = self.get_db_session()
        try:
            logs = session.query(SessionLog)\
                         .filter(SessionLog.session_id == session_id)\
                         .filter(SessionLog.is_deleted == False)\
                         .order_by(SessionLog.created_at)\
                         .all()

            log_list = []
            for log in logs:
                log_info = {
                    'role': log.role,
                    'content': log.content,
                    'agent_id': log.agent_id,
                    'created_at': log.created_at
                }
                log_list.append(log_info)

            logger.info(f"Found {len(log_list)} logs for session {session_id}")
            return log_list

        except Exception as e:
            logger.error(f"Failed to get logs for session {session_id}: {e}")
            raise
        finally:
            self.close_db_session()

    @database_retry
    def get_user_memory_stats(self, username: str) -> Dict[str, Any]:
        """
        获取用户记忆统计信息

        Args:
            username: 用户名

        Returns:
            统计信息字典
        """
        session = self.get_db_session()
        try:
            # 获取用户总会话数
            # 这里需要根据实际的业务逻辑调整查询条件
            total_sessions = session.query(func.count(func.distinct(SessionLog.session_id)))\
                                  .filter(SessionLog.is_deleted == False)\
                                  .scalar() or 0

            # 获取总消息数
            total_messages = session.query(func.count(SessionLog.id))\
                                  .filter(SessionLog.is_deleted == False)\
                                  .scalar() or 0

            # 获取最近活动时间
            last_activity = session.query(func.max(SessionLog.created_at))\
                                 .filter(SessionLog.is_deleted == False)\
                                 .scalar()

            stats = {
                'username': username,
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'last_activity': last_activity,
                'memory_enabled': True
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get memory stats for user {username}: {e}")
            raise
        finally:
            self.close_db_session()

    def get_user_sessions_batch(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        批量获取用户会话数据（包含日志）

        Args:
            username: 用户名
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            会话数据列表，每个会话包含完整的日志信息
        """
        sessions_data = []
        offset = 0

        while True:
            # 获取会话列表
            sessions = self.get_user_sessions_by_date_range(
                username, start_date, end_date, offset, BATCH_SIZE
            )

            if not sessions:
                break

            # 为每个会话获取日志
            for session_info in sessions:
                try:
                    logs = self.get_session_logs(session_info['session_id'])
                    session_info['logs'] = logs
                    session_info['log_count'] = len(logs)
                    sessions_data.append(session_info)

                except Exception as e:
                    logger.error(f"Failed to get logs for session {session_info['session_id']}: {e}")
                    continue

            offset += BATCH_SIZE

            # 如果返回的会话数少于批次大小，说明已经获取完所有数据
            if len(sessions) < BATCH_SIZE:
                break

        logger.info(f"Retrieved {len(sessions_data)} sessions with logs for user {username}")
        return sessions_data

    def get_sync_date_range(self, target_date: datetime = None) -> Tuple[datetime, datetime]:
        """
        获取同步的日期范围

        Args:
            target_date: 目标日期，默认为昨天

        Returns:
            (开始日期, 结束日期)
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=MEMORY_SYNC_DATE_RANGE_DAYS)

        start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        return start_date, end_date

    def validate_session_data(self, session_data: Dict[str, Any]) -> bool:
        """
        验证会话数据的有效性

        Args:
            session_data: 会话数据

        Returns:
            是否有效
        """
        required_fields = ['session_id', 'agent_id', 'title', 'logs']

        for field in required_fields:
            if field not in session_data:
                logger.warning(f"Session data missing required field: {field}")
                return False

        # 验证日志数据
        logs = session_data['logs']
        if not isinstance(logs, list) or len(logs) == 0:
            logger.warning(f"Session {session_data['session_id']} has no valid logs")
            return False

        # 验证每条日志的必要字段
        for log in logs:
            if not all(key in log for key in ['role', 'content']):
                logger.warning(f"Invalid log format in session {session_data['session_id']}")
                return False

        return True