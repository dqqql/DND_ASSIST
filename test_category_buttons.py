#!/usr/bin/env python3
"""
分类按钮显示测试
验证四个分类按钮（人物卡、怪物卡、地图、剧情）是否正确显示
"""

import tkinter as tk
import os
import sys
from main import App, CATEGORIES, DATA_DIR


def test_category_buttons():
    """测试分类按钮显示"""
    print("测试分类按钮显示...")
    
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 创建一个测试跑团目录
    test_campaign = "测试跑团"
    test_campaign_path = os.path.join(DATA_DIR, test_campaign)
    
    if not os.path.exists(test_campaign_path):
        os.makedirs(test_campaign_path)
        for folder in CATEGORIES.values():
            os.makedirs(os.path.join(test_campaign_path, folder), exist_ok=True)
    
    # 创建应用程序实例
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    try:
        app = App(root)
        
        # 检查分类按钮是否存在
        print(f"分类按钮字典: {app.category_buttons}")
        print(f"分类常量: {CATEGORIES}")
        
        # 模拟选择跑团
        app.campaign_list.insert(tk.END, test_campaign)
        app.current_campaign = test_campaign
        app.show_categories()
        
        # 验证分类按钮是否创建
        expected_categories = list(CATEGORIES.keys())
        actual_categories = list(app.category_buttons.keys())
        
        print(f"期望的分类: {expected_categories}")
        print(f"实际的分类: {actual_categories}")
        
        # 检查每个分类按钮
        for category in expected_categories:
            if category in app.category_buttons:
                button = app.category_buttons[category]
                print(f"✓ 分类按钮 '{category}' 创建成功")
                print(f"  - 按钮文本: {button.cget('text')}")
                print(f"  - 按钮状态: {button.cget('state')}")
            else:
                print(f"✗ 分类按钮 '{category}' 未找到")
        
        # 检查分类框架是否有子控件
        category_frame_children = app.category_frame.winfo_children()
        print(f"分类框架子控件数量: {len(category_frame_children)}")
        
        if len(category_frame_children) == len(CATEGORIES):
            print("✅ 所有分类按钮都已正确创建并添加到界面")
            return True
        else:
            print(f"❌ 分类按钮数量不匹配: 期望 {len(CATEGORIES)}, 实际 {len(category_frame_children)}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()


def test_category_button_visibility():
    """测试分类按钮可见性"""
    print("\n测试分类按钮可见性...")
    
    root = tk.Tk()
    root.title("分类按钮可见性测试")
    root.geometry("800x600")
    
    try:
        app = App(root)
        
        # 创建测试跑团并选择
        test_campaign = "可见性测试跑团"
        app.campaign_list.insert(tk.END, test_campaign)
        app.campaign_list.selection_set(0)
        app.current_campaign = test_campaign
        app.show_categories()
        
        print("分类按钮可见性测试窗口已启动")
        print("请检查界面上是否显示了四个分类按钮：人物卡、怪物卡、地图、剧情")
        print("按钮应该在跑团列表的右侧区域显示")
        
        # 显示窗口5秒钟用于视觉检查
        root.after(5000, root.quit)
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ 可见性测试出现错误: {str(e)}")
        return False
    finally:
        try:
            root.destroy()
        except:
            pass


def main():
    """主测试函数"""
    print("开始分类按钮测试...")
    print("=" * 50)
    
    # 运行逻辑测试
    logic_test_passed = test_category_buttons()
    
    if logic_test_passed:
        print("\n✅ 逻辑测试通过！")
        
        # 询问是否运行可见性测试
        print("\n是否运行可见性测试（会显示窗口5秒）？(y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', '是', '']:
                visibility_test_passed = test_category_button_visibility()
                if visibility_test_passed:
                    print("✅ 可见性测试完成")
                else:
                    print("❌ 可见性测试失败")
        except (EOFError, KeyboardInterrupt):
            print("\n跳过可见性测试")
    else:
        print("\n❌ 逻辑测试失败")
    
    print("\n" + "=" * 50)
    print("测试完成")
    
    return logic_test_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)