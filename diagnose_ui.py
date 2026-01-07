#!/usr/bin/env python3
"""
UI问题诊断脚本
帮助诊断分类按钮不显示的问题
"""

import tkinter as tk
import os
import sys
from main import App, CATEGORIES, DATA_DIR

def diagnose_ui_issue():
    """诊断UI显示问题"""
    print("🔍 开始诊断UI问题...")
    print("=" * 50)
    
    # 检查数据目录
    print(f"1. 检查数据目录: {DATA_DIR}")
    if not os.path.exists(DATA_DIR):
        print("❌ 数据目录不存在，正在创建...")
        os.makedirs(DATA_DIR, exist_ok=True)
    else:
        print("✅ 数据目录存在")
    
    # 列出现有跑团
    campaigns = []
    if os.path.exists(DATA_DIR):
        campaigns = [name for name in os.listdir(DATA_DIR) 
                    if os.path.isdir(os.path.join(DATA_DIR, name))]
    
    print(f"2. 现有跑团数量: {len(campaigns)}")
    for campaign in campaigns:
        print(f"   - {campaign}")
    
    # 创建测试应用
    print("\n3. 创建测试应用...")
    root = tk.Tk()
    root.title("UI诊断 - DND跑团管理器")
    root.geometry("900x500")
    
    try:
        app = App(root)
        print("✅ 应用创建成功")
        
        # 检查关键组件
        print("\n4. 检查关键UI组件:")
        
        # 检查分类框架
        if hasattr(app, 'category_frame'):
            print("✅ 分类框架存在")
            children_count = len(app.category_frame.winfo_children())
            print(f"   分类框架子控件数量: {children_count}")
        else:
            print("❌ 分类框架不存在")
        
        # 检查分类按钮字典
        if hasattr(app, 'category_buttons'):
            print("✅ 分类按钮字典存在")
            print(f"   按钮数量: {len(app.category_buttons)}")
            for name, btn in app.category_buttons.items():
                print(f"   - {name}: {btn}")
        else:
            print("❌ 分类按钮字典不存在")
        
        # 检查当前跑团状态
        print(f"\n5. 当前状态:")
        print(f"   当前跑团: {getattr(app, 'current_campaign', 'None')}")
        print(f"   当前分类: {getattr(app, 'current_category', 'None')}")
        
        # 如果有跑团，尝试选择第一个
        if campaigns:
            print(f"\n6. 尝试选择跑团: {campaigns[0]}")
            
            # 清空并重新加载跑团列表
            app.load_campaigns()
            
            # 模拟选择第一个跑团
            if app.campaign_list.size() > 0:
                app.campaign_list.selection_set(0)
                app.current_campaign = campaigns[0]
                print(f"   设置当前跑团: {app.current_campaign}")
                
                # 手动调用show_categories
                print("   调用show_categories()...")
                app.show_categories()
                
                # 检查结果
                children_count = len(app.category_frame.winfo_children())
                button_count = len(app.category_buttons)
                print(f"   分类框架子控件数量: {children_count}")
                print(f"   分类按钮数量: {button_count}")
                
                if button_count == 4:
                    print("✅ 分类按钮创建成功！")
                    for name in CATEGORIES:
                        if name in app.category_buttons:
                            btn = app.category_buttons[name]
                            print(f"   ✅ {name}: 已创建，文本='{btn.cget('text')}'")
                        else:
                            print(f"   ❌ {name}: 未找到")
                else:
                    print(f"❌ 分类按钮数量不正确，期望4个，实际{button_count}个")
            else:
                print("❌ 跑团列表为空")
        else:
            print("\n6. 没有现有跑团，创建测试跑团...")
            
            # 创建测试跑团
            test_campaign = "诊断测试跑团"
            test_path = os.path.join(DATA_DIR, test_campaign)
            
            if not os.path.exists(test_path):
                os.makedirs(test_path)
                for folder in CATEGORIES.values():
                    os.makedirs(os.path.join(test_path, folder), exist_ok=True)
                print(f"✅ 创建测试跑团: {test_campaign}")
            
            # 重新加载并选择
            app.load_campaigns()
            if app.campaign_list.size() > 0:
                app.campaign_list.selection_set(0)
                app.current_campaign = test_campaign
                app.show_categories()
                
                children_count = len(app.category_frame.winfo_children())
                button_count = len(app.category_buttons)
                print(f"   分类框架子控件数量: {children_count}")
                print(f"   分类按钮数量: {button_count}")
        
        print("\n7. 启动可视化诊断窗口...")
        print("   请检查右侧是否显示了四个分类按钮")
        print("   窗口将在10秒后自动关闭，或手动关闭")
        
        # 添加诊断信息到窗口
        info_label = tk.Label(root, 
                             text=f"诊断信息：跑团={getattr(app, 'current_campaign', 'None')}, 按钮数={len(app.category_buttons)}",
                             bg="yellow", fg="black")
        info_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 10秒后自动关闭
        root.after(10000, root.quit)
        
        # 显示窗口
        root.mainloop()
        
    except Exception as e:
        print(f"❌ 应用创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            root.destroy()
        except:
            pass
    
    print("\n" + "=" * 50)
    print("🔍 诊断完成")

if __name__ == "__main__":
    diagnose_ui_issue()