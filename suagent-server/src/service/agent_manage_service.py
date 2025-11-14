"""
智能体管理服务层
"""

from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.model.crud_agent import CRUDAgent
from src.model.database import get_db
from src.model.agent import Agent
from src.request.agent_manage_request import (
    AgentCreateRequest, AgentUpdateRequest, AgentListRequest,
    AgentCardListRequest, AgentToolsUpdateRequest, AgentMcpUpdateRequest
)
from src.response.agent_manage_response import (
    AgentInfo, AgentSimpleInfo, AgentListItem,
    AgentCreateResponse, AgentUpdateResponse, AgentDeleteResponse
)
from src.consts.agent_consts import AgentConsts
from src.utils.logger import get_logger
from src.utils.snowflake_id import Snowflake
from src.response.pageable import Pageable
from src.api_middlewares.exception_middleware import (
    BusinessException, NotFoundError, ConflictError
)

logger = get_logger(__name__)


class AgentManageService:
    """智能体管理服务类"""

    def __init__(self):
        self.agent_crud = CRUDAgent(Agent)
        # 注意：由于不修改数据库表，这里不使用雪花ID生成器

    def create_agent(self, agent_create: AgentCreateRequest, user_id: int, username: str) -> AgentCreateResponse:
        """
        创建新智能体

        Args:
            agent_create: 智能体创建请求

        Returns:
            AgentCreateResponse: 创建的智能体信息

        Raises:
            Exception: 创建失败时抛出异常
        """
        db = next(get_db())
        try:
            # 检查智能体ID是否已存在
            if self.agent_crud.check_agent_id_exists(db, agent_create.agent_id):
                raise ConflictError(f"智能体ID '{agent_create.agent_id}' 已存在")

            # 处理MCP配置
            mcp_servers = {}
            if agent_create.mcp_config:
                try:
                    import json
                    mcp_servers = json.loads(agent_create.mcp_config)
                except json.JSONDecodeError:
                    raise BusinessException("MCP配置必须是有效的JSON字符串")

            # 转换MCP状态
            mcp_enabled = agent_create.mcp_status

            # 创建智能体
            created_agent = self.agent_crud.create_agent(
                db=db,
                agent_id=agent_create.agent_id,
                agent_name=agent_create.agent_name,
                system_prompt=agent_create.system_prompt,
                description=agent_create.description,
                tools=agent_create.tools,
                mcp_enabled=mcp_enabled,
                mcp_servers=mcp_servers,
                created_by=username
            )

            if not created_agent:
                raise BusinessException("智能体创建失败")

            logger.info(f"智能体创建成功: agent_id={agent_create.agent_id}, agent_name={agent_create.agent_name}")

            return AgentCreateResponse(
                agent_id=created_agent.agent_id,
                agent_name=created_agent.agent_name
            )

        except IntegrityError as e:
            logger.error(f"智能体创建失败 - 数据库错误: {e}")
            raise BusinessException("智能体创建失败")
        except Exception as e:
            logger.error(f"智能体创建失败: {e}")
            raise

        finally:
            db.close()

    def update_agent(self, agent_update: AgentUpdateRequest, user_id: int, username: str) -> AgentUpdateResponse:
        """
        修改智能体信息

        Args:
            agent_update: 智能体信息修改请求

        Returns:
            AgentUpdateResponse: 更新结果

        Raises:
            Exception: 更新失败时抛出异常
        """
        db = next(get_db())
        try:
            # 检查智能体是否存在
            existing_agent = self.agent_crud.get_by_agent_id(db, agent_update.agent_id)
            if not existing_agent:
                raise NotFoundError("智能体不存在")

            # 准备更新数据
            update_data = {}
            updated_fields = []

            if agent_update.agent_name is not None:
                update_data["agent_name"] = agent_update.agent_name
                updated_fields.append("agent_name")

            if agent_update.description is not None:
                update_data["description"] = agent_update.description
                updated_fields.append("description")

            if agent_update.system_prompt is not None:
                update_data["system_prompt"] = agent_update.system_prompt
                updated_fields.append("system_prompt")

            if agent_update.tools is not None:
                update_data["tools"] = agent_update.tools
                updated_fields.append("tools")

            # 处理MCP配置更新
            if agent_update.mcp_status is not None or agent_update.mcp_config is not None:
                mcp_enabled = existing_agent.mcp_enabled
                mcp_servers = existing_agent.mcp_servers

                if agent_update.mcp_status is not None:
                    mcp_enabled = agent_update.mcp_status
                    updated_fields.append("mcp_status")

                if agent_update.mcp_config is not None:
                    try:
                        import json
                        mcp_servers = json.loads(agent_update.mcp_config)
                        updated_fields.append("mcp_config")
                    except json.JSONDecodeError:
                        raise BusinessException("MCP配置必须是有效的JSON字符串")

                update_data["mcp_enabled"] = mcp_enabled
                update_data["mcp_servers"] = mcp_servers

            # 如果没有需要更新的字段
            if not update_data:
                return AgentUpdateResponse(
                    agent_id=agent_update.agent_id,
                    updated_fields=[]
                )

            # 更新智能体信息
            updated_agent = self.agent_crud.update(
                db=db,
                db_obj=existing_agent,
                obj_in=update_data,
                updated_by=username
            )

            if not updated_agent:
                raise BusinessException("智能体信息更新失败")

            logger.info(f"智能体信息更新成功: agent_id={agent_update.agent_id}, fields={updated_fields}")

            return AgentUpdateResponse(
                agent_id=updated_agent.agent_id,
                updated_fields=updated_fields
            )

        except Exception as e:
            logger.error(f"智能体信息更新失败: {e}")
            raise

        finally:
            db.close()

    def get_agent_by_id(self, agent_id: str) -> AgentInfo:
        """
        根据智能体ID获取智能体详情

        Args:
            agent_id: 智能体ID

        Returns:
            AgentInfo: 智能体详情

        Raises:
            Exception: 查询失败时抛出异常
        """
        db = next(get_db())
        try:
            agent = self.agent_crud.get_by_agent_id(db, agent_id)
            if not agent:
                raise NotFoundError("智能体不存在")

            return self._convert_to_agent_info(agent)

        except Exception as e:
            logger.error(f"获取智能体详情失败: {e}")
            raise

        finally:
            db.close()

    def get_agent_card_list(self, request: AgentCardListRequest) -> Pageable[AgentSimpleInfo]:
        """
        分页查询智能体卡片列表

        Args:
            request: 智能体卡片列表查询请求

        Returns:
            Pageable[AgentSimpleInfo]: 分页智能体卡片列表

        Raises:
            Exception: 查询失败时抛出异常
        """
        db = next(get_db())
        try:
            # 查询智能体列表
            agents, total = self.agent_crud.get_agent_list(
                db=db,
                page=request.page,
                page_size=request.page_size,
                keyword=request.keyword
            )

            # 转换为响应格式
            agent_items = [self._convert_to_agent_simple_info(agent) for agent in agents]

            # 构建分页结果
            page_result = Pageable(
                page=request.page,
                page_size=request.page_size,
                total=total,
                data=agent_items
            )

            logger.info(f"查询智能体卡片列表成功: page={request.page}, count={len(agent_items)}, total={total}")

            return page_result

        except Exception as e:
            logger.error(f"查询智能体卡片列表失败: {e}")
            raise

        finally:
            db.close()

    def get_agent_management_list(self, page: int, page_size: int, keyword: str = None, current_user_id: int = None, current_username: str = None) -> Pageable[AgentListItem]:
        """
        分页查询智能体管理列表

        Args:
            page: 页码
            page_size: 每页数量
            keyword: 关键词搜索（按名称或介绍）
            current_user_id: 当前用户ID，None表示管理员查询所有
            current_username: 当前用户名

        Returns:
            Pageable[AgentListItem]: 分页智能体管理列表

        Raises:
            Exception: 查询失败时抛出异常
        """
        db = next(get_db())
        try:
            # 查询智能体列表
            agents, total = self.agent_crud.get_agent_management_list(
                db=db,
                page=page,
                page_size=page_size,
                keyword=keyword,
                created_by=current_username if current_user_id else None  # 如果有current_user_id则只查询该用户创建的智能体
            )

            # 转换为响应格式
            agent_items = [self._convert_to_agent_list_item(agent, current_username) for agent in agents]

            # 构建分页结果
            page_result = Pageable(
                page=page,
                page_size=page_size,
                total=total,
                data=agent_items
            )

            logger.info(f"查询智能体管理列表成功: page={page}, count={len(agent_items)}, total={total}, user_filter={'admin' if current_user_id is None else current_username}")

            return page_result

        except Exception as e:
            logger.error(f"查询智能体管理列表失败: {e}")
            raise

        finally:
            db.close()

    def delete_agent(self, agent_id: str, user_id: int, username: str) -> AgentDeleteResponse:
        """
        删除智能体

        Args:
            agent_id: 智能体ID
            user_id: 当前用户ID
            username: 当前用户名

        Returns:
            AgentDeleteResponse: 删除结果

        Raises:
            Exception: 删除失败时抛出异常
        """
        db = next(get_db())
        try:
            # 检查智能体是否存在
            agent = self.agent_crud.get_by_agent_id(db, agent_id)
            if not agent:
                raise NotFoundError("智能体不存在")

            # 检查权限：管理员可以删除所有智能体，普通用户只能删除自己创建的智能体
            if agent.created_by != username:
                # 如果不是创建者，需要检查是否为管理员
                # 这里需要通过用户名查询用户角色来判断
                from src.model.crud_user import CRUDUser
                user_crud = CRUDUser(None)  # 只用于查询，不需要模型类
                current_user = user_crud.get_by_username(db, username)

                if not current_user or current_user.role != "admin":
                    raise Exception("权限不足，只能删除自己创建的智能体")

            # 逻辑删除智能体
            success = self.agent_crud.soft_delete_agent(db, agent_id, username)
            if not success:
                raise BusinessException("智能体删除失败")

            logger.info(f"智能体删除成功: agent_id={agent_id}, deleted_by={username}")

            return AgentDeleteResponse(
                agent_id=agent_id,
                deleted=True
            )

        except Exception as e:
            logger.error(f"智能体删除失败: {e}")
            raise

        finally:
            db.close()

    def update_agent_tools(self, request: AgentToolsUpdateRequest, user_id: int, username: str) -> AgentUpdateResponse:
        """
        更新智能体工具列表

        Args:
            request: 智能体工具更新请求

        Returns:
            AgentUpdateResponse: 更新结果

        Raises:
            Exception: 更新失败时抛出异常
        """
        db = next(get_db())
        try:
            # 检查智能体是否存在
            existing_agent = self.agent_crud.get_by_agent_id(db, request.agent_id)
            if not existing_agent:
                raise NotFoundError("智能体不存在")

            # 更新工具列表
            updated_agent = self.agent_crud.update_tools(
                db=db,
                agent_id=request.agent_id,
                tools=request.tools,
                updated_by=username
            )

            if not updated_agent:
                raise BusinessException("智能体工具更新失败")

            logger.info(f"智能体工具更新成功: agent_id={request.agent_id}, tools={request.tools}")

            return AgentUpdateResponse(
                agent_id=updated_agent.agent_id,
                updated_fields=["tools"]
            )

        except Exception as e:
            logger.error(f"智能体工具更新失败: {e}")
            raise

        finally:
            db.close()

    def update_agent_mcp(self, request: AgentMcpUpdateRequest, user_id: int, username: str) -> AgentUpdateResponse:
        """
        更新智能体MCP配置

        Args:
            request: 智能体MCP配置更新请求

        Returns:
            AgentUpdateResponse: 更新结果

        Raises:
            Exception: 更新失败时抛出异常
        """
        db = next(get_db())
        try:
            # 检查智能体是否存在
            existing_agent = self.agent_crud.get_by_agent_id(db, request.agent_id)
            if not existing_agent:
                raise NotFoundError("智能体不存在")

            # 处理MCP配置
            mcp_servers = existing_agent.mcp_servers
            if request.mcp_config is not None:
                try:
                    import json
                    mcp_servers = json.loads(request.mcp_config)
                except json.JSONDecodeError:
                    raise BusinessException("MCP配置必须是有效的JSON字符串")

            # 转换MCP状态
            mcp_enabled = request.mcp_status

            # 更新MCP配置
            updated_agent = self.agent_crud.update_mcp_config(
                db=db,
                agent_id=request.agent_id,
                mcp_enabled=mcp_enabled,
                mcp_servers=mcp_servers,
                updated_by=username
            )

            if not updated_agent:
                raise BusinessException("智能体MCP配置更新失败")

            updated_fields = ["mcp_status"]
            if request.mcp_config is not None:
                updated_fields.append("mcp_config")

            logger.info(f"智能体MCP配置更新成功: agent_id={request.agent_id}")

            return AgentUpdateResponse(
                agent_id=updated_agent.agent_id,
                updated_fields=updated_fields
            )

        except Exception as e:
            logger.error(f"智能体MCP配置更新失败: {e}")
            raise

        finally:
            db.close()

    def _convert_to_agent_info(self, agent) -> AgentInfo:
        """将Agent模型转换为AgentInfo响应模型"""
        return AgentInfo(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            description=agent.description or "",
            system_prompt=agent.system_prompt,
            tools=agent.tools or [],
            mcp_status=agent.mcp_enabled,
            mcp_config=str(agent.mcp_servers) if agent.mcp_servers else None,
            creator_id=0,  # 由于没有单独的creator_id字段，暂时使用0
            creator_username=agent.created_by or "system",
            created_at=agent.created_at,
            updated_by_id=None,  # 由于没有单独的updated_by_id字段，暂时使用None
            updated_by_username=agent.updated_by,
            updated_at=agent.updated_at
        )

    def _convert_to_agent_simple_info(self, agent) -> AgentSimpleInfo:
        """将Agent模型转换为AgentSimpleInfo响应模型"""
        return AgentSimpleInfo(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            description=agent.description or "",
            tools_count=len(agent.tools) if agent.tools else 0,
            mcp_enabled=agent.mcp_enabled,
            creator_username=agent.created_by or "system",
            created_at=agent.created_at
        )

    def _convert_to_agent_list_item(self, agent, current_username: str = None) -> AgentListItem:
        """将Agent模型转换为AgentListItem响应模型"""
        return AgentListItem(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            description=agent.description or "",
            tools_count=len(agent.tools) if agent.tools else 0,
            mcp_enabled=agent.mcp_enabled,
            creator_username=agent.created_by or "system",
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )


# 创建服务实例
agent_manage_service = AgentManageService()