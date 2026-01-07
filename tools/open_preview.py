#!/usr/bin/env python3
"""
打开剧情预览的工具
"""

import sys
import os
import webbrowser
from pathlib import Path
from urllib.parse import urlencode


def open_preview(campaign_name=None, script_name=None, story_name=None):
    """打开剧情预览页面"""
    
    # 获取preview.html的路径
    tools_dir = Path(__file__).parent
    preview_html = tools_dir / "preview" / "preview.html"
    
    if not preview_html.exists():
        print(f"错误：找不到预览文件 {preview_html}")
        return False
    
    # 构建URL
    file_url = f"file:///{preview_html.as_posix()}"
    
    # 如果指定了参数，添加URL参数
    if campaign_name and story_name:
        params = {
            'campaign': campaign_name,
            'story': story_name
        }
        if script_name:
            params['script'] = script_name
        
        file_url += '?' + urlencode(params)
    
    print(f"打开预览页面：{file_url}")
    
    try:
        webbrowser.open(file_url)
        return True
    except Exception as e:
        print(f"打开浏览器失败：{e}")
        return False


def list_available_stories():
    """列出可用的剧情文件"""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output"
    
    if not output_dir.exists():
        print("output目录不存在")
        return []
    
    stories = []
    for campaign_dir in output_dir.iterdir():
        if campaign_dir.is_dir() and campaign_dir.name != "__pycache__":
            for script_dir in campaign_dir.iterdir():
                if script_dir.is_dir():
                    # 新结构：output/跑团/剧本/文件.json
                    for json_file in script_dir.glob("*.json"):
                        story_name = json_file.stem
                        stories.append((campaign_dir.name, script_dir.name, story_name))
                else:
                    # 兼容旧结构：output/跑团/文件.json
                    for json_file in campaign_dir.glob("*.json"):
                        story_name = json_file.stem
                        stories.append((campaign_dir.name, None, story_name))
    
    return stories


def find_story_files(campaign_name, script_name, story_name):
    """查找剧情文件路径"""
    base_dir = Path(__file__).parent.parent
    
    if script_name:
        # 新结构：output/跑团/剧本/文件
        story_dir = base_dir / "output" / campaign_name / script_name
        json_path = story_dir / f"{story_name}.json"
        svg_path = story_dir / f"{story_name}.svg"
    else:
        # 旧结构：output/跑团/文件
        story_dir = base_dir / "output" / campaign_name
        json_path = story_dir / f"{story_name}.json"
        svg_path = story_dir / f"{story_name}.svg"
    
    return json_path, svg_path


def main():
    if len(sys.argv) == 1:
        # 无参数：列出可用剧情并打开默认预览
        stories = list_available_stories()
        
        if not stories:
            print("未找到任何剧情文件")
            print("请先使用剧情编辑器创建剧情，或运行 generate_preview.py 生成预览文件")
            return
        
        print("可用的剧情文件：")
        for i, (campaign, script, story) in enumerate(stories, 1):
            if script:
                print(f"  {i}. {campaign}/{script}/{story}")
            else:
                print(f"  {i}. {campaign}/{story}")
        
        # 打开第一个剧情的预览
        campaign, script, story = stories[0]
        if script:
            print(f"\n打开默认预览：{campaign}/{script}/{story}")
        else:
            print(f"\n打开默认预览：{campaign}/{story}")
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
        print("  python open_preview.py                        # 列出可用剧情并打开默认预览")
        print("  python open_preview.py 跑团名 剧情名          # 打开指定剧情的预览（旧格式）")
        print("  python open_preview.py 跑团名 剧本名 剧情名   # 打开指定剧情的预览（新格式）")
        sys.exit(1)


if __name__ == "__main__":
    main()