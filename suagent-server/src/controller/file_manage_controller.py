"""
文件管理控制器
"""

from fastapi import APIRouter, Depends, Request, UploadFile, File, Query, HTTPException, status
from typing import Optional
from src.api_middlewares.role_middleware import require_roles
from src.api_middlewares.jwt_middleware import get_current_user_from_token
from src.consts import StatusCode
from src.service.file_manage_service import file_manage_service
from src.request.file_manage_request import FileListRequest, FileChunksRequest, FileDeleteRequest
from src.response.base_response import ApiResponse, success_response, business_error_response
from src.response.file_manage_response import (
    FileUploadResponse, FileListResponse, FileChunksResponse, FileDeleteResponse
)
from src.response.auth_response import UserInfo
from src.consts.user_consts import UserConsts
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["文件管理"])


@router.post("/files/upload", response_model=ApiResponse[FileUploadResponse], summary="上传文件")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def upload_file(
    request: Request,
    agent_id: str = Query(..., description="智能体ID"),
    file: UploadFile = File(..., description="上传的文件"),
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    上传文件到知识库

    功能点：
    - 按 agent_id/username 路径存储
    - 自动创建路径（如不存在）
    - 上传到MinIO，分块处理由桶监听服务完成

    权限控制：
    - 仅限登录用户
    """
    try:
        logger.info(f"用户上传文件: user={current_user.username}, agent_id={agent_id}, filename={file.filename}")

        # 读取文件数据
        file_data = await file.read()
        file_size = len(file_data)

        # 将bytes转换为BytesIO
        from io import BytesIO
        file_stream = BytesIO(file_data)

        # 上传文件
        result = file_manage_service.upload_file(
            file_data=file_stream,
            file_name=file.filename,
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            agent_id=agent_id,
            username=current_user.username
        )

        return success_response(result=result, message="文件上传成功")

    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return business_error_response(f"文件上传失败: {str(e)}")


@router.get("/files", response_model=ApiResponse[FileListResponse], summary="文件列表")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def get_file_list(
    request: Request,
    agent_id: str = Query(..., description="智能体ID"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    查看知识库文件列表

    功能点：
    - 显示文件名、类型、作者、分块数、状态
    - 显示创建和更新时间
    - 支持分页

    权限控制：
    - 用户只能查看自己的文件
    """
    try:
        logger.info(f"用户查询文件列表: user={current_user.username}, agent_id={agent_id}, page={page}")

        result = file_manage_service.get_file_list(
            agent_id=agent_id,
            username=current_user.username,
            page=page,
            page_size=page_size
        )

        return success_response(result=result, message="查询成功")

    except Exception as e:
        logger.error(f"查询文件列表失败: {e}")
        return business_error_response(f"查询文件列表失败: {str(e)}")


@router.get("/files/chunks", response_model=ApiResponse[FileChunksResponse], summary="文件分块查看")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def get_file_chunks(
    request: Request,
    agent_id: str = Query(..., description="智能体ID"),
    source: str = Query(..., description="文件路径"),
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    查看文件的分块详情

    功能点：
    - 显示分块个数、索引和内容
    - 显示文件属性信息

    权限控制：
    - 用户只能查看自己的文件
    """
    try:
        logger.info(f"用户查询文件分块: user={current_user.username}, agent_id={agent_id}, source={source}")

        result = file_manage_service.get_file_chunks(
            agent_id=agent_id,
            username=current_user.username,
            source=f"{agent_id}/{current_user.username}/{source}"
        )

        return success_response(result=result, message="查询成功")

    except ValueError as e:
        logger.warning(f"文件不存在: {e}")
        return business_error_response(str(e))
    except Exception as e:
        logger.error(f"查询文件分块失败: {e}")
        return business_error_response(f"查询文件分块失败: {str(e)}")


@router.delete("/files", response_model=ApiResponse[FileDeleteResponse], summary="删除文件")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def delete_file(
    request: Request,
    agent_id: str = Query(..., description="智能体ID"),
    source: str = Query(..., description="文件路径"),
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    删除知识库文件

    功能点：
    - 删除 MinIO 中的文件
    - 向量库的清理由桶监听服务处理

    权限控制：
    - 用户只能删除自己的文件
    """
    try:
        logger.info(f"用户删除文件: user={current_user.username}, agent_id={agent_id}, source={source}")

        result = file_manage_service.delete_file(
            agent_id=agent_id,
            username=current_user.username,
            source=f"{agent_id}/{current_user.username}/{source}"
        )

        return success_response(result=result, message="文件删除成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文件失败: {e}")
        return business_error_response(f"删除文件失败: {str(e)}")

