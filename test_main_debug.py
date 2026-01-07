#!/usr/bin/env python3
"""
自动化测试main.py的分类按钮显示问题
"""

import tkinter as tk
import os
import sys
from main import App, CATEGORIES, DATA_DIR

def test_main_with_debug():
    """测试main.py并捕获调试信息"""
    print("🚀 启动main.py调试测试...")
    print("=" * 60)
    
    # 确保有测试数据
    test_campaign = "自动测试跑团"
    test_path = os.path.join(DATA_DIR, test_campaign)
    
    if not os.path.exists(test_path):
        print(f"📁 创建测试跑团: {test_campaign}")
        os.makedirs(test_path, exist_ok=True)
        for folder in CATEGORIES.values():
            os.makedirs(os.path.join(test_path, folder), exist_ok=True)
    
    # 创建应用
    root = tk.Tk()
    root.title("DEBUG - DND跑团管理器")
    root.geometry("900x500")
    
    try:
        print("🔧 创建App实例...")
        app = App(root)
        
        print("📋 初始状态检查:")
        print(f"   跑团列表大小: {app.campaign_list.size()}")
        print(f"   当前跑团: {app.current_campaign}")
        print(f"   分类按钮数量: {len(app.category_buttons)}")
        
        # 等待界面完全加载
        root.update_idletasks()
        
        print("\n🎯 模拟用户选择跑团...")
        
        # 查找测试跑团在列表中的位置
        campaign_index = -1
        for i in range(app.campaign_list.size()):
            if app.campaign_list.get(i) == test_campaign:
                campaign_index = i
                break
        
        if campaign_index >= 0:
            print(f"   找到测试跑团，索引: {campaign_index}")
            
            # 模拟点击选择
            app.campaign_list.selection_set(campaign_index)
            app.campaign_list.activate(campaign_index)
            
            # 手动触发选择事件
            print("   触发选择事件...")
            app.campaign_list.event_generate("<<ListboxSelect>>")
            
            # 等待事件处理
            root.update_idletasks()
            
            print("\n📊 选择后状态检查:")
            print(f"   当前跑团: {app.current_campaign}")
            print(f"   分类按钮数量: {len(app.category_buttons)}")
            print(f"   分类框架子控件数量: {len(app.category_frame.winfo_children())}")
            
            # 检查每个按钮
            for name in CATEGORIES:
                if name in app.category_buttons:
                    btn = app.category_buttons[name]
                    pack_info = btn.pack_info()
                    print(f"   ✅ {name}: 存在, pack={bool(pack_info)}, 可见={btn.winfo_viewable()}")
                else:
                    print(f"   ❌ {name}: 不存在")
            
            # 检查分类框架的几何信息
            root.update_idletasks()
            frame_width = app.category_frame.winfo_width()
            frame_height = app.category_frame.winfo_height()
            print(f"   分类框架尺寸: {frame_width}x{frame_height}")
            
            if len(app.category_buttons) == 4:
                print("\n🎉 成功！分类按钮已正确创建")
                
                # 测试按钮点击
                print("\n🖱️  测试按钮点击...")
                first_category = list(CATEGORIES.keys())[0]
                if first_category in app.category_buttons:
                    btn = app.category_buttons[first_category]
                    print(f"   点击按钮: {first_category}")
                    btn.invoke()
                    
                    print(f"   当前分类: {app.current_category}")
                    print(f"   操作按钮状态: {app.action_button.cget('state')}")
                    print(f"   操作按钮文本: {app.action_button.cget('text')}")
            else:
                print(f"\n❌ 失败！期望4个按钮，实际{len(app.category_buttons)}个")
        else:
            print(f"   ❌ 未找到测试跑团: {test_campaign}")
            print("   可用跑团:")
            for i in range(app.campaign_list.size()):
                print(f"     {i}: {app.campaign_list.get(i)}")
        
        print(f"\n⏰ 显示界面5秒钟供视觉检查...")
        
        # 添加状态信息到界面
        status_text = f"调试信息: 跑团={app.current_campaign}, 按钮={len(app.category_buttons)}/4"
        status_label = tk.Label(root, text=status_text, bg="lightblue", fg="black")
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 5秒后自动关闭
        root.after(5000, root.quit)
        root.mainloop()
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            root.destroy()
        except:
            pass
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")

if __name__ == "__main__":
    test_main_with_debug()