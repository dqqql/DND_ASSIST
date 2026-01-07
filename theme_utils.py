"""
主题工具模块
提供主题应用的便捷函数和装饰器
"""

import tkinter as tk
from typing import Dict, Any, Callable, Optional
from theme_system import get_theme_manager, ThemeManager


def apply_button_theme(button: tk.Button, variant: str = "normal") -> None:
    """为按钮应用主题样式"""
    theme_manager = get_theme_manager()
    theme_manager.apply_theme_to_widget(button, "button", variant)


def apply_listbox_theme(listbox: tk.Listbox) -> None:
    """为列表框应用主题样式"""
    theme_manager = get_theme_manager()
    theme_manager.apply_theme_to_widget(listbox, "listbox", "normal")


def apply_text_theme(text_widget: tk.Text) -> None:
    """为文本控件应用主题样式"""
    theme_manager = get_theme_manager()
    theme_manager.apply_theme_to_widget(text_widget, "text", "normal")


def apply_label_theme(label: tk.Label, variant: str = "normal") -> None:
    """为标签应用主题样式"""
    theme_manager = get_theme_manager()
    theme_manager.apply_theme_to_widget(label, "label", variant)


def apply_frame_theme(frame: tk.Frame, variant: str = "normal") -> None:
    """为框架应用主题样式"""
    theme_manager = get_theme_manager()
    theme_manager.apply_theme_to_widget(frame, "frame", variant)


def create_themed_button(parent: tk.Widget, text: str = "", command: Callable = None, 
                        variant: str = "normal", **kwargs) -> tk.Button:
    """创建应用了主题的按钮"""
    theme_manager = get_theme_manager()
    button_kwargs = {"text": text}
    if command:
        button_kwargs["command"] = command
    button_kwargs.update(kwargs)
    
    return theme_manager.create_themed_widget(parent, tk.Button, "button", variant, **button_kwargs)


def create_themed_listbox(parent: tk.Widget, **kwargs) -> tk.Listbox:
    """创建应用了主题的列表框"""
    theme_manager = get_theme_manager()
    return theme_manager.create_themed_widget(parent, tk.Listbox, "listbox", "normal", **kwargs)


def create_themed_text(parent: tk.Widget, **kwargs) -> tk.Text:
    """创建应用了主题的文本控件"""
    theme_manager = get_theme_manager()
    return theme_manager.create_themed_widget(parent, tk.Text, "text", "normal", **kwargs)


def create_themed_label(parent: tk.Widget, text: str = "", variant: str = "normal", **kwargs) -> tk.Label:
    """创建应用了主题的标签"""
    theme_manager = get_theme_manager()
    label_kwargs = {"text": text}
    label_kwargs.update(kwargs)
    
    return theme_manager.create_themed_widget(parent, tk.Label, "label", variant, **label_kwargs)


def create_themed_frame(parent: tk.Widget, variant: str = "normal", **kwargs) -> tk.Frame:
    """创建应用了主题的框架"""
    theme_manager = get_theme_manager()
    return theme_manager.create_themed_widget(parent, tk.Frame, "frame", variant, **kwargs)


class ListInteractionHandler:
    """增强的列表交互处理器 - 专门处理列表控件的交互效果"""
    
    def __init__(self, listbox: tk.Listbox):
        self.listbox = listbox
        self.theme_manager = get_theme_manager()
        self._hover_index = -1
        self._has_focus = False
        self._setup_list_bindings()
        self._apply_enhanced_styling()
    
    def _setup_list_bindings(self):
        """设置列表特定的事件绑定 - 增强的交互反馈"""
        # 绑定鼠标移动事件以实现hover效果
        self.listbox.bind("<Motion>", self._on_motion, add="+")
        self.listbox.bind("<Leave>", self._on_leave, add="+")
        self.listbox.bind("<Enter>", self._on_enter, add="+")
        
        # 绑定鼠标点击事件
        self.listbox.bind("<Button-1>", self._on_click, add="+")
        self.listbox.bind("<Double-Button-1>", self._on_double_click, add="+")
        
        # 绑定焦点事件 - 清晰的焦点指示器
        self.listbox.bind("<FocusIn>", self._on_focus_in, add="+")
        self.listbox.bind("<FocusOut>", self._on_focus_out, add="+")
        
        # 绑定键盘事件 - 支持键盘导航
        self.listbox.bind("<KeyPress-Up>", self._on_key_up, add="+")
        self.listbox.bind("<KeyPress-Down>", self._on_key_down, add="+")
        self.listbox.bind("<KeyPress-Return>", self._on_key_return, add="+")
        
        # 绑定选择变化事件
        self.listbox.bind("<<ListboxSelect>>", self._on_select, add="+")
    
    def _apply_enhanced_styling(self):
        """应用增强的列表样式 - 改进视觉反馈"""
        theme = self.theme_manager.get_current_theme()
        
        # 设置统一的列表项高度和字体
        self.listbox.configure(
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
            exportselection=False,
            # 设置光标样式
            cursor="hand2"
        )
    
    def _on_motion(self, event):
        """鼠标移动事件 - 实现即时hover效果"""
        # 获取鼠标下的列表项索引
        index = self.listbox.nearest(event.y)
        if 0 <= index < self.listbox.size():
            if index != self._hover_index:
                self._hover_index = index
                self._update_hover_feedback()
        else:
            if self._hover_index != -1:
                self._hover_index = -1
                self._update_hover_feedback()
    
    def _on_leave(self, event):
        """鼠标离开列表 - 清除hover效果"""
        self._hover_index = -1
        self._update_hover_feedback()
        self.listbox.configure(cursor="")
    
    def _on_enter(self, event):
        """鼠标进入列表 - 设置交互光标"""
        self.listbox.configure(cursor="hand2")
    
    def _on_click(self, event):
        """鼠标点击事件 - 即时选择反馈"""
        index = self.listbox.nearest(event.y)
        if 0 <= index < self.listbox.size():
            # 提供即时的点击反馈
            self._add_click_feedback(index)
    
    def _on_double_click(self, event):
        """双击事件 - 增强的双击反馈"""
        index = self.listbox.nearest(event.y)
        if 0 <= index < self.listbox.size():
            # 提供双击反馈效果
            self._add_double_click_feedback(index)
    
    def _on_select(self, event):
        """列表项选择事件 - 选择状态反馈"""
        selection = self.listbox.curselection()
        if selection:
            # 可以在这里添加选择反馈效果
            self._add_selection_feedback(selection[0])
    
    def _on_focus_in(self, event):
        """获得焦点 - 增强的焦点指示器"""
        self._has_focus = True
        theme = self.theme_manager.get_current_theme()
        self.listbox.configure(
            highlightcolor=theme.colors.focus_color,
            highlightthickness=2,
            highlightbackground=theme.colors.focus_color
        )
    
    def _on_focus_out(self, event):
        """失去焦点 - 恢复正常边框"""
        self._has_focus = False
        theme = self.theme_manager.get_current_theme()
        self.listbox.configure(
            highlightcolor=theme.colors.border_color,
            highlightthickness=1,
            highlightbackground=theme.colors.border_color
        )
    
    def _on_key_up(self, event):
        """上箭头键 - 键盘导航反馈"""
        self._add_keyboard_navigation_feedback("up")
    
    def _on_key_down(self, event):
        """下箭头键 - 键盘导航反馈"""
        self._add_keyboard_navigation_feedback("down")
    
    def _on_key_return(self, event):
        """回车键 - 激活当前项"""
        selection = self.listbox.curselection()
        if selection:
            self._add_activation_feedback(selection[0])
    
    def _update_hover_feedback(self):
        """更新hover反馈效果"""
        # 由于Tkinter Listbox的限制，我们主要通过光标和选择状态来提供反馈
        # 在更高级的实现中，可以考虑使用Canvas或其他控件来实现更丰富的hover效果
        pass
    
    def _add_click_feedback(self, index):
        """添加点击反馈效果"""
        # 可以在这里添加点击时的视觉反馈
        # 例如短暂的颜色变化或动画效果
        pass
    
    def _add_double_click_feedback(self, index):
        """添加双击反馈效果"""
        # 可以在这里添加双击时的特殊反馈
        pass
    
    def _add_selection_feedback(self, index):
        """添加选择反馈效果"""
        # 可以在这里添加选择时的反馈效果
        pass
    
    def _add_keyboard_navigation_feedback(self, direction):
        """添加键盘导航反馈"""
        # 可以在这里添加键盘导航时的反馈效果
        pass
    
    def _add_activation_feedback(self, index):
        """添加激活反馈效果"""
        # 可以在这里添加激活时的反馈效果
        pass


def add_list_interaction_feedback(listbox: tk.Listbox) -> ListInteractionHandler:
    """为列表框添加增强的交互反馈"""
    return ListInteractionHandler(listbox)


def create_enhanced_listbox(parent: tk.Widget, **kwargs) -> tk.Listbox:
    """创建增强的主题化列表框"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    # 默认配置
    default_config = {
        "font": theme.typography.get_font_tuple(theme.typography.size_medium),
        "bg": theme.colors.secondary_bg,
        "fg": theme.colors.text_primary,
        "selectbackground": theme.colors.selection_bg,
        "selectforeground": theme.colors.text_primary,
        "relief": tk.SUNKEN,
        "bd": 1,
        "highlightthickness": 1,
        "highlightcolor": theme.colors.focus_color,
        "highlightbackground": theme.colors.border_color,
        "activestyle": "dotbox",
        "selectborderwidth": 0,
        "exportselection": False
    }
    
    # 合并用户配置
    final_config = {**default_config, **kwargs}
    
    # 创建列表框
    listbox = tk.Listbox(parent, **final_config)
    
    # 添加交互反馈
    add_list_interaction_feedback(listbox)
    
    return listbox


class InteractionHandler:
    """增强的交互处理器 - 处理控件的交互状态变化，提供即时视觉反馈"""
    
    def __init__(self, widget: tk.Widget, style_type: str):
        self.widget = widget
        self.style_type = style_type
        self.theme_manager = get_theme_manager()
        self._original_config = {}
        self._is_pressed = False
        self._has_focus = False
        self._is_hovered = False
        self._is_active_button = False  # 用于分类按钮等需要保持激活状态的按钮
        self._setup_bindings()
        self._apply_initial_styling()
    
    def _setup_bindings(self):
        """设置事件绑定 - 增强的交互事件处理"""
        # 保存原始配置
        self._save_original_config()
        
        # 绑定鼠标事件 - 提供即时视觉反馈
        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<Button-1>", self._on_click, add="+")
        self.widget.bind("<ButtonRelease-1>", self._on_release, add="+")
        
        # 绑定焦点事件 - 清晰的焦点指示器
        self.widget.bind("<FocusIn>", self._on_focus_in, add="+")
        self.widget.bind("<FocusOut>", self._on_focus_out, add="+")
        
        # 绑定键盘事件 - 支持键盘交互
        self.widget.bind("<KeyPress-Return>", self._on_key_activate, add="+")
        self.widget.bind("<KeyPress-space>", self._on_key_activate, add="+")
        
        # 绑定状态变化事件
        self.widget.bind("<Configure>", self._on_configure, add="+")
    
    def _apply_initial_styling(self):
        """应用初始样式 - 确保控件有正确的初始外观"""
        if str(self.widget.cget("state")) != "disabled":
            self.theme_manager.apply_theme_to_widget(self.widget, self.style_type, "normal")
            # 设置光标样式以提供视觉提示
            try:
                self.widget.configure(cursor="hand2")
            except tk.TclError:
                pass  # 某些控件可能不支持cursor选项
    
    def _save_original_config(self):
        """保存控件的原始配置"""
        try:
            self._original_config = {
                "bg": self.widget.cget("bg"),
                "fg": self.widget.cget("fg"),
                "relief": self.widget.cget("relief"),
                "cursor": self.widget.cget("cursor") if hasattr(self.widget, 'cursor') else ""
            }
        except tk.TclError:
            # 某些控件可能不支持所有选项
            pass
    
    def _get_current_state(self):
        """获取当前应该显示的状态"""
        if str(self.widget.cget("state")) == "disabled":
            return "disabled"
        elif self._is_pressed:
            return "active"
        elif self._has_focus and not self._is_hovered:
            return "focused"
        elif self._is_hovered:
            return "hover"
        elif self._is_active_button:
            return "active"
        else:
            return "normal"
    
    def _update_visual_state(self):
        """更新视觉状态 - 提供即时反馈"""
        current_state = self._get_current_state()
        self.theme_manager.apply_theme_to_widget(self.widget, self.style_type, current_state)
        
        # 增强焦点指示器的可见性
        if current_state == "focused":
            self._enhance_focus_indicator()
    
    def _enhance_focus_indicator(self):
        """增强焦点指示器的可见性"""
        theme = self.theme_manager.get_current_theme()
        try:
            # 设置更明显的焦点边框
            if hasattr(self.widget, 'configure'):
                self.widget.configure(
                    highlightthickness=2,
                    highlightcolor=theme.colors.focus_color,
                    highlightbackground=theme.colors.focus_color
                )
        except tk.TclError:
            pass
    
    def _on_enter(self, event):
        """鼠标进入事件 - 即时hover反馈"""
        if str(self.widget.cget("state")) != "disabled":
            self._is_hovered = True
            self._update_visual_state()
            
            # 添加微妙的视觉增强
            try:
                self.widget.configure(cursor="hand2")
            except tk.TclError:
                pass
    
    def _on_leave(self, event):
        """鼠标离开事件 - 恢复正常状态"""
        if str(self.widget.cget("state")) != "disabled":
            self._is_hovered = False
            self._update_visual_state()
            
            # 恢复默认光标
            try:
                if not self._has_focus:
                    self.widget.configure(cursor="")
            except tk.TclError:
                pass
    
    def _on_click(self, event):
        """鼠标点击事件 - 即时按下反馈"""
        if str(self.widget.cget("state")) != "disabled":
            self._is_pressed = True
            self._update_visual_state()
            
            # 添加点击反馈效果
            self._add_click_feedback()
    
    def _on_release(self, event):
        """鼠标释放事件 - 恢复适当状态"""
        if str(self.widget.cget("state")) != "disabled":
            self._is_pressed = False
            
            # 检查鼠标是否还在控件内
            try:
                x, y = event.x, event.y
                widget_width = self.widget.winfo_width()
                widget_height = self.widget.winfo_height()
                
                if 0 <= x <= widget_width and 0 <= y <= widget_height:
                    # 鼠标仍在控件内，显示hover状态
                    self._is_hovered = True
                else:
                    # 鼠标已离开控件
                    self._is_hovered = False
            except tk.TclError:
                self._is_hovered = False
            
            self._update_visual_state()
    
    def _on_focus_in(self, event):
        """获得焦点事件 - 清晰的焦点指示器"""
        if str(self.widget.cget("state")) != "disabled":
            self._has_focus = True
            self._update_visual_state()
    
    def _on_focus_out(self, event):
        """失去焦点事件 - 移除焦点指示器"""
        if str(self.widget.cget("state")) != "disabled":
            self._has_focus = False
            self._update_visual_state()
            
            # 重置焦点相关的视觉效果
            try:
                theme = self.theme_manager.get_current_theme()
                self.widget.configure(
                    highlightthickness=1,
                    highlightcolor=theme.colors.border_color,
                    highlightbackground=theme.colors.border_color
                )
            except tk.TclError:
                pass
    
    def _on_key_activate(self, event):
        """键盘激活事件 - 支持键盘交互"""
        if str(self.widget.cget("state")) != "disabled":
            # 模拟点击效果
            self._is_pressed = True
            self._update_visual_state()
            
            # 短暂延迟后恢复
            self.widget.after(100, self._key_release_feedback)
            
            # 触发按钮的command（如果有的话）
            try:
                command = self.widget.cget("command")
                if command:
                    self.widget.invoke()
            except (tk.TclError, AttributeError):
                pass
    
    def _key_release_feedback(self):
        """键盘释放反馈"""
        self._is_pressed = False
        self._update_visual_state()
    
    def _on_configure(self, event):
        """配置变化事件 - 处理状态变化"""
        # 检查是否被禁用
        try:
            if str(self.widget.cget("state")) == "disabled":
                self._is_hovered = False
                self._is_pressed = False
                self._has_focus = False
                self._update_visual_state()
        except tk.TclError:
            pass
    
    def _add_click_feedback(self):
        """添加点击反馈效果"""
        # 可以在这里添加更多的视觉反馈效果
        # 例如轻微的颜色变化或动画效果
        pass
    
    def set_active_state(self, is_active: bool):
        """设置激活状态 - 用于分类按钮等需要保持激活状态的控件"""
        self._is_active_button = is_active
        self._update_visual_state()
    
    def is_active(self) -> bool:
        """检查是否处于激活状态"""
        return self._is_active_button


def add_interaction_feedback(widget: tk.Widget, style_type: str) -> InteractionHandler:
    """为控件添加增强的交互反馈"""
    return InteractionHandler(widget, style_type)


def apply_enhanced_interaction_feedback(parent: tk.Widget) -> None:
    """为所有可点击元素添加增强的交互反馈
    
    递归遍历所有子控件，为可点击的控件添加交互反馈
    """
    def _apply_recursive(widget: tk.Widget):
        widget_class = widget.__class__.__name__
        
        # 为按钮添加交互反馈
        if widget_class == "Button":
            add_interaction_feedback(widget, "button")
        
        # 为列表框添加交互反馈
        elif widget_class == "Listbox":
            add_list_interaction_feedback(widget)
        
        # 为其他可点击控件添加反馈
        elif widget_class in ["Checkbutton", "Radiobutton", "Scale"]:
            add_interaction_feedback(widget, "button")
        
        # 为Entry控件添加焦点反馈
        elif widget_class == "Entry":
            _add_entry_focus_feedback(widget)
        
        # 为Text控件添加焦点反馈
        elif widget_class == "Text":
            _add_text_focus_feedback(widget)
        
        # 递归处理子控件
        try:
            for child in widget.winfo_children():
                _apply_recursive(child)
        except tk.TclError:
            # 某些控件可能不支持winfo_children()
            pass
    
    _apply_recursive(parent)


def _add_entry_focus_feedback(entry: tk.Entry) -> None:
    """为Entry控件添加焦点反馈"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    # 首先应用基本主题样式
    theme_manager.apply_theme_to_widget(entry, "dialog_entry", "normal")
    
    def on_focus_in(event):
        entry.configure(
            highlightthickness=2,
            highlightcolor=theme.colors.focus_color,
            highlightbackground=theme.colors.focus_color,
            bd=2
        )
    
    def on_focus_out(event):
        entry.configure(
            highlightthickness=1,
            highlightcolor=theme.colors.border_color,
            highlightbackground=theme.colors.border_color,
            bd=1
        )
    
    entry.bind("<FocusIn>", on_focus_in, add="+")
    entry.bind("<FocusOut>", on_focus_out, add="+")


def _add_text_focus_feedback(text: tk.Text) -> None:
    """为Text控件添加焦点反馈"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    # 首先应用基本主题样式
    theme_manager.apply_theme_to_widget(text, "text", "normal")
    
    def on_focus_in(event):
        text.configure(
            highlightthickness=2,
            highlightcolor=theme.colors.focus_color,
            highlightbackground=theme.colors.focus_color
        )
    
    def on_focus_out(event):
        text.configure(
            highlightthickness=1,
            highlightcolor=theme.colors.border_color,
            highlightbackground=theme.colors.border_color
        )
    
    text.bind("<FocusIn>", on_focus_in, add="+")
    text.bind("<FocusOut>", on_focus_out, add="+")


def enhance_category_button_feedback(buttons: Dict[str, tk.Button]) -> Dict[str, InteractionHandler]:
    """增强分类按钮的交互反馈
    
    为分类按钮添加特殊的激活状态管理
    """
    handlers = {}
    
    for name, button in buttons.items():
        handler = add_interaction_feedback(button, "button")
        handlers[name] = handler
    
    return handlers


def update_category_button_states(handlers: Dict[str, InteractionHandler], active_category: str) -> None:
    """更新分类按钮的激活状态
    
    确保只有当前选中的分类按钮显示为激活状态
    """
    for name, handler in handlers.items():
        is_active = (name == active_category)
        handler.set_active_state(is_active)


def setup_window_theme(window: tk.Tk) -> None:
    """设置窗口的主题样式"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    # 设置窗口背景色
    window.configure(bg=theme.colors.primary_bg)


def apply_theme_to_existing_widgets(parent: tk.Widget, widget_mapping: Optional[Dict[str, str]] = None) -> None:
    """递归地为现有控件应用主题
    
    Args:
        parent: 父控件
        widget_mapping: 控件类型到样式类型的映射，如果为None则使用默认映射
    """
    if widget_mapping is None:
        widget_mapping = {
            "Button": "button",
            "Listbox": "listbox", 
            "Text": "text",
            "Label": "label",
            "Frame": "frame"
        }
    
    theme_manager = get_theme_manager()
    
    def _apply_recursive(widget: tk.Widget):
        # 获取控件类型
        widget_class = widget.__class__.__name__
        
        # 应用主题
        if widget_class in widget_mapping:
            style_type = widget_mapping[widget_class]
            theme_manager.apply_theme_to_widget(widget, style_type, "normal")
            
            # 为按钮添加交互反馈
            if widget_class == "Button":
                add_interaction_feedback(widget, style_type)
        
        # 递归处理子控件
        for child in widget.winfo_children():
            _apply_recursive(child)
    
    _apply_recursive(parent)


def get_themed_colors() -> Dict[str, str]:
    """获取当前主题的颜色配置"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    return {
        "primary_bg": theme.colors.primary_bg,
        "secondary_bg": theme.colors.secondary_bg,
        "accent_color": theme.colors.accent_color,
        "text_primary": theme.colors.text_primary,
        "text_secondary": theme.colors.text_secondary,
        "text_disabled": theme.colors.text_disabled,
        "button_normal": theme.colors.button_normal,
        "button_hover": theme.colors.button_hover,
        "button_active": theme.colors.button_active,
        "selection_bg": theme.colors.selection_bg,
        "border_color": theme.colors.border_color,
        "focus_color": theme.colors.focus_color,
        "content_bg": theme.colors.content_bg,
        "content_border": theme.colors.content_border
    }


def get_themed_fonts() -> Dict[str, tuple]:
    """获取当前主题的字体配置"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    return {
        "normal": theme.typography.get_font_tuple(),
        "small": theme.typography.get_font_tuple(theme.typography.size_small),
        "medium": theme.typography.get_font_tuple(theme.typography.size_medium),
        "large": theme.typography.get_font_tuple(theme.typography.size_large),
        "title": theme.typography.get_font_tuple(theme.typography.size_title, theme.typography.weight_bold),
        "monospace": theme.typography.get_monospace_font_tuple(),
        "monospace_small": theme.typography.get_monospace_font_tuple(theme.typography.size_small)
    }


def get_themed_spacing() -> Dict[str, int]:
    """获取当前主题的间距配置"""
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    
    return {
        "xs": theme.spacing.xs,
        "sm": theme.spacing.sm,
        "md": theme.spacing.md,
        "lg": theme.spacing.lg,
        "xl": theme.spacing.xl,
        "button_padding_x": theme.spacing.button_padding_x,
        "button_padding_y": theme.spacing.button_padding_y,
        "list_item_height": theme.spacing.list_item_height,
        "section_margin": theme.spacing.section_margin,
        "window_padding": theme.spacing.window_padding,
        "panel_spacing": theme.spacing.panel_spacing
    }