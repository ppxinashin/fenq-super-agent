"""
Memory Formatter - 记忆数据格式化工具
"""

import re
import html
from datetime import datetime
from typing import List, Dict, Any

class MemoryFormatter:
    """记忆数据格式化器"""

    @staticmethod
    def format_session_to_markdown(session_logs: List[Dict[str, Any]], session_title: str = "会话记录") -> str:
        """
        将会话日志格式化为标准 Markdown 格式

        Args:
            session_logs: 会话日志列表
            session_title: 会话标题

        Returns:
            格式化后的 Markdown 内容
        """
        if not session_logs:
            return "# 会话记录\n\n暂无对话内容。\n"

        # 文档头部信息
        markdown_lines = [
            f"# {session_title}",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**对话轮次**: {len([log for log in session_logs if log['role'] == 'user'])}",
            f"**消息总数**: {len(session_logs)}",
            "",
            "---",
            ""
        ]

        # 格式化每条消息
        for log in session_logs:
            role_display = {
                'user': '👤 用户',
                'assistant': '🤖 助手',
                'system': '⚙️ 系统'
            }.get(log['role'], log['role'])

            # 清理和转义内容
            content = log['content']
            content = html.unescape(content)  # 转义HTML实体
            content = content.strip()  # 去除首尾空白

            # 处理代码块
            content = MemoryFormatter._format_code_blocks(content)

            # 处理列表项
            content = MemoryFormatter._format_list_items(content)

            markdown_lines.extend([
                f"## {role_display}",
                "",
                content,
                "",
                "---",
                ""
            ])

        return "\n".join(markdown_lines)

    @staticmethod
    def _format_code_blocks(content: str) -> str:
        """格式化代码块"""
        # 处理现有的代码块标记
        content = re.sub(r'```(\w+)?\s*\n', r'```\1\n', content)

        # 为没有语言标记的代码块添加通用标记
        content = re.sub(r'```\s*\n([^`]+?)\n```', lambda m: f"```\n{m.group(1)}\n```", content, flags=re.DOTALL)

        return content

    @staticmethod
    def _format_list_items(content: str) -> str:
        """格式化列表项"""
        lines = content.split('\n')
        formatted_lines = []

        for line in lines:
            stripped = line.strip()
            # 确保列表项有正确的空格缩进
            if stripped.startswith(('- ', '* ', '+ ')):
                formatted_lines.append(line)
            elif stripped and not line.startswith('    ') and not line.startswith('#'):
                # 普通段落文本
                formatted_lines.append(line)
            else:
                formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    @staticmethod
    def generate_filename(session_title: str, date: datetime = None) -> str:
        """
        生成标准化的文件名

        Args:
            session_title: 会话标题
            date: 日期对象，默认为当前时间

        Returns:
            标准化的文件名
        """
        if date is None:
            date = datetime.now()

        # 清理标题中的特殊字符
        clean_title = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', session_title)
        clean_title = re.sub(r'\s+', '_', clean_title.strip())
        clean_title = clean_title[:50] if len(clean_title) > 50 else clean_title

        date_str = date.strftime('%Y%m%d')
        return f"{clean_title}_{date_str}.md" if clean_title else f"会话记录_{date_str}.md"

    @staticmethod
    def validate_content(content: str) -> bool:
        """
        验证内容是否符合存储要求

        Args:
            content: 待验证的内容

        Returns:
            是否有效
        """
        if not content or not content.strip():
            return False

        # 检查内容长度限制（避免过大文件）
        if len(content) > 10 * 1024 * 1024:  # 10MB
            return False

        # 检查是否包含潜在恶意内容
        forbidden_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html',
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return False

        return True

    @staticmethod
    def get_content_summary(content: str, max_length: int = 200) -> str:
        """
        获取内容摘要

        Args:
            content: 原始内容
            max_length: 摘要最大长度

        Returns:
            内容摘要
        """
        if not content:
            return "空内容"

        # 移除 Markdown 标记，获取纯文本
        plain_text = re.sub(r'[#*`\-\[\]()]', ' ', content)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()

        if len(plain_text) <= max_length:
            return plain_text

        return plain_text[:max_length] + "..."

    @staticmethod
    def calculate_size(content: str) -> int:
        """
        计算内容大小（字节）

        Args:
            content: 内容字符串

        Returns:
            字节大小
        """
        return len(content.encode('utf-8'))