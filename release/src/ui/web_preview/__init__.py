"""
Web 预览模块
负责剧情图可视化和未来的编辑器功能
与 Tkinter 主界面通过 HTTP 通信
"""

from .server import WebPreviewServer
from .manager import WebPreviewManager

__all__ = ['WebPreviewServer', 'WebPreviewManager']