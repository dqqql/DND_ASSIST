#!/usr/bin/env python3
"""
剧情预览生成工具
自动化执行 JSON -> DOT -> SVG 的转换流程
"""

import sys
import os
import subprocess
from pathlib import Path


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False


def generate_all_previews():
    """生成所有剧情的预览文件"""
    print("=== 剧情预览生成工具 ===")
    
    # 步骤1：JSON -> DOT（自动跳过已存在的文件）
    success1 = run_command("echo s | python tools/json_to_dot.py", "步骤1：生成DOT文件")
    
    if not success1:
        print("DOT文件生成失败，停止处理")
        return False
    
    # 步骤2：DOT -> SVG（使用自动模式，跳过已存在的文件）
    success2 = run_command("python tools/dot_to_svg.py --auto", "步骤2：生成SVG文件")
    
    if success2:
        print("\n=== 处理完成 ===")
        print("所有预览文件已生成完成！")
        print("\n使用方法：")
        print("  python tools/open_preview.py                    # 查看所有可用剧情")
        print("  python tools/open_preview.py 跑团名 剧本名 剧情名  # 打开指定预览")
    else:
        print("SVG文件生成失败")
    
    return success2


def generate_specific_preview(campaign_name, script_name, story_name):
    """生成特定剧情的预览文件"""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output" / campaign_name / script_name
    
    json_path = output_dir / f"{story_name}.json"
    
    if not json_path.exists():
        print(f"错误：找不到文件 {json_path}")
        return False
    
    print(f"处理剧情：{campaign_name}/{script_name}/{story_name}")
    
    # 生成DOT文件
    dot_path = json_path.with_suffix('.dot')
    cmd1 = f"python tools/json_to_dot.py \"{json_path}\" \"{dot_path}\""
    success1 = run_command(cmd1, f"生成DOT文件: {story_name}.dot")
    
    if not success1:
        return False
    
    # 生成SVG文件
    svg_path = json_path.with_suffix('.svg')
    cmd2 = f"python tools/dot_to_svg.py \"{dot_path}\" \"{svg_path}\""
    success2 = run_command(cmd2, f"生成SVG文件: {story_name}.svg")
    
    return success2


def main():
    if len(sys.argv) == 1:
        # 处理所有文件
        generate_all_previews()
    elif len(sys.argv) == 4:
        # 处理特定文件：跑团名 剧本名 剧情名
        campaign_name = sys.argv[1]
        script_name = sys.argv[2]
        story_name = sys.argv[3]
        if story_name.endswith('.json'):
            story_name = story_name[:-5]  # 移除.json扩展名
        
        generate_specific_preview(campaign_name, script_name, story_name)
    else:
        print("用法：")
        print("  python generate_preview.py                         # 处理所有剧情文件")
        print("  python generate_preview.py 跑团名 剧本名 剧情名      # 处理特定剧情")
        sys.exit(1)


if __name__ == "__main__":
    main()