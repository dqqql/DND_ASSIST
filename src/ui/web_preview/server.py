"""
Web 预览服务器
提供本地 HTTP 服务，支持剧情可视化预览和编辑功能
"""

import os
import socket
import threading
import time
import webbrowser
import json
import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlencode, urlparse
from typing import Optional, Callable

# 日志文件路径
LOG_FILE = Path(__file__).parent.parent.parent.parent / "web_editor_debug.log"

def log_debug(message):
    """写入调试日志"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
        print(f"[DEBUG] {message}")
    except Exception as e:
        print(f"[ERROR] 写入日志失败: {e}")

from .editor_api import EditorAPIHandler


class WebPreviewRequestHandler(SimpleHTTPRequestHandler):
    """Web 预览请求处理器"""
    
    def log_message(self, format, *args):
        """静默处理请求日志"""
        pass
    
    def _send_error_response(self, status_code, message):
        """发送错误响应，避免中文编码问题"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = json.dumps({
            "error": message,
            "status": status_code
        }, ensure_ascii=False, indent=2)
        self.wfile.write(error_response.encode('utf-8'))
    
    def do_GET(self):
        """处理 GET 请求"""
        # 记录访问时间
        if hasattr(self.server, '_preview_server'):
            self.server._preview_server.last_access_time = time.time()
        
        # 检查是否是 API 请求
        if self.path.startswith('/api/'):
            try:
                self._handle_api_request()
            except Exception as e:
                print(f"[ERROR] GET API请求处理失败: {e}")
                self._send_error_response(500, f"API请求处理失败: {str(e)}")
            return
        
        return super().do_GET()
    
    def do_POST(self):
        """处理 POST 请求"""
        # 记录访问时间
        if hasattr(self.server, '_preview_server'):
            self.server._preview_server.last_access_time = time.time()
        
        # 检查是否是 API 请求
        if self.path.startswith('/api/'):
            try:
                self._handle_api_request()
            except Exception as e:
                print(f"[ERROR] POST API请求处理失败: {e}")
                self._send_error_response(500, f"API请求处理失败: {str(e)}")
            return
        
        return super().do_POST()
    
    def do_DELETE(self):
        """处理 DELETE 请求"""
        # 记录访问时间
        if hasattr(self.server, '_preview_server'):
            self.server._preview_server.last_access_time = time.time()
        
        # 检查是否是 API 请求
        if self.path.startswith('/api/'):
            try:
                self._handle_api_request()
            except Exception as e:
                print(f"[ERROR] DELETE API请求处理失败: {e}")
                self._send_error_response(500, f"API请求处理失败: {str(e)}")
            return
        
        return super().do_DELETE() if hasattr(super(), 'do_DELETE') else self._send_error_response(405, "Method not allowed")
        """处理 OPTIONS 请求（CORS 预检）"""
        # 记录访问时间
        if hasattr(self.server, '_preview_server'):
            self.server._preview_server.last_access_time = time.time()
        
        # 检查是否是 API 请求
        if self.path.startswith('/api/'):
            try:
                self._handle_api_request()
            except Exception as e:
                print(f"[ERROR] OPTIONS API请求处理失败: {e}")
                self._send_error_response(500, f"API请求处理失败: {str(e)}")
            return
        
        # 对于非 API 请求，返回基本的 CORS 头
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _handle_api_request(self):
        """处理 API 请求"""
        try:
            # 获取服务实例
            log_debug("获取服务实例...")
            campaign_service, editor_service, file_manager_service = EditorAPIHandler.get_services()
            log_debug("服务实例获取成功")
            
            # 解析 URL
            url_parts = urlparse(self.path)
            path = url_parts.path
            
            log_debug(f"API请求: {self.command} {path}")
            
            # 更安全的参数解析
            params = {}
            if url_parts.query:
                try:
                    import urllib.parse
                    params = urllib.parse.parse_qs(url_parts.query)
                    # 将列表值转换为单个值
                    params = {k: v[0] if v else '' for k, v in params.items()}
                except Exception as e:
                    log_debug(f"参数解析失败: {e}")
                    params = {}
            
            # 读取请求体（对于 POST 和 DELETE 请求）
            request_data = {}
            if self.command in ['POST', 'DELETE']:
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        post_data = self.rfile.read(content_length)
                        request_data = json.loads(post_data.decode('utf-8'))
                        log_debug(f"请求数据: {str(request_data)[:200]}...")  # 只记录前200个字符
                except (ValueError, json.JSONDecodeError) as e:
                    log_debug(f"请求数据解析失败: {e}")
                    self._send_api_error(400, f"Invalid request data: {str(e)}")
                    return
            
            try:
                if self.command == 'GET':
                    self._handle_api_get(path, params, campaign_service, editor_service, file_manager_service)
                elif self.command == 'POST':
                    self._handle_api_post(path, request_data, campaign_service, editor_service, file_manager_service)
                elif self.command == 'DELETE':
                    self._handle_api_delete(path, request_data, campaign_service, editor_service, file_manager_service)
                elif self.command == 'OPTIONS':
                    self._handle_api_options()
                else:
                    self._send_api_error(405, "Method not allowed")
            except Exception as e:
                log_debug(f"API处理异常: {e}")
                import traceback
                log_debug(f"错误堆栈: {traceback.format_exc()}")
                self._send_api_error(500, f"Internal server error: {str(e)}")
        except Exception as e:
            log_debug(f"API请求处理失败: {e}")
            import traceback
            log_debug(f"错误堆栈: {traceback.format_exc()}")
            self._send_api_error(500, f"API request failed: {str(e)}")
    
    def _handle_api_get(self, path, params, campaign_service, editor_service, file_manager_service):
        """处理 GET API 请求"""
        if path == '/api/campaigns':
            campaigns = campaign_service.list_campaigns()
            self._send_api_response({"campaigns": campaigns})
        elif path == '/api/stories':
            campaign_name = params.get('campaign')
            if not campaign_name:
                self._send_api_error(400, "Missing campaign parameter")
                return
            stories = editor_service.list_available_stories(campaign_name)
            self._send_api_response({"stories": stories})
        elif path == '/api/story':
            campaign_name = params.get('campaign')
            story_name = params.get('story')
            if not campaign_name or not story_name:
                self._send_api_error(400, "Missing campaign or story parameter")
                return
            story_data = editor_service.load_story(campaign_name, story_name)
            if story_data is None:
                self._send_api_error(404, "Story not found")
                return
            self._send_api_response(story_data)
        elif path == '/api/story/statistics':
            campaign_name = params.get('campaign')
            story_name = params.get('story')
            if not campaign_name or not story_name:
                self._send_api_error(400, "Missing campaign or story parameter")
                return
            story_data = editor_service.load_story(campaign_name, story_name)
            if story_data is None:
                self._send_api_error(404, "Story not found")
                return
            statistics = editor_service.get_story_statistics(story_data)
            self._send_api_response(statistics)
        elif path == '/api/characters':
            self._handle_character_list(params, campaign_service, file_manager_service)
        elif path == '/api/character':
            self._handle_character_detail(params, campaign_service, file_manager_service)
        elif path == '/api/monsters':
            self._handle_monster_list(params, campaign_service, file_manager_service)
        elif path == '/api/monster':
            self._handle_monster_detail(params, campaign_service, file_manager_service)
        elif path == '/api/maps':
            self._handle_map_list(params, campaign_service, file_manager_service)
        elif path == '/api/map':
            self._handle_map_detail(params, campaign_service, file_manager_service)
        else:
            self._send_api_error(404, "API endpoint not found")
    
    def _handle_api_post(self, path, request_data, campaign_service, editor_service, file_manager_service):
        """处理 POST API 请求"""
        if path == '/api/campaigns':
            # 创建跑团
            name = request_data.get('name')
            if not name:
                self._send_api_error(400, "Missing campaign name")
                return
            
            success = campaign_service.create_campaign(name)
            if success:
                self._send_api_response({"success": True, "message": f"跑团 {name} 创建成功"})
            else:
                self._send_api_response({"success": False, "error": "跑团已存在或创建失败"}, status_code=400)
        elif path == '/api/files':
            # 创建文件
            campaign_name = request_data.get('campaign')
            category = request_data.get('category')
            filename = request_data.get('filename')
            file_type = request_data.get('file_type', 'txt')
            
            if not campaign_name or not category or not filename:
                self._send_api_error(400, "Missing required parameters")
                return
            
            # 选择跑团
            campaign = campaign_service.select_campaign(campaign_name)
            if not campaign:
                self._send_api_error(404, "Campaign not found")
                return
            
            # 创建文件
            success = file_manager_service.create_file(category, filename)
            if success:
                self._send_api_response({"success": True, "message": f"文件 {filename} 创建成功"})
            else:
                self._send_api_response({"success": False, "error": "文件创建失败或文件已存在"}, status_code=400)
        elif path == '/api/story/save':
            log_debug("处理保存剧情请求...")
            campaign_name = request_data.get('campaign')
            story_name = request_data.get('story')
            story_data = request_data.get('data')
            
            log_debug(f"保存参数: campaign={campaign_name}, story={story_name}")
            
            if not campaign_name or not story_name or not story_data:
                log_debug("保存参数不完整")
                self._send_api_error(400, "Missing required parameters")
                return
            
            log_debug("调用editor_service.save_story...")
            success, message = editor_service.save_story(campaign_name, story_name, story_data)
            
            log_debug(f"保存结果: success={success}, message={message}")
            
            if success:
                self._send_api_response({"success": True, "message": message})
            else:
                self._send_api_response({"success": False, "error": message}, status_code=400)
        elif path == '/api/story/validate':
            story_data = request_data.get('data')
            if not story_data:
                self._send_api_error(400, "Missing story data")
                return
            
            is_valid, message = editor_service.validate_story_data(story_data)
            self._send_api_response({
                "valid": is_valid,
                "message": message
            })
        elif path == '/api/story/new':
            title = request_data.get('title', '新剧情')
            story_data = editor_service.create_new_story(title)
            self._send_api_response(story_data)
        elif path == '/api/file/save':
            # 保存文件内容
            campaign_name = request_data.get('campaign')
            category = request_data.get('category')
            filename = request_data.get('filename')
            content = request_data.get('content')
            
            if not campaign_name or not category or not filename or content is None:
                self._send_api_error(400, "Missing required parameters")
                return
            
            success, message = file_manager_service.save_file_content(
                campaign_name, category, filename, content
            )
            
            if success:
                self._send_api_response({"success": True, "message": message})
            else:
                self._send_api_response({"success": False, "error": message}, status_code=400)
        else:
            self._send_api_error(404, "API endpoint not found")
    
    def _handle_api_delete(self, path, request_data, campaign_service, editor_service, file_manager_service):
        """处理 DELETE API 请求"""
        if path == '/api/campaigns':
            # 删除跑团
            name = request_data.get('name')
            if not name:
                self._send_api_error(400, "Missing campaign name")
                return
            
            success = campaign_service.delete_campaign(name)
            if success:
                self._send_api_response({"success": True, "message": f"跑团 {name} 删除成功"})
            else:
                self._send_api_response({"success": False, "error": "删除跑团失败"}, status_code=400)
        elif path == '/api/files':
            # 删除文件
            campaign_name = request_data.get('campaign')
            category = request_data.get('category')
            filename = request_data.get('filename')
            
            if not campaign_name or not category or not filename:
                self._send_api_error(400, "Missing required parameters")
                return
            
            # 选择跑团
            campaign = campaign_service.select_campaign(campaign_name)
            if not campaign:
                self._send_api_error(404, "Campaign not found")
                return
            
            # 删除文件（软删除）
            success = file_manager_service.delete_file(category, filename)
            if success:
                self._send_api_response({"success": True, "message": f"文件 {filename} 删除成功"})
            else:
                self._send_api_response({"success": False, "error": "删除文件失败"}, status_code=400)
        else:
            self._send_api_error(404, "API endpoint not found")
    
    def _handle_api_options(self):
        """处理 OPTIONS API 请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_api_response(self, data, status_code=200):
        """发送 API 响应"""
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(response_data.encode('utf-8'))
    
    def _send_api_error(self, status_code, message):
        """发送 API 错误响应"""
        self._send_api_response({
            "error": message,
            "status": status_code
        }, status_code)
    
    def _handle_character_list(self, params, campaign_service, file_manager_service):
        """处理人物卡列表请求"""
        campaign_name = params.get('campaign')
        if not campaign_name:
            self._send_api_error(400, "Missing campaign parameter")
            return
        
        try:
            # 选择跑团
            campaign = campaign_service.select_campaign(campaign_name)
            if not campaign:
                self._send_api_error(404, "Campaign not found")
                return
            
            # 获取人物卡文件列表
            files = file_manager_service.list_files("characters")
            
            # 转换为 API 响应格式
            characters = []
            for file_info in files:
                if not file_info.is_directory:
                    characters.append({
                        "name": file_info.get_display_name(),
                        "filename": file_info.name,
                        "file_type": file_info.file_type,
                        "is_hidden": file_info.is_hidden
                    })
            
            self._send_api_response({"characters": characters})
            
        except Exception as e:
            self._send_api_error(500, f"获取人物卡列表失败: {str(e)}")
    
    def _handle_character_detail(self, params, campaign_service, file_manager_service):
        """处理人物卡详情请求"""
        campaign_name = params.get('campaign')
        character_name = params.get('name')
        
        if not campaign_name or not character_name:
            self._send_api_error(400, "Missing campaign or name parameter")
            return
        
        try:
            # 选择跑团
            campaign = campaign_service.select_campaign(campaign_name)
            if not campaign:
                self._send_api_error(404, "Campaign not found")
                return
            
            # 读取人物卡内容
            content = file_manager_service.read_file_content("characters", character_name)
            if content is None:
                self._send_api_error(404, "Character not found")
                return
            
            # 解析人物卡内容
            character_data = self._parse_character_content(content, character_name)
            self._send_api_response(character_data)
            
        except Exception as e:
            self._send_api_error(500, f"获取人物卡失败: {str(e)}")
    
    def _handle_monster_list(self, params, campaign_service, file_manager_service):
        """处理怪物卡列表请求"""
        campaign_name = params.get('campaign')
        if not campaign_name:
            self._send_api_error(400, "Missing campaign parameter")
            return
        
        try:
            # 选择跑团
            campaign = campaign_service.select_campaign(campaign_name)
            if not campaign:
                self._send_api_error(404, "Campaign not found")
                return
            
            # 获取怪物卡文件列表
            files = file_manager_service.list_files("monsters")
            
            # 转换为 API 响应格式
            monsters = []
            for file_info in files:
                if not file_info.is_directory:
                    monsters.append({
                        "name": file_info.get_display_name(),
                        "filename": file_info.name,
                        "file_type": file_info.file_type,
                        "is_hidden": file_info.is_hidden
                    })
            
            self._send_api_response({"monsters": monsters})
            
        except Exception as e:
            self._send_api_error(500, f"获取怪物卡列表失败: {str(e)}")
    
    def _handle_monster_detail(self, params, campaign_service, file_manager_service):
        """处理怪物卡详情请求"""
        campaign_name = params.get('campaign')
        monster_name = params.get('name')
        
        if not campaign_name or not monster_name:
            self._send_api_error(400, "Missing campaign or name parameter")
            return
        
        try:
            # 选择跑团
            campaign = campaign_service.select_campaign(campaign_name)
            if not campaign:
                self._send_api_error(404, "Campaign not found")
                return
            
            # 读取怪物卡内容
            content = file_manager_service.read_file_content("monsters", monster_name)
            if content is None:
                self._send_api_error(404, "Monster not found")
                return
            
            # 解析怪物卡内容
            monster_data = self._parse_monster_content(content, monster_name)
            self._send_api_response(monster_data)
            
        except Exception as e:
            self._send_api_error(500, f"获取怪物卡失败: {str(e)}")
    
    def _handle_map_list(self, params, campaign_service, file_manager_service):
        """处理地图列表请求"""
        campaign_name = params.get('campaign')
        if not campaign_name:
            self._send_api_error(400, "Missing campaign parameter")
            return
        
        try:
            # 选择跑团
            campaign = campaign_service.select_campaign(campaign_name)
            if not campaign:
                self._send_api_error(404, "Campaign not found")
                return
            
            # 获取地图文件列表
            files = file_manager_service.list_files("maps")
            
            # 转换为 API 响应格式
            maps = []
            for file_info in files:
                if not file_info.is_directory:
                    maps.append({
                        "name": file_info.get_display_name(),
                        "filename": file_info.name,
                        "file_type": file_info.file_type,
                        "is_hidden": file_info.is_hidden
                    })
            
            self._send_api_response({"maps": maps})
            
        except Exception as e:
            self._send_api_error(500, f"获取地图列表失败: {str(e)}")
    
    def _handle_map_detail(self, params, campaign_service, file_manager_service):
        """处理地图详情请求"""
        campaign_name = params.get('campaign')
        map_name = params.get('name')
        
        if not campaign_name or not map_name:
            self._send_api_error(400, "Missing campaign or name parameter")
            return
        
        try:
            # 选择跑团
            campaign = campaign_service.select_campaign(campaign_name)
            if not campaign:
                self._send_api_error(404, "Campaign not found")
                return
            
            # 读取地图内容
            content = file_manager_service.read_file_content("maps", map_name)
            if content is None:
                self._send_api_error(404, "Map not found")
                return
            
            # 获取文件信息
            files = file_manager_service.list_files("maps")
            file_info = next((f for f in files if f.get_display_name() == map_name), None)
            
            if file_info and file_info.file_type == "image":
                # 对于图片文件，返回文件路径信息
                map_data = {
                    "name": map_name,
                    "type": "image",
                    "file_type": file_info.file_type,
                    "filename": file_info.name,
                    "content": None  # 图片内容通过单独的接口获取
                }
            else:
                # 对于文本文件，返回内容
                map_data = {
                    "name": map_name,
                    "type": "text",
                    "file_type": file_info.file_type if file_info else "text",
                    "filename": file_info.name if file_info else map_name,
                    "content": content
                }
            
            self._send_api_response(map_data)
            
        except Exception as e:
            self._send_api_error(500, f"获取地图失败: {str(e)}")
    
    def _parse_character_content(self, content: str, name: str):
        """解析人物卡内容"""
        character_data = {
            "name": name,
            "type": "character",
            "raw_content": content,
            "fields": {}
        }
        
        # 解析键值对格式的内容
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                character_data["fields"][key.strip()] = value.strip()
        
        return character_data
    
    def _parse_monster_content(self, content: str, name: str):
        """解析怪物卡内容"""
        monster_data = {
            "name": name,
            "type": "monster",
            "raw_content": content,
            "fields": {}
        }
        
        # 解析键值对格式的内容
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                monster_data["fields"][key.strip()] = value.strip()
        
        return monster_data


class WebPreviewServer:
    """Web 预览服务器管理器"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化服务器
        
        Args:
            base_dir: 服务器根目录，默认为项目根目录
        """
        if base_dir is None:
            # 默认使用项目根目录
            base_dir = Path(__file__).parent.parent.parent.parent
        
        self.base_dir = base_dir
        self.port = self._find_free_port()
        self.httpd: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        self.last_access_time = 0
        self.on_server_stop: Optional[Callable] = None
        
        log_debug(f"WebPreviewServer初始化: base_dir={base_dir}, port={self.port}")
    
    def _find_free_port(self) -> int:
        """找到一个可用的端口"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def start(self, auto_monitor: bool = True) -> bool:
        """
        启动服务器
        
        Args:
            auto_monitor: 是否自动监控浏览器活动（已禁用，保留参数兼容性）
            
        Returns:
            bool: 启动是否成功
        """
        log_debug("=== 开始启动Web预览服务器 ===")
        
        if self.running:
            log_debug(f"服务器已在端口 {self.port} 运行")
            return True
        
        try:
            log_debug(f"正在启动Web预览服务器，端口: {self.port}")
            
            # 切换到服务器根目录并保持
            original_cwd = os.getcwd()
            log_debug(f"切换工作目录: {original_cwd} -> {self.base_dir}")
            os.chdir(self.base_dir)
            
            # 创建 HTTP 服务器
            log_debug(f"创建HTTP服务器...")
            self.httpd = HTTPServer(('localhost', self.port), WebPreviewRequestHandler)
            self.httpd._preview_server = self  # 让处理器能访问到服务器实例
            self.running = True
            self.last_access_time = time.time()
            
            # 在后台线程中启动服务器
            log_debug(f"启动服务器线程...")
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            # 等待服务器启动
            time.sleep(0.5)
            
            # 验证服务器是否真的启动了
            if not self.server_thread.is_alive():
                raise Exception("服务器线程启动失败")
            
            log_debug(f"服务器启动成功，访问地址: http://localhost:{self.port}")
            
            # 不再启动任何自动监控
            log_debug("服务器启动完成，无自动监控")
            
            return True
            
        except Exception as e:
            log_debug(f"启动服务器失败: {e}")
            import traceback
            log_debug(f"错误堆栈: {traceback.format_exc()}")
            self.running = False
            # 如果启动失败，恢复原始目录
            try:
                os.chdir(original_cwd)
            except:
                pass
            return False
    
    def _run_server(self):
        """在后台运行服务器"""
        try:
            log_debug(f"服务器开始监听端口 {self.port}")
            self.httpd.serve_forever()
        except Exception as e:
            log_debug(f"服务器运行异常: {e}")
            import traceback
            log_debug(f"错误堆栈: {traceback.format_exc()}")
            self.running = False
        finally:
            log_debug("服务器线程结束")
    
    def stop(self):
        """停止服务器"""
        if self.running:
            log_debug(f"正在停止服务器...")
            self.running = False
            
            if self.httpd:
                try:
                    self.httpd.shutdown()
                    self.httpd.server_close()
                    log_debug(f"HTTP服务器已关闭")
                except Exception as e:
                    log_debug(f"关闭HTTP服务器时出错: {e}")
            
            # 等待服务器线程结束
            if hasattr(self, 'server_thread') and self.server_thread.is_alive():
                try:
                    self.server_thread.join(timeout=2)
                    if self.server_thread.is_alive():
                        log_debug(f"服务器线程未能在2秒内结束")
                    else:
                        log_debug(f"服务器线程已结束")
                except Exception as e:
                    log_debug(f"等待服务器线程结束时出错: {e}")
            
            if self.on_server_stop:
                self.on_server_stop()
            
            log_debug(f"服务器已停止")
    
    def get_url(self, path: str = "", params: dict = None) -> str:
        """
        获取服务器 URL
        
        Args:
            path: 路径
            params: URL 参数
            
        Returns:
            str: 完整的 URL
        """
        url = f"http://localhost:{self.port}"
        if path:
            if not path.startswith('/'):
                path = '/' + path
            url += path
        
        if params:
            url += '?' + urlencode(params)
        
        return url
    
    def open_story_editor(self, campaign_name: str, story_name: str = None) -> bool:
        """
        打开剧情编辑器页面
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称（可选，用于编辑现有剧情）
            
        Returns:
            bool: 是否成功打开
        """
        log_debug(f"=== 打开Web编辑器 ===")
        log_debug(f"跑团: {campaign_name}, 剧情: {story_name}")
        
        # 确保服务器正在运行
        if not self.running:
            log_debug("服务器未运行，正在启动...")
            if not self.start():
                log_debug("服务器启动失败")
                return False
        else:
            # 检查服务器是否真的在运行
            log_debug("检查服务器连接...")
            if not self._test_server_connection():
                log_debug("服务器连接测试失败，尝试重启...")
                self.stop()
                if not self.start():
                    log_debug("服务器重启失败")
                    return False
            else:
                log_debug("服务器连接正常")
        
        # 构建 URL 参数
        params = {
            'campaign': campaign_name
        }
        if story_name:
            params['story'] = story_name
        
        # 获取编辑器页面 URL
        url = self.get_url("tools/editor/editor.html", params)
        log_debug(f"打开Web编辑器URL: {url}")
        
        try:
            webbrowser.open(url)
            log_debug("浏览器打开成功")
            return True
        except Exception as e:
            log_debug(f"打开浏览器失败: {e}")
            return False
    
    def _test_server_connection(self) -> bool:
        """测试服务器连接是否正常"""
        try:
            log_debug("开始测试服务器连接...")
            import urllib.request
            import urllib.error
            
            test_url = self.get_url("api/campaigns")
            log_debug(f"测试URL: {test_url}")
            request = urllib.request.Request(test_url)
            
            # 优化：减少超时时间到3秒，提高响应速度
            with urllib.request.urlopen(request, timeout=3) as response:
                result = response.status == 200
                log_debug(f"连接测试结果: {result} (状态码: {response.status})")
                return result
                
        except Exception as e:
            log_debug(f"服务器连接测试失败: {e}")
            return False
    
    def open_preview(self, campaign_name: str, story_name: str, script_name: Optional[str] = None) -> bool:
        """
        打开剧情预览页面
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称
            script_name: 剧本名称（可选）
            
        Returns:
            bool: 是否成功打开
        """
        if not self.running:
            if not self.start():
                return False
        
        # 构建 URL 参数
        params = {
            'campaign': campaign_name,
            'story': story_name
        }
        if script_name:
            params['script'] = script_name
        
        # 获取预览页面 URL
        url = self.get_url("tools/preview/preview.html", params)
        
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"打开浏览器失败: {e}")
            return False
    
    def open_character_viewer(self, campaign_name: str = None) -> bool:
        """
        打开角色卡查看器页面
        
        Args:
            campaign_name: 跑团名称（可选，用于预选跑团）
            
        Returns:
            bool: 是否成功打开
        """
        if not self.running:
            if not self.start():
                return False
        
        # 构建 URL 参数
        params = {}
        if campaign_name:
            params['campaign'] = campaign_name
        
        # 获取角色卡查看器页面 URL
        url = self.get_url("tools/characters/characters.html", params)
        
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"打开浏览器失败: {e}")
            return False
    
    def is_running(self) -> bool:
        """检查服务器是否正在运行"""
        return self.running
    
    def get_port(self) -> int:
        """获取服务器端口"""
        return self.port
