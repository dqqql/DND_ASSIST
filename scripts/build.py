#!/usr/bin/env python3
"""
项目构建和打包脚本
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    
    # 要清理的目录和文件
    clean_targets = [
        "build/",
        "dist/", 
        "*.egg-info/",
        "__pycache__/",
        "**/__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache/",
        "output/"
    ]
    
    base_dir = Path(__file__).parent.parent
    
    for target in clean_targets:
        if "*" in target:
            # 使用glob模式
            for path in base_dir.glob(target):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                    print(f"  删除目录: {path}")
                else:
                    path.unlink(missing_ok=True)
                    print(f"  删除文件: {path}")
        else:
            path = base_dir / target
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                    print(f"  删除目录: {path}")
                else:
                    path.unlink()
                    print(f"  删除文件: {path}")


def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    try:
        import PIL
        print("  ✅ Pillow")
    except ImportError:
        print("  ❌ Pillow - 请运行: pip install Pillow")
        return False
    
    try:
        import psutil
        print("  ✅ psutil")
    except ImportError:
        print("  ⚠️  psutil (可选) - 建议安装: pip install psutil")
    
    # 检查Graphviz
    try:
        result = subprocess.run(["dot", "-V"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Graphviz")
        else:
            print("  ⚠️  Graphviz - 剧情可视化功能需要安装Graphviz")
    except FileNotFoundError:
        print("  ⚠️  Graphviz - 剧情可视化功能需要安装Graphviz")
    
    return True


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    base_dir = Path(__file__).parent.parent
    
    # 测试示例数据生成
    try:
        result = subprocess.run([
            sys.executable, "examples/sample_campaign.py"
        ], cwd=base_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ 示例数据生成测试通过")
        else:
            print(f"  ❌ 示例数据生成测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ 测试执行失败: {e}")
        return False
    
    # 测试主程序导入
    try:
        result = subprocess.run([
            sys.executable, "-c", "import main; print('主程序导入成功')"
        ], cwd=base_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ 主程序导入测试通过")
        else:
            print(f"  ❌ 主程序导入测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ 主程序测试失败: {e}")
        return False
    
    return True


def create_distribution():
    """创建发布包"""
    print("📦 创建发布包...")
    
    base_dir = Path(__file__).parent.parent
    dist_dir = base_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # 要包含的文件和目录
    include_items = [
        "main.py",
        "start_server.py", 
        "src/",
        "tools/",
        "examples/",
        "requirements.txt",
        "README.md",
        "LICENSE",
        ".gitignore"
    ]
    
    # 创建发布目录
    release_dir = dist_dir / "dnd-manager"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制文件
    for item in include_items:
        src_path = base_dir / item
        if src_path.exists():
            if src_path.is_dir():
                shutil.copytree(src_path, release_dir / item)
                print(f"  复制目录: {item}")
            else:
                shutil.copy2(src_path, release_dir / item)
                print(f"  复制文件: {item}")
        else:
            print(f"  ⚠️  跳过不存在的项目: {item}")
    
    # 创建启动脚本
    if sys.platform.startswith("win"):
        start_script = release_dir / "start.bat"
        start_script.write_text("""@echo off
echo 启动 DND 跑团管理器...
python main.py
pause
""", encoding='utf-8')
        print("  创建启动脚本: start.bat")
    else:
        start_script = release_dir / "start.sh"
        start_script.write_text("""#!/bin/bash
echo "启动 DND 跑团管理器..."
python3 main.py
""")
        start_script.chmod(0o755)
        print("  创建启动脚本: start.sh")
    
    print(f"✅ 发布包创建完成: {release_dir}")
    return release_dir


def main():
    """主函数"""
    print("🚀 DND 跑团管理器 - 构建脚本")
    print("=" * 50)
    
    # 步骤1: 清理
    clean_build()
    print()
    
    # 步骤2: 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请安装缺失的依赖")
        return 1
    print()
    
    # 步骤3: 运行测试
    if not run_tests():
        print("❌ 测试失败，请检查代码")
        return 1
    print()
    
    # 步骤4: 创建发布包
    release_dir = create_distribution()
    print()
    
    print("🎉 构建完成！")
    print(f"📁 发布包位置: {release_dir}")
    print()
    print("📋 使用说明:")
    print("1. 将发布包复制到目标机器")
    print("2. 安装Python 3.7+")
    print("3. 运行: pip install -r requirements.txt")
    print("4. 启动程序: python main.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())