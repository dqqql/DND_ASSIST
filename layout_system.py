"""
布局和间距系统
实现8px网格对齐系统，优化界面区域的间距和边距，改进视觉层次和组件对齐
"""

import tkinter as tk
from typing import Dict, Tuple, Any, Optional, Union
from dataclasses import dataclass
from theme_system import get_theme_manager


@dataclass
class LayoutConfig:
    """布局配置 - 基于8px网格系统的布局规范"""
    
    # 8px网格系统基础单位
    grid_size: int = 8
    
    # 预定义间距值
    xs: int = 4   # 0.5单位
    sm: int = 8   # 1单位
    md: int = 16  # 2单位
    lg: int = 24  # 3单位
    xl: int = 32  # 4单位
    
    # 组件间距配置
    component_spacing: Dict[str, int] = None
    
    # 区域边距配置
    section_margins: Dict[str, int] = None
    
    # 响应式断点配置
    responsive_breakpoints: Dict[str, int] = None
    
    def __post_init__(self):
        """初始化默认配置"""
        if self.component_spacing is None:
            self.component_spacing = {
                "button_group": self.grid_size // 2,      # 4px - 按钮组内间距
                "section": self.grid_size * 2,            # 16px - 区域间距
                "panel": self.grid_size,                  # 8px - 面板间距
                "list_item": self.grid_size // 2,         # 4px - 列表项间距
                "content": self.grid_size * 3,            # 24px - 内容区域间距
                "dialog": self.grid_size * 2,             # 16px - 对话框内间距
                "window_edge": self.grid_size + 2,        # 10px - 窗口边缘间距
                "category_button": self.grid_size         # 8px - 分类按钮间距
            }
        
        if self.section_margins is None:
            self.section_margins = {
                "left_panel": self.grid_size + 2,         # 10px - 左侧面板边距
                "right_panel": self.grid_size + 2,        # 10px - 右侧面板边距
                "top_section": self.grid_size + 2,        # 10px - 顶部区域边距
                "content_viewer": self.grid_size,         # 8px - 内容查看器边距
                "file_list": self.grid_size + 2,          # 10px - 文件列表边距
                "button_area": self.grid_size             # 8px - 按钮区域边距
            }
        
        if self.responsive_breakpoints is None:
            self.responsive_breakpoints = {
                "small": 600,
                "medium": 900,
                "large": 1200
            }
    
    def calculate_spacing(self, component_type: str, context: str = "default") -> int:
        """计算组件在特定上下文中的适当间距"""
        base_spacing = self.component_spacing.get(component_type, self.grid_size)
        
        # 根据上下文调整间距
        context_multipliers = {
            "compact": 0.5,
            "default": 1.0,
            "spacious": 1.5,
            "dialog": 1.25
        }
        
        multiplier = context_multipliers.get(context, 1.0)
        return int(base_spacing * multiplier)
    
    def get_grid_aligned_value(self, value: int) -> int:
        """将值对齐到8px网格"""
        return round(value / self.grid_size) * self.grid_size
    
    def get_section_margin(self, section_type: str) -> int:
        """获取区域边距"""
        return self.section_margins.get(section_type, self.grid_size)


class LayoutManager:
    """布局管理器 - 负责应用布局和间距规范"""
    
    def __init__(self):
        self.config = LayoutConfig()
        self.theme_manager = get_theme_manager()
        self._applied_layouts = set()
    
    def apply_grid_layout(self, widget: tk.Widget, layout_type: str = "default") -> None:
        """为控件应用网格布局"""
        if id(widget) in self._applied_layouts:
            return
        
        # 根据布局类型应用不同的网格配置
        if layout_type == "main_window":
            self._apply_main_window_layout(widget)
        elif layout_type == "left_panel":
            self._apply_left_panel_layout(widget)
        elif layout_type == "right_panel":
            self._apply_right_panel_layout(widget)
        elif layout_type == "button_group":
            self._apply_button_group_layout(widget)
        elif layout_type == "content_area":
            self._apply_content_area_layout(widget)
        
        self._applied_layouts.add(id(widget))
    
    def _apply_main_window_layout(self, window: tk.Widget) -> None:
        """应用主窗口布局"""
        # 设置窗口内边距
        window_padding = self.config.get_section_margin("window_edge")
        
        # 为主窗口的直接子控件设置统一间距
        for child in window.winfo_children():
            child_class = child.__class__.__name__
            if child_class == "Frame":
                # 检查是否是左侧或右侧面板
                try:
                    pack_info = child.pack_info()
                    if pack_info.get("side") == "left":
                        # 左侧面板
                        child.pack_configure(
                            padx=(window_padding, self.config.component_spacing["panel"]),
                            pady=window_padding
                        )
                    elif pack_info.get("side") == "right":
                        # 右侧面板
                        child.pack_configure(
                            padx=(self.config.component_spacing["panel"], window_padding),
                            pady=window_padding
                        )
                except tk.TclError:
                    # 如果控件没有被pack管理，跳过
                    continue
    
    def _apply_left_panel_layout(self, panel: tk.Widget) -> None:
        """应用左侧面板布局"""
        section_spacing = self.config.component_spacing["section"]
        button_spacing = self.config.component_spacing["button_group"]
        
        # 为面板内的控件设置间距
        children = panel.winfo_children()
        for i, child in enumerate(children):
            child_class = child.__class__.__name__
            
            if child_class == "Label":
                # 标题标签
                child.pack_configure(pady=(0, self.config.grid_size))
            elif child_class == "Listbox" or hasattr(child, 'listbox'):
                # 列表控件
                child.pack_configure(pady=(0, self.config.grid_size))
            elif child_class == "Button":
                # 按钮 - 使用较小的间距
                child.pack_configure(pady=button_spacing // 2)
    
    def _apply_right_panel_layout(self, panel: tk.Widget) -> None:
        """应用右侧面板布局"""
        content_spacing = self.config.component_spacing["content"]
        
        # 为右侧面板的子控件设置间距
        children = panel.winfo_children()
        for child in children:
            child_class = child.__class__.__name__
            try:
                pack_info = child.pack_info()
                
                if pack_info.get("side") == "top":
                    # 顶部区域（分类按钮区域）
                    child.pack_configure(pady=(0, self.config.component_spacing["section"]))
                elif pack_info.get("fill") == "both":
                    # 文件管理区域
                    child.pack_configure(pady=0)
            except tk.TclError:
                # 如果控件没有被pack管理，跳过
                continue
    
    def _apply_button_group_layout(self, button_container: tk.Widget) -> None:
        """应用按钮组布局"""
        button_spacing = self.config.component_spacing["button_group"]
        category_spacing = self.config.component_spacing["category_button"]
        
        # 为按钮容器内的按钮设置间距
        for child in button_container.winfo_children():
            if child.__class__.__name__ == "Button":
                try:
                    pack_info = child.pack_info()
                    if pack_info.get("side") == "left":
                        # 分类按钮 - 使用较小间距
                        child.pack_configure(padx=category_spacing)
                    else:
                        # 其他按钮 - 使用标准间距
                        child.pack_configure(padx=button_spacing // 2)
                except tk.TclError:
                    # 如果控件没有被pack管理，跳过
                    continue
    
    def _apply_content_area_layout(self, content_area: tk.Widget) -> None:
        """应用内容区域布局"""
        content_margin = self.config.get_section_margin("content_viewer")
        
        # 为内容区域的子控件设置间距
        for child in content_area.winfo_children():
            child_class = child.__class__.__name__
            try:
                pack_info = child.pack_info()
                
                if child_class == "Label":
                    # 内容标题
                    child.pack_configure(pady=(0, self.config.grid_size))
                elif child_class == "Frame":
                    # 文本或图片显示框架
                    child.pack_configure(pady=0)
            except tk.TclError:
                # 如果控件没有被pack管理，跳过
                continue
    
    def optimize_widget_spacing(self, widget: tk.Widget, widget_type: str) -> None:
        """优化单个控件的间距"""
        if widget_type == "listbox":
            self._optimize_listbox_spacing(widget)
        elif widget_type == "button":
            self._optimize_button_spacing(widget)
        elif widget_type == "text":
            self._optimize_text_spacing(widget)
        elif widget_type == "label":
            self._optimize_label_spacing(widget)
    
    def _optimize_listbox_spacing(self, listbox: tk.Widget) -> None:
        """优化列表框间距"""
        # 设置列表项高度以改善可读性
        theme = self.theme_manager.get_current_theme()
        
        # 计算基于字体大小的最佳行高
        font_size = theme.typography.size_medium
        optimal_height = self.config.get_grid_aligned_value(font_size + self.config.grid_size)
        
        # 应用间距优化
        try:
            listbox.configure(
                # 使用网格对齐的内边距
                selectborderwidth=0,
                # 改善视觉间距
                activestyle="dotbox"
            )
        except tk.TclError:
            pass
    
    def _optimize_button_spacing(self, button: tk.Widget) -> None:
        """优化按钮间距"""
        theme = self.theme_manager.get_current_theme()
        
        # 应用网格对齐的内边距
        padx = self.config.get_grid_aligned_value(theme.spacing.button_padding_x)
        pady = self.config.get_grid_aligned_value(theme.spacing.button_padding_y)
        
        try:
            button.configure(padx=padx, pady=pady)
        except tk.TclError:
            pass
    
    def _optimize_text_spacing(self, text_widget: tk.Widget) -> None:
        """优化文本控件间距"""
        # 设置文本控件的内边距
        padding = self.config.grid_size
        
        try:
            text_widget.configure(
                padx=padding,
                pady=padding
            )
        except tk.TclError:
            pass
    
    def _optimize_label_spacing(self, label: tk.Widget) -> None:
        """优化标签间距"""
        # 标签通常不需要特殊的内边距调整
        # 主要通过pack配置来控制外边距
        pass
    
    def apply_visual_hierarchy(self, container: tk.Widget) -> None:
        """应用视觉层次改进"""
        self._improve_section_separation(container)
        self._enhance_content_grouping(container)
        self._optimize_alignment(container)
    
    def _improve_section_separation(self, container: tk.Widget) -> None:
        """改进区域分离"""
        section_spacing = self.config.component_spacing["section"]
        
        # 为主要区域添加适当的分离间距
        children = container.winfo_children()
        for i, child in enumerate(children):
            try:
                pack_info = child.pack_info()
                
                # 为不同类型的区域设置不同的间距
                if pack_info.get("side") in ["top", "bottom"]:
                    # 水平分离的区域
                    if i > 0:  # 不是第一个子控件
                        current_pady = pack_info.get("pady", 0)
                        if isinstance(current_pady, tuple):
                            new_pady = (max(current_pady[0], section_spacing), current_pady[1])
                        else:
                            new_pady = (section_spacing, current_pady)
                        child.pack_configure(pady=new_pady)
            except tk.TclError:
                # 如果控件没有被pack管理，跳过
                continue
    
    def _enhance_content_grouping(self, container: tk.Widget) -> None:
        """增强内容分组"""
        # 为相关内容添加视觉分组
        group_spacing = self.config.component_spacing["panel"]
        
        # 识别并分组相关控件
        self._group_related_widgets(container, group_spacing)
    
    def _group_related_widgets(self, container: tk.Widget, spacing: int) -> None:
        """分组相关控件"""
        # 这里可以实现更复杂的控件分组逻辑
        # 目前主要通过间距来实现视觉分组
        pass
    
    def _optimize_alignment(self, container: tk.Widget) -> None:
        """优化对齐"""
        # 确保所有控件都对齐到网格
        for child in container.winfo_children():
            self._align_widget_to_grid(child)
    
    def _align_widget_to_grid(self, widget: tk.Widget) -> None:
        """将控件对齐到网格"""
        try:
            pack_info = widget.pack_info()
            
            # 对齐内边距到网格
            padx = pack_info.get("padx", 0)
            pady = pack_info.get("pady", 0)
            
            if isinstance(padx, tuple):
                aligned_padx = (
                    self.config.get_grid_aligned_value(padx[0]),
                    self.config.get_grid_aligned_value(padx[1])
                )
            else:
                aligned_padx = self.config.get_grid_aligned_value(padx)
            
            if isinstance(pady, tuple):
                aligned_pady = (
                    self.config.get_grid_aligned_value(pady[0]),
                    self.config.get_grid_aligned_value(pady[1])
                )
            else:
                aligned_pady = self.config.get_grid_aligned_value(pady)
            
            # 应用对齐后的间距
            try:
                widget.pack_configure(padx=aligned_padx, pady=aligned_pady)
            except tk.TclError:
                pass
        except tk.TclError:
            # 如果控件没有被pack管理，跳过
            pass
    
    def get_responsive_spacing(self, window_width: int, base_spacing: int) -> int:
        """根据窗口宽度获取响应式间距"""
        if window_width < self.config.responsive_breakpoints["small"]:
            return int(base_spacing * 0.75)  # 紧凑模式
        elif window_width > self.config.responsive_breakpoints["large"]:
            return int(base_spacing * 1.25)  # 宽松模式
        else:
            return base_spacing  # 标准模式
    
    def apply_responsive_layout(self, window: tk.Widget) -> None:
        """应用响应式布局"""
        window_width = window.winfo_width()
        
        # 根据窗口宽度调整间距
        if window_width > 1:  # 确保窗口已经渲染
            self._adjust_spacing_for_width(window, window_width)
    
    def _adjust_spacing_for_width(self, container: tk.Widget, width: int) -> None:
        """根据宽度调整间距"""
        # 计算响应式间距
        base_spacing = self.config.component_spacing["section"]
        responsive_spacing = self.get_responsive_spacing(width, base_spacing)
        
        # 应用到主要区域
        for child in container.winfo_children():
            # 检查子控件是否有pack_info方法（排除Toplevel等窗口）
            if not hasattr(child, 'pack_info'):
                continue
                
            try:
                pack_info = child.pack_info()
                if pack_info.get("side") in ["left", "right"]:
                    # 调整面板间距
                    current_padx = pack_info.get("padx", 0)
                    if isinstance(current_padx, tuple):
                        new_padx = (current_padx[0], responsive_spacing)
                        child.pack_configure(padx=new_padx)
            except tk.TclError:
                # 如果控件没有被pack管理，跳过
                continue


# 全局布局管理器实例
layout_manager = LayoutManager()


def get_layout_manager() -> LayoutManager:
    """获取全局布局管理器实例"""
    return layout_manager


def apply_layout_improvements(app_instance) -> None:
    """为应用程序应用布局改进"""
    manager = get_layout_manager()
    
    # 应用主窗口布局
    manager.apply_grid_layout(app_instance.root, "main_window")
    
    # 查找并优化各个区域
    _optimize_app_layout(app_instance, manager)


def _optimize_app_layout(app_instance, manager: LayoutManager) -> None:
    """优化应用程序布局"""
    # 优化左侧面板
    left_panel = _find_widget_by_side(app_instance.root, "left")
    if left_panel:
        manager.apply_grid_layout(left_panel, "left_panel")
        manager.apply_visual_hierarchy(left_panel)
    
    # 优化右侧面板
    right_panel = _find_widget_by_side(app_instance.root, "right")
    if right_panel:
        manager.apply_grid_layout(right_panel, "right_panel")
        manager.apply_visual_hierarchy(right_panel)
    
    # 优化按钮组
    if hasattr(app_instance, 'category_frame'):
        manager.apply_grid_layout(app_instance.category_frame, "button_group")
    
    # 优化内容区域
    if hasattr(app_instance, 'file_frame'):
        manager.apply_grid_layout(app_instance.file_frame, "content_area")
    
    # 优化各种控件的间距
    _optimize_widget_spacing(app_instance, manager)


def _find_widget_by_side(parent: tk.Widget, side: str) -> Optional[tk.Widget]:
    """根据pack的side参数查找控件"""
    for child in parent.winfo_children():
        try:
            pack_info = child.pack_info()
            if pack_info.get("side") == side:
                return child
        except tk.TclError:
            # 如果控件没有被pack管理，跳过
            continue
    return None


def _optimize_widget_spacing(app_instance, manager: LayoutManager) -> None:
    """优化各种控件的间距"""
    # 优化列表控件
    if hasattr(app_instance, 'campaign_list'):
        manager.optimize_widget_spacing(app_instance.campaign_list, "listbox")
    
    if hasattr(app_instance, 'file_list'):
        manager.optimize_widget_spacing(app_instance.file_list, "listbox")
    
    # 优化文本控件
    if hasattr(app_instance, 'content_text'):
        manager.optimize_widget_spacing(app_instance.content_text, "text")
    
    # 优化按钮
    buttons_to_optimize = []
    if hasattr(app_instance, 'action_button'):
        buttons_to_optimize.append(app_instance.action_button)
    if hasattr(app_instance, 'delete_button'):
        buttons_to_optimize.append(app_instance.delete_button)
    if hasattr(app_instance, 'back_button'):
        buttons_to_optimize.append(app_instance.back_button)
    
    for button in buttons_to_optimize:
        manager.optimize_widget_spacing(button, "button")
    
    # 优化分类按钮
    if hasattr(app_instance, 'category_buttons'):
        for button in app_instance.category_buttons.values():
            manager.optimize_widget_spacing(button, "button")


def setup_responsive_layout(window: tk.Widget) -> None:
    """设置响应式布局"""
    manager = get_layout_manager()
    
    def on_window_resize(event):
        if event.widget == window:
            manager.apply_responsive_layout(window)
    
    # 绑定窗口大小变化事件
    window.bind("<Configure>", on_window_resize)


def get_grid_aligned_spacing(value: int) -> int:
    """获取网格对齐的间距值"""
    return get_layout_manager().config.get_grid_aligned_value(value)


def get_component_spacing(component_type: str, context: str = "default") -> int:
    """获取组件间距"""
    return get_layout_manager().config.calculate_spacing(component_type, context)