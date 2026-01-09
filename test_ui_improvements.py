#!/usr/bin/env python3
"""
测试 UI 改进：按钮颜色和角色卡头像颜色
"""

import sys
import time
import webbrowser
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.web_preview.server import WebPreviewServer


def test_ui_improvements():
    """测试 UI 改进"""
    print("🎨 测试 UI 改进")
    print("=" * 40)
    
    # 启动服务器
    server = WebPreviewServer()
    if not server.start(auto_monitor=False):
        print("❌ 服务器启动失败")
        return False
    
    base_url = f"http://localhost:{server.get_port()}"
    print(f"✅ 服务器启动成功: {base_url}")
    
    try:
        time.sleep(1)
        
        viewer_url = f"{base_url}/tools/characters/characters.html"
        
        print(f"\n🔧 UI 改进内容:")
        print(f"   1. 按钮颜色修复:")
        print(f"      • 修改了 button_normal 颜色为更亮的 #f8f9fa")
        print(f"      • 按钮默认状态应该更明亮")
        print(f"      • 鼠标悬停时有明显的颜色变化")
        
        print(f"\n   2. 角色卡头像颜色:")
        print(f"      • 人物卡：5种颜色变体（蓝、紫、橙、青、黄）")
        print(f"      • 怪物卡：5种颜色变体（红、深紫、深灰、深橙、灰）")
        print(f"      • 地图：5种颜色变体（绿、深蓝、紫、棕、深青）")
        print(f"      • 根据名称自动分配颜色，相同名称始终相同颜色")
        
        # 询问是否打开浏览器测试
        try:
            user_input = input(f"\n是否在浏览器中查看改进效果？(y/n): ").strip().lower()
            if user_input in ['y', 'yes', '是', '']:
                print(f"\n🌐 正在打开页面: {viewer_url}")
                webbrowser.open(viewer_url)
                
                print(f"\n✅ 请检查以下改进:")
                print(f"   • 角色卡头像是否有不同的颜色")
                print(f"   • 相同类型的卡片颜色是否有变化")
                print(f"   • 颜色搭配是否美观")
                
                print(f"\n📝 同时请检查 Tkinter 主应用:")
                print(f"   • 启动 main.py")
                print(f"   • 查看右上角的三个按钮（新建文件、删除文件、Web查看）")
                print(f"   • 按钮默认状态应该更亮，不再是暗灰色")
                
                input(f"\n按 Enter 键结束测试...")
                print(f"✅ 测试完成")
            else:
                print(f"跳过浏览器测试")
        except KeyboardInterrupt:
            print(f"\n用户取消测试")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        print(f"\n🔧 停止服务器...")
        server.stop()
        print(f"✅ 服务器已停止")


if __name__ == "__main__":
    success = test_ui_improvements()
    sys.exit(0 if success else 1)