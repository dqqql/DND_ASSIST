import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import subprocess
import sys
from pathlib import Path

# 导入core层服务
from src.core import CampaignService, FileManagerService
from src.core.config import CATEGORIES, IMAGE_PREVIEW_MAX_WIDTH, IMAGE_PREVIEW_MAX_HEIGHT

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

# 导入Web预览模块
from src.ui.web_preview import WebPreviewManager


def open_file_with_system(path):
    """使用系统默认程序打开文件"""
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

        # 初始化core层服务
        self.campaign_service = CampaignService()
        self.file_service = FileManagerService(self.campaign_service)
        
        # 初始化Web预览管理器
        self.web_preview = WebPreviewManager()
        self.web_preview.set_server_stop_callback(self._on_preview_server_stopped)

        # UI状态变量
        self.current_category = None
        self.category_buttons = {}  # 存储分类按钮
        self.category_handlers = {}  # 存储分类按钮的交互处理器
        self.current_notes_path = ""  # notes 当前路径（相对于 notes 根目录）

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
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

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
        """加载跑团列表"""
        self.campaign_list.delete(0, tk.END)
        campaigns = self.campaign_service.list_campaigns()
        for name in campaigns:
            self.campaign_list.insert(tk.END, name)

    def create_campaign(self):
        """创建新跑团"""
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
        
        # 使用core层服务创建跑团
        if self.campaign_service.create_campaign(name):
            self.load_campaigns()
        else:
            show_themed_error(self.root, "错误", "跑团已存在或创建失败")

    def delete_campaign(self):
        """删除跑团"""
        sel = self.campaign_list.curselection()
        if not sel:
            return
        
        name = self.campaign_list.get(sel[0])
        
        if ask_themed_yesno(self.root, "确认", f"确定删除跑团【{name}】？"):
            if self.campaign_service.delete_campaign(name):
                self.clear_categories()
                self.file_list.delete(0, tk.END)
                self.load_campaigns()
            else:
                show_themed_error(self.root, "错误", "删除跑团失败")

    def on_campaign_select(self, event):
        """跑团选择事件"""
        sel = self.campaign_list.curselection()
        if not sel:
            return
        
        name = self.campaign_list.get(sel[0])
        campaign = self.campaign_service.select_campaign(name)
        
        if campaign:
            self.show_categories()
        else:
            show_themed_error(self.root, "错误", "选择跑团失败")

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
        """加载文件列表"""
        self.file_list.delete(0, tk.END)
        self.clear_content_viewer()
        
        if not self.current_category:
            return
        
        # 使用core层服务获取文件列表
        files = self.file_service.list_files(self.current_category, self.current_notes_path)
        
        for file_info in files:
            display_name = file_info.get_display_name()
            self.file_list.insert(tk.END, display_name)

    def import_file(self):
        """导入文件"""
        if not self.current_category:
            return
        
        files = filedialog.askopenfilenames()
        if not files:
            return
        
        success_count = 0
        for file_path in files:
            if self.file_service.import_file(self.current_category, file_path, self.current_notes_path):
                success_count += 1
        
        if success_count > 0:
            self.load_files()
            show_themed_info(self.root, "导入完成", f"成功导入 {success_count} 个文件")
        else:
            show_themed_error(self.root, "导入失败", "没有文件被成功导入")

    def get_template_content(self, category):
        """根据分类返回模板内容（保留用于向后兼容）"""
        from src.core.config import get_template_content
        return get_template_content(category)

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
        """生成JSON剧情文件模板（保留用于向后兼容）"""
        from src.core.config import get_json_story_template
        return get_json_story_template()

    def create_file(self):
        """创建文件"""
        if not self.current_category:
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
        
        # 根据文件类型添加扩展名
        if file_type == "json":
            if not filename.endswith('.json'):
                filename = filename + ".json"
        else:
            if not filename.endswith('.txt'):
                filename = filename + ".txt"
        
        # 使用core层服务创建文件
        if self.file_service.create_file(self.current_category, filename, self.current_notes_path):
            self.load_files()
            # 创建后自动打开文件
            file_path = self.file_service.get_file_path(self.current_category, filename, self.current_notes_path)
            if file_path:
                open_file_with_system(str(file_path))
        else:
            show_themed_error(self.root, "错误", "文件创建失败或文件已存在")

    def on_file_select(self, event):
        """文件列表选择事件处理"""
        sel = self.file_list.curselection()
        if not sel:
            self.clear_content_viewer()
            return
        
        display_name = self.file_list.get(sel[0])
        
        # 处理 notes 文件夹
        if self.current_category == "notes" and display_name.startswith("[DIR] "):
            # 文件夹不显示内容
            self.clear_content_viewer()
            return
        
        # 获取文件路径
        file_path = self.file_service.get_file_path(self.current_category, display_name, self.current_notes_path)
        if not file_path:
            self.clear_content_viewer()
            return

        # 根据文件类型显示内容
        if self.current_category in ["characters", "monsters"] and str(file_path).endswith('.txt'):
            self.show_text_content(file_path)
        elif self.current_category == "notes":
            if str(file_path).endswith('.json'):
                self.show_json_story_preview_info(file_path, display_name)
            elif str(file_path).endswith('.txt'):
                self.show_text_content(file_path)
        elif self.current_category == "maps":
            self.show_image_content(file_path)
        else:
            self.clear_content_viewer()

    def show_text_content(self, file_path):
        """显示文本文件内容"""
        content = self.file_service.read_text_file(file_path)
        
        if content is not None:
            # 显示文本区域，隐藏图片区域
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.image_frame.pack_forget()
            
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, content)
            self.content_text.config(state=tk.DISABLED)
        else:
            # 错误信息显示在文本区域
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.image_frame.pack_forget()
            
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, "无法读取文件")
            self.content_text.config(state=tk.DISABLED)

    def show_json_story_preview_info(self, file_path, display_name):
        """显示JSON剧情文件的预览信息和操作按钮"""
        story_name = Path(display_name).stem
        campaign = self.campaign_service.get_current_campaign()
        
        if not campaign:
            self._show_preview_error("未选择跑团")
            return
        
        # 显示文本区域，隐藏图片区域
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        self.image_frame.pack_forget()
        
        # 构建预览信息
        info_text = f"剧情文件：{story_name}\n"
        info_text += f"跑团：{campaign.name}\n"
        info_text += f"文件路径：{file_path}\n\n"
        
        # 检查预览文件状态
        from src.ui.web_preview.preview_generator import PreviewGenerator
        generator = PreviewGenerator()
        dot_exists, svg_exists = generator.check_preview_files_exist(campaign.name, story_name)
        
        info_text += "预览文件状态：\n"
        info_text += f"• DOT 文件：{'✓ 已生成' if dot_exists else '✗ 未生成'}\n"
        info_text += f"• SVG 文件：{'✓ 已生成' if svg_exists else '✗ 未生成'}\n\n"
        
        info_text += "编辑器选项：\n"
        info_text += "• Web 编辑器：推荐的现代化编辑体验\n"
        info_text += "• Legacy 编辑器：传统 Tkinter 编辑器（应急使用）\n\n"
        
        if svg_exists:
            info_text += "可以打开剧情图预览。\n\n"
            info_text += "操作说明：\n"
            info_text += "• 双击文件名：使用系统默认程序打开\n"
            info_text += "• 点击下方按钮：选择编辑器或预览方式\n"
        else:
            info_text += "需要先生成预览文件才能查看剧情图。\n\n"
            info_text += "操作说明：\n"
            info_text += "• 双击文件名：使用系统默认程序打开\n"
            info_text += "• 点击下方按钮：选择编辑器或生成预览\n"
        
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, info_text)
        self.content_text.config(state=tk.DISABLED)
        
        # 添加操作按钮
        self._add_story_action_buttons(campaign.name, story_name, svg_exists)
    
    def _add_story_action_buttons(self, campaign_name: str, story_name: str, svg_exists: bool):
        """添加剧情操作按钮到内容区域"""
        # 移除之前的按钮（如果存在）
        if hasattr(self, '_story_action_button_frame'):
            self._story_action_button_frame.destroy()
        
        # 创建按钮框架
        self._story_action_button_frame = tk.Frame(self.text_frame)
        self._story_action_button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # 第一行：编辑器按钮
        editor_frame = tk.Frame(self._story_action_button_frame)
        editor_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Web 编辑器按钮（推荐）
        web_editor_btn = create_themed_button(
            editor_frame,
            text="🌐 Web 编辑器 (推荐)",
            command=lambda: self._open_web_editor(campaign_name, story_name)
        )
        web_editor_btn.pack(side=tk.LEFT, padx=5)
        
        # Legacy 编辑器按钮
        legacy_editor_btn = create_themed_button(
            editor_frame,
            text="📝 Legacy 编辑器",
            command=lambda: self._open_legacy_editor(campaign_name, story_name)
        )
        legacy_editor_btn.pack(side=tk.LEFT, padx=5)
        
        # 第二行：预览按钮
        preview_frame = tk.Frame(self._story_action_button_frame)
        preview_frame.pack(fill=tk.X, pady=(5, 0))
        
        if svg_exists:
            # 如果预览文件存在，显示打开预览按钮
            preview_btn = create_themed_button(
                preview_frame,
                text="🎭 打开剧情图预览",
                command=lambda: self._open_story_preview(campaign_name, story_name)
            )
            preview_btn.pack(side=tk.LEFT, padx=5)
        else:
            # 如果预览文件不存在，显示生成预览按钮
            generate_btn = create_themed_button(
                preview_frame,
                text="🔄 生成预览文件",
                command=lambda: self._generate_and_open_preview(campaign_name, story_name)
            )
            generate_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加刷新按钮
        refresh_btn = create_themed_button(
            preview_frame,
            text="🔄 刷新状态",
            command=lambda: self.on_file_select(None)  # 重新加载当前文件信息
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)
    
    def _open_web_editor(self, campaign_name: str, story_name: str):
        """打开 Web 编辑器"""
        success = self.web_preview.open_story_editor(campaign_name, story_name)
        
        if success:
            show_themed_info(self.root, "Web 编辑器已打开", 
                           f"🚀 Web 编辑器已在浏览器中打开\n\n"
                           f"📋 跑团：{campaign_name}\n"
                           f"📖 剧情：{story_name}\n\n"
                           f"✨ 这是推荐的编辑方式，提供现代化的编辑体验：\n"
                           f"   • 实时保存和数据验证\n"
                           f"   • 响应式界面设计\n"
                           f"   • 智能节点管理\n"
                           f"   • 快捷键支持 (Ctrl+S 保存, Ctrl+N 新建)\n\n"
                           f"💡 使用提示：\n"
                           f"   • 编辑器会自动加载当前跑团和剧情\n"
                           f"   • 所有更改会实时验证数据完整性\n"
                           f"   • 关闭浏览器标签页后服务器将自动停止\n\n"
                           f"🔧 如果遇到问题，可以使用 Legacy 编辑器作为备用方案")
        else:
            show_themed_error(self.root, "打开失败", 
                            "无法打开 Web 编辑器\n\n"
                            "可能的原因：\n"
                            "• 无法启动本地服务器\n"
                            "• 无法打开浏览器\n"
                            "• 端口被占用\n\n"
                            "请尝试使用 Legacy 编辑器作为备用方案。")
    
    def _open_legacy_editor(self, campaign_name: str, story_name: str):
        """打开 Legacy 编辑器"""
        try:
            # 构建剧情文件路径
            campaign = self.campaign_service.get_current_campaign()
            if not campaign:
                show_themed_error(self.root, "错误", "未选择跑团")
                return
            
            story_path = campaign.get_notes_path() / f"{story_name}.json"
            
            if not story_path.exists():
                show_themed_error(self.root, "错误", f"剧情文件不存在：{story_path}")
                return
            
            # 启动 Legacy 编辑器
            import subprocess
            import sys
            from pathlib import Path
            
            editor_script = Path(__file__).parent / "src" / "story_editor" / "editor.py"
            
            # 使用 subprocess 启动编辑器
            subprocess.Popen([
                sys.executable, str(editor_script)
            ], cwd=str(Path(__file__).parent))
            
            show_themed_info(self.root, "Legacy 编辑器已启动", 
                           f"Legacy 编辑器已启动\n\n"
                           f"这是传统的 Tkinter 编辑器，仅用于基础维护和应急修改。\n"
                           f"推荐使用 Web 编辑器获得更好的编辑体验。\n\n"
                           f"请在编辑器中手动打开文件：\n{story_path}")
            
        except Exception as e:
            show_themed_error(self.root, "启动失败", 
                            f"无法启动 Legacy 编辑器\n\n"
                            f"错误信息：{str(e)}\n\n"
                            f"请尝试使用 Web 编辑器。")
    
    def _open_story_preview(self, campaign_name: str, story_name: str):
        """打开剧情预览"""
        success = self.web_preview.open_story_preview(campaign_name, story_name)
        
        if success:
            show_themed_info(self.root, "预览已打开", 
                           f"剧情预览已在浏览器中打开\n\n"
                           f"跑团：{campaign_name}\n"
                           f"剧情：{story_name}\n\n"
                           f"关闭浏览器标签页后服务器将自动停止")
        else:
            show_themed_error(self.root, "打开失败", 
                            "无法打开剧情预览\n\n"
                            "可能的原因：\n"
                            "• 预览文件不存在或损坏\n"
                            "• 无法启动本地服务器\n"
                            "• 无法打开浏览器")
    
    def _generate_and_open_preview(self, campaign_name: str, story_name: str):
        """生成预览文件并打开预览"""
        from src.ui.web_preview.preview_generator import PreviewGenerator
        
        # 显示生成进度
        progress_dialog = create_themed_dialog(self.root, "生成预览", "400x150")
        progress_label = tk.Label(progress_dialog, text="正在生成预览文件，请稍候...")
        progress_label.pack(expand=True)
        
        # 在后台线程中生成预览
        import threading
        
        def generate_preview():
            generator = PreviewGenerator()
            success = generator.generate_preview_for_story(campaign_name, story_name)
            
            # 在主线程中更新UI
            self.root.after(0, lambda: self._on_preview_generated(progress_dialog, success, campaign_name, story_name))
        
        thread = threading.Thread(target=generate_preview, daemon=True)
        thread.start()
    
    def _on_preview_generated(self, progress_dialog, success: bool, campaign_name: str, story_name: str):
        """预览生成完成后的回调"""
        progress_dialog.destroy()
        
        if success:
            # 刷新文件信息显示
            self.on_file_select(None)
            
            # 打开预览
            self._open_story_preview(campaign_name, story_name)
        else:
            show_themed_error(self.root, "生成失败", 
                            "无法生成预览文件\n\n"
                            "可能的原因：\n"
                            "• JSON 文件格式错误\n"
                            "• 缺少必要的工具\n"
                            "• 文件权限问题")
    
    def _show_preview_error(self, error_message: str):
        """显示预览错误信息"""
        # 显示文本区域，隐藏图片区域
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        self.image_frame.pack_forget()
        
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, f"预览错误：{error_message}")
        self.content_text.config(state=tk.DISABLED)
    
    def _on_preview_server_stopped(self):
        """预览服务器停止时的回调"""
        # 可以在这里添加UI状态更新逻辑
        pass

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
        
        # 清理预览按钮
        if hasattr(self, '_story_action_button_frame'):
            self._story_action_button_frame.destroy()
            delattr(self, '_story_action_button_frame')

    def open_selected_file(self, event):
        """双击文件打开，notes 分类双击文件夹进入"""
        sel = self.file_list.curselection()
        if not sel:
            return
        
        display_name = self.file_list.get(sel[0])
        
        # notes 分类双击文件夹进入
        if self.current_category == "notes" and display_name.startswith("[DIR] "):
            folder_name = display_name.replace("[DIR] ", "")
            self.enter_notes_folder(folder_name)
            return
        
        # 获取文件路径
        file_path = self.file_service.get_file_path(self.current_category, display_name, self.current_notes_path)
        if file_path:
            open_file_with_system(str(file_path))
    
    def enter_notes_folder(self, folder_name):
        """进入 notes 子文件夹"""
        if self.current_notes_path:
            self.current_notes_path = str(Path(self.current_notes_path) / folder_name)
        else:
            self.current_notes_path = folder_name
        
        self.update_back_button()
        self.load_files()
    
    def go_back_notes(self):
        """返回 notes 上级目录"""
        if not self.current_notes_path:
            return
        
        # 返回上级目录
        parent_path = Path(self.current_notes_path).parent
        self.current_notes_path = str(parent_path) if str(parent_path) != "." else ""
        
        self.update_back_button()
        self.load_files()
    
    def update_back_button(self):
        """更新返回上级按钮的显示状态"""
        from src.ui.layout_system import get_component_spacing
        
        if self.current_category == "notes" and self.current_notes_path:
            # 在 notes 分类且不在根目录时显示
            back_button_spacing = get_component_spacing("panel")
            self.back_button.pack(side=tk.RIGHT, padx=(0, back_button_spacing))
        else:
            # 其他情况隐藏
            self.back_button.pack_forget()
    
    def delete_file(self):
        """删除选中的文件（软删除，添加到隐藏列表）"""
        sel = self.file_list.curselection()
        if not sel:
            show_themed_info(self.root, "提示", "请先选择要删除的文件")
            return
        
        display_name = self.file_list.get(sel[0])
        
        # 确认删除
        file_type = "文件夹" if display_name.startswith("[DIR] ") else "文件"
        actual_name = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
        
        if not ask_themed_yesno(self.root, "确认删除", f"确定要删除{file_type}【{actual_name}】吗？\n\n注意：这只会从软件中隐藏，不会删除实际文件。"):
            return
        
        # 使用core层服务删除文件
        if self.file_service.delete_file(self.current_category, display_name, self.current_notes_path):
            # 刷新文件列表
            self.load_files()
            self.clear_content_viewer()
            show_themed_info(self.root, "删除成功", f"{file_type}【{actual_name}】已从软件中删除\n\n实际文件仍保存在磁盘上")
        else:
            show_themed_error(self.root, "删除失败", "无法删除文件")
    
    def _on_window_close(self):
        """窗口关闭时的清理工作"""
        # 停止Web预览服务器
        if self.web_preview:
            self.web_preview.stop_server()
        
        # 关闭主窗口
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
