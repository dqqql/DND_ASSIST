import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import subprocess
import sys
import json

# 导入主题系统
from src.ui.theme_integration import (
    integrate_theme_with_app, create_themed_dialog, create_themed_dialog_content,
    show_themed_info, show_themed_error, show_themed_warning, ask_themed_yesno
)
from src.ui.theme_utils import (
    create_themed_button, add_interaction_feedback, create_enhanced_listbox, add_list_interaction_feedback,
    apply_enhanced_interaction_feedback, enhance_category_button_feedback, update_category_button_states
)
from src.ui.theme_system import get_theme_manager

# ==================== 常量定义区域 ====================
# Prompt 2: 所有路径和分类相关的常量集中在文件顶部

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "campaigns")

CATEGORIES = {
    "人物卡": "characters",
    "怪物卡": "monsters",
    "地图": "maps",
    "剧情": "notes"
}

# 文件名非法字符（Prompt 9）
INVALID_FILENAME_CHARS = r'/\:*?"<>|'

# 图片预览最大尺寸（Prompt 6）
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


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DND 跑团管理器")
        self.root.geometry("1170x650")

        ensure_dirs()

        self.current_campaign = None
        self.current_category = None
        self.category_buttons = {}  # 存储分类按钮
        self.category_handlers = {}  # 存储分类按钮的交互处理器
        self.current_notes_path = ""  # Prompt 5: notes 当前路径（相对于 notes 根目录）
        self.hidden_files = {}  # 存储每个跑团分类的隐藏文件列表

        self.build_ui()
        self.load_campaigns()
        
        # 应用主题系统到整个应用
        self.theme_integrator = integrate_theme_with_app(self)
        
        # 应用增强的交互反馈到所有控件
        self._apply_enhanced_feedback()
        
        # 应用视觉元素优化
        self._apply_visual_enhancements()
        
        # 确保视觉一致性
        self._enhance_visual_consistency()

    def build_ui(self):
        # 获取布局管理器和主题管理器
        from src.ui.layout_system import get_layout_manager, get_component_spacing, get_grid_aligned_spacing
        layout_manager = get_layout_manager()
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()
        
        # 左侧面板 - 使用网格对齐的内边距
        left_panel_padding = get_component_spacing("window_edge")
        panel_spacing = get_component_spacing("panel")
        
        left = tk.Frame(self.root, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y, 
                 padx=(left_panel_padding, panel_spacing), 
                 pady=left_panel_padding)

        # 右侧面板 - 使用网格对齐的内边距
        right = tk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, 
                  padx=(panel_spacing, left_panel_padding), 
                  pady=left_panel_padding)

        # 跑团列表标题 - 改进字体和间距，使用网格对齐
        title_spacing = get_grid_aligned_spacing(8)
        tk.Label(left, text="跑团列表", 
                font=theme.typography.get_font_tuple(theme.typography.size_large, theme.typography.weight_bold)
                ).pack(pady=(0, title_spacing))

        # 跑团列表 - 使用增强的列表控件和网格对齐间距
        list_spacing = get_grid_aligned_spacing(8)
        self.campaign_list = create_enhanced_listbox(left, font=theme.typography.get_font_tuple(theme.typography.size_medium))
        self.campaign_list.pack(fill=tk.BOTH, expand=True, pady=(0, list_spacing))
        self.campaign_list.bind("<<ListboxSelect>>", self.on_campaign_select)

        # 按钮样式优化 - 使用主题化按钮，统一字体、间距和大小，网格对齐间距
        button_spacing = get_component_spacing("button_group") // 2
        
        create_campaign_btn = create_themed_button(left, text="新建跑团", command=self.create_campaign)
        create_campaign_btn.pack(fill=tk.X, pady=button_spacing)
        
        delete_campaign_btn = create_themed_button(left, text="删除跑团", command=self.delete_campaign)
        delete_campaign_btn.pack(fill=tk.X, pady=button_spacing)

        # 顶部分类按钮区域 - 使用网格对齐的内边距
        section_spacing = get_component_spacing("section")
        top = tk.Frame(right)
        top.pack(fill=tk.X, pady=(0, section_spacing))

        # 分类按钮容器 - 改进间距
        category_spacing = get_component_spacing("content")
        self.category_frame = tk.Frame(top)
        self.category_frame.pack(side=tk.LEFT, padx=(0, category_spacing))

        # 操作按钮放在右上角 - 使用主题化按钮和网格对齐间距
        button_frame = tk.Frame(top)
        button_frame.pack(side=tk.RIGHT)
        
        action_button_spacing = get_component_spacing("button_group") // 2
        self.action_button = create_themed_button(button_frame, text="请选择分类", width=12, state=tk.DISABLED)
        self.action_button.pack(side=tk.LEFT, padx=action_button_spacing)
        
        # 删除按钮
        self.delete_button = create_themed_button(button_frame, text="删除文件", width=12, command=self.delete_file, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=action_button_spacing)
        
        # 返回上级按钮（仅在 notes 分类显示）- 使用主题化按钮和网格对齐间距
        back_button_spacing = get_component_spacing("panel")
        self.back_button = create_themed_button(top, text="返回上级", width=12, command=self.go_back_notes)
        # 初始不显示

        # 文件管理区域 - 改进布局和间距，使用网格对齐
        self.file_frame = tk.Frame(right)
        self.file_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧文件列表 - 优化间距和字体，使用网格对齐
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

        # 右侧内容查看器 - 改进标题和布局，使用网格对齐间距
        content_frame = tk.Frame(self.file_frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        content_title_spacing = get_grid_aligned_spacing(8)
        content_label = tk.Label(content_frame, text="文件内容", 
                               font=theme.typography.get_font_tuple(theme.typography.size_large, theme.typography.weight_bold))
        content_label.pack(anchor=tk.W, pady=(0, content_title_spacing))

        # 内容查看器容器 - 使用主题化样式和改进的边框
        content_viewer_frame = tk.Frame(content_frame)
        theme_manager.apply_theme_to_widget(content_viewer_frame, "frame", "content_viewer")
        content_viewer_frame.pack(fill=tk.BOTH, expand=True)

        # 文本显示区域 - 改进字体、背景和行间距，使用主题颜色
        self.text_frame = tk.Frame(content_viewer_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        # 使用网格对齐的内边距和改进的文本样式
        text_padding = get_grid_aligned_spacing(12)  # 增加内边距以提升可读性
        self.content_text = tk.Text(self.text_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                   padx=text_padding, pady=text_padding)
        # 应用主题样式
        theme_manager.apply_theme_to_widget(self.content_text, "text", "normal")
        # 重新设置内边距，确保不被主题覆盖
        self.content_text.config(padx=text_padding, pady=text_padding)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content_scrollbar = tk.Scrollbar(self.text_frame, command=self.content_text.yview)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=content_scrollbar.set)

        # 图片显示区域（初始隐藏）- 改进样式，使用主题颜色和一致的边框
        self.image_frame = tk.Frame(content_viewer_frame)
        self.image_label = tk.Label(self.image_frame, text="选择地图文件查看")
        # 应用主题样式
        theme_manager.apply_theme_to_widget(self.image_label, "content_image", "normal")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=text_padding, pady=text_padding)

    def load_campaigns(self):
        self.campaign_list.delete(0, tk.END)
        for name in os.listdir(DATA_DIR):
            if os.path.isdir(os.path.join(DATA_DIR, name)):
                self.campaign_list.insert(tk.END, name)

    def create_campaign(self):
        # 创建主题化对话框
        dialog = create_themed_dialog(self.root, "新建跑团", "450x180")
        
        # 创建主题化对话框内容
        main_frame, entry, ok_button, cancel_button = create_themed_dialog_content(
            dialog, "请输入跑团名称:", 35
        )
        
        result = {"name": None}
        
        def on_ok():
            result["name"] = entry.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # 配置按钮命令
        ok_button.config(command=on_ok)
        cancel_button.config(command=on_cancel)
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: on_ok())
        
        dialog.wait_window()
        
        name = result["name"]
        if not name:
            return
        path = os.path.join(DATA_DIR, name)
        if os.path.exists(path):
            show_themed_error(self.root, "错误", "跑团已存在")
            return

        os.makedirs(path)
        for folder in CATEGORIES.values():
            os.makedirs(os.path.join(path, folder))

        self.load_campaigns()

    def delete_campaign(self):
        sel = self.campaign_list.curselection()
        if not sel:
            return
        name = self.campaign_list.get(sel[0])
        path = os.path.join(DATA_DIR, name)
        if ask_themed_yesno(self.root, "确认", f"确定删除跑团【{name}】？"):
            shutil.rmtree(path)
            self.current_campaign = None
            self.clear_categories()
            self.file_list.delete(0, tk.END)
            self.load_campaigns()

    def on_campaign_select(self, event):
        sel = self.campaign_list.curselection()
        if not sel:
            return
        self.current_campaign = self.campaign_list.get(sel[0])
        self.load_hidden_files()  # 加载隐藏文件列表
        self.show_categories()

    def clear_categories(self):
        for w in self.category_frame.winfo_children():
            w.destroy()
        self.category_buttons.clear()

    def show_categories(self):
        self.clear_categories()
        theme_manager = get_theme_manager()
        from src.ui.layout_system import get_component_spacing
        
        # 获取分类按钮间距
        category_button_spacing = get_component_spacing("category_button")
        
        for name in CATEGORIES:
            btn = create_themed_button(
                self.category_frame,
                text=name,
                command=lambda n=name: self.select_category(n)
            )
            btn.pack(side=tk.LEFT, padx=category_button_spacing)
            self.category_buttons[name] = btn
        
        # 为分类按钮添加增强的交互反馈
        self.category_handlers = enhance_category_button_feedback(self.category_buttons)

    def select_category(self, name):
        self.current_category = CATEGORIES[name]
        
        # 更新分类按钮的激活状态
        if self.category_handlers:
            update_category_button_states(self.category_handlers, name)
        
        # Prompt 5: 重置 notes 路径
        if self.current_category == "notes":
            self.current_notes_path = ""
        
        # 根据分类设置操作按钮
        if self.current_category == "maps":
            self.action_button.config(text="导入文件", command=self.import_file, state=tk.NORMAL)
        else:
            self.action_button.config(text="新建文件", command=self.create_file, state=tk.NORMAL)
        
        # 启用删除按钮
        self.delete_button.config(state=tk.NORMAL)
        
        # Prompt 5: 显示或隐藏返回上级按钮
        self.update_back_button()
        
        self.load_files()
    
    def _apply_enhanced_feedback(self):
        """为整个应用添加增强的交互反馈"""
        # 为根窗口的所有控件添加交互反馈
        apply_enhanced_interaction_feedback(self.root)
        
        # 确保所有现有的按钮都有正确的交互反馈
        self._ensure_button_feedback()
    
    def _ensure_button_feedback(self):
        """确保所有按钮都有正确的交互反馈"""
        # 这个方法会在UI构建完成后调用，确保所有按钮都有交互反馈
        # 由于apply_enhanced_interaction_feedback已经递归处理了所有控件，
        # 这里主要是作为备用确保机制
        pass
    
    def _apply_visual_enhancements(self):
        """应用视觉元素优化 - 添加微妙的视觉增强"""
        # 简化版视觉增强，直接在这里实现
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()
        
        # 确保主窗口背景色正确
        if hasattr(self, 'root'):
            self.root.configure(bg=theme.colors.primary_bg)
        
        # 增强内容查看器的边界
        if hasattr(self, 'content_text'):
            try:
                self.content_text.configure(
                    relief=tk.SUNKEN,
                    bd=2,
                    highlightthickness=1,
                    highlightcolor=theme.colors.border_color,
                    highlightbackground=theme.colors.border_color
                )
            except tk.TclError:
                pass
        
        # 增强图片显示区域的边界
        if hasattr(self, 'image_label'):
            try:
                self.image_label.configure(
                    relief=tk.SUNKEN,
                    bd=2,
                    highlightthickness=1,
                    highlightcolor=theme.colors.border_color,
                    highlightbackground=theme.colors.border_color
                )
            except tk.TclError:
                pass

    
    def _enhance_visual_consistency(self):
        """增强视觉一致性 - 确保所有元素遵循统一的视觉语言"""
        # 简化版视觉一致性增强，直接在这里实现
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()
        
        def apply_consistent_theming(widget):
            try:
                widget_class = widget.__class__.__name__
                
                if widget_class == "Frame":
                    widget.configure(bg=theme.colors.primary_bg)
                elif widget_class == "Label":
                    widget.configure(
                        bg=theme.colors.primary_bg,
                        fg=theme.colors.text_primary
                    )
                
                for child in widget.winfo_children():
                    apply_consistent_theming(child)
            except tk.TclError:
                pass
        
        if hasattr(self, 'root'):
            apply_consistent_theming(self.root)

    def load_files(self):
        """Prompt 3: 文件列表按文件名升序排序
           Prompt 4: notes 支持子文件夹，文件夹显示在前"""
        self.file_list.delete(0, tk.END)
        self.clear_content_viewer()
        if not self.current_campaign or not self.current_category:
            return
        
        base_path = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        current_path = os.path.join(base_path, self.current_notes_path) if self.current_category == "notes" else base_path
        
        if not os.path.exists(current_path):
            return
        
        items = os.listdir(current_path)
        
        # 获取当前路径的隐藏文件列表
        hidden_key = f"{self.current_category}:{self.current_notes_path}" if self.current_category == "notes" else self.current_category
        hidden_set = self.hidden_files.get(hidden_key, set())
        
        # Prompt 4: notes 分类支持子文件夹
        if self.current_category == "notes":
            folders = []
            files = []
            for item in items:
                # 跳过隐藏的文件和文件夹
                if item in hidden_set:
                    continue
                    
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    folders.append(item)
                else:
                    # 只显示 .txt 和 .json 文件，过滤掉 .dot 和 .svg 文件
                    if item.lower().endswith(('.txt', '.json')):
                        files.append(item)
            
            # Prompt 3: 排序
            folders.sort()
            files.sort()
            
            # Prompt 4: 文件夹显示在前，格式为 "[DIR] 文件夹名"
            for folder in folders:
                self.file_list.insert(tk.END, f"[DIR] {folder}")
            for file in files:
                self.file_list.insert(tk.END, file)
        else:
            # 其他分类只显示文件，按文件名排序，过滤隐藏文件
            visible_items = [item for item in items if item not in hidden_set]
            visible_items.sort()
            for item in visible_items:
                self.file_list.insert(tk.END, item)

    def import_file(self):
        if not self.current_campaign or not self.current_category:
            return
        files = filedialog.askopenfilenames()
        if not files:
            return
        target_dir = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        for f in files:
            shutil.copy(f, target_dir)
        self.load_files()

    def get_template_content(self, category):
        """根据分类返回模板内容，如果不需要模板则返回空字符串"""
        if category == "characters":
            return "姓名: \n\n种族: \n\n职业: \n\n技能: \n\n装备: \n\n背景: \n\n"
        elif category == "monsters":
            return "姓名: \n\nCR: \n\n属性: \n\n攻击: \n\n特性: 无\n\n"
        return ""

    def select_file_type(self):
        """在notes分类中选择文件类型"""
        # 创建文件类型选择对话框
        dialog = create_themed_dialog(self.root, "选择文件类型", "400x200")
        
        # 创建主框架
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 提示标签
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()
        
        label = tk.Label(main_frame, text="请选择要创建的文件类型:", 
                        font=theme.typography.get_font_tuple(theme.typography.size_medium))
        theme_manager.apply_theme_to_widget(label, "label", "normal")
        label.pack(pady=(0, 15))
        
        result = {"file_type": None}
        
        def select_txt():
            result["file_type"] = "txt"
            dialog.destroy()
        
        def select_json():
            result["file_type"] = "json"
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # 按钮框架
        button_frame = tk.Frame(main_frame)
        theme_manager.apply_theme_to_widget(button_frame, "frame", "normal")
        button_frame.pack(pady=10)
        
        # 文件类型按钮
        txt_button = create_themed_button(button_frame, text="普通剧情 (.txt)", command=select_txt, width=15)
        txt_button.pack(pady=5)
        
        json_button = create_themed_button(button_frame, text="结构化剧情 (.json)", command=select_json, width=15)
        json_button.pack(pady=5)
        
        # 取消按钮
        cancel_button = create_themed_button(button_frame, text="取消", command=on_cancel, width=15)
        cancel_button.pack(pady=(10, 0))
        
        dialog.wait_window()
        
        return result["file_type"]

    def get_json_story_template(self):
        """生成JSON剧情文件模板"""
        import json
        
        template = {
            "title": "新剧情",
            "nodes": [
                {
                    "id": "main_01",
                    "type": "main",
                    "title": "开始",
                    "content": "你们的冒险从这里开始...",
                    "next": "main_02",
                    "branches": [
                        {
                            "choice": "选择路径A",
                            "entry": "branch_A_01",
                            "exit": "main_02"
                        },
                        {
                            "choice": "选择路径B", 
                            "entry": "branch_B_01",
                            "exit": "main_02"
                        }
                    ]
                },
                {
                    "id": "main_02",
                    "type": "main",
                    "title": "汇合点",
                    "content": "无论选择哪条路径，你们都来到了这里...",
                    "next": None,
                    "branches": []
                },
                {
                    "id": "branch_A_01",
                    "type": "branch",
                    "title": "路径A - 第一步",
                    "content": "你们选择了路径A，遇到了...",
                    "next": None
                },
                {
                    "id": "branch_B_01", 
                    "type": "branch",
                    "title": "路径B - 第一步",
                    "content": "你们选择了路径B，发现了...",
                    "next": None
                }
            ]
        }
        
        return json.dumps(template, ensure_ascii=False, indent=2)

    def create_file(self):
        if not self.current_campaign or not self.current_category:
            return
        
        # 如果是notes分类，先选择文件类型
        if self.current_category == "notes":
            file_type = self.select_file_type()
            if not file_type:
                return
        else:
            file_type = "txt"
        
        # 创建主题化对话框
        dialog = create_themed_dialog(self.root, "新建文件", "450x180")
        
        # 创建主题化对话框内容
        main_frame, entry, ok_button, cancel_button = create_themed_dialog_content(
            dialog, "请输入文件名（不需要扩展名）:", 35
        )
        
        result = {"filename": None}
        
        def on_ok():
            result["filename"] = entry.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # 配置按钮命令
        ok_button.config(command=on_ok)
        cancel_button.config(command=on_cancel)
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: on_ok())
        
        dialog.wait_window()
        
        filename = result["filename"]
        if not filename:
            return
        
        # Prompt 9: 文件名合法性检查
        for char in INVALID_FILENAME_CHARS:
            if char in filename:
                show_themed_error(self.root, "错误", f"文件名不能包含以下字符: {INVALID_FILENAME_CHARS}")
                return
        
        # 根据文件类型添加扩展名
        if file_type == "json":
            filename = filename + ".json"
        else:
            filename = filename + ".txt"
        
        base_dir = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        target_dir = os.path.join(base_dir, self.current_notes_path) if self.current_category == "notes" else base_dir
        file_path = os.path.join(target_dir, filename)
        
        if os.path.exists(file_path):
            show_themed_error(self.root, "错误", "文件已存在")
            return
        
        # 获取模板内容并创建文件
        if file_type == "json":
            template_content = self.get_json_story_template()
        else:
            template_content = self.get_template_content(self.current_category)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        self.load_files()
        # 创建后自动打开文件
        open_file_with_system(file_path)

    def on_file_select(self, event):
        """文件列表选择事件处理
           Prompt 5: notes 分类支持双击文件夹进入"""
        sel = self.file_list.curselection()
        if not sel:
            self.clear_content_viewer()
            return
        
        display_name = self.file_list.get(sel[0])
        
        # Prompt 4 & 5: 处理 notes 文件夹
        if self.current_category == "notes" and display_name.startswith("[DIR] "):
            # 文件夹不显示内容
            self.clear_content_viewer()
            return
        
        filename = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
        
        base_path = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        current_path = os.path.join(base_path, self.current_notes_path) if self.current_category == "notes" else base_path
        file_path = os.path.join(current_path, filename)

        # 如果是文本文件，显示内容
        if self.current_category in ["characters", "monsters", "notes"] and filename.endswith('.txt'):
            self.show_text_content(file_path)
        # 如果是JSON剧情文件，显示结构化内容
        elif self.current_category == "notes" and filename.endswith('.json'):
            self.show_json_story_content(file_path)
        # 如果是地图文件，显示图片
        elif self.current_category == "maps":
            self.show_image_content(file_path)
        else:
            self.clear_content_viewer()

    def show_text_content(self, file_path):
        """显示文本文件内容
           Prompt 7: 每次从磁盘重新读取
           Prompt 8: 错误处理不弹窗"""
        try:
            # Prompt 7: 每次从磁盘重新读取，不使用缓存
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 显示文本区域，隐藏图片区域
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.image_frame.pack_forget()
            
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, content)
            self.content_text.config(state=tk.DISABLED)
        except Exception as e:
            # Prompt 8: 错误信息显示在文本区域，不弹窗
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.image_frame.pack_forget()
            
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, f"无法读取文件: {str(e)}")
            self.content_text.config(state=tk.DISABLED)

    def show_json_story_content(self, file_path):
        """显示JSON剧情文件的统计信息"""
        try:
            # 从磁盘重新读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析JSON内容
            story_data = json.loads(content)
            
            # 构建统计信息显示文本
            display_text = self._build_story_statistics(story_data, file_path)
            
            # 显示文本区域，隐藏图片区域
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.image_frame.pack_forget()
            
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, display_text)
            self.content_text.config(state=tk.DISABLED)
            
        except json.JSONDecodeError as e:
            # JSON格式错误处理
            error_msg = f"JSON格式错误: {str(e)}\n\n"
            error_msg += "常见问题和解决方案:\n"
            error_msg += "• 检查是否有多余的逗号\n"
            error_msg += "• 确保所有字符串都用双引号包围\n"
            error_msg += "• 检查括号和大括号是否匹配\n"
            error_msg += "• 确保最后一个元素后没有逗号\n\n"
            error_msg += "建议使用JSON格式验证工具检查文件格式。"
            self._show_json_error(error_msg)
        except FileNotFoundError:
            self._show_json_error("文件不存在，请检查文件路径。")
        except PermissionError:
            self._show_json_error("没有权限读取文件，请检查文件权限。")
        except UnicodeDecodeError:
            self._show_json_error("文件编码错误，请确保文件使用UTF-8编码保存。")
        except Exception as e:
            # 其他错误处理
            self._show_json_error(f"无法读取文件: {str(e)}\n\n请检查文件是否损坏或格式是否正确。")
    
    def _build_story_statistics(self, story_data, file_path):
        """构建剧情统计信息"""
        lines = []
        
        # 文件基本信息
        filename = os.path.basename(file_path)
        lines.append("=" * 50)
        lines.append(f"剧情文件: {filename}")
        lines.append("=" * 50)
        lines.append("")
        
        # 剧情标题
        title = story_data.get("title", "未命名剧情").strip()
        lines.append(f"📖 剧情标题: {title}")
        lines.append("")
        
        # 获取所有节点
        nodes = story_data.get("nodes", [])
        
        if not nodes:
            lines.append("⚠️  警告: 剧情中没有找到任何节点")
            return "\n".join(lines)
        
        # 统计不同类型的节点
        main_nodes = [node for node in nodes if node.get("type") == "main"]
        branch_nodes = [node for node in nodes if node.get("type") == "branch"]
        other_nodes = [node for node in nodes if node.get("type") not in ["main", "branch"]]
        
        # 基本统计
        lines.append("📊 基本统计:")
        lines.append(f"   • 节点总数: {len(nodes)}")
        lines.append(f"   • 主线节点: {len(main_nodes)}")
        lines.append(f"   • 分支节点: {len(branch_nodes)}")
        if other_nodes:
            lines.append(f"   • 其他节点: {len(other_nodes)}")
        lines.append("")
        
        # 分支统计
        total_branches = 0
        nodes_with_branches = 0
        for node in main_nodes:
            branches = node.get("branches", [])
            if branches:
                nodes_with_branches += 1
                total_branches += len(branches)
        
        lines.append("🌿 分支统计:")
        lines.append(f"   • 总分支数: {total_branches}")
        lines.append(f"   • 有分支的主线节点: {nodes_with_branches}")
        if nodes_with_branches > 0:
            avg_branches = total_branches / nodes_with_branches
            lines.append(f"   • 平均每个分支点的选择数: {avg_branches:.1f}")
        lines.append("")
        
        # 内容完整性检查
        lines.append("✅ 内容完整性:")
        
        # 检查空标题和空内容
        empty_title_count = 0
        empty_content_count = 0
        meaningful_nodes = 0
        
        for node in nodes:
            title = node.get("title", "").strip()
            content = node.get("content", "").strip()
            
            if not title or title in ["新节点", "未命名节点", "未命名"]:
                empty_title_count += 1
            if not content:
                empty_content_count += 1
            
            # 判断是否是有意义的节点
            if title and title not in ["新节点", "未命名节点", "未命名"]:
                meaningful_nodes += 1
        
        lines.append(f"   • 有意义的节点: {meaningful_nodes}/{len(nodes)}")
        if empty_title_count > 0:
            lines.append(f"   • 空标题节点: {empty_title_count}")
        if empty_content_count > 0:
            lines.append(f"   • 空内容节点: {empty_content_count}")
        
        # 连接性检查
        connected_nodes = set()
        orphaned_nodes = []
        
        # 找到所有被引用的节点
        for node in nodes:
            next_id = node.get("next")
            if next_id:
                connected_nodes.add(next_id)
            
            for branch in node.get("branches", []):
                entry_id = branch.get("entry")
                exit_id = branch.get("exit")
                if entry_id:
                    connected_nodes.add(entry_id)
                if exit_id:
                    connected_nodes.add(exit_id)
        
        # 找到孤立节点（除了第一个节点）
        node_ids = [node.get("id") for node in nodes if node.get("id")]
        if node_ids:
            first_node_id = node_ids[0]  # 假设第一个节点是起始节点
            for node_id in node_ids[1:]:  # 跳过第一个节点
                if node_id not in connected_nodes:
                    orphaned_nodes.append(node_id)
        
        if orphaned_nodes:
            lines.append(f"   • 孤立节点: {len(orphaned_nodes)} ({', '.join(orphaned_nodes[:3])}{'...' if len(orphaned_nodes) > 3 else ''})")
        else:
            lines.append("   • 所有节点都已连接")
        
        lines.append("")
        
        # 主线节点列表
        if main_nodes:
            lines.append("🎯 主线流程:")
            for i, node in enumerate(main_nodes[:5], 1):  # 只显示前5个
                title = node.get("title", "未命名")
                node_id = node.get("id", "")
                branches_count = len(node.get("branches", []))
                
                branch_info = f" ({branches_count}个选择)" if branches_count > 0 else ""
                lines.append(f"   {i}. {title} [{node_id}]{branch_info}")
            
            if len(main_nodes) > 5:
                lines.append(f"   ... 还有 {len(main_nodes) - 5} 个主线节点")
            lines.append("")
        
        # 检查是否有对应的SVG文件
        svg_path = self._get_svg_path_for_json(file_path)
        if svg_path and os.path.exists(svg_path):
            lines.append("")
            lines.append("📈 流程图: 已生成，可双击文件名在外部查看")
        
        return "\n".join(lines)
    
    def _get_svg_path_for_json(self, json_file_path):
        """根据JSON文件路径查找对应的SVG文件路径"""
        try:
            # 获取文件名（不含扩展名）
            filename = os.path.basename(json_file_path)
            filename_without_ext = os.path.splitext(filename)[0]
            
            # 在当前跑团的notes文件夹中查找对应的SVG文件
            notes_dir = os.path.join(DATA_DIR, self.current_campaign, "notes")
            
            if not os.path.exists(notes_dir):
                return None
            
            # 直接在notes目录中查找SVG文件
            svg_path = os.path.join(notes_dir, f"{filename_without_ext}.svg")
            if os.path.exists(svg_path):
                return svg_path
            
            return None
        except Exception:
            return None
    
    def _show_json_error(self, error_message):
        """显示JSON错误信息"""
        # 显示文本区域，隐藏图片区域
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        self.image_frame.pack_forget()
        
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, error_message)
        self.content_text.config(state=tk.DISABLED)

    def show_image_content(self, file_path):
        """在右侧显示图片内容
           Prompt 6: 按右侧显示区域大小自适应缩放，保持宽高比"""
        try:
            # 隐藏文本区域，显示图片区域
            self.text_frame.pack_forget()
            self.image_frame.pack(fill=tk.BOTH, expand=True)
            
            # 强制更新以获取实际显示区域大小
            self.image_frame.update_idletasks()
            
            # Prompt 6: 获取右侧显示区域的实际大小
            frame_width = self.image_frame.winfo_width()
            frame_height = self.image_frame.winfo_height()
            
            # 如果窗口还没有完全渲染，使用默认值
            if frame_width <= 1:
                frame_width = IMAGE_PREVIEW_MAX_WIDTH
            if frame_height <= 1:
                frame_height = IMAGE_PREVIEW_MAX_HEIGHT
            
            img = Image.open(file_path)
            
            # Prompt 6: 按显示区域大小自适应缩放，保持宽高比
            img.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
            
            # 确保图片标签保持主题样式
            theme_manager = get_theme_manager()
            theme_manager.apply_theme_to_widget(self.image_label, "content_image", "normal")
            
        except Exception as e:
            self.image_label.config(image="", text=f"无法显示图片: {str(e)}")
            # 重新应用主题样式
            theme_manager = get_theme_manager()
            theme_manager.apply_theme_to_widget(self.image_label, "content_image", "normal")



    def clear_content_viewer(self):
        """清空内容查看器"""
        # 显示文本区域，隐藏图片区域
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        self.image_frame.pack_forget()
        
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.config(state=tk.DISABLED)
        
        # 清除图片并重新应用主题样式
        self.image_label.config(image="", text="选择地图文件查看")
        theme_manager = get_theme_manager()
        theme_manager.apply_theme_to_widget(self.image_label, "content_image", "normal")

    def open_selected_file(self, event):
        """Prompt 5: 双击文件打开，notes 分类双击文件夹进入"""
        sel = self.file_list.curselection()
        if not sel:
            return
        
        display_name = self.file_list.get(sel[0])
        
        # Prompt 5: notes 分类双击文件夹进入
        if self.current_category == "notes" and display_name.startswith("[DIR] "):
            folder_name = display_name.replace("[DIR] ", "")
            self.enter_notes_folder(folder_name)
            return
        
        filename = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
        
        base_path = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        current_path = os.path.join(base_path, self.current_notes_path) if self.current_category == "notes" else base_path
        path = os.path.join(current_path, filename)
        
        open_file_with_system(path)
    
    def enter_notes_folder(self, folder_name):
        """Prompt 5: 进入 notes 子文件夹"""
        if self.current_notes_path:
            self.current_notes_path = os.path.join(self.current_notes_path, folder_name)
        else:
            self.current_notes_path = folder_name
        
        self.update_back_button()
        self.load_files()
    
    def go_back_notes(self):
        """Prompt 5: 返回 notes 上级目录"""
        if not self.current_notes_path:
            return
        
        # 返回上级目录
        parent = os.path.dirname(self.current_notes_path)
        self.current_notes_path = parent
        
        self.update_back_button()
        self.load_files()
    
    def update_back_button(self):
        """Prompt 5: 更新返回上级按钮的显示状态"""
        from src.ui.layout_system import get_component_spacing
        
        if self.current_category == "notes" and self.current_notes_path:
            # 在 notes 分类且不在根目录时显示，使用网格对齐的间距
            back_button_spacing = get_component_spacing("panel")
            self.back_button.pack(side=tk.RIGHT, padx=(0, back_button_spacing))
        else:
            # 其他情况隐藏
            self.back_button.pack_forget()
    
    def load_hidden_files(self):
        """加载当前跑团的隐藏文件列表"""
        if not self.current_campaign:
            return
        
        hidden_file_path = os.path.join(DATA_DIR, self.current_campaign, HIDDEN_FILES_LIST)
        self.hidden_files = {}
        
        if os.path.exists(hidden_file_path):
            try:
                with open(hidden_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and ':' in line:
                            key, filename = line.split(':', 1)
                            if key not in self.hidden_files:
                                self.hidden_files[key] = set()
                            self.hidden_files[key].add(filename)
            except Exception:
                # 如果读取失败，使用空的隐藏列表
                self.hidden_files = {}
    
    def save_hidden_files(self):
        """保存当前跑团的隐藏文件列表"""
        if not self.current_campaign:
            return
        
        hidden_file_path = os.path.join(DATA_DIR, self.current_campaign, HIDDEN_FILES_LIST)
        
        try:
            with open(hidden_file_path, 'w', encoding='utf-8') as f:
                for key, filenames in self.hidden_files.items():
                    for filename in filenames:
                        f.write(f"{key}:{filename}\n")
        except Exception:
            # 保存失败时静默处理
            pass
    
    def delete_file(self):
        """删除选中的文件（仅从界面隐藏，不删除实际文件）"""
        sel = self.file_list.curselection()
        if not sel:
            show_themed_info(self.root, "提示", "请先选择要删除的文件")
            return
        
        display_name = self.file_list.get(sel[0])
        filename = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
        
        # 确认删除
        file_type = "文件夹" if display_name.startswith("[DIR] ") else "文件"
        if not ask_themed_yesno(self.root, "确认删除", f"确定要删除{file_type}【{filename}】吗？\n\n注意：这只会从软件中隐藏，不会删除实际文件。"):
            return
        
        # 添加到隐藏列表
        hidden_key = f"{self.current_category}:{self.current_notes_path}" if self.current_category == "notes" else self.current_category
        if hidden_key not in self.hidden_files:
            self.hidden_files[hidden_key] = set()
        
        self.hidden_files[hidden_key].add(filename)
        self.save_hidden_files()
        
        # 刷新文件列表
        self.load_files()
        self.clear_content_viewer()
        
        show_themed_info(self.root, "删除成功", f"{file_type}【{filename}】已从软件中删除\n\n实际文件仍保存在磁盘上")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
