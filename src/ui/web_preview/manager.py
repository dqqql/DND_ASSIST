"""
Web 预览管理器
负责协调 Tkinter 界面与 Web 预览的交互
"""

from pathlib import Path
from typing import Optional, Callable
from .server import WebPreviewServer


class WebPreviewManager:
    """Web 预览管理器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化管理器
        
        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent
        
        self.project_root = project_root
        self.server: Optional[WebPreviewServer] = None
        self.on_server_stop: Optional[Callable] = None
    
    def start_server(self) -> bool:
        """
        启动预览服务器
        
        Returns:
            bool: 启动是否成功
        """
        if self.server and self.server.is_running():
            return True
        
        self.server = WebPreviewServer(self.project_root)
        self.server.on_server_stop = self._on_server_stopped
        
        return self.server.start()
    
    def stop_server(self):
        """停止预览服务器"""
        if self.server:
            self.server.stop()
    
    def open_story_editor(self, campaign_name: str, story_name: Optional[str] = None) -> bool:
        """
        打开剧情编辑器
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称（可选，用于编辑现有剧情）
            
        Returns:
            bool: 是否成功打开
        """
        # 启动服务器（如果尚未启动）
        if not self.start_server():
            return False
        
        # 打开编辑器页面
        return self.server.open_story_editor(campaign_name, story_name)
    
    def open_character_viewer(self, campaign_name: str = None) -> bool:
        """
        打开角色卡查看器
        
        Args:
            campaign_name: 跑团名称（可选，用于预选跑团）
            
        Returns:
            bool: 是否成功打开
        """
        # 启动服务器（如果尚未启动）
        if not self.start_server():
            return False
        
        return self.server.open_character_viewer(campaign_name)
    
    def open_story_preview(self, campaign_name: str, story_name: str, script_name: Optional[str] = None) -> bool:
        """
        打开剧情预览
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称
            script_name: 剧本名称（可选）
            
        Returns:
            bool: 是否成功打开
        """
        # 检查必要的文件是否存在
        if not self._check_story_files(campaign_name, story_name, script_name):
            return False
        
        # 启动服务器（如果尚未启动）
        if not self.start_server():
            return False
        
        # 打开预览页面
        return self.server.open_preview(campaign_name, story_name, script_name)
    
    def _check_story_files(self, campaign_name: str, story_name: str, script_name: Optional[str] = None) -> bool:
        """
        检查剧情文件是否存在
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称
            script_name: 剧本名称（可选）
            
        Returns:
            bool: 文件是否存在
        """
        # 构建文件路径
        story_dir = self.project_root / "data" / "campaigns" / campaign_name / "notes"
        json_path = story_dir / f"{story_name}.json"
        svg_path = story_dir / f"{story_name}.svg"
        
        # 检查 JSON 文件
        if not json_path.exists():
            return False
        
        # 检查 SVG 文件
        if not svg_path.exists():
            return False
        
        return True
    
    def get_server_status(self) -> dict:
        """
        获取服务器状态
        
        Returns:
            dict: 服务器状态信息
        """
        if not self.server:
            return {
                'running': False,
                'port': None,
                'url': None
            }
        
        return {
            'running': self.server.is_running(),
            'port': self.server.get_port(),
            'url': self.server.get_url() if self.server.is_running() else None
        }
    
    def _on_server_stopped(self):
        """服务器停止时的回调"""
        if self.on_server_stop:
            self.on_server_stop()
    
    def set_server_stop_callback(self, callback: Callable):
        """
        设置服务器停止时的回调函数
        
        Args:
            callback: 回调函数
        """
        self.on_server_stop = callback
    
    def is_server_running(self) -> bool:
        """检查服务器是否正在运行"""
        return self.server is not None and self.server.is_running()
    
    def get_preview_url(self, campaign_name: str, story_name: str, script_name: Optional[str] = None) -> Optional[str]:
        """
        获取预览页面 URL
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称
            script_name: 剧本名称（可选）
            
        Returns:
            Optional[str]: 预览页面 URL，如果服务器未运行则返回 None
        """
        if not self.server or not self.server.is_running():
            return None
        
        params = {
            'campaign': campaign_name,
            'story': story_name
        }
        if script_name:
            params['script'] = script_name
        
        return self.server.get_url("tools/preview/preview.html", params)