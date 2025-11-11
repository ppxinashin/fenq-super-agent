"""
认证拦截器

提供登录验证和权限验证功能
"""

from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.model.crud_user import crud_user
from src.model.user import User, UserRole
from src.utils.jwt_util import jwt_util
from src.utils.redis_util import redis_util
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户（从 Header 中的 Authorization 获取 Token）
    
    Args:
        authorization: Authorization Header（格式: "Bearer {token}"）
        db: 数据库会话
        
    Returns:
        当前登录的用户对象
        
    Raises:
        HTTPException: 未登录或 Token 无效
    """
    # 检查是否提供了 Authorization Header
    if not authorization:
        logger.warning("未提供 Authorization Header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 解析 Token（支持 "Bearer {token}" 格式）
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization[7:]  # 移除 "Bearer " 前缀
    
    # 验证 Token 是否有效
    if not jwt_util.verify_token(token):
        logger.warning(f"Token 无效或已过期: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查 Redis 中是否存在该 Token（如果不存在说明已登出）
    if not redis_util.exists(token):
        logger.warning(f"Token 在 Redis 中不存在（可能已登出）: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态已失效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从 Token 中获取用户 ID
    user_id = jwt_util.get_user_id_from_token(token)
    if not user_id:
        logger.warning("无法从 Token 中获取用户 ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 格式错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户信息
    user = crud_user.get(db=db, id=user_id)
    if not user:
        logger.warning(f"用户不存在: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"用户认证成功: {user.username} (ID: {user.id})")
    return user


async def verify_token_interceptor(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    登录验证拦截器
    
    验证用户是否已登录（Header 中是否包含有效的 Token）
    
    Args:
        authorization: Authorization Header（格式: "Bearer {token}"）
        
    Returns:
        验证通过的 Token
        
    Raises:
        HTTPException: 未登录或 Token 无效
        
    使用示例:
        @router.get("/protected")
        async def protected_route(token: str = Depends(verify_token_interceptor)):
            return {"message": "This is a protected route"}
    """
    # 检查是否提供了 Authorization Header
    if not authorization:
        logger.warning("未提供 Authorization Header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 解析 Token（支持 "Bearer {token}" 格式）
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization[7:]  # 移除 "Bearer " 前缀
    
    # 验证 Token 是否有效
    if not jwt_util.verify_token(token):
        logger.warning(f"Token 无效或已过期: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查 Redis 中是否存在该 Token（如果不存在说明已登出）
    if not redis_util.exists(token):
        logger.warning(f"Token 在 Redis 中不存在（可能已登出）: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态已失效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Token 验证成功: {token[:20]}...")
    return token


async def verify_admin_interceptor(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    管理员权限验证拦截器
    
    验证当前用户是否为管理员（角色为 admin）
    
    Args:
        current_user: 当前登录的用户（通过 get_current_user 依赖注入）
        
    Returns:
        当前用户对象（管理员）
        
    Raises:
        HTTPException: 用户不是管理员
        
    使用示例:
        @router.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: int,
            admin: User = Depends(verify_admin_interceptor)
        ):
            return {"message": "User deleted"}
    """
    # 检查用户角色是否为管理员
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            f"用户 {current_user.username} (ID: {current_user.id}) "
            f"尝试访问管理员功能，但角色为 {current_user.role.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问，仅管理员可操作"
        )
    
    logger.info(f"管理员权限验证成功: {current_user.username} (ID: {current_user.id})")
    return current_user

