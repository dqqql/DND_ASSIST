#!/usr/bin/env python3
"""
独立的Web预览系统
提供剧情预览的独立启动功能
"""

import sys
import os
import webbrowser
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.web_preview.server import WebPreviewServer
from src.ui.web_preview.preview_generator import PreviewGenerator


def select_story_interactive():
    """交互式选择剧情"""
    generator = PreviewGenerator()
    stories = generator.list_available_stories()
    
    if not stories:
        print("❌ 没有找到可用的剧情文件")
        print("请确保在 data/campaigns/跑团名/notes/ 目录下有 .json 剧情文件")
        return None
    
    print("\n📚 可用的剧情文件:")
    for i, (campaign, story) in enumerate(stories, 1):
        print(f"  {i}. {campaign} - {story}")
    
    try:
        choice = input(f"\n请选择剧情 (1-{len(stories)}) 或按回车键启动主界面: ").strip()
        
        if not choice:
            return None  # 启动主界面
        
        index = int(choice) - 1
        if 0 <= index < len(stories):
            return stories[index]
        else:
            print("❌ 无效的选择")
            return None
            
    except (ValueError, KeyboardInterrupt):
        print("\n❌ 操作取消")
        return None


def start_preview_server(campaign=None, story=None):
    """启动预览服务器"""
    print("🚀 正在启动预览服务器...")
    
    # 创建服务器实例
    server = WebPreviewServer(project_root)
    
    # 启动服务器
    success = server.start()
    
    if not success:
        print("❌ 服务器启动失败")
        return None
    
    print(f"✅ 服务器已启动: {server.get_url()}")
    
    # 构建预览URL
    if campaign and story:
        # 直接预览指定剧情
        preview_url = server.get_url(f"tools/preview/preview.html?campaign={campaign}&story={story}")
        print(f"🎭 剧情预览: {preview_url}")
    else:
        # 打开主界面
        preview_url = server.get_url("tools/web_ui/index.html")
        print(f"🌐 主界面: {preview_url}")
    
    # 自动打开浏览器
    try:
        webbrowser.open(preview_url)
        print("✅ 已在浏览器中打开预览")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print(f"请手动访问: {preview_url}")
    
    return server


def wait_for_server(server):
    """等待服务器运行"""
    print("\n💡 使用提示:")
    print("   • 服务器将持续运行直到手动停止")
    print("   • 按 Ctrl+C 停止服务器")
    print("   • 可以在浏览器中查看和编辑剧情")
    
    try:
        # 保持服务器运行
        while server.is_running():
            time.sleep(1)
        
        print("\n✅ 服务器已停止")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  正在停止服务器...")
        server.stop()
        print("✅ 服务器已停止")


def main():
    """主函数"""
    print("🎲 DND 剧情预览工具")
    print("=" * 40)
    
    # 交互式选择剧情
    selection = select_story_interactive()
    
    if selection:
        campaign, story = selection
        print(f"\n🎯 准备预览: {campaign} - {story}")
        server = start_preview_server(campaign, story)
    else:
        print("\n🌐 启动主界面...")
        server = start_preview_server()
    
    if server:
        wait_for_server(server)
    else:
        print("❌ 启动失败")
        sys.exit(1)


if __name__ == "__main__":
    main()