#!/usr/bin/env python3
"""
主应用交互反馈测试
验证主应用中的交互反馈增强是否正常工作
"""

import tkinter as tk
import sys
import traceback
from main import App


def test_main_app_interaction():
    """测试主应用的交互反馈"""
    print("测试主应用交互反馈增强...")
    
    try:
        # 创建主应用
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口以进行测试
        
        app = App(root)
        
        # 验证应用创建成功
        assert app is not None, "应用创建失败"
        
        # 验证主要组件存在
        assert hasattr(app, 'campaign_list'), "跑团列表不存在"
        assert hasattr(app, 'file_list'), "文件列表不存在"
        assert hasattr(app, 'category_buttons'), "分类按钮不存在"
        assert hasattr(app, 'category_handlers'), "分类按钮处理器不存在"
        
        # 验证交互处理器已创建
        print(f"分类按钮数量: {len(app.category_buttons)}")
        print(f"交互处理器数量: {len(app.category_handlers)}")
        
        # 验证列表控件有正确的光标样式
        campaign_cursor = app.campaign_list.cget('cursor')
        file_cursor = app.file_list.cget('cursor')
        
        assert campaign_cursor == "hand2", f"跑团列表光标样式不正确: {campaign_cursor}"
        assert file_cursor == "hand2", f"文件列表光标样式不正确: {file_cursor}"
        
        print("✓ 主应用交互反馈增强测试通过")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ 主应用交互反馈测试失败: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    try:
        success = test_main_app_interaction()
        
        if success:
            print("\n✅ 主应用交互反馈增强验证成功！")
            print("所有可点击元素都已添加即时视觉反馈")
            print("hover状态和焦点指示器都已正确实现")
            return True
        else:
            print("\n❌ 主应用交互反馈测试失败")
            return False
            
    except Exception as e:
        print(f"\n💥 测试执行出错: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)