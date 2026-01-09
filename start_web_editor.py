#!/usr/bin/env python3
"""
Web 编辑器独立启动器
用于测试和独立使用 Web 编辑器
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.web_preview import WebPreviewManager
from src.core import CampaignService


def list_available_campaigns():
    """列出可用的跑团"""
    campaign_service = CampaignService()
    return campaign_service.list_campaigns()


def select_campaign_interactive():
    """交互式选择跑团"""
    campaigns = list_available_campaigns()
    
    if not campaigns:
        print("未找到任何跑团")
        print("请先使用主程序创建跑团")
        return None
    
    print("\n=== Web 剧情编辑器启动器 ===")
    for i, campaign in enumerate(campaigns, 1):
        print(f"  {i}. {campaign}")
    
    print(f"\n共找到 {len(campaigns)} 个跑团")
    
    while True:
        try:
            choice = input(f"请选择跑团 (1-{len(campaigns)})，或按回车选择第一个: ").strip()
            
            if not choice:  # 按回车选择第一个
                print("已选择第一个跑团")
                return campaigns[0]
            
            index = int(choice) - 1
            if 0 <= index < len(campaigns):
                campaign = campaigns[index]
                print(f"已选择：{campaign}")
                return campaign
            else:
                print(f"❌ 请输入 1 到 {len(campaigns)} 之间的数字")
        
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n已取消启动")
            return None


def open_web_editor(campaign_name: str, story_name: str = None):
    """打开 Web 编辑器"""
    print(f"🎯 准备打开 Web 编辑器：{campaign_name}")
    if story_name:
        print(f"   剧情：{story_name}")
    
    # 启动 Web 编辑器
    manager = WebPreviewManager()
    success = manager.open_story_editor(campaign_name, story_name)
    
    if success:
        print(f"🚀 Web 编辑器已在浏览器中打开")
        print(f"🌐 服务器地址：{manager.get_server_status()['url']}")
        print("💡 提示：关闭浏览器标签页后服务器将自动停止")
        print("⌨️  或者按 Ctrl+C 手动停止服务器")
        
        try:
            # 保持服务器运行
            while manager.is_server_running():
                import time
                time.sleep(1)
            print("✅ 编辑会话已结束")
        except KeyboardInterrupt:
            print("\n⏹️  手动停止服务器")
            manager.stop_server()
        
        return True
    else:
        print("❌ 无法打开 Web 编辑器")
        print("\n可能的原因：")
        print("• 无法启动本地服务器")
        print("• 无法打开浏览器")
        print("• 端口被占用")
        return False


def main():
    if len(sys.argv) == 1:
        # 无参数：交互式选择跑团
        selected_campaign = select_campaign_interactive()
        if not selected_campaign:
            return
        
        open_web_editor(selected_campaign)
        
    elif len(sys.argv) == 2:
        # 指定跑团
        campaign_name = sys.argv[1]
        open_web_editor(campaign_name)
        
    elif len(sys.argv) == 3:
        # 指定跑团和剧情
        campaign_name = sys.argv[1]
        story_name = sys.argv[2]
        open_web_editor(campaign_name, story_name)
        
    else:
        print("用法：")
        print("  python start_web_editor.py                    # 交互式选择跑团")
        print("  python start_web_editor.py 跑团名             # 打开指定跑团的编辑器")
        print("  python start_web_editor.py 跑团名 剧情名      # 打开指定剧情的编辑器")
        print("\n功能特性：")
        print("  🎯 现代化的 Web 编辑界面")
        print("  🔄 实时保存和验证")
        print("  🚀 自动启动本地HTTP服务器")
        print("  🔍 智能监控浏览器活动")
        print("  ⏰ 浏览器关闭后自动停止服务器")
        print("  📱 响应式设计，支持多种屏幕尺寸")
        sys.exit(1)


if __name__ == "__main__":
    main()