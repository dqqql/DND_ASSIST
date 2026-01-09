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
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlencode, urlparse
from typing import Optional, Callable

from .editor_api import EditorAPIHandler

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


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
    
    def do_OPTIONS(self):
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _handle_api_request(self):
        """处理 API 请求"""
        # 获取服务实例
        campaign_service, editor_service, file_manager_service = EditorAPIHandler.get_services()
        
        # 解析 URL
        url_parts = urlparse(self.path)
        path = url_parts.path
        
        # 更安全的参数解析
        params = {}
        if url_parts.query:
            try:
                import urllib.parse
                params = urllib.parse.parse_qs(url_parts.query)
                # 将列表值转换为单个值
                params = {k: v[0] if v else '' for k, v in params.items()}
            except Exception as e:
                print(f"[ERROR] 参数解析失败: {e}")
                params = {}
        
        try:
            if self.command == 'GET':
                self._handle_api_get(path, params, campaign_service, editor_service, file_manager_service)
            elif self.command == 'POST':
                self._handle_api_post(path, campaign_service, editor_service)
            elif self.command == 'OPTIONS':
                self._handle_api_options()
            else:
                self._send_api_error(405, "Method not allowed")
        except Exception as e:
            print(f"[ERROR] API处理异常: {e}")
            self._send_api_error(500, f"Internal server error: {str(e)}")
    
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
    
    def _handle_api_post(self, path, campaign_service, editor_service):
        """处理 POST API 请求"""
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_api_error(400, "Invalid JSON data")
            return
        
        if path == '/api/story/save':
            campaign_name = request_data.get('campaign')
            story_name = request_data.get('story')
            story_data = request_data.get('data')
            
            if not campaign_name or not story_name or not story_data:
                self._send_api_error(400, "Missing required parameters")
                return
            
            success, message = editor_service.save_story(campaign_name, story_name, story_data)
            
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
        else:
            self._send_api_error(404, "API endpoint not found")
    
    def _handle_api_options(self):
        """处理 OPTIONS API 请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_api_response(self, data, status_code=200):
        """发送 API 响应"""
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
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
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False
        self.last_access_time = 0
        self.on_server_stop: Optional[Callable] = None
    
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
            auto_monitor: 是否自动监控浏览器活动
            
        Returns:
            bool: 启动是否成功
        """
        if self.running:
            return True
        
        try:
            # 切换到服务器根目录
            original_cwd = os.getcwd()
            os.chdir(self.base_dir)
            
            # 创建 HTTP 服务器
            self.httpd = HTTPServer(('localhost', self.port), WebPreviewRequestHandler)
            self.httpd._preview_server = self  # 让处理器能访问到服务器实例
            self.running = True
            self.last_access_time = time.time()
            
            # 在后台线程中启动服务器
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            # 等待服务器启动
            time.sleep(0.5)
            
            # 启动监控（如果需要）
            if auto_monitor:
                self.start_monitoring()
            
            # 恢复原始工作目录
            os.chdir(original_cwd)
            
            return True
            
        except Exception as e:
            print(f"启动服务器失败: {e}")
            self.running = False
            return False
    
    def _run_server(self):
        """在后台运行服务器"""
        try:
            self.httpd.serve_forever()
        except Exception:
            pass  # 服务器被关闭时会抛出异常，这是正常的
    
    def stop(self):
        """停止服务器"""
        if self.httpd and self.running:
            self.running = False
            self.httpd.shutdown()
            self.httpd.server_close()
            
            if self.on_server_stop:
                self.on_server_stop()
    
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
        if not self.running:
            if not self.start():
                return False
        
        # 构建 URL 参数
        params = {
            'campaign': campaign_name
        }
        if story_name:
            params['story'] = story_name
        
        # 获取编辑器页面 URL
        url = self.get_url("tools/editor/editor.html", params)
        
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"打开浏览器失败: {e}")
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
    
    def start_monitoring(self, check_interval: int = 3, idle_threshold: int = 15):
        """
        开始监控浏览器活动
        
        Args:
            check_interval: 检查间隔（秒）
            idle_threshold: 空闲阈值（秒）
        """
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_browser_activity,
            args=(check_interval, idle_threshold),
            daemon=True
        )
        self.monitor_thread.start()
    
    def _monitor_browser_activity(self, check_interval: int, idle_threshold: int):
        """监控浏览器活动，如果长时间无访问则关闭服务器"""
        while self.running:
            time.sleep(check_interval)
            
            # 检查是否有浏览器进程在运行（如果有psutil）
            browser_running = True
            if HAS_PSUTIL:
                browser_running = self._check_browser_processes()
            
            # 如果没有浏览器进程，或者超过阈值时间没有访问
            idle_time = time.time() - self.last_access_time
            
            if not browser_running:
                self.stop()
                break
            elif idle_time > idle_threshold:
                self.stop()
                break
    
    def _check_browser_processes(self) -> bool:
        """检查是否有浏览器进程在运行"""
        if not HAS_PSUTIL:
            return True
        
        browser_names = [
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 
            'safari.exe', 'brave.exe', 'vivaldi.exe',
            'chrome', 'firefox', 'safari', 'opera', 'brave', 'vivaldi'
        ]
        
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and any(browser in proc.info['name'].lower() for browser in browser_names):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
        return False
    
    def is_running(self) -> bool:
        """检查服务器是否正在运行"""
        return self.running
    
    def get_port(self) -> int:
        """获取服务器端口"""
        return self.port