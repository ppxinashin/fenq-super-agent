"""
用户管理控制器（管理员专用）

提供用户的增删改查功能，所有接口都需要管理员权限
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.model.crud_user import crud_user
from src.model.user import User, UserRole
from src.api.request.base_request import BasePageKeywordRequest
from src.api.request.user_request import UserAddRequest, UserEditRequest
from src.api.response.user_response import UserResponse
from src.api.response.pageable import PageableResponse
from src.api.interceptor import verify_admin_interceptor
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/user/manage",
    tags=["用户管理（管理员）"],
    dependencies=[Depends(verify_admin_interceptor)]  # 所有接口都需要管理员权限
)


@router.post("/", response_model=UserResponse, summary="新增用户")
async def create_user(
    request: UserAddRequest,
    admin: User = Depends(verify_admin_interceptor),
    db: Session = Depends(get_db)
):
    """
    新增用户（仅管理员）
    
    - **username**: 用户名
    - **password**: 密码
    - **role**: 用户角色（admin/user）
    """
    try:
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
            role=UserRole.ADMIN if request.role == "admin" else UserRole.USER,
            created_by=admin.username
        )
        
        logger.info(f"管理员 {admin.username} 创建了用户: {user.username}")
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败，请稍后重试"
        )


@router.get("/", response_model=PageableResponse[UserResponse], summary="分页查询用户")
async def list_users(
    request: BasePageKeywordRequest = Depends(),
    admin: User = Depends(verify_admin_interceptor),
    db: Session = Depends(get_db)
):
    """
    分页查询用户（仅管理员）
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页记录数（1-100）
    - **keyword**: 搜索关键词（可选，搜索用户名）
    """
    try:
        # 如果有关键词，进行搜索
        if request.keyword:
            # 计算总数
            total = db.query(User).filter(
                User.username.like(f"%{request.keyword}%"),
                User.is_deleted == False
            ).count()
            
            # 计算总页数
            total_pages = (total + request.page_size - 1) // request.page_size if total > 0 else 1
            
            # 确保页码在有效范围内
            page = max(1, min(request.page, total_pages))
            
            # 计算跳过记录数
            skip = (page - 1) * request.page_size
            
            # 查询数据
            users = db.query(User).filter(
                User.username.like(f"%{request.keyword}%"),
                User.is_deleted == False
            ).order_by(User.id.desc()).offset(skip).limit(request.page_size).all()
            
            result = {
                "items": users,
                "total": total,
                "page": page,
                "page_size": request.page_size,
                "total_pages": total_pages,
                "has_prev": page > 1,
                "has_next": page < total_pages
            }
        else:
            # 使用基类的分页查询
            result = crud_user.get_paginated(
                db=db,
                page=request.page,
                page_size=request.page_size
            )
        
        logger.info(
            f"管理员 {admin.username} 查询用户列表: "
            f"page={request.page}, page_size={request.page_size}, keyword={request.keyword}, total={result['total']}"
        )
        
        # 转换为响应模型
        return PageableResponse[UserResponse](
            items=[UserResponse.model_validate(user) for user in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
            has_prev=result["has_prev"],
            has_next=result["has_next"]
        )
        
    except Exception as e:
        logger.error(f"查询用户列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询用户列表失败，请稍后重试"
        )


@router.get("/{user_id}", response_model=UserResponse, summary="查询用户详情")
async def get_user_detail(
    user_id: int,
    admin: User = Depends(verify_admin_interceptor),
    db: Session = Depends(get_db)
):
    """
    查询用户详细信息（仅管理员）
    
    - **user_id**: 用户ID
    """
    try:
        user = crud_user.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        logger.info(f"管理员 {admin.username} 查询用户详情: {user.username} (ID: {user_id})")
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询用户详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询用户详情失败，请稍后重试"
        )


@router.put("/{user_id}", response_model=UserResponse, summary="编辑用户信息")
async def update_user(
    user_id: int,
    request: UserEditRequest,
    admin: User = Depends(verify_admin_interceptor),
    db: Session = Depends(get_db)
):
    """
    编辑用户信息（仅管理员）
    
    只能修改密码和角色，不能修改用户名
    
    - **user_id**: 用户ID
    - **password**: 新密码（可选）
    - **role**: 用户角色（可选，admin/user）
    """
    try:
        # 获取用户
        user = crud_user.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 准备更新数据
        update_data = {}
        
        # 更新密码
        if request.password:
            salt = User.generate_salt()
            password = User.hash_password(request.password, salt)
            update_data["password"] = password
            update_data["salt"] = salt
            logger.info(f"管理员 {admin.username} 修改了用户 {user.username} 的密码")
        
        # 更新角色
        if request.role:
            new_role = UserRole.ADMIN if request.role == "admin" else UserRole.USER
            if user.role != new_role:
                update_data["role"] = new_role
                logger.info(
                    f"管理员 {admin.username} 将用户 {user.username} 的角色从 "
                    f"{user.role.value} 修改为 {new_role.value}"
                )
        
        # 如果没有任何修改
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供任何修改内容"
            )
        
        # 更新用户
        updated_user = crud_user.update(
            db=db,
            db_obj=user,
            obj_in=update_data,
            updated_by=admin.username
        )
        
        logger.info(f"管理员 {admin.username} 更新了用户: {user.username} (ID: {user_id})")
        
        return UserResponse.model_validate(updated_user)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"更新用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败，请稍后重试"
        )


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    admin: User = Depends(verify_admin_interceptor),
    db: Session = Depends(get_db)
):
    """
    删除用户（软删除，仅管理员）
    
    - **user_id**: 用户ID
    """
    try:
        # 获取用户
        user = crud_user.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 不能删除自己
        if user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除自己"
            )
        
        # 软删除用户
        crud_user.delete_by_user_id(db=db, user_id=user_id, deleted_by=admin.username)
        
        logger.info(f"管理员 {admin.username} 删除了用户: {user.username} (ID: {user_id})")
        
        return {
            "message": "删除成功",
            "user_id": user_id,
            "username": user.username,
            "deleted_by": admin.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败，请稍后重试"
        )

