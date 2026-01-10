#!/usr/bin/env python3
"""
DND 跑团管理器 - 发行版构建脚本
用于构建可分发的Web UI版本，支持免安装部署
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform


def print_banner():
    """打印构建横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                DND 跑团管理器 - 发行版构建                    ║
║                     Web UI 版本                             ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 构建免安装的跑团管理工具发行版                            ║
║  📦 无需Python环境，开箱即用                                 ║
║  🚀 一键打包，跨平台部署                                     ║
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
    
    dirs_to_clean = ['build', 'dist', 'release', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   🗑️  已删除: {dir_name}")
    
    # 清理.spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   🗑️  已删除: {spec_file}")
    
    # 清理旧的压缩包
    for zip_file in Path('.').glob('DND_Manager_*.zip'):
        zip_file.unlink()
        print(f"   🗑️  已删除: {zip_file}")
    
    print("✅ 构建目录清理完成")


def create_release_structure():
    """创建发行版目录结构"""
    print("📁 创建发行版目录结构...")
    
    release_dir = Path('release')
    release_dir.mkdir()
    
    # 复制必要的文件和目录
    files_to_copy = [
        'main_web.py',
        'src/',
        'tools/',
        'examples/',
        'requirements.txt',
        'README.md',
        'LICENSE',
        'WEB_FILE_EDITOR_GUIDE.md',
        'TROUBLESHOOTING.md'
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


def create_pyinstaller_spec(release_dir):
    """创建PyInstaller配置文件"""
    print("📝 创建PyInstaller配置文件...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None

# 数据文件
datas = [
    ('tools', 'tools'),
    ('src', 'src'),
    ('examples', 'examples'),
    ('data', 'data'),
]

# 隐藏导入
hiddenimports = [
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'http.server',
    'socketserver',
    'webbrowser',
    'json',
    'pathlib',
    'urllib.parse',
    'urllib.request',
]

a = Analysis(
    ['main_web.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'tkinter.ttk',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DND_Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 保留控制台以显示启动信息
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DND_Manager',
)
'''
    
    spec_file = release_dir / 'DND_Manager.spec'
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("   ✅ 已创建: DND_Manager.spec")
    return spec_file


def build_executable_version(release_dir):
    """构建可执行文件"""
    print("🔨 构建免安装可执行文件...")
    
    # 切换到发行版目录
    original_cwd = os.getcwd()
    os.chdir(release_dir)
    
    try:
        # 创建spec文件
        spec_file = create_pyinstaller_spec(Path('.'))
        
        # 执行PyInstaller
        cmd = ['pyinstaller', '--clean', str(spec_file.name)]
        
        print(f"   🔧 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ 可执行文件构建成功")
            return True
        else:
            print("   ❌ 可执行文件构建失败")
            print(f"   错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ 构建过程出错: {e}")
        return False
    finally:
        os.chdir(original_cwd)


def create_startup_scripts(target_dir):
    """创建启动脚本"""
    print("📜 创建启动脚本...")
    
    system = platform.system()
    
    if system == "Windows":
        # Windows批处理脚本
        bat_script = target_dir / 'start_dnd_manager.bat'
        with open(bat_script, 'w', encoding='utf-8') as f:
            f.write("""@echo off
chcp 65001 > nul
title DND 跑团管理器 - Web UI 版本

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎲 DND 跑团管理器                         ║
echo ║                      Web UI 版本                            ║
echo ║                     免安装版本                               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 正在启动Web服务器...
echo 📱 浏览器将自动打开管理界面
echo 💡 关闭此窗口将停止服务器
echo.

DND_Manager.exe
pause
""")
        print("   ✅ 已创建: start_dnd_manager.bat")
    
    # Linux/Mac shell脚本
    sh_script = target_dir / 'start_dnd_manager.sh'
    with open(sh_script, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎲 DND 跑团管理器                         ║"
echo "║                      Web UI 版本                            ║"
echo "║                     免安装版本                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 正在启动Web服务器..."
echo "📱 浏览器将自动打开管理界面"
echo "💡 按Ctrl+C停止服务器"
echo ""

./DND_Manager
""")
    
    # 设置执行权限
    os.chmod(sh_script, 0o755)
    print("   ✅ 已创建: start_dnd_manager.sh")


def create_user_guide(target_dir):
    """创建用户指南"""
    print("📖 创建用户指南...")
    
    guide_content = """# DND 跑团管理器 - 免安装版本

## 🚀 快速开始

### Windows用户
1. 解压下载的压缩包到任意目录
2. 双击运行 `start_dnd_manager.bat`
3. 等待浏览器自动打开管理界面

### Linux/Mac用户
1. 解压下载的压缩包到任意目录
2. 在终端中运行: `./start_dnd_manager.sh`
3. 等待浏览器自动打开管理界面

### 手动启动
如果启动脚本无法运行，可以直接运行可执行文件：
- Windows: 双击 `DND_Manager.exe`
- Linux/Mac: 在终端运行 `./DND_Manager`

## ✨ 特性说明

### 🎯 免安装特性
- ✅ **无需Python环境** - 内置Python运行时
- ✅ **无需安装依赖** - 所有依赖已打包
- ✅ **开箱即用** - 解压即可运行
- ✅ **绿色软件** - 不修改系统注册表
- ✅ **便携部署** - 可放在U盘中随身携带

### 🌐 Web界面特性
- 📱 **响应式设计** - 适配各种屏幕尺寸
- 🎨 **现代化UI** - 美观易用的界面设计
- ⚡ **实时保存** - 自动保存编辑内容
- 🔒 **本地存储** - 数据完全存储在本地

### 🎲 跑团管理功能
- 📂 **跑团管理** - 创建、删除、切换跑团
- 👥 **人物卡管理** - 角色信息和属性管理
- 👹 **怪物卡管理** - 怪物数据和能力管理
- 🗺️ **地图管理** - 地图图片和说明管理
- 📖 **剧情管理** - 文本笔记和结构化剧情

### ✏️ 编辑功能
- 📝 **通用文件编辑器** - 支持所有文本文件编辑
- 🎭 **专用剧情编辑器** - 可视化节点编辑
- 📊 **数据可视化** - 剧情流程图生成
- 🔍 **实时验证** - 数据格式自动检查

## 📁 目录结构

```
DND_Manager/
├── DND_Manager.exe          # 主程序（Windows）
├── DND_Manager              # 主程序（Linux/Mac）
├── start_dnd_manager.bat    # Windows启动脚本
├── start_dnd_manager.sh     # Linux/Mac启动脚本
├── data/                    # 数据目录
│   └── campaigns/           # 跑团数据存储
├── tools/                   # Web界面文件
├── examples/                # 示例文件
└── README.md               # 本文件
```

## 🎯 使用流程

1. **启动应用** - 运行启动脚本或可执行文件
2. **创建跑团** - 在Web界面点击"新建跑团"
3. **管理内容** - 选择分类，创建和编辑文件
4. **保存数据** - 所有更改自动保存到本地
5. **关闭应用** - 关闭浏览器和控制台窗口

## 💾 数据管理

### 数据位置
- 所有跑团数据存储在 `data/campaigns/` 目录
- 每个跑团有独立的文件夹
- 支持直接文件系统操作

### 备份数据
- 复制整个 `data` 文件夹即可备份
- 支持跨设备数据迁移
- 建议定期备份重要数据

### 导入数据
- 将备份的数据文件夹复制到 `data/campaigns/`
- 重启应用即可看到导入的跑团

## 🔧 故障排除

### 常见问题

**Q: 程序无法启动**
A: 
- 检查是否有杀毒软件阻止运行
- 尝试以管理员权限运行
- 检查系统是否支持该版本

**Q: 浏览器无法打开**
A:
- 手动打开浏览器访问 http://localhost:端口号
- 检查防火墙设置
- 尝试使用不同的浏览器

**Q: 数据丢失**
A:
- 检查 `data/campaigns/` 目录是否存在
- 查看是否有备份文件
- 确认程序有写入权限

**Q: 端口被占用**
A:
- 程序会自动寻找可用端口
- 如需指定端口，使用命令行参数
- 关闭占用端口的其他程序

### 技术支持
- 查看控制台输出的错误信息
- 检查 `data` 目录的权限设置
- 确保有足够的磁盘空间

## 🎮 高级用法

### 命令行参数
```bash
# 指定端口
./DND_Manager --port 8080

# 不自动打开浏览器
./DND_Manager --no-browser

# 开发模式
./DND_Manager --dev

# 查看帮助
./DND_Manager --help
```

### 网络访问
- 默认只允许本地访问
- 可通过参数开启局域网访问
- 支持多设备同时访问

## 📄 许可证

本软件采用 MIT 许可证，免费使用。

---

🎲 **享受免安装的跑团管理体验！**

如有问题或建议，欢迎反馈。
"""
    
    readme_file = target_dir / 'README.md'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("   ✅ 已创建: README.md")


def create_archive(source_dir, name_suffix=""):
    """创建发行版压缩包"""
    print(f"📦 创建发行版压缩包{name_suffix}...")
    
    try:
        import zipfile
        
        # 确定压缩包名称
        system = platform.system().lower()
        arch = platform.machine().lower()
        if arch == 'amd64':
            arch = 'x64'
        elif arch in ['i386', 'i686']:
            arch = 'x86'
        
        zip_name = f"DND_Manager_WebUI_{system}_{arch}{name_suffix}.zip"
        zip_path = Path(zip_name)
        
        if zip_path.exists():
            zip_path.unlink()
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    # 排除不需要的文件
                    if any(exclude in str(file_path) for exclude in ['.pyc', '__pycache__', '.spec']):
                        continue
                    
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)
        
        size = zip_path.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✅ 已创建: {zip_name} ({size:.1f} MB)")
        return zip_path
        
    except Exception as e:
        print(f"   ❌ 创建压缩包失败: {e}")
        return None


def main():
    """主构建流程"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        print("\n💡 提示: 如果只需要源码版本，可以跳过PyInstaller安装")
        choice = input("是否继续构建源码版本？(y/N): ").strip().lower()
        if choice != 'y':
            sys.exit(1)
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建发行版目录结构
    release_dir = create_release_structure()
    
    print("\n" + "="*60)
    print("📋 构建选项:")
    print("   1. 源码版本 (需要Python环境)")
    print("   2. 免安装可执行版本 (推荐)")
    print("   3. 同时构建两个版本")
    print("="*60)
    
    choice = input("请选择构建选项 (1-3): ").strip()
    
    build_source = choice in ['1', '3']
    build_executable = choice in ['2', '3']
    
    success_count = 0
    
    # 构建源码版本
    if build_source:
        print("\n🔨 构建源码版本...")
        
        # 创建源码版启动脚本
        create_startup_scripts(release_dir)
        
        # 创建源码版用户指南
        source_guide = """# DND 跑团管理器 - 源码版本

## 📋 系统要求
- Python 3.7 或更高版本
- pip 包管理器

## 🚀 安装和运行
1. 安装依赖: `pip install -r requirements.txt`
2. 运行程序: `python main_web.py`

## 📖 详细说明
请参考项目文档了解更多功能和使用方法。
"""
        with open(release_dir / 'README_SOURCE.md', 'w', encoding='utf-8') as f:
            f.write(source_guide)
        
        # 创建源码版压缩包
        source_zip = create_archive(release_dir, "_Source")
        if source_zip:
            success_count += 1
    
    # 构建可执行版本
    if build_executable:
        print("\n🔨 构建免安装可执行版本...")
        
        if build_executable_version(release_dir):
            # 可执行文件构建成功
            dist_dir = release_dir / 'dist' / 'DND_Manager'
            
            if dist_dir.exists():
                # 创建可执行版启动脚本
                create_startup_scripts(dist_dir)
                
                # 创建可执行版用户指南
                create_user_guide(dist_dir)
                
                # 复制示例文件
                if (release_dir / 'examples').exists():
                    shutil.copytree(release_dir / 'examples', dist_dir / 'examples')
                
                # 创建可执行版压缩包
                exe_zip = create_archive(dist_dir, "_Executable")
                if exe_zip:
                    success_count += 1
            else:
                print("❌ 可执行文件目录不存在")
        else:
            print("❌ 可执行版本构建失败")
    
    # 构建总结
    print("\n" + "="*60)
    if success_count > 0:
        print("🎉 发行版构建完成！")
        print(f"\n📦 成功创建 {success_count} 个版本:")
        
        for zip_file in Path('.').glob('DND_Manager_WebUI_*.zip'):
            size = zip_file.stat().st_size / (1024 * 1024)  # MB
            if "Source" in zip_file.name:
                print(f"   📁 {zip_file.name} ({size:.1f} MB) - 需要Python环境")
            else:
                print(f"   📁 {zip_file.name} ({size:.1f} MB) - 免安装版本 ⭐")
        
        print("\n🚀 使用方法:")
        print("   1. 解压压缩包到目标目录")
        print("   2. 运行启动脚本或可执行文件")
        print("   3. 浏览器将自动打开管理界面")
        
        print("\n✨ 免安装版本特点:")
        print("   • 无需安装Python")
        print("   • 无需安装依赖包")
        print("   • 解压即可运行")
        print("   • 支持便携部署")
        
        print("\n🎲 享受全新的Web UI跑团管理体验！")
    else:
        print("❌ 构建失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()