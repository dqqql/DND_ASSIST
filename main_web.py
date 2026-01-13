#!/usr/bin/env python3
"""
DND 跑团管理器 - Web UI 版本
纯Web界面的跑团管理工具，提供现代化的用户体验

使用方法：
    python main_web.py              # 启动Web界面
    python main_web.py --port 8080  # 指定端口启动
    python main_web.py --help       # 查看帮助信息

功能特性：
    🎯 统一的Web界面管理所有跑团资料
    📊 现代化的响应式设计
    🔄 实时数据同步和自动保存
    🌐 跨平台兼容，支持所有现代浏览器
    🚀 一键启动，自动打开浏览器
"""

import sys
import os 
import argparse
import webbrowser
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.web_preview.server import WebPreviewServer


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='DND 跑团管理器 - Web UI 版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main_web.py                    # 使用默认端口启动
  python main_web.py --port 8080       # 指定端口8080启动
  python main_web.py --no-browser      # 启动但不自动打开浏览器
  python main_web.py --dev             # 开发模式（不自动监控关闭）

功能说明:
  🎯 跑团管理：创建、删除、切换跑团
  📝 内容管理：人物卡、怪物卡、地图、剧情
  🌐 Web编辑器：现代化的剧情编辑体验
  📊 数据可视化：剧情流程图生成和预览
  🔒 安全机制：软删除和文件恢复功能
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=None,
        help='指定服务器端口（默认自动分配）'
    )
    
    parser.add_argument(
        '--no-browser', '-n',
        action='store_true',
        help='启动服务器但不自动打开浏览器'
    )
    
    parser.add_argument(
        '--dev', '-d',
        action='store_true',
        help='开发模式：禁用自动监控关闭功能'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='服务器主机地址（默认：localhost）'
    )
    
    return parser.parse_args()


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎲 DND 跑团管理器                         ║
║                      Web UI 版本                            ║
╠══════════════════════════════════════════════════════════════╣
║  🎯 现代化的Web界面，告别传统桌面应用的束缚                    ║
║  📊 响应式设计，完美适配各种设备屏幕                          ║
║  🔄 实时保存，再也不用担心数据丢失                            ║
║  🌐 跨平台兼容，Windows/Mac/Linux 通用                       ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """检查必要的依赖（优化版本）"""
    missing_deps = []
    
    try:
        # 使用更快的导入检查
        import importlib.util
        
        # 检查 Pillow
        if importlib.util.find_spec("PIL") is None:
            missing_deps.append("Pillow")
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print("❌ 缺少必要的依赖包:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n请运行以下命令安装依赖:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def setup_project_structure():
    """确保项目结构完整（优化版本）"""
    # 确保数据目录存在
    data_dir = project_root / "data" / "campaigns"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 批量创建Web资源目录
    web_dirs = [
        "tools/web_ui",
        "tools/editor", 
        "tools/characters",
        "tools/preview"
    ]
    
    for web_dir in web_dirs:
        (project_root / web_dir).mkdir(parents=True, exist_ok=True)
    
    return True


def start_web_server(args):
    """启动Web服务器"""
    print("🚀 正在启动Web服务器...")
    
    # 创建服务器实例
    server = WebPreviewServer(project_root)
    
    # 如果指定了端口，设置端口
    if args.port:
        server.port = args.port
    
    # 启动服务器（不再有自动监控）
    success = server.start()
    
    if not success:
        print("❌ 服务器启动失败")
        print("\n可能的原因:")
        print("   • 端口被占用")
        print("   • 权限不足")
        print("   • 防火墙阻止")
        return None
    
    return server


def open_web_interface(server, args):
    """打开Web界面"""
    if args.no_browser:
        return
    
    print("🌐 正在打开Web界面...")
    
    # 构建主界面URL
    main_url = server.get_url("tools/web_ui/index.html")
    
    try:
        webbrowser.open(main_url)
        print("✅ Web界面已在浏览器中打开")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print(f"请手动访问: {main_url}")


def print_server_info(server, args):
    """打印服务器信息"""
    print("\n" + "="*60)
    print("📋 服务器信息:")
    print(f"   🌐 主界面: {server.get_url('tools/web_ui/index.html')}")
    print(f"   📝 编辑器: {server.get_url('tools/editor/editor.html')}")
    print(f"   👥 角色卡: {server.get_url('tools/characters/characters.html')}")
    print(f"   🎭 预览器: {server.get_url('tools/preview/preview.html')}")
    print(f"   🔧 API接口: {server.get_url('api/')}")
    print(f"   📡 端口: {server.get_port()}")
    print(f"   🏠 主机: {args.host}")
    
    if args.dev:
        print("   🔧 模式: 开发模式（手动关闭）")
    else:
        print("   🔧 模式: 稳定模式（手动关闭）")
    
    print("="*60)


def wait_for_server(server, args):
    """等待服务器运行"""
    print("\n💡 使用提示:")
    print("   • 服务器将持续运行直到手动停止")
    print("   • 按 Ctrl+C 停止服务器")
    print("   • 服务器不会自动关闭，确保稳定的编辑体验")
    
    print("\n🎯 开始使用 DND 跑团管理器吧！")
    print("   1. 创建或选择跑团")
    print("   2. 管理人物卡、怪物卡、地图和剧情")
    print("   3. 使用现代化的Web编辑器编辑剧情")
    print("   4. 生成和查看剧情流程图")
    
    try:
        # 保持服务器运行
        while server.is_running():
            time.sleep(1)
        
        print("\n✅ 服务器已停止")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  正在停止服务器...")
        server.stop()
        print("✅ 服务器已停止")


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 打印启动横幅
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置项目结构
    if not setup_project_structure():
        print("❌ 项目结构设置失败")
        sys.exit(1)
    
    # 启动Web服务器
    server = start_web_server(args)
    if not server:
        sys.exit(1)
    
    # 打印服务器信息
    print_server_info(server, args)
    
    # 打开Web界面
    open_web_interface(server, args)
    
    # 等待服务器运行
    wait_for_server(server, args)


if __name__ == "__main__":
    main()