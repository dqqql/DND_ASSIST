"""
Web 编辑器 API
为 Web 编辑器提供 HTTP API 接口
"""

import json
import urllib.parse
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any, Optional

# 使用相对导入
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.campaign import CampaignService
from src.core.story_editor_service import StoryEditorService


class EditorAPIHandler(BaseHTTPRequestHandler):
    """编辑器 API 请求处理器"""
    
    # 类级别的服务实例，避免每次请求都重新创建
    _campaign_service = None
    _editor_service = None
    
    @classmethod
    def get_services(cls):
        """获取服务实例（单例模式）"""
        if cls._campaign_service is None:
            # 确保使用正确的工作目录
            import os
            from pathlib import Path
            
            # 保存当前工作目录
            original_cwd = os.getcwd()
            
            try:
                # 切换到项目根目录
                project_root = Path(__file__).parent.parent.parent.parent
                os.chdir(project_root)
                
                # 创建服务实例
                cls._campaign_service = CampaignService()
                cls._editor_service = StoryEditorService(cls._campaign_service)
                
            finally:
                # 恢复原始工作目录
                os.chdir(original_cwd)
                
        return cls._campaign_service, cls._editor_service
    
    def __init__(self, *args, **kwargs):
        # 获取共享的服务实例
        self.campaign_service, self.editor_service = self.get_services()
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """静默处理日志"""
        pass
    
    def do_GET(self):
        """处理 GET 请求"""
        try:
            # 解析 URL
            url_parts = urllib.parse.urlparse(self.path)
            path = url_parts.path
            params = urllib.parse.parse_qs(url_parts.query)
            
            # API 路由
            if path == '/api/campaigns':
                self._handle_list_campaigns()
            elif path == '/api/stories':
                self._handle_list_stories(params)
            elif path == '/api/story':
                self._handle_get_story(params)
            elif path == '/api/story/statistics':
                self._handle_get_statistics(params)
            else:
                self._send_error(404, "API endpoint not found")
                
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_POST(self):
        """处理 POST 请求"""
        try:
            # 解析 URL
            url_parts = urllib.parse.urlparse(self.path)
            path = url_parts.path
            
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self._send_error(400, "Invalid JSON data")
                return
            
            # API 路由
            if path == '/api/story/save':
                self._handle_save_story(request_data)
            elif path == '/api/story/validate':
                self._handle_validate_story(request_data)
            elif path == '/api/story/new':
                self._handle_new_story(request_data)
            else:
                self._send_error(404, "API endpoint not found")
                
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def _handle_list_campaigns(self):
        """处理获取跑团列表请求"""
        try:
            campaigns = self.campaign_service.list_campaigns()
            self._send_json_response({"campaigns": campaigns})
        except Exception as e:
            self._send_error(500, f"获取跑团列表失败: {str(e)}")
    
    def _handle_list_stories(self, params: Dict[str, list]):
        """处理获取剧情列表请求"""
        campaign_name = self._get_param(params, 'campaign')
        if not campaign_name:
            self._send_error(400, "Missing campaign parameter")
            return
        
        stories = self.editor_service.list_available_stories(campaign_name)
        self._send_json_response({"stories": stories})
    
    def _handle_get_story(self, params: Dict[str, list]):
        """处理获取剧情数据请求"""
        campaign_name = self._get_param(params, 'campaign')
        story_name = self._get_param(params, 'story')
        
        if not campaign_name or not story_name:
            self._send_error(400, "Missing campaign or story parameter")
            return
        
        story_data = self.editor_service.load_story(campaign_name, story_name)
        if story_data is None:
            self._send_error(404, "Story not found")
            return
        
        self._send_json_response(story_data)
    
    def _handle_get_statistics(self, params: Dict[str, list]):
        """处理获取剧情统计请求"""
        campaign_name = self._get_param(params, 'campaign')
        story_name = self._get_param(params, 'story')
        
        if not campaign_name or not story_name:
            self._send_error(400, "Missing campaign or story parameter")
            return
        
        story_data = self.editor_service.load_story(campaign_name, story_name)
        if story_data is None:
            self._send_error(404, "Story not found")
            return
        
        statistics = self.editor_service.get_story_statistics(story_data)
        self._send_json_response(statistics)
    
    def _handle_save_story(self, request_data: Dict[str, Any]):
        """处理保存剧情请求"""
        campaign_name = request_data.get('campaign')
        story_name = request_data.get('story')
        story_data = request_data.get('data')
        
        if not campaign_name or not story_name or not story_data:
            self._send_error(400, "Missing required parameters")
            return
        
        success, message = self.editor_service.save_story(campaign_name, story_name, story_data)
        
        if success:
            self._send_json_response({"success": True, "message": message})
        else:
            self._send_json_response({"success": False, "error": message}, status_code=400)
    
    def _handle_validate_story(self, request_data: Dict[str, Any]):
        """处理验证剧情数据请求"""
        story_data = request_data.get('data')
        
        if not story_data:
            self._send_error(400, "Missing story data")
            return
        
        is_valid, message = self.editor_service.validate_story_data(story_data)
        self._send_json_response({
            "valid": is_valid,
            "message": message
        })
    
    def _handle_new_story(self, request_data: Dict[str, Any]):
        """处理创建新剧情请求"""
        title = request_data.get('title', '新剧情')
        story_data = self.editor_service.create_new_story(title)
        self._send_json_response(story_data)
    
    def _get_param(self, params: Dict[str, list], key: str) -> Optional[str]:
        """从参数字典中获取单个参数值"""
        values = params.get(key, [])
        return values[0] if values else None
    
    def _send_json_response(self, data: Any, status_code: int = 200):
        """发送 JSON 响应"""
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(response_data.encode('utf-8'))
    
    def _send_error(self, status_code: int, message: str):
        """发送错误响应"""
        self._send_json_response({
            "error": message,
            "status": status_code
        }, status_code)
    
    def do_OPTIONS(self):
        """处理 OPTIONS 请求（CORS 预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()