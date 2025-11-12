"""
用户相关控制器
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.model.crud_user import crud_user
from src.api.request.user_request import UserLoginRequest, UserRegisterRequest
from src.api.response.user_response import UserLoginResponse, UserRegisterResponse, UserResponse
from src.utils.jwt_util import jwt_util
from src.utils.redis_util import redis_util
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/user", tags=["用户管理"])


@router.post("/register", response_model=UserRegisterResponse, summary="用户注册")
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    - **username**: 用户名，最多20个字符，只支持大小写字母和下划线
    - **password**: 密码，至少8位，只允许ASCII范围内的可见字符
    - **password_confirm**: 确认密码，必须与密码一致
    """
    try:
        # 验证密码是否匹配
        request.validate_password_match()
        
        # 检查用户名是否已存在
        existing_user = crud_user.get_by_username(db=db, username=request.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 创建用户
        user = crud_user.create_user(
            db=db,
            username=request.username,
            plain_password=request.password,
            created_by="system"
        )
        
        logger.info(f"用户注册成功: {user.username}")
        
        # 返回响应
        return UserRegisterResponse(
            user=UserResponse.model_validate(user),
            message="注册成功"
        )
        
    except ValueError as e:
        logger.warning(f"注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=UserLoginResponse, summary="用户登录")
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    登录成功返回 JWT Token，Token 会存储在 Redis 中
    """
    try:
        # 验证用户名和密码
        user = crud_user.authenticate(
            db=db,
            username=request.username,
            plain_password=request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 生成 JWT Token
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value
        }
        token = jwt_util.create_token(token_data)
        
        # 将用户信息存储到 Redis（以 Token 为键）
        user_info = {
            "id": user.id,
            "username": user.username,
            "role": user.role.value,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
        user_info_json = json.dumps(user_info, ensure_ascii=False)
        
        # 设置过期时间（与 JWT Token 一致）
        expire_seconds = settings.jwt_expire_minutes * 60
        redis_util.set(token, user_info_json, expire=expire_seconds)
        
        logger.info(f"用户登录成功: {user.username}")
        
        # 返回响应
        return UserLoginResponse(
            token=token,
            user=UserResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post("/logout", summary="用户登出")
async def logout(token: str):
    """
    用户登出
    
    - **token**: JWT Token
    
    登出时会删除 Redis 中的 Token
    """
    try:
        # 验证 Token 是否有效
        if not jwt_util.verify_token(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 无效或已过期"
            )
        
        # 从 Redis 中删除 Token
        redis_util.delete(token)
        
        logger.info("用户登出成功")
        
        return {"message": "登出成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登出失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败，请稍后重试"
        )


@router.get("/info", response_model=UserResponse, summary="获取当前用户信息")
async def get_user_info(
    token: str,
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    
    - **token**: JWT Token
    """
    try:
        # 验证 Token 并获取用户 ID
        user_id = jwt_util.get_user_id_from_token(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 无效或已过期"
            )
        
        # 先从 Redis 获取用户信息
        user_info_json = redis_util.get(token)
        if user_info_json:
            user_info = json.loads(user_info_json)
            # 从数据库获取完整用户信息（包括创建人等字段）
            user = crud_user.get(db=db, id=user_id)
            if user:
                return UserResponse.model_validate(user)
        
        # Redis 中没有，从数据库获取
        user = crud_user.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败，请稍后重试"
        )

