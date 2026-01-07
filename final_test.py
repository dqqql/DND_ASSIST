#!/usr/bin/env python3
"""
最终测试 - 验证分类按钮修复
"""

import tkinter as tk
import os
from main import App, CATEGORIES, DATA_DIR

def final_test():
    """最终测试"""
    print("🔧 最终测试开始...")
    
    # 确保测试跑团存在
    test_campaign = "最终测试"
    test_path = os.path.join(DATA_DIR, test_campaign)
    os.makedirs(test_path, exist_ok=True)
    for folder in CATEGORIES.values():
        os.makedirs(os.path.join(test_path, folder), exist_ok=True)
    
    # 创建应用
    root = tk.Tk()
    root.title("最终测试 - DND跑团管理器")
    root.geometry("900x500")
    
    app = App(root)
    
    # 等待界面加载
    root.update_idletasks()
    
    print(f"📊 初始状态: 跑团数={app.campaign_list.size()}, 按钮数={len(app.category_buttons)}")
    
    # 手动选择跑团
    for i in range(app.campaign_list.size()):
        campaign_name = app.campaign_list.get(i)
        if campaign_name == test_campaign:
            print(f"🎯 选择跑团: {campaign_name}")
            app.campaign_list.selection_set(i)
            app.on_campaign_select(None)  # 直接调用方法
            break
    
    root.update_idletasks()
    
    print(f"📊 选择后状态: 当前跑团={app.current_campaign}, 按钮数={len(app.category_buttons)}")
    
    if len(app.category_buttons) == 4:
        print("🎉 成功！分类按钮正常显示")
        
        # 显示界面供用户确认
        status_label = tk.Label(root, text="✅ 修复成功！分类按钮应该可见", 
                               bg="lightgreen", fg="black", font=("Arial", 12, "bold"))
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        print("👀 请查看界面，分类按钮应该在右上角显示")
        print("⏰ 窗口将在8秒后自动关闭")
        
        root.after(8000, root.quit)
        root.mainloop()
    else:
        print("❌ 失败！分类按钮仍未显示")
        root.destroy()

if __name__ == "__main__":
    final_test()