"""
YouTube 视频搜索 MCP 服务器（SSE）— FastMCP 版本
=================================================

一个基于 **FastMCP** 的最小可运行示例，提供一个工具 `youtube.search` 用于搜索 YouTube 视频。

快速开始
-----------

工具名：`youtube.search`
调用示例：
    {"query": "python asyncio tutorial"}

返回字段：`title, author, url, published_at`
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field, field_validator
from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config.settings import settings


# -----------------------
# Pydantic param schemas
# -----------------------

class SearchParams(BaseModel):
    query: str = Field(..., description="搜索关键字。")
    max_results: int = Field(5, ge=1, le=50, description="返回条数。")
    order: str = Field(
        "relevance",
        description="排序方式：relevance | date | viewCount | rating | title | videoCount",
    )
    published_after: Optional[str] = Field(
        None, description="ISO 8601 时间（可选，例如 '2024-01-01T00:00:00Z'）"
    )
    duration: Optional[str] = Field(
        None, description="可选：short | medium | long"
    )
    language: Optional[str] = Field(
        None, description="BCP-47 语言代码"
    )

    @field_validator("order")
    @classmethod
    def _validate_order(cls, v: str) -> str:
        allowed = {"relevance", "date", "viewCount", "rating", "title", "videoCount"}
        if v not in allowed:
            raise ValueError(f"order must be one of {sorted(allowed)}")
        return v

    @field_validator("duration")
    @classmethod
    def _validate_duration(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = {"short", "medium", "long"}
        if v not in allowed:
            raise ValueError("duration must be short | medium | long")
        return v


class VideoRow(TypedDict):
    title: str
    author: str
    url: str
    published_at: str


# -----------------------
# YouTube helpers
# -----------------------

def youtube_client():
    key = settings.youtube_api_key
    if not key:
        raise RuntimeError(
            "YOUTUBE_API_KEY is not set. Create an API key (YouTube Data API v3) and export it."
        )
    return build("youtube", "v3", developerKey=key)


def iso8601_duration_to_compact(iso: str) -> str:
    """Convert ISO8601 duration (PT1H2M7S) to 'H:MM:SS' or 'M:SS'."""
    try:
        import isodate
        td = isodate.parse_duration(iso)
        total = int(td.total_seconds())
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"
    except Exception:
        return iso  # graceful fallback


async def do_search(params: SearchParams) -> List[VideoRow]:
    yt = youtube_client()

    search_kwargs = dict(
        part="id,snippet",
        q=params.query,
        type="video",
        maxResults=params.max_results,
        order=params.order,
    )
    if params.published_after:
        search_kwargs["publishedAfter"] = params.published_after
    if params.duration:
        search_kwargs["videoDuration"] = params.duration
    if params.language:
        search_kwargs["relevanceLanguage"] = params.language

    try:
        search_resp = yt.search().list(**search_kwargs).execute()
    except HttpError as e:
        raise RuntimeError(f"YouTube API search failed: {e}")

    items = search_resp.get("items", [])
    if not items:
        return []

    video_ids = ",".join(i["id"].get("videoId", "") for i in items if i.get("id"))
    details_by_id: Dict[str, Dict[str, Any]] = {}
    if video_ids:
        try:
            vids_resp = yt.videos().list(part="contentDetails,statistics", id=video_ids).execute()
            details_by_id = {v["id"]: v for v in vids_resp.get("items", [])}
        except HttpError:
            details_by_id = {}

    rows: List[VideoRow] = []
    for it in items:
        vid = it["id"].get("videoId")
        if not vid:
            continue
        sn = it.get("snippet", {})
        rows.append(
            VideoRow(
                title=sn.get("title", ""),
                author=sn.get("channelTitle", ""),
                url=f"https://www.youtube.com/watch?v={vid}",
                published_at=sn.get("publishedAt", ""),
            )
        )

    return rows


# -----------------------
# FastMCP server
# -----------------------

mcp = FastMCP(
    name="suagent-youtube-mcp",
    host=settings.fastmcp_host,
    port=settings.fastmcp_port,
)


@mcp.tool()
async def youtube_search(query: str) -> Any:
    """搜索 YouTube 视频（仅返回前 5 条最相关结果）。

    入参：
      - query: 搜索关键词
    返回：JSON 数组，元素包含：title, author, url, published_at
    """
    params = SearchParams(
        query=query,
        max_results=settings.youtube_search_limit,  # 从配置中获取，默认为 5
        order="relevance",     # 固定按相关度
        published_after=None,
        duration=None,
        language=None,          # 语言不限
    )
    return await do_search(params)


def run_youtube_mcp_server():
    mcp.run(transport="sse")
