"""
Web 预览服务器
提供本地 HTTP 服务，支持剧情可视化预览
"""

import os
import socket
import threading
import time
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlencode
from typing import Optional, Callable

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


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
            
            # 创建静默的请求处理器
            class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
                def log_message(self, format, *args):
                    # 静默处理请求日志
                    pass
                
                def do_GET(self):
                    # 记录访问时间
                    if hasattr(self.server, '_preview_server'):
                        self.server._preview_server.last_access_time = time.time()
                    return super().do_GET()
                
                def do_POST(self):
                    # 记录访问时间
                    if hasattr(self.server, '_preview_server'):
                        self.server._preview_server.last_access_time = time.time()
                    return super().do_POST()
            
            # 创建 HTTP 服务器
            self.httpd = HTTPServer(('localhost', self.port), QuietHTTPRequestHandler)
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