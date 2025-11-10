"""
CRUD操作使用示例
演示如何使用数据库模型和CRUD操作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.model import (
    init_database,
    get_db_session,
    crud_user,
    crud_agent,
    crud_session_log,
    UserRole
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def example_user_crud():
    """用户表CRUD示例"""
    logger.info("=== 用户表CRUD示例 ===")
    
    with get_db_session() as db:
        # 1. 创建普通用户
        logger.info("1. 创建普通用户")
        user = crud_user.create_user(
            db=db,
            username="zhangsan",
            plain_password="password123",
            role=UserRole.USER,
            created_by="admin"
        )
        logger.info(f"创建用户: {user}")
        
        # 2. 创建管理员用户
        logger.info("\n2. 创建管理员用户")
        admin_user = crud_user.create_user(
            db=db,
            username="admin",
            plain_password="admin123",
            role=UserRole.ADMIN,
            created_by="system"
        )
        logger.info(f"创建管理员: {admin_user}")
        
        # 3. 根据用户名查询
        logger.info("\n3. 根据用户名查询")
        found_user = crud_user.get_by_username(db=db, username="zhangsan")
        logger.info(f"查询到用户: {found_user}")
        
        # 4. 用户认证
        logger.info("\n4. 用户认证")
        auth_user = crud_user.authenticate(db=db, username="zhangsan", plain_password="password123")
        logger.info(f"认证成功: {auth_user is not None}")
        
        # 5. 检查是否为管理员
        logger.info("\n5. 检查用户角色")
        is_admin = crud_user.is_admin(db=db, user_id=user.id)
        logger.info(f"用户 {user.username} 是否为管理员: {is_admin}")
        is_admin_admin = crud_user.is_admin(db=db, user_id=admin_user.id)
        logger.info(f"用户 {admin_user.username} 是否为管理员: {is_admin_admin}")
        
        # 6. 根据角色查询用户
        logger.info("\n6. 根据角色查询用户")
        admin_users = crud_user.get_by_role(db=db, role=UserRole.ADMIN)
        logger.info(f"查询到 {len(admin_users)} 个管理员用户")
        
        normal_users = crud_user.get_by_role(db=db, role=UserRole.USER)
        logger.info(f"查询到 {len(normal_users)} 个普通用户")
        
        # 7. 更新用户角色
        logger.info("\n7. 更新用户角色")
        updated_user = crud_user.update_role(
            db=db,
            user_id=user.id,
            new_role=UserRole.ADMIN,
            updated_by="admin"
        )
        logger.info(f"角色更新成功: {updated_user is not None}, 新角色: {updated_user.role.value}")
        
        # 8. 更新密码
        logger.info("\n8. 更新密码")
        updated_user = crud_user.update_password(
            db=db,
            user_id=user.id,
            new_password="newpassword456",
            updated_by="admin"
        )
        logger.info(f"密码更新成功: {updated_user is not None}")
        
        # 9. 分页查询
        logger.info("\n9. 分页查询用户")
        page_result = crud_user.get_paginated(db=db, page=1, page_size=10)
        logger.info(f"总记录数: {page_result['total']}, 当前页: {page_result['page']}")
        logger.info(f"用户列表: {page_result['items']}")
        
        # 10. 列表查询
        logger.info("\n10. 列表查询用户")
        users = crud_user.get_multi(db=db, skip=0, limit=10)
        logger.info(f"用户列表: {users}")


def example_agent_crud():
    """智能体表CRUD示例"""
    logger.info("\n=== 智能体表CRUD示例 ===")
    
    with get_db_session() as db:
        # 1. 创建智能体
        logger.info("1. 创建智能体")
        agent = crud_agent.create_agent(
            db=db,
            agent_id="test_agent",
            agent_name="测试智能体",
            system_prompt="你是一个测试智能体，帮助用户进行测试。",
            description="这是一个用于测试的智能体",
            tools=["tool1", "tool2"],
            mcp_enabled=True,
            mcp_servers={
                "amap-maps": {
                    "type": "sse",
                    "url": "https://mcp.api-inference.modelscope.net/afbe1094621a49/sse"
                }
            },
            created_by="admin"
        )
        logger.info(f"创建智能体: {agent}")
        
        # 2. 根据agent_id查询
        logger.info("\n2. 根据agent_id查询")
        found_agent = crud_agent.get_by_agent_id(db=db, agent_id="test_agent")
        logger.info(f"查询到智能体: {found_agent}")
        
        # 3. 根据名称查询
        logger.info("\n3. 根据名称查询")
        agent_by_name = crud_agent.get_by_name(db=db, agent_name="测试智能体")
        logger.info(f"查询到智能体: {agent_by_name}")
        
        # 4. 模糊搜索
        logger.info("\n4. 模糊搜索智能体")
        agents = crud_agent.search_by_name(db=db, keyword="测试")
        logger.info(f"搜索结果: {agents}")
        
        # 5. 更新工具列表
        logger.info("\n5. 更新工具列表")
        updated_agent = crud_agent.update_tools(
            db=db,
            agent_id="test_agent",
            tools=["tool1", "tool2", "tool3"],
            updated_by="admin"
        )
        logger.info(f"工具更新成功: {updated_agent is not None}")
        
        # 6. 更新MCP配置
        logger.info("\n6. 更新MCP配置")
        updated_agent = crud_agent.update_mcp_config(
            db=db,
            agent_id="test_agent",
            mcp_enabled=False,
            updated_by="admin"
        )
        logger.info(f"MCP配置更新成功: {updated_agent is not None}")
        
        # 7. 分页查询
        logger.info("\n7. 分页查询智能体")
        page_result = crud_agent.get_paginated(db=db, page=1, page_size=10)
        logger.info(f"总记录数: {page_result['total']}, 当前页: {page_result['page']}")


def example_session_log_crud():
    """会话日志表CRUD示例"""
    logger.info("\n=== 会话日志表CRUD示例 ===")
    
    with get_db_session() as db:
        session_id = 123456789  # 示例会话ID
        agent_id = "test_agent"  # 智能体ID
        
        # 1. 创建会话日志
        logger.info("1. 创建会话日志")
        log1 = crud_session_log.create_log(
            db=db,
            session_id=session_id,
            agent_id=agent_id,
            role="user",
            content="你好，请帮我查询天气",
            created_by="system"
        )
        logger.info(f"创建日志1: {log1}")
        
        log2 = crud_session_log.create_log(
            db=db,
            session_id=session_id,
            agent_id=agent_id,
            role="assistant",
            content="好的，我来帮您查询天气信息。",
            created_by="system"
        )
        logger.info(f"创建日志2: {log2}")
        
        # 测试会话ID绑定验证
        logger.info("\n测试会话ID绑定验证")
        try:
            # 尝试用不同的agent_id创建日志（应该失败）
            crud_session_log.create_log(
                db=db,
                session_id=session_id,
                agent_id="another_agent",
                role="user",
                content="测试消息",
                created_by="system"
            )
            logger.warning("警告：应该抛出异常但没有！")
        except ValueError as e:
            logger.info(f"验证成功：{e}")
        
        # 2. 根据会话ID查询所有日志
        logger.info("\n2. 根据会话ID查询所有日志")
        logs = crud_session_log.get_by_session_id(db=db, session_id=session_id)
        logger.info(f"查询到 {len(logs)} 条日志")
        
        # 3. 获取最新的N条日志
        logger.info("\n3. 获取最新的N条日志")
        latest_logs = crud_session_log.get_latest_by_session_id(
            db=db,
            session_id=session_id,
            limit=10
        )
        logger.info(f"最新 {len(latest_logs)} 条日志")
        
        # 4. 分页查询会话日志
        logger.info("\n4. 分页查询会话日志")
        page_result = crud_session_log.get_paginated_by_session(
            db=db,
            session_id=session_id,
            page=1,
            page_size=20
        )
        logger.info(f"总记录数: {page_result['total']}, 当前页: {page_result['page']}")
        
        # 5. 统计日志数量
        logger.info("\n5. 统计日志数量")
        count = crud_session_log.count_by_session_id(db=db, session_id=session_id)
        logger.info(f"会话 {session_id} 共有 {count} 条日志")
        
        # 6. 获取会话所属的智能体
        logger.info("\n6. 获取会话所属的智能体")
        session_agent = crud_session_log.get_session_agent(db=db, session_id=session_id)
        logger.info(f"会话 {session_id} 属于智能体: {session_agent}")
        
        # 7. 根据智能体ID查询日志
        logger.info("\n7. 根据智能体ID查询日志")
        agent_logs = crud_session_log.get_by_agent_id(db=db, agent_id=agent_id, limit=10)
        logger.info(f"智能体 {agent_id} 共有 {len(agent_logs)} 条日志")
        
        # 8. 根据会话ID和智能体ID查询
        logger.info("\n8. 根据会话ID和智能体ID查询")
        specific_logs = crud_session_log.get_by_session_and_agent(
            db=db,
            session_id=session_id,
            agent_id=agent_id
        )
        logger.info(f"查询到 {len(specific_logs)} 条日志")
        
        # 9. 获取智能体的所有会话ID
        logger.info("\n9. 获取智能体的所有会话ID")
        session_ids = crud_session_log.get_sessions_by_agent(db=db, agent_id=agent_id)
        logger.info(f"智能体 {agent_id} 的会话列表: {session_ids}")


def main():
    """主函数"""
    try:
        # 初始化数据库
        logger.info("初始化数据库...")
        init_database()
        
        # 执行示例
        example_user_crud()
        example_agent_crud()
        example_session_log_crud()
        
        logger.info("\n=== 所有示例执行完成 ===")
        
    except Exception as e:
        logger.error(f"执行示例时出错: {e}", exc_info=True)


if __name__ == "__main__":
    main()

