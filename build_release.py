#!/usr/bin/env python3
"""
DND 跑团管理器 - 发行版构建脚本
用于构建可分发的Web UI版本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_banner():
    """打印构建横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                DND 跑团管理器 - 发行版构建                    ║
║                     Web UI 版本                             ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 构建纯Web界面的跑团管理工具发行版                         ║
║  📦 移除Tkinter依赖，专注Web体验                             ║
║  🚀 一键打包，即开即用                                       ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """检查构建依赖"""
    print("🔍 检查构建依赖...")
    
    missing_deps = []
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"   ✅ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        missing_deps.append("PyInstaller")
    
    # 检查项目依赖
    try:
        from PIL import Image
        print("   ✅ Pillow: 已安装")
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print("❌ 缺少必要的依赖包:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n请运行以下命令安装依赖:")
        if "PyInstaller" in missing_deps:
            print("   pip install pyinstaller")
        if "Pillow" in missing_deps:
            print("   pip install Pillow")
        return False
    
    print("✅ 所有依赖检查通过")
    return True


def clean_build_dirs():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   🗑️  已删除: {dir_name}")
    
    # 清理.spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   🗑️  已删除: {spec_file}")
    
    print("✅ 构建目录清理完成")


def create_release_structure():
    """创建发行版目录结构"""
    print("📁 创建发行版目录结构...")
    
    release_dir = Path('release')
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # 复制必要的文件和目录
    files_to_copy = [
        'main_web.py',
        'src/',
        'tools/',
        'examples/',
        'requirements.txt',
        'README.md',
        'WEB_UI_REFACTOR.md',
        'LICENSE'
    ]
    
    for item in files_to_copy:
        src_path = Path(item)
        if src_path.exists():
            if src_path.is_dir():
                shutil.copytree(src_path, release_dir / src_path.name)
                print(f"   📂 已复制目录: {item}")
            else:
                shutil.copy2(src_path, release_dir / src_path.name)
                print(f"   📄 已复制文件: {item}")
        else:
            print(f"   ⚠️  文件不存在: {item}")
    
    # 创建数据目录
    data_dir = release_dir / 'data' / 'campaigns'
    data_dir.mkdir(parents=True)
    print("   📂 已创建数据目录: data/campaigns")
    
    print("✅ 发行版目录结构创建完成")
    return release_dir


def remove_tkinter_dependencies(release_dir):
    """移除Tkinter相关依赖"""
    print("🚫 移除Tkinter依赖...")
    
    # 移除main.py（Tkinter版本）
    main_py = release_dir / 'main.py'
    if main_py.exists():
        main_py.unlink()
        print("   🗑️  已移除: main.py (Tkinter版本)")
    
    # 移除UI层的Tkinter相关文件
    ui_dir = release_dir / 'src' / 'ui'
    if ui_dir.exists():
        tkinter_files = [
            'theme_integration.py',
            'theme_utils.py',
            'theme_system.py',
            'layout_system.py'
        ]
        
        for file_name in tkinter_files:
            file_path = ui_dir / file_name
            if file_path.exists():
                file_path.unlink()
                print(f"   🗑️  已移除: src/ui/{file_name}")
    
    # 移除story_editor目录（Tkinter编辑器）
    story_editor_dir = release_dir / 'src' / 'story_editor'
    if story_editor_dir.exists():
        shutil.rmtree(story_editor_dir)
        print("   🗑️  已移除: src/story_editor/ (Tkinter编辑器)")
    
    print("✅ Tkinter依赖移除完成")


def update_requirements(release_dir):
    """更新requirements.txt，移除Tkinter相关依赖"""
    print("📝 更新依赖文件...")
    
    requirements_file = release_dir / 'requirements.txt'
    
    # Web UI版本的最小依赖
    web_requirements = [
        "Pillow>=9.0.0",
        "psutil>=5.8.0  # 用于智能浏览器监控（可选）"
    ]
    
    with open(requirements_file, 'w', encoding='utf-8') as f:
        f.write("# DND 跑团管理器 - Web UI 版本依赖\n")
        f.write("# 最小化依赖，专注Web体验\n\n")
        for req in web_requirements:
            f.write(req + '\n')
    
    print("   ✅ requirements.txt 已更新")


def create_startup_scripts(release_dir):
    """创建启动脚本"""
    print("📜 创建启动脚本...")
    
    # Windows批处理脚本
    bat_script = release_dir / 'start_dnd_manager.bat'
    with open(bat_script, 'w', encoding='utf-8') as f:
        f.write("""@echo off
chcp 65001 > nul
title DND 跑团管理器 - Web UI 版本

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎲 DND 跑团管理器                         ║
echo ║                      Web UI 版本                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

python main_web.py
pause
""")
    print("   ✅ 已创建: start_dnd_manager.bat")
    
    # Linux/Mac shell脚本
    sh_script = release_dir / 'start_dnd_manager.sh'
    with open(sh_script, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎲 DND 跑团管理器                         ║"
echo "║                      Web UI 版本                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

python3 main_web.py
""")
    
    # 设置执行权限
    os.chmod(sh_script, 0o755)
    print("   ✅ 已创建: start_dnd_manager.sh")


def create_readme(release_dir):
    """创建发行版README"""
    print("📖 创建发行版README...")
    
    readme_content = """# DND 跑团管理器 - Web UI 版本

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

**Windows用户:**
```
双击运行 start_dnd_manager.bat
```

**Linux/Mac用户:**
```bash
./start_dnd_manager.sh
```

### 方法二：命令行启动

```bash
# 基本启动
python main_web.py

# 指定端口
python main_web.py --port 8080

# 查看帮助
python main_web.py --help
```

## 📋 系统要求

- **Python**: 3.7 或更高版本
- **浏览器**: Chrome、Firefox、Safari、Edge等现代浏览器
- **操作系统**: Windows、macOS、Linux

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🎯 功能特性

- 🌐 **纯Web界面**: 现代化的浏览器界面，无需安装桌面应用
- 📱 **响应式设计**: 完美适配桌面、平板、手机等各种设备
- 🎲 **跑团管理**: 创建、删除、切换跑团，管理所有跑团资料
- 📝 **内容管理**: 人物卡、怪物卡、地图、剧情四大分类管理
- ✏️ **Web编辑器**: 现代化的剧情编辑体验，支持可视化节点编辑
- 📊 **数据可视化**: 剧情流程图生成和预览
- 🔒 **安全机制**: 软删除和文件恢复功能，数据本地存储

## 📚 使用指南

1. **启动应用**: 运行启动脚本或使用命令行
2. **创建跑团**: 点击"新建跑团"按钮，输入跑团名称
3. **管理内容**: 选择分类标签，创建和编辑文件
4. **Web编辑**: 对于JSON剧情文件，使用Web编辑器进行可视化编辑
5. **查看预览**: 生成和查看剧情流程图

## 🆘 常见问题

**Q: 如何创建示例数据？**
A: 运行 `python examples/sample_campaign.py` 创建示例跑团

**Q: 浏览器无法打开？**
A: 检查防火墙设置，确保允许Python程序访问网络

**Q: 数据存储在哪里？**
A: 所有数据存储在 `data/campaigns/` 目录下

**Q: 如何备份数据？**
A: 直接复制 `data` 文件夹即可备份所有跑团数据

## 📄 许可证

本项目采用 MIT 许可证。

---

🎲 **让每一次跑团都成为难忘的冒险！**
"""
    
    readme_file = release_dir / 'README_RELEASE.md'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✅ 已创建: README_RELEASE.md")


def build_with_pyinstaller(release_dir):
    """使用PyInstaller构建可执行文件"""
    print("🔨 使用PyInstaller构建可执行文件...")
    
    # 切换到发行版目录
    original_cwd = os.getcwd()
    os.chdir(release_dir)
    
    try:
        # PyInstaller命令
        cmd = [
            'pyinstaller',
            '--onedir',  # 打包为目录（推荐）
            '--windowed',  # Windows下隐藏控制台
            '--add-data', 'tools;tools',
            '--add-data', 'src;src',
            '--add-data', 'examples;examples',
            '--name', 'DND_Manager_WebUI',
            '--icon', 'tools/web_ui/favicon.ico' if Path('tools/web_ui/favicon.ico').exists() else None,
            'main_web.py'
        ]
        
        # 移除None值
        cmd = [arg for arg in cmd if arg is not None]
        
        print(f"   🔧 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ PyInstaller构建成功")
            
            # 复制额外文件到dist目录
            dist_dir = Path('dist/DND_Manager_WebUI')
            if dist_dir.exists():
                # 复制启动脚本
                shutil.copy2('start_dnd_manager.bat', dist_dir)
                shutil.copy2('start_dnd_manager.sh', dist_dir)
                
                # 复制README
                shutil.copy2('README_RELEASE.md', dist_dir / 'README.md')
                
                print("   ✅ 额外文件复制完成")
            
        else:
            print("   ❌ PyInstaller构建失败")
            print(f"   错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ 构建过程出错: {e}")
        return False
    finally:
        os.chdir(original_cwd)
    
    return True


def create_archive(release_dir):
    """创建发行版压缩包"""
    print("📦 创建发行版压缩包...")
    
    try:
        import zipfile
        
        # 创建源码版压缩包
        source_zip = Path('DND_Manager_WebUI_Source.zip')
        if source_zip.exists():
            source_zip.unlink()
        
        with zipfile.ZipFile(source_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in release_dir.rglob('*'):
                if file_path.is_file() and not file_path.name.endswith('.pyc'):
                    arcname = file_path.relative_to(release_dir)
                    zf.write(file_path, arcname)
        
        print(f"   ✅ 源码版: {source_zip}")
        
        # 创建可执行版压缩包（如果存在）
        dist_dir = release_dir / 'dist' / 'DND_Manager_WebUI'
        if dist_dir.exists():
            exe_zip = Path('DND_Manager_WebUI_Executable.zip')
            if exe_zip.exists():
                exe_zip.unlink()
            
            with zipfile.ZipFile(exe_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in dist_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(dist_dir)
                        zf.write(file_path, arcname)
            
            print(f"   ✅ 可执行版: {exe_zip}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 创建压缩包失败: {e}")
        return False


def main():
    """主构建流程"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建发行版目录结构
    release_dir = create_release_structure()
    
    # 移除Tkinter依赖
    remove_tkinter_dependencies(release_dir)
    
    # 更新依赖文件
    update_requirements(release_dir)
    
    # 创建启动脚本
    create_startup_scripts(release_dir)
    
    # 创建发行版README
    create_readme(release_dir)
    
    print("\n" + "="*60)
    print("📋 构建选项:")
    print("   1. 仅创建源码发行版")
    print("   2. 创建源码 + PyInstaller可执行版")
    print("="*60)
    
    choice = input("请选择构建选项 (1-2): ").strip()
    
    if choice == '2':
        # 使用PyInstaller构建
        if build_with_pyinstaller(release_dir):
            print("✅ PyInstaller构建完成")
        else:
            print("❌ PyInstaller构建失败，仅创建源码版")
    
    # 创建压缩包
    if create_archive(release_dir):
        print("✅ 发行版压缩包创建完成")
    
    print("\n" + "="*60)
    print("🎉 发行版构建完成！")
    print("\n📦 输出文件:")
    
    for zip_file in Path('.').glob('DND_Manager_WebUI_*.zip'):
        size = zip_file.stat().st_size / (1024 * 1024)  # MB
        print(f"   📁 {zip_file.name} ({size:.1f} MB)")
    
    print(f"\n📂 发行版目录: {release_dir}")
    print("\n🚀 使用方法:")
    print("   1. 解压压缩包到目标目录")
    print("   2. 安装Python依赖: pip install -r requirements.txt")
    print("   3. 运行启动脚本或执行: python main_web.py")
    print("\n🎲 享受全新的Web UI跑团管理体验！")


if __name__ == "__main__":
    main()