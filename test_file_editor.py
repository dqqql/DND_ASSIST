#!/usr/bin/env python3
"""
测试文件编辑器功能
"""

import sys
import os
import time
import webbrowser
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.web_preview.server import WebPreviewServer


def test_file_editor():
    """测试文件编辑器功能"""
    print("🧪 测试文件编辑器功能")
    print("="*50)
    
    # 启动服务器
    print("🚀 启动Web服务器...")
    server = WebPreviewServer(project_root)
    
    if not server.start(auto_monitor=False):
        print("❌ 服务器启动失败")
        return False
    
    try:
        print(f"✅ 服务器已启动，端口: {server.get_port()}")
        
        # 打开主界面
        main_url = server.get_url("tools/web_ui/index.html")
        print(f"🌐 主界面: {main_url}")
        
        # 打开文件编辑器测试页面
        editor_url = server.get_url("tools/web_ui/file_editor.html?campaign=test&category=characters&file=test.txt")
        print(f"📝 文件编辑器: {editor_url}")
        
        print("\n💡 测试步骤:")
        print("1. 在主界面创建一个跑团")
        print("2. 创建一些文件")
        print("3. 点击编辑按钮测试文件编辑器")
        print("4. 测试保存功能")
        
        # 自动打开浏览器
        try:
            webbrowser.open(main_url)
            print("✅ 浏览器已打开")
        except Exception as e:
            print(f"⚠️ 无法自动打开浏览器: {e}")
        
        print("\n按 Ctrl+C 停止服务器...")
        
        # 保持服务器运行
        while server.is_running():
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 正在停止服务器...")
        server.stop()
        print("✅ 服务器已停止")
        return True
    
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        server.stop()
        return False


if __name__ == "__main__":
    success = test_file_editor()
    sys.exit(0 if success else 1)