#!/usr/bin/env python3
"""
打开剧情预览的工具
"""

import sys
import os
import webbrowser
import threading
import time
import socket
from pathlib import Path
from urllib.parse import urlencode
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 尝试导入psutil，如果不可用则使用基础监控
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def find_free_port():
    """找到一个可用的端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


class ServerManager:
    """服务器管理器，支持自动关闭功能"""
    
    def __init__(self, port, base_dir):
        self.port = port
        self.base_dir = base_dir
        self.httpd = None
        self.server_thread = None
        self.monitor_thread = None
        self.running = False
    
    def start_server(self):
        """启动HTTP服务器"""
        os.chdir(self.base_dir)
        
        class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                # 静默处理请求日志
                pass
        
        self.httpd = HTTPServer(('localhost', self.port), QuietHTTPRequestHandler)
        self.running = True
        
        try:
            self.httpd.serve_forever()
        except Exception:
            pass  # 服务器被关闭时会抛出异常，这是正常的
    
    def start(self):
        """在后台启动服务器"""
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()
        time.sleep(1)  # 等待服务器启动
    
    def stop(self):
        """停止服务器"""
        if self.httpd and self.running:
            self.running = False
            self.httpd.shutdown()
            self.httpd.server_close()
            print("🛑 服务器已停止")
    
    def monitor_browser_activity(self, check_interval=3):
        """监控浏览器活动，如果长时间无访问则关闭服务器"""
        
        # 重写请求处理器以记录访问时间
        original_handler = self.httpd.RequestHandlerClass
        server_manager = self
        
        class MonitoringHandler(original_handler):
            def do_GET(self):
                server_manager.last_access_time = time.time()
                return super().do_GET()
            
            def do_POST(self):
                server_manager.last_access_time = time.time()
                return super().do_POST()
        
        if self.httpd:
            self.httpd.RequestHandlerClass = MonitoringHandler
        
        self.last_access_time = time.time()
        idle_threshold = 15  # 15秒无活动则认为浏览器已关闭
        
        if HAS_PSUTIL:
            print(f"🔍 开始智能监控浏览器活动（{idle_threshold}秒无活动将自动关闭）")
        else:
            print(f"🔍 开始基础监控浏览器活动（{idle_threshold}秒无活动将自动关闭）")
        
        while self.running:
            time.sleep(check_interval)
            
            # 检查是否有浏览器进程在运行（如果有psutil）
            browser_running = True
            if HAS_PSUTIL:
                browser_running = self._check_browser_processes()
            
            # 如果没有浏览器进程，或者超过阈值时间没有访问
            idle_time = time.time() - self.last_access_time
            
            if not browser_running:
                print("🔍 检测到浏览器进程已关闭，自动停止服务器...")
                self.stop()
                break
            elif idle_time > idle_threshold:
                print(f"⏰ 检测到浏览器已无活动（{idle_time:.1f}秒），自动停止服务器...")
                self.stop()
                break
    
    def _check_browser_processes(self):
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
    
    def start_monitoring(self):
        """开始监控浏览器活动"""
        self.monitor_thread = threading.Thread(target=self.monitor_browser_activity, daemon=True)
        self.monitor_thread.start()


def select_story_interactive():
    """交互式选择剧情"""
    stories = list_available_stories()
    
    if not stories:
        print("未找到任何剧情文件")
        print("请先使用剧情编辑器创建剧情，或运行 generate_preview.py 生成预览文件")
        return None
    
    print("\n=== 剧情预览选择器 ===")
    for i, (campaign, script, story) in enumerate(stories, 1):
        if script:
            print(f"  {i}. {campaign}/{script}/{story}")
        else:
            print(f"  {i}. {campaign}/{story}")
    
    print(f"\n共找到 {len(stories)} 个剧情文件")
    
    while True:
        try:
            choice = input(f"请选择要预览的剧情 (1-{len(stories)})，或按回车选择第一个: ").strip()
            
            if not choice:  # 按回车选择第一个
                print("已选择第一个剧情")
                return stories[0]
            
            index = int(choice) - 1
            if 0 <= index < len(stories):
                campaign, script, story = stories[index]
                if script:
                    print(f"已选择：{campaign}/{script}/{story}")
                else:
                    print(f"已选择：{campaign}/{story}")
                return stories[index]
            else:
                print(f"❌ 请输入 1 到 {len(stories)} 之间的数字")
        
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n已取消预览")
            return None


def open_preview(campaign_name=None, script_name=None, story_name=None):
    """打开剧情预览页面"""
    
    # 获取项目根目录
    base_dir = Path(__file__).parent.parent
    preview_html = base_dir / "tools" / "preview" / "preview.html"
    
    if not preview_html.exists():
        print(f"错误：找不到预览文件 {preview_html}")
        return False
    
    # 找到可用端口
    port = find_free_port()
    
    # 创建服务器管理器
    server_manager = ServerManager(port, base_dir)
    
    # 启动服务器
    server_manager.start()
    
    # 构建URL
    url = f"http://localhost:{port}/tools/preview/preview.html"
    
    # 如果指定了参数，添加URL参数
    if campaign_name and story_name:
        params = {
            'campaign': campaign_name,
            'story': story_name
        }
        if script_name:
            params['script'] = script_name
        
        url += '?' + urlencode(params)
    
    print(f"🚀 启动本地服务器：http://localhost:{port}")
    print(f"✅ 打开预览页面：{url}")
    
    try:
        webbrowser.open(url)
        
        # 开始监控浏览器活动
        server_manager.start_monitoring()
        
        print("💡 提示：关闭浏览器标签页后服务器将自动停止")
        print("⌨️  或者按 Ctrl+C 手动停止服务器")
        print("🌐 服务器运行中，等待浏览器访问...")
        
        try:
            # 保持主线程运行，直到服务器停止
            while server_manager.running:
                time.sleep(1)
            print("✅ 预览会话已结束")
        except KeyboardInterrupt:
            print("\n⏹️  手动停止服务器")
            server_manager.stop()
        
        return True
    except Exception as e:
        print(f"❌ 打开浏览器失败：{e}")
        server_manager.stop()
        return False


def list_available_stories():
    """列出可用的剧情文件"""
    base_dir = Path(__file__).parent.parent
    campaigns_dir = base_dir / "data" / "campaigns"
    
    if not campaigns_dir.exists():
        print("data/campaigns目录不存在")
        return []
    
    stories = []
    for campaign_dir in campaigns_dir.iterdir():
        if campaign_dir.is_dir():
            notes_dir = campaign_dir / "notes"
            if notes_dir.exists():
                for json_file in notes_dir.glob("*.json"):
                    story_name = json_file.stem
                    stories.append((campaign_dir.name, None, story_name))
    
    return stories


def find_story_files(campaign_name, script_name, story_name):
    """查找剧情文件路径"""
    base_dir = Path(__file__).parent.parent
    
    # 新的文件结构：data/campaigns/跑团/notes/文件
    story_dir = base_dir / "data" / "campaigns" / campaign_name / "notes"
    json_path = story_dir / f"{story_name}.json"
    svg_path = story_dir / f"{story_name}.svg"
    
    return json_path, svg_path


def main():
    if len(sys.argv) == 1:
        # 无参数：交互式选择剧情
        selected = select_story_interactive()
        if not selected:
            return
        
        campaign, script, story = selected
        
        # 检查文件是否存在
        json_path, svg_path = find_story_files(campaign, script, story)
        
        if not json_path.exists():
            print(f"错误：找不到剧情文件 {json_path}")
            return
        
        if not svg_path.exists():
            print(f"警告：找不到SVG文件 {svg_path}")
            print("请先运行 generate_preview.py 生成预览文件")
            return
        
        if script:
            print(f"\n即将打开预览：{campaign}/{script}/{story}")
        else:
            print(f"\n即将打开预览：{campaign}/{story}")
        
        open_preview(campaign, script, story)
        
    elif len(sys.argv) == 3:
        # 兼容旧格式：跑团名 剧情名
        campaign_name = sys.argv[1]
        story_name = sys.argv[2]
        
        # 检查文件是否存在（先检查新结构，再检查旧结构）
        json_path, svg_path = find_story_files(campaign_name, None, story_name)
        
        if not json_path.exists():
            print(f"错误：找不到剧情文件 {json_path}")
            return
        
        if not svg_path.exists():
            print(f"警告：找不到SVG文件 {svg_path}")
            print("请先运行工具生成预览文件")
            return
        
        open_preview(campaign_name, None, story_name)
        
    elif len(sys.argv) == 4:
        # 新格式：跑团名 剧本名 剧情名
        campaign_name = sys.argv[1]
        script_name = sys.argv[2]
        story_name = sys.argv[3]
        
        # 检查文件是否存在
        json_path, svg_path = find_story_files(campaign_name, script_name, story_name)
        
        if not json_path.exists():
            print(f"错误：找不到剧情文件 {json_path}")
            return
        
        if not svg_path.exists():
            print(f"警告：找不到SVG文件 {svg_path}")
            print("请先运行工具生成预览文件")
            return
        
        open_preview(campaign_name, script_name, story_name)
        
    else:
        print("用法：")
        print("  python open_preview.py                        # 交互式选择剧情预览")
        print("  python open_preview.py 跑团名 剧情名          # 打开指定剧情的预览（旧格式）")
        print("  python open_preview.py 跑团名 剧本名 剧情名   # 打开指定剧情的预览（新格式）")
        print("\n功能特性：")
        print("  🎯 交互式剧情选择")
        print("  🚀 自动启动本地HTTP服务器")
        print("  🔍 智能监控浏览器活动")
        print("  ⏰ 浏览器关闭后自动停止服务器")
        sys.exit(1)


if __name__ == "__main__":
    main()