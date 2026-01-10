#!/usr/bin/env python3
"""
剧情预览工具 - 重构版
使用新的 Web 预览系统，支持独立运行和与主应用集成
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入新的 Web 预览系统
from tools.web_preview_standalone import main as standalone_main

# 为了向后兼容，保留原有的函数接口
def open_preview(campaign_name=None, script_name=None, story_name=None):
    """打开剧情预览页面（向后兼容接口）"""
    from src.ui.web_preview import WebPreviewManager
    
    if not campaign_name or not story_name:
        print("错误：缺少必要参数")
        return False
    
    manager = WebPreviewManager()
    return manager.open_story_preview(campaign_name, story_name, script_name)


def list_available_stories():
    """列出可用的剧情文件（向后兼容接口）"""
    from src.ui.web_preview.preview_generator import PreviewGenerator
    
    generator = PreviewGenerator()
    stories = generator.list_available_stories()
    
    # 转换为原有格式 (campaign, script, story)
    return [(campaign, None, story) for campaign, story in stories]


def find_story_files(campaign_name, script_name, story_name):
    """查找剧情文件路径（向后兼容接口）"""
    base_dir = Path(__file__).parent.parent
    
    # 新的文件结构：data/campaigns/跑团/notes/文件
    story_dir = base_dir / "data" / "campaigns" / campaign_name / "notes"
    json_path = story_dir / f"{story_name}.json"
    svg_path = story_dir / f"{story_name}.svg"
    
    return json_path, svg_path


def select_story_interactive():
    """交互式选择剧情（向后兼容接口）"""
    from tools.web_preview_standalone import select_story_interactive as new_select
    
    result = new_select()
    if result:
        campaign, story = result
        return (campaign, None, story)  # 转换为原有格式
    return None


def main():
    """主函数 - 使用新的独立预览系统"""
    # 直接调用新的独立预览系统
    standalone_main()


if __name__ == "__main__":
    main()