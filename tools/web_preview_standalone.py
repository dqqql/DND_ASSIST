#!/usr/bin/env python3
"""
独立的 Web 预览启动器
可以在不启动主应用的情况下直接打开剧情预览
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.web_preview import WebPreviewManager
from src.ui.web_preview.preview_generator import PreviewGenerator


def list_available_stories():
    """列出可用的剧情文件"""
    generator = PreviewGenerator()
    return generator.list_available_stories()


def select_story_interactive():
    """交互式选择剧情"""
    stories = list_available_stories()
    
    if not stories:
        print("未找到任何剧情文件")
        print("请先使用剧情编辑器创建剧情，或确保 data/campaigns/ 目录下有 JSON 剧情文件")
        return None
    
    print("\n=== Web 剧情预览选择器 ===")
    for i, (campaign, story) in enumerate(stories, 1):
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
                campaign, story = stories[index]
                print(f"已选择：{campaign}/{story}")
                return stories[index]
            else:
                print(f"❌ 请输入 1 到 {len(stories)} 之间的数字")
        
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n已取消预览")
            return None


def open_preview(campaign_name: str, story_name: str):
    """打开剧情预览"""
    print(f"🎯 准备打开预览：{campaign_name}/{story_name}")
    
    # 检查并生成预览文件
    generator = PreviewGenerator()
    dot_exists, svg_exists = generator.check_preview_files_exist(campaign_name, story_name)
    
    if not svg_exists:
        print("📄 预览文件不存在，正在生成...")
        success = generator.generate_preview_for_story(campaign_name, story_name)
        
        if not success:
            print("❌ 预览文件生成失败")
            print("\n可能的原因：")
            print("• JSON 文件格式错误")
            print("• 缺少 Graphviz 工具（需要安装 dot 命令）")
            print("• 文件权限问题")
            return False
        
        print("✅ 预览文件生成成功")
    
    # 启动 Web 预览
    manager = WebPreviewManager()
    success = manager.open_story_preview(campaign_name, story_name)
    
    if success:
        print(f"🚀 预览已在浏览器中打开")
        print(f"🌐 服务器地址：{manager.get_server_status()['url']}")
        print("💡 提示：关闭浏览器标签页后服务器将自动停止")
        print("⌨️  或者按 Ctrl+C 手动停止服务器")
        
        try:
            # 保持服务器运行
            while manager.is_server_running():
                import time
                time.sleep(1)
            print("✅ 预览会话已结束")
        except KeyboardInterrupt:
            print("\n⏹️  手动停止服务器")
            manager.stop_server()
        
        return True
    else:
        print("❌ 无法打开预览")
        print("\n可能的原因：")
        print("• 无法启动本地服务器")
        print("• 无法打开浏览器")
        print("• 预览文件损坏")
        return False


def main():
    if len(sys.argv) == 1:
        # 无参数：交互式选择剧情
        selected = select_story_interactive()
        if not selected:
            return
        
        campaign, story = selected
        open_preview(campaign, story)
        
    elif len(sys.argv) == 3:
        # 指定参数：跑团名 剧情名
        campaign_name = sys.argv[1]
        story_name = sys.argv[2]
        
        open_preview(campaign_name, story_name)
        
    else:
        print("用法：")
        print("  python web_preview_standalone.py                    # 交互式选择剧情预览")
        print("  python web_preview_standalone.py 跑团名 剧情名      # 打开指定剧情的预览")
        print("\n功能特性：")
        print("  🎯 独立运行，无需启动主应用")
        print("  🔄 自动生成缺失的预览文件")
        print("  🚀 自动启动本地HTTP服务器")
        print("  🔍 智能监控浏览器活动")
        print("  ⏰ 浏览器关闭后自动停止服务器")
        sys.exit(1)


if __name__ == "__main__":
    main()