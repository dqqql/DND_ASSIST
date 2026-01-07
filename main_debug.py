#!/usr/bin/env python3
"""
调试版本的main.py - 添加调试信息来诊断分类按钮显示问题
"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import subprocess
import sys

# 导入主题系统
from theme_integration import (
    integrate_theme_with_app, create_themed_dialog, create_themed_dialog_content,
    show_themed_info, show_themed_error, show_themed_warning, ask_themed_yesno
)
from theme_utils import create_themed_button, add_interaction_feedback, create_enhanced_listbox, add_list_interaction_feedback
from theme_system import get_theme_manager

# ==================== 常量定义区域 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "campaigns")

CATEGORIES = {
    "人物卡": "characters",
    "怪物卡": "monsters",
    "地图": "maps",
    "剧情": "notes"
}

# 文件名非法字符
INVALID_FILENAME_CHARS = r'/\:*?"<>|'

# 图片预览最大尺寸
IMAGE_PREVIEW_MAX_WIDTH = 600
IMAGE_PREVIEW_MAX_HEIGHT = 600

# 隐藏文件列表文件名
HIDDEN_FILES_LIST = ".hidden_files"

# ==================== 常量定义结束 ====================


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def open_file_with_system(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform.startswith("darwin"):
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


class DebugApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DND 跑团管理器 (调试版)")
        self.root.geometry("900x500")

        ensure_dirs()

        self.current_campaign = None
        self.current_category = None
        self.category_buttons = {}
        self.current_notes_path = ""
        self.hidden_files = {}

        # 添加调试信息显示
        self.debug_frame = tk.Frame(self.root, bg='lightyellow', height=30)
        self.debug_frame.pack(side=tk.TOP, fill=tk.X)
        self.debug_frame.pack_propagate(False)
        
        self.debug_label = tk.Label(self.debug_frame, 
                                   text="调试信息: 启动完成", 
                                   bg='lightyellow', fg='darkblue')
        self.debug_label.pack(pady=5)

        self.build_ui()
        self.load_campaigns()
        
        # 应用主题系统到整个应用
        self.theme_integrator = integrate_theme_with_app(self)
        
        self.update_debug_info("应用初始化完成")

    def update_debug_info(self, message):
        """更新调试信息"""
        print(f"[DEBUG] {message}")
        self.debug_label.config(text=f"调试: {message}")
        self.root.update_idletasks()

    def build_ui(self):
        # 获取布局管理器和主题管理器
        from layout_system import get_layout_manager, get_component_spacing, get_grid_aligned_spacing
        layout_manager = get_layout_manager()
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()
        
        # 左侧面板
        left_panel_padding = get_component_spacing("window_edge")
        panel_spacing = get_component_spacing("panel")
        
        left = tk.Frame(self.root, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y, 
                 padx=(left_panel_padding, panel_spacing), 
                 pady=left_panel_padding)

        # 右侧面板
        right = tk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, 
                  padx=(panel_spacing, left_panel_padding), 
                  pady=left_panel_padding)

        # 跑团列表标题
        title_spacing = get_grid_aligned_spacing(8)
        tk.Label(left, text="跑团列表", 
                font=theme.typography.get_font_tuple(theme.typography.size_large, theme.typography.weight_bold)
                ).pack(pady=(0, title_spacing))

        # 跑团列表
        list_spacing = get_grid_aligned_spacing(8)
        self.campaign_list = create_enhanced_listbox(left, font=theme.typography.get_font_tuple(theme.typography.size_medium))
        self.campaign_list.pack(fill=tk.BOTH, expand=True, pady=(0, list_spacing))
        self.campaign_list.bind("<<ListboxSelect>>", self.on_campaign_select)

        # 按钮
        button_spacing = get_component_spacing("button_group") // 2
        
        create_campaign_btn = create_themed_button(left, text="新建跑团", command=self.create_campaign)
        create_campaign_btn.pack(fill=tk.X, pady=button_spacing)
        add_interaction_feedback(create_campaign_btn, "button")
        
        delete_campaign_btn = create_themed_button(left, text="删除跑团", command=self.delete_campaign)
        delete_campaign_btn.pack(fill=tk.X, pady=button_spacing)
        add_interaction_feedback(delete_campaign_btn, "button")

        # 顶部分类按钮区域
        section_spacing = get_component_spacing("section")
        top = tk.Frame(right)
        top.pack(fill=tk.X, pady=(0, section_spacing))

        # 分类按钮容器
        category_spacing = get_component_spacing("content")
        self.category_frame = tk.Frame(top, bg='lightgreen')  # 添加背景色便于调试
        self.category_frame.pack(side=tk.LEFT, padx=(0, category_spacing))

        # 操作按钮
        button_frame = tk.Frame(top)
        button_frame.pack(side=tk.RIGHT)
        
        action_button_spacing = get_component_spacing("button_group") // 2
        self.action_button = create_themed_button(button_frame, text="请选择分类", width=12, state=tk.DISABLED)
        self.action_button.pack(side=tk.LEFT, padx=action_button_spacing)
        add_interaction_feedback(self.action_button, "button")
        
        self.delete_button = create_themed_button(button_frame, text="删除文件", width=12, command=self.delete_file, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=action_button_spacing)
        add_interaction_feedback(self.delete_button, "button")
        
        back_button_spacing = get_component_spacing("panel")
        self.back_button = create_themed_button(top, text="返回上级", width=12, command=self.go_back_notes)
        add_interaction_feedback(self.back_button, "button")

        # 文件管理区域
        self.file_frame = tk.Frame(right)
        self.file_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧文件列表
        file_list_spacing = get_component_spacing("content")
        file_list_frame = tk.Frame(self.file_frame)
        file_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, file_list_spacing))

        self.file_list = create_enhanced_listbox(file_list_frame, width=30, 
                                               font=theme.typography.get_font_tuple(theme.typography.size_medium))
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_list.bind("<Double-Button-1>", self.open_selected_file)
        self.file_list.bind("<<ListboxSelect>>", self.on_file_select)

        scrollbar = tk.Scrollbar(file_list_frame, command=self.file_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.config(yscrollcommand=scrollbar.set)

        # 右侧内容查看器
        content_frame = tk.Frame(self.file_frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        content_title_spacing = get_grid_aligned_spacing(8)
        content_label = tk.Label(content_frame, text="文件内容", 
                               font=theme.typography.get_font_tuple(theme.typography.size_large, theme.typography.weight_bold))
        content_label.pack(anchor=tk.W, pady=(0, content_title_spacing))

        content_viewer_frame = tk.Frame(content_frame)
        theme_manager.apply_theme_to_widget(content_viewer_frame, "frame", "content_viewer")
        content_viewer_frame.pack(fill=tk.BOTH, expand=True)

        self.text_frame = tk.Frame(content_viewer_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        text_padding = get_grid_aligned_spacing(12)
        self.content_text = tk.Text(self.text_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                   padx=text_padding, pady=text_padding)
        theme_manager.apply_theme_to_widget(self.content_text, "text", "normal")
        self.content_text.config(padx=text_padding, pady=text_padding)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content_scrollbar = tk.Scrollbar(self.text_frame, command=self.content_text.yview)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=content_scrollbar.set)

        self.image_frame = tk.Frame(content_viewer_frame)
        self.image_label = tk.Label(self.image_frame, text="选择地图文件查看")
        theme_manager.apply_theme_to_widget(self.image_label, "content_image", "normal")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=text_padding, pady=text_padding)

    def load_campaigns(self):
        self.campaign_list.delete(0, tk.END)
        campaigns = []
        for name in os.listdir(DATA_DIR):
            if os.path.isdir(os.path.join(DATA_DIR, name)):
                self.campaign_list.insert(tk.END, name)
                campaigns.append(name)
        
        self.update_debug_info(f"加载了 {len(campaigns)} 个跑团: {campaigns}")

    def on_campaign_select(self, event):
        self.update_debug_info("跑团选择事件触发")
        
        sel = self.campaign_list.curselection()
        if not sel:
            self.update_debug_info("没有选择任何跑团")
            return
        
        self.current_campaign = self.campaign_list.get(sel[0])
        self.update_debug_info(f"选择了跑团: {self.current_campaign}")
        
        self.load_hidden_files()
        self.show_categories()

    def show_categories(self):
        self.update_debug_info("开始显示分类按钮")
        
        self.clear_categories()
        theme_manager = get_theme_manager()
        from layout_system import get_component_spacing
        
        category_button_spacing = get_component_spacing("category_button")
        self.update_debug_info(f"分类按钮间距: {category_button_spacing}px")
        
        button_count = 0
        for name in CATEGORIES:
            self.update_debug_info(f"创建分类按钮: {name}")
            
            btn = create_themed_button(
                self.category_frame,
                text=name,
                command=lambda n=name: self.select_category(n)
            )
            btn.pack(side=tk.LEFT, padx=category_button_spacing)
            add_interaction_feedback(btn, "button")
            self.category_buttons[name] = btn
            button_count += 1
        
        self.update_debug_info(f"创建了 {button_count} 个分类按钮")
        
        # 强制更新界面
        self.category_frame.update_idletasks()
        self.root.update_idletasks()

    def clear_categories(self):
        for w in self.category_frame.winfo_children():
            w.destroy()
        self.category_buttons.clear()
        self.update_debug_info("清除了所有分类按钮")

    def select_category(self, name):
        self.update_debug_info(f"选择了分类: {name}")
        
        theme_manager = get_theme_manager()
        
        for btn in self.category_buttons.values():
            theme_manager.apply_theme_to_widget(btn, "button", "normal")
        
        if name in self.category_buttons:
            theme_manager.apply_theme_to_widget(self.category_buttons[name], "button", "active")
        
        self.current_category = CATEGORIES[name]
        
        if self.current_category == "notes":
            self.current_notes_path = ""
        
        if self.current_category == "maps":
            self.action_button.config(text="导入文件", command=self.import_file, state=tk.NORMAL)
        else:
            self.action_button.config(text="新建文件", command=self.create_file, state=tk.NORMAL)
        
        self.delete_button.config(state=tk.NORMAL)
        self.update_back_button()
        self.load_files()

    # 其他方法保持不变，这里只是为了演示，实际使用时需要完整的方法
    def create_campaign(self):
        self.update_debug_info("点击了新建跑团")
        # 简化版本，实际使用时需要完整实现
        pass
    
    def delete_campaign(self):
        self.update_debug_info("点击了删除跑团")
        pass
    
    def import_file(self):
        pass
    
    def create_file(self):
        pass
    
    def delete_file(self):
        pass
    
    def go_back_notes(self):
        pass
    
    def update_back_button(self):
        pass
    
    def load_files(self):
        pass
    
    def load_hidden_files(self):
        pass
    
    def on_file_select(self, event):
        pass
    
    def open_selected_file(self, event):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = DebugApp(root)
    root.mainloop()