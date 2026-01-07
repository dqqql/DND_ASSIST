"""
主题集成模块
提供与现有应用程序的集成接口，使主题系统能够无缝集成到现有代码中
"""

import tkinter as tk
from typing import Dict, Any, Optional
from theme_system import get_theme_manager, ThemeConfig, ColorPalette, Typography, Spacing
from theme_utils import (
    apply_theme_to_existing_widgets, 
    setup_window_theme,
    add_interaction_feedback,
    get_themed_colors,
    get_themed_fonts,
    get_themed_spacing
)
from layout_system import apply_layout_improvements, setup_responsive_layout


class ThemeIntegrator:
    """主题集成器 - 负责将主题系统集成到现有应用中"""
    
    def __init__(self, app_instance):
        """
        初始化主题集成器
        
        Args:
            app_instance: 现有的App实例
        """
        self.app = app_instance
        self.theme_manager = get_theme_manager()
        self._original_methods = {}
        self._theme_applied = False
    
    def apply_theme_to_app(self) -> None:
        """将主题应用到整个应用程序"""
        if self._theme_applied:
            return
        
        # 设置窗口主题
        setup_window_theme(self.app.root)
        
        # 应用布局和间距改进
        apply_layout_improvements(self.app)
        
        # 设置响应式布局
        setup_responsive_layout(self.app.root)
        
        # 应用主题到现有控件
        self._apply_theme_to_existing_widgets()
        
        # 增强交互反馈
        self._enhance_interaction_feedback()
        
        # 标记主题已应用
        self._theme_applied = True
    
    def _apply_theme_to_existing_widgets(self) -> None:
        """为现有控件应用主题"""
        # 定义控件映射
        widget_mapping = {
            "Button": "button",
            "Listbox": "listbox",
            "Text": "text", 
            "Label": "label",
            "Frame": "frame"
        }
        
        # 递归应用主题
        apply_theme_to_existing_widgets(self.app.root, widget_mapping)
        
        # 特殊处理某些控件
        self._apply_special_widget_themes()
    
    def _apply_special_widget_themes(self) -> None:
        """为特殊控件应用主题"""
        theme = self.theme_manager.get_current_theme()
        
        # 为内容文本区域应用现代化样式
        if hasattr(self.app, 'content_text'):
            # 保存当前的内边距设置
            current_padx = self.app.content_text.cget('padx')
            current_pady = self.app.content_text.cget('pady')
            
            # 应用主题样式
            self.theme_manager.apply_theme_to_widget(self.app.content_text, "text", "normal")
            
            # 恢复内边距设置
            self.app.content_text.config(padx=current_padx, pady=current_pady)
        
        # 为图片标签应用现代化样式
        if hasattr(self.app, 'image_label'):
            self.theme_manager.apply_theme_to_widget(self.app.image_label, "content_image", "normal")
        
        # 为列表控件应用增强样式
        if hasattr(self.app, 'campaign_list'):
            self._apply_enhanced_list_theme(self.app.campaign_list)
        
        if hasattr(self.app, 'file_list'):
            self._apply_enhanced_list_theme(self.app.file_list)
        
        # 为分类按钮应用特殊样式
        if hasattr(self.app, 'category_buttons'):
            for button in self.app.category_buttons.values():
                # 应用按钮主题
                self.theme_manager.apply_theme_to_widget(button, "button", "normal")
                # 添加交互反馈
                add_interaction_feedback(button, "button")
    
    def _apply_enhanced_list_theme(self, listbox: tk.Listbox) -> None:
        """为列表控件应用增强主题"""
        from theme_utils import add_list_interaction_feedback
        
        theme = self.theme_manager.get_current_theme()
        
        # 应用增强的列表样式
        listbox.configure(
            font=theme.typography.get_font_tuple(theme.typography.size_medium),
            bg=theme.colors.secondary_bg,
            fg=theme.colors.text_primary,
            selectbackground=theme.colors.selection_bg,
            selectforeground=theme.colors.text_primary,
            relief=tk.SUNKEN,
            bd=1,
            highlightthickness=1,
            highlightcolor=theme.colors.focus_color,
            highlightbackground=theme.colors.border_color,
            activestyle="dotbox",
            selectborderwidth=0,
            exportselection=False
        )
        
        # 添加交互反馈
        add_list_interaction_feedback(listbox)
    
    def _enhance_interaction_feedback(self) -> None:
        """增强交互反馈"""
        # 为主要按钮添加交互反馈
        buttons_to_enhance = []
        
        # 收集需要增强的按钮
        if hasattr(self.app, 'action_button'):
            buttons_to_enhance.append(self.app.action_button)
        
        if hasattr(self.app, 'delete_button'):
            buttons_to_enhance.append(self.app.delete_button)
        
        if hasattr(self.app, 'back_button'):
            buttons_to_enhance.append(self.app.back_button)
        
        # 为按钮添加交互反馈
        for button in buttons_to_enhance:
            add_interaction_feedback(button, "button")
    
    def update_theme_colors(self, color_overrides: Dict[str, str]) -> None:
        """更新主题颜色"""
        current_theme = self.theme_manager.get_current_theme()
        
        # 创建新的颜色配置
        new_colors = ColorPalette()
        for key, value in color_overrides.items():
            if hasattr(new_colors, key):
                setattr(new_colors, key, value)
        
        # 创建新主题
        new_theme = ThemeConfig(
            name=f"{current_theme.name}_custom",
            colors=new_colors,
            typography=current_theme.typography,
            spacing=current_theme.spacing
        )
        
        # 应用新主题
        self.theme_manager.set_theme(new_theme)
        
        # 重新应用主题
        self._theme_applied = False
        self.apply_theme_to_app()
    
    def get_theme_info(self) -> Dict[str, Any]:
        """获取当前主题信息"""
        return {
            "colors": get_themed_colors(),
            "fonts": get_themed_fonts(),
            "spacing": get_themed_spacing(),
            "applied": self._theme_applied
        }
    
    def reset_to_default_theme(self) -> None:
        """重置为默认主题"""
        default_theme = ThemeConfig(
            name="default",
            colors=ColorPalette(),
            typography=Typography(),
            spacing=Spacing()
        )
        
        self.theme_manager.set_theme(default_theme)
        self._theme_applied = False
        self.apply_theme_to_app()


def integrate_theme_with_app(app_instance) -> ThemeIntegrator:
    """
    将主题系统集成到现有应用程序中
    
    Args:
        app_instance: 现有的App实例
        
    Returns:
        ThemeIntegrator: 主题集成器实例
    """
    integrator = ThemeIntegrator(app_instance)
    integrator.apply_theme_to_app()
    return integrator


def create_themed_dialog(parent: tk.Widget, title: str, geometry: str = "450x180") -> tk.Toplevel:
    """创建应用了主题的对话框"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry(geometry)
    dialog.transient(parent)
    dialog.grab_set()
    
    # 应用主题背景色
    dialog.configure(bg=theme.colors.primary_bg)
    
    # 改进的居中定位 - 相对于父窗口居中
    dialog.update_idletasks()  # 确保几何信息已更新
    
    # 获取父窗口的位置和大小
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    
    # 解析对话框尺寸
    if 'x' in geometry:
        dialog_width, dialog_height = map(int, geometry.split('x'))
    else:
        dialog_width, dialog_height = 450, 180
    
    # 计算居中位置
    center_x = parent_x + (parent_width - dialog_width) // 2
    center_y = parent_y + (parent_height - dialog_height) // 2
    
    # 确保对话框不会超出屏幕边界
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    
    center_x = max(0, min(center_x, screen_width - dialog_width))
    center_y = max(0, min(center_y, screen_height - dialog_height))
    
    dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")
    
    # 设置最小尺寸以防止对话框过小
    dialog.minsize(300, 150)
    
    # 设置对话框图标（如果父窗口有图标）
    try:
        if hasattr(parent, 'iconbitmap') and parent.winfo_toplevel().iconbitmap():
            dialog.iconbitmap(parent.winfo_toplevel().iconbitmap())
    except:
        pass  # 忽略图标设置错误
    
    # 设置对话框样式
    dialog.configure(relief=tk.FLAT, bd=0)
    
    return dialog


def create_themed_dialog_content(dialog: tk.Toplevel, label_text: str, entry_width: int = 35) -> tuple:
    """
    创建应用了主题的对话框内容
    
    Returns:
        tuple: (main_frame, entry_widget, ok_button, cancel_button)
    """
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    # 主框架 - 使用改进的内边距
    main_frame = tk.Frame(dialog, bg=theme.colors.primary_bg)
    main_frame.pack(fill=tk.BOTH, expand=True, 
                   padx=theme.spacing.lg, 
                   pady=theme.spacing.lg)
    
    # 标签 - 改进字体和间距
    label = tk.Label(main_frame, 
                    text=label_text,
                    bg=theme.colors.primary_bg,
                    fg=theme.colors.text_primary,
                    font=theme.typography.get_font_tuple(theme.typography.size_medium))
    label.pack(pady=(0, theme.spacing.md))
    
    # 输入框 - 改进样式和尺寸
    entry = tk.Entry(main_frame, 
                    width=entry_width,
                    font=theme.typography.get_font_tuple(theme.typography.size_medium),
                    relief=tk.FLAT, 
                    bd=2,
                    highlightthickness=2,
                    highlightcolor=theme.colors.focus_color,
                    highlightbackground=theme.colors.border_color,
                    bg=theme.colors.secondary_bg,
                    fg=theme.colors.text_primary,
                    insertbackground=theme.colors.text_primary,
                    selectbackground=theme.colors.selection_bg,
                    selectforeground=theme.colors.text_primary)
    entry.pack(pady=(0, theme.spacing.lg))
    entry.focus()
    
    # 按钮框架 - 改进布局
    button_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    button_frame.pack()
    
    # 确定按钮 - 使用一致的按钮样式
    ok_button = theme_manager.create_themed_widget(
        button_frame, tk.Button, "button", "normal",
        text="确定", width=12
    )
    ok_button.pack(side=tk.LEFT, padx=(0, theme.spacing.sm))
    add_interaction_feedback(ok_button, "button")
    
    # 取消按钮 - 使用一致的按钮样式
    cancel_button = theme_manager.create_themed_widget(
        button_frame, tk.Button, "button", "normal", 
        text="取消", width=12
    )
    cancel_button.pack(side=tk.LEFT, padx=(theme.spacing.sm, 0))
    add_interaction_feedback(cancel_button, "button")
    
    return main_frame, entry, ok_button, cancel_button


def apply_theme_to_new_widgets(parent: tk.Widget) -> None:
    """为新创建的控件应用主题（用于动态创建的控件）"""
    theme_manager = get_theme_manager()
    
    def _apply_to_new_widget(widget: tk.Widget):
        widget_class = widget.__class__.__name__
        
        if widget_class == "Button":
            theme_manager.apply_theme_to_widget(widget, "button", "normal")
            add_interaction_feedback(widget, "button")
        elif widget_class == "Listbox":
            theme_manager.apply_theme_to_widget(widget, "listbox", "normal")
        elif widget_class == "Text":
            theme_manager.apply_theme_to_widget(widget, "text", "normal")
        elif widget_class == "Label":
            theme_manager.apply_theme_to_widget(widget, "label", "normal")
        elif widget_class == "Frame":
            theme_manager.apply_theme_to_widget(widget, "frame", "normal")
    
    # 应用到父控件
    _apply_to_new_widget(parent)
    
    # 递归应用到所有子控件
    for child in parent.winfo_children():
        apply_theme_to_new_widgets(child)


def create_themed_message_dialog(parent: tk.Widget, title: str, message: str, 
                                dialog_type: str = "info", buttons: list = None) -> str:
    """
    创建现代化的消息对话框，替代标准messagebox
    
    Args:
        parent: 父窗口
        title: 对话框标题
        message: 消息内容
        dialog_type: 对话框类型 ("info", "error", "warning", "question")
        buttons: 按钮列表，默认根据类型自动设置
    
    Returns:
        str: 用户点击的按钮名称
    """
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    # 根据对话框类型设置默认按钮
    if buttons is None:
        if dialog_type == "question":
            buttons = ["是", "否"]
        elif dialog_type == "error":
            buttons = ["确定"]
        elif dialog_type == "warning":
            buttons = ["确定"]
        else:  # info
            buttons = ["确定"]
    
    # 计算对话框尺寸
    dialog_width = max(400, len(message) * 8 + 100)
    dialog_width = min(dialog_width, 600)  # 最大宽度限制
    dialog_height = 200 + (len(buttons) - 1) * 20
    
    # 创建对话框
    dialog = create_themed_dialog(parent, title, f"{dialog_width}x{dialog_height}")
    
    result = {"button": None}
    
    # 主框架
    main_frame = tk.Frame(dialog, bg=theme.colors.primary_bg)
    main_frame.pack(fill=tk.BOTH, expand=True, 
                   padx=theme.spacing.lg, 
                   pady=theme.spacing.lg)
    
    # 图标和消息区域
    content_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, theme.spacing.lg))
    
    # 图标（使用文本符号）
    icon_text = {
        "info": "ℹ",
        "error": "✖",
        "warning": "⚠",
        "question": "?"
    }.get(dialog_type, "ℹ")
    
    icon_color = {
        "info": theme.colors.accent_color,
        "error": "#dc3545",
        "warning": "#fd7e14", 
        "question": theme.colors.accent_color
    }.get(dialog_type, theme.colors.accent_color)
    
    icon_label = tk.Label(content_frame,
                         text=icon_text,
                         font=(theme.typography.primary_font[0], 24, "bold"),
                         fg=icon_color,
                         bg=theme.colors.primary_bg)
    icon_label.pack(side=tk.LEFT, padx=(0, theme.spacing.md))
    
    # 消息文本
    message_label = tk.Label(content_frame,
                           text=message,
                           font=theme.typography.get_font_tuple(theme.typography.size_medium),
                           fg=theme.colors.text_primary,
                           bg=theme.colors.primary_bg,
                           wraplength=dialog_width - 120,
                           justify=tk.LEFT)
    message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    button_frame.pack()
    
    # 创建按钮
    for i, button_text in enumerate(buttons):
        def make_button_command(btn_text):
            def command():
                result["button"] = btn_text
                dialog.destroy()
            return command
        
        # 第一个按钮使用强调样式（对于确认操作）
        button_variant = "active" if i == 0 and dialog_type == "question" else "normal"
        
        button = theme_manager.create_themed_widget(
            button_frame, tk.Button, "button", button_variant,
            text=button_text, width=12,
            command=make_button_command(button_text)
        )
        
        # 按钮间距
        padx = (0, theme.spacing.sm) if i < len(buttons) - 1 else (0, 0)
        button.pack(side=tk.LEFT, padx=padx)
        add_interaction_feedback(button, "button")
        
        # 设置默认按钮（第一个按钮）
        if i == 0:
            button.focus()
            dialog.bind('<Return>', lambda e: button.invoke())
    
    # ESC键关闭对话框
    def on_escape(event):
        result["button"] = buttons[-1] if len(buttons) > 1 else buttons[0]
        dialog.destroy()
    
    dialog.bind('<Escape>', on_escape)
    
    # 等待用户操作
    dialog.wait_window()
    
    return result["button"]


def show_themed_info(parent: tk.Widget, title: str, message: str) -> None:
    """显示信息对话框"""
    create_themed_message_dialog(parent, title, message, "info", ["确定"])


def show_themed_error(parent: tk.Widget, title: str, message: str) -> None:
    """显示错误对话框"""
    create_themed_message_dialog(parent, title, message, "error", ["确定"])


def show_themed_warning(parent: tk.Widget, title: str, message: str) -> None:
    """显示警告对话框"""
    create_themed_message_dialog(parent, title, message, "warning", ["确定"])


def ask_themed_yesno(parent: tk.Widget, title: str, message: str) -> bool:
    """显示是/否确认对话框"""
    result = create_themed_message_dialog(parent, title, message, "question", ["是", "否"])
    return result == "是"


# 便捷函数，用于快速集成
def quick_theme_setup(app_instance):
    """快速设置主题（一行代码集成）"""
    return integrate_theme_with_app(app_instance)