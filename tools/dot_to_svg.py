import subprocess
import sys
import os
from pathlib import Path

def find_dot_executable():
    """查找dot可执行文件的路径"""
    # 常见的Graphviz安装路径
    possible_paths = [
        "dot",  # 如果在PATH中
        "C:\\Program Files\\Graphviz\\bin\\dot.exe",
        "C:\\Program Files (x86)\\Graphviz\\bin\\dot.exe",
        "C:\\Graphviz\\bin\\dot.exe",
        "/usr/bin/dot",  # Linux
        "/usr/local/bin/dot",  # macOS
        "/opt/homebrew/bin/dot",  # macOS with Homebrew
    ]
    
    for path in possible_paths:
        try:
            # 测试是否可以执行
            result = subprocess.run([path, "-V"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                return path
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return None

def convert_dot_to_svg(dot_path: Path, svg_path: Path):
    """将DOT文件转换为SVG"""
    dot_executable = find_dot_executable()
    
    if not dot_executable:
        print("[ERROR] 错误：未找到 Graphviz 的 dot 命令")
        print("请确保 Graphviz 已正确安装并添加到系统PATH中")
        print("下载地址：https://graphviz.org/download/")
        return False
    
    try:
        subprocess.run([
            dot_executable,
            "-Tsvg",
            str(dot_path),
            "-o",
            str(svg_path)
        ], check=True)
        
        print(f"[OK] SVG 已生成：{svg_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 转换失败：{e}")
        return False
    except Exception as e:
        print(f"[ERROR] 执行出错：{e}")
        return False


def find_dot_files():
    """查找output目录下的所有DOT文件"""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output"
    
    dot_files = []
    if output_dir.exists():
        for campaign_dir in output_dir.iterdir():
            if campaign_dir.is_dir():
                for script_dir in campaign_dir.iterdir():
                    if script_dir.is_dir():
                        # 新结构：output/跑团/剧本/文件.dot
                        for dot_file in script_dir.glob("*.dot"):
                            dot_files.append(dot_file)
                    elif campaign_dir.name != "__pycache__":
                        # 兼容旧结构：output/跑团/文件.dot
                        for dot_file in campaign_dir.glob("*.dot"):
                            dot_files.append(dot_file)
    
    return dot_files


def ask_user_confirmation(dot_files):
    """询问用户是否要转换文件"""
    print(f"\n找到 {len(dot_files)} 个DOT文件：")
    
    for i, dot_file in enumerate(dot_files, 1):
        # 解析路径结构
        parts = dot_file.parts
        if len(parts) >= 4 and parts[-4] == "output":
            # 新结构：output/跑团/剧本/文件.dot
            campaign = parts[-3]
            script = parts[-2]
            filename = parts[-1]
            print(f"  {i}. {campaign}/{script}/{filename}")
        elif len(parts) >= 3 and parts[-3] == "output":
            # 旧结构：output/跑团/文件.dot
            campaign = parts[-2]
            filename = parts[-1]
            print(f"  {i}. {campaign}/{filename}")
        else:
            print(f"  {i}. {dot_file}")
    
    print("\n选项：")
    print("  a) 转换所有文件")
    print("  s) 跳过已存在的SVG文件，只转换新文件")
    print("  n) 取消转换")
    
    while True:
        choice = input("\n请选择 (a/s/n): ").lower().strip()
        if choice in ['a', 's', 'n']:
            return choice
        print("无效选择，请输入 a、s 或 n")


def should_process_file(dot_file, mode):
    """判断是否应该处理文件"""
    if mode == 'n':  # 取消
        return False
    elif mode == 'a':  # 转换所有
        return True
    elif mode == 's':  # 跳过已存在的
        svg_file = dot_file.with_suffix('.svg')
        if svg_file.exists():
            print(f"跳过 {dot_file.name}（SVG文件已存在）")
            return False
        return True
    return False


def process_dot_file(dot_path: Path):
    """处理单个DOT文件，生成对应的SVG文件"""
    svg_path = dot_path.with_suffix('.svg')
    return convert_dot_to_svg(dot_path, svg_path)


def main():
    if len(sys.argv) == 1:
        # 无参数模式：处理output目录下的所有DOT文件
        dot_files = find_dot_files()
        if not dot_files:
            print("未找到任何DOT文件")
            return
        
        # 询问用户确认
        mode = ask_user_confirmation(dot_files)
        if mode == 'n':
            print("已取消转换")
            return
        
        print(f"\n开始转换...")
        
        success_count = 0
        skipped_count = 0
        
        for dot_file in dot_files:
            if should_process_file(dot_file, mode):
                if process_dot_file(dot_file):
                    success_count += 1
            else:
                skipped_count += 1
        
        print(f"\n转换完成：{success_count} 个文件成功，{skipped_count} 个文件跳过")
        
    elif len(sys.argv) == 2 and sys.argv[1] == "--auto":
        # 自动模式：跳过已存在的文件，不询问用户
        dot_files = find_dot_files()
        if not dot_files:
            print("未找到任何DOT文件")
            return
        
        print(f"找到 {len(dot_files)} 个DOT文件，自动转换模式...")
        
        success_count = 0
        skipped_count = 0
        
        for dot_file in dot_files:
            if should_process_file(dot_file, 's'):  # 使用跳过模式
                if process_dot_file(dot_file):
                    success_count += 1
            else:
                skipped_count += 1
        
        print(f"转换完成：{success_count} 个文件成功，{skipped_count} 个文件跳过")
        
    elif len(sys.argv) == 3:
        # 传统模式：指定输入输出文件
        dot_path = Path(sys.argv[1])
        svg_path = Path(sys.argv[2])
        
        convert_dot_to_svg(dot_path, svg_path)
        
    else:
        print("用法：")
        print("  python dot_to_svg.py                    # 转换output目录下的所有DOT文件（交互模式）")
        print("  python dot_to_svg.py --auto             # 转换output目录下的所有DOT文件（自动模式）")
        print("  python dot_to_svg.py input.dot output.svg  # 转换指定文件")
        sys.exit(1)


if __name__ == "__main__":
    main()