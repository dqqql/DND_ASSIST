#!/usr/bin/env python3
"""
测试列表框事件绑定
"""

import tkinter as tk
from theme_utils import create_enhanced_listbox

def test_listbox_events():
    """测试列表框事件是否正常工作"""
    
    root = tk.Tk()
    root.title("列表框事件测试")
    root.geometry("400x300")
    
    # 创建测试框架
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 标题
    tk.Label(frame, text="请点击列表项测试事件", font=("Arial", 12, "bold")).pack(pady=(0, 10))
    
    # 事件计数器
    event_count = {"count": 0}
    
    def on_select(event):
        event_count["count"] += 1
        sel = listbox.curselection()
        if sel:
            selected_item = listbox.get(sel[0])
            result_label.config(text=f"选择了: {selected_item} (事件触发次数: {event_count['count']})")
            print(f"选择事件触发: {selected_item}")
        else:
            result_label.config(text=f"取消选择 (事件触发次数: {event_count['count']})")
            print("取消选择")
    
    # 创建增强列表框
    listbox = create_enhanced_listbox(frame)
    listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # 绑定选择事件
    listbox.bind("<<ListboxSelect>>", on_select)
    
    # 添加测试数据
    test_items = ["测试跑团1", "测试跑团2", "矿坑探险", "城市迷雾"]
    for item in test_items:
        listbox.insert(tk.END, item)
    
    # 结果显示
    result_label = tk.Label(frame, text="请选择一个列表项", fg="blue")
    result_label.pack()
    
    # 测试按钮
    def manual_select():
        listbox.selection_set(0)
        listbox.event_generate("<<ListboxSelect>>")
    
    test_btn = tk.Button(frame, text="手动选择第一项", command=manual_select)
    test_btn.pack(pady=10)
    
    print("列表框事件测试启动")
    print("请点击列表项或使用测试按钮")
    
    root.mainloop()

if __name__ == "__main__":
    test_listbox_events()