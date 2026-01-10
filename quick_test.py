#!/usr/bin/env python3
"""
快速测试Web UI功能
"""

import webbrowser
import time

def main():
    print("🧪 快速测试Web UI功能")
    
    # 打开测试页面
    test_urls = [
        "http://localhost:58184/tools/web_ui/test_simple.html",
        "http://localhost:58184/debug_web_ui.html",
        "http://localhost:58184/tools/web_ui/index.html"
    ]
    
    print("📋 测试页面列表:")
    for i, url in enumerate(test_urls, 1):
        print(f"   {i}. {url}")
    
    choice = input("\n请选择要打开的测试页面 (1-3): ").strip()
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(test_urls):
            url = test_urls[index]
            print(f"\n🌐 正在打开: {url}")
            webbrowser.open(url)
            print("✅ 页面已在浏览器中打开")
            print("\n💡 测试说明:")
            if index == 0:
                print("   • 这是简化的测试页面，用于验证基本功能")
                print("   • 点击按钮测试JavaScript和API功能")
            elif index == 1:
                print("   • 这是完整的调试页面，包含详细的测试功能")
                print("   • 可以测试API连接、JavaScript功能等")
            else:
                print("   • 这是完整的主界面")
                print("   • 如果按钮无法点击，请检查浏览器控制台的错误信息")
                print("   • 按F12打开开发者工具查看Console标签")
        else:
            print("❌ 无效的选择")
    except ValueError:
        print("❌ 请输入有效的数字")

if __name__ == "__main__":
    main()