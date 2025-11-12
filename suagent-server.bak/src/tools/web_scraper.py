"""
网页抓取工具 - 使用 Playwright 和 BeautifulSoup
"""

import asyncio
from typing import Optional
from langchain_core.tools import tool
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from src.utils import get_logger

logger = get_logger(__name__)


async def _fetch_webpage_content(url: str, wait_time: int = 2000) -> str:
    """
    使用 Playwright 异步抓取网页内容
    
    Args:
        url: 目标网页 URL
        wait_time: 等待时间（毫秒）
    
    Returns:
        网页的文本内容
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(wait_time)
            
            content = await page.content()
            await browser.close()
            
            return content
    except Exception as e:
        logger.error(f"抓取网页失败 {url}: {str(e)}")
        raise


def _extract_text_from_html(html_content: str, max_length: int = 5000) -> str:
    """
    从 HTML 中提取文本内容
    
    Args:
        html_content: HTML 内容
        max_length: 最大文本长度
    
    Returns:
        提取的文本内容
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 移除脚本和样式
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # 提取文本
    text = soup.get_text(separator="\n", strip=True)
    
    # 清理多余的空行
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length] + "\n\n[内容已截断...]"
    
    return text


@tool
def scrape_webpage(url: str, max_length: Optional[int] = 5000) -> str:
    """
    抓取指定 URL 的网页内容并提取文本
    
    Args:
        url: 目标网页 URL
        max_length: 最大文本长度（默认 5000 字符）
    
    Returns:
        网页的文本内容
    """
    try:
        logger.info(f"开始抓取网页: {url}")
        
        # 使用 asyncio 运行异步函数
        html_content = asyncio.run(_fetch_webpage_content(url))
        text_content = _extract_text_from_html(html_content, max_length)
        
        logger.info(f"网页抓取完成，提取了 {len(text_content)} 字符")
        return text_content
    
    except Exception as e:
        logger.error(f"网页抓取失败: {str(e)}")
        return f"抓取网页失败: {str(e)}"


def create_web_scraper_tool():
    """创建网页抓取工具"""
    return scrape_webpage

