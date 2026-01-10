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
        print("  python tools/open_preview.py 跑团名 剧情名          # 打开指定预览")
    else:
        print("SVG文件生成失败")
    
    return success2


def main():
    if len(sys.argv) == 1:
        # 处理所有文件
        generate_all_previews()
    else:
        print("用法：")
        print("  python generate_preview.py                         # 处理所有剧情文件")
        print("\n注意：此工具会自动处理 data/campaigns/ 目录下的所有JSON剧情文件")
        sys.exit(1)


if __name__ == "__main__":
    main()